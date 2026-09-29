"""Offline Markdown retrieval: SQLite FTS5 and safe YAML front matter."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import yaml
from errors import RequestError

API_VERSION = 1
CHUNK_CHARS = 1800
STOP = set("a an the is are was were be been being to of in on at for from with and or if then it its this that these those i me my you your we our they their please can could would should will do does did have has how what which when where why use using used write create implement make give explain tell about as by into all any just some task file files code function functions return returns need want look review inspect analyze analyse".split())


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def terms(text: str) -> list[str]:
    text = re.sub(r"c\+\+|\bcxx\b", " cpp ", text.lower())
    return list(dict.fromkeys(t for t in re.findall(r"0x[0-9a-f]+|[a-z_][a-z0-9_]*|[0-9]+", text)
                             if t not in STOP and len(t) > 1))


def chunks(text: str):
    """Contiguous exact source slices; headings retained as searchable metadata."""
    start, pos, heading, fenced = 0, 0, "", False
    for line in text.splitlines(keepends=True):
        is_heading = not fenced and re.match(r"^#{1,6}\s+", line)
        if pos > start and (is_heading or pos + len(line) - start > CHUNK_CHARS):
            yield start, pos, heading
            start = pos
        if is_heading:
            heading = line.strip().lstrip("#").strip()
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        # Even one oversized line is fully recoverable without a hidden prefix.
        while pos + len(line) - start > CHUNK_CHARS:
            end = start + CHUNK_CHARS
            yield start, end, heading
            start = end
        pos += len(line)
    if start < len(text):
        yield start, len(text), heading


def metadata(text: str, path: str):
    values, body_start = {}, 0
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end < 0 or end > 16000:
            raise ValueError(f"Missing or oversized YAML front matter in {path}")
        header = text[4:end]
        if any(isinstance(token, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken)) for token in yaml.scan(header)):
            raise ValueError(f"YAML aliases/anchors are not supported in {path}")
        values = yaml.safe_load(header) or {}
        body_start = end + 5
        if not isinstance(values, dict) or any(key not in {"id", "title", "kind", "topics", "platforms", "architectures"} for key in values):
            raise ValueError(f"Invalid metadata keys in {path}; use id/title/kind/topics/platforms/architectures")
    result = {"id": path, "kind": "reference", "topics": [], "platforms": [], "architectures": [], **values, "path": path}
    if not isinstance(result["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,255}", result["id"]):
        raise ValueError(f"Invalid document id in {path}")
    if result["kind"] not in ("playbook", "reference", "note"):
        raise ValueError(f"Invalid kind in {path}")
    if "title" in result and (not isinstance(result["title"], str) or not 0 < len(result["title"]) <= 300):
        raise ValueError(f"Invalid title in {path}")
    for key in ("topics", "platforms", "architectures"):
        items = result[key]
        if not isinstance(items, list) or len(items) > 32 or any(not isinstance(item, str) or not 0 < len(item) <= 64 for item in items):
            raise ValueError(f"{key} must be a list of up to 32 short strings in {path}")
        result[key] = list(dict.fromkeys(item.lower() for item in items))
    return result, body_start


def integer(data, name, default, minimum, maximum):
    value = data.get(name, default)
    if type(value) is not int or not minimum <= value <= maximum:
        raise RequestError(f"{name} must be an integer between {minimum} and {maximum}")
    return value


def string(data, name, default=None, maximum=16000):
    value = data.get(name, default)
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise RequestError(f"{name} must be a nonempty string of at most {maximum} characters")
    return value


class Index:
    def __init__(self, documents: Path, database: Path):
        self.documents = documents.resolve()
        database.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(database, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        self.last_scan = 0.0
        self.error = None
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS revisions (
                source_id TEXT, revision TEXT, title TEXT, text TEXT,
                PRIMARY KEY (source_id, revision));
            CREATE TABLE IF NOT EXISTS current (source_id TEXT PRIMARY KEY, revision TEXT);
            CREATE TABLE IF NOT EXISTS source_metadata (
                source_id TEXT, revision TEXT, metadata TEXT, PRIMARY KEY (source_id, revision));
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY, source_id TEXT, revision TEXT, heading TEXT,
                start INTEGER, end INTEGER, start_line INTEGER, end_line INTEGER, text TEXT);
            CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(title, heading, body);
        """)
        self.refresh(force=True)

    def close(self):
        self.db.close()

    def revision(self):
        row = self.db.execute("SELECT value FROM metadata WHERE key='revision'").fetchone()
        return row[0] if row else ""

    def refresh(self, force=False):
        with self.lock:
            if not force and time.monotonic() - self.last_scan < 5:
                return
            self.last_scan = time.monotonic()
            try:
                if not self.documents.is_dir():
                    raise ValueError(f"Document directory unavailable: {self.documents}")
                sources, ids = [], set()
                for path in sorted(self.documents.rglob("*.md")):
                    resolved = path.resolve()
                    if not resolved.is_relative_to(self.documents) or path.is_symlink():
                        raise ValueError(f"Symlink/out-of-library document rejected: {path.name}")
                    if path.stat().st_size > 32 * 1024 * 1024:
                        raise ValueError(f"Split document larger than 32 MiB into chapters: {path.name}")
                    text = path.read_text(encoding="utf-8-sig")
                    meta, body_start = metadata(text, path.relative_to(self.documents).as_posix())
                    source_id = meta["id"]
                    if source_id in ids:
                        raise ValueError(f"Duplicate document id: {source_id}")
                    ids.add(source_id)
                    title = meta.get("title") or next((line[2:].strip() for line in text[body_start:].splitlines() if line.startswith("# ")), source_id)
                    sources.append((source_id, digest(text), title, text, meta, body_start))
                revision = digest(json.dumps(["metadata-v1", [(s[0], s[1], s[4]) for s in sources]]))
                if revision != self.revision():
                    with self.db:
                        self.db.execute("DELETE FROM current")
                        self.db.execute("DELETE FROM chunks")
                        self.db.execute("DELETE FROM search")
                        for source_id, source_rev, title, text, meta, body_start in sources:
                            self.db.execute("INSERT OR IGNORE INTO revisions VALUES (?,?,?,?)", (source_id, source_rev, title, text))
                            self.db.execute("INSERT OR REPLACE INTO source_metadata VALUES (?,?,?)", (source_id, source_rev, json.dumps(meta)))
                            self.db.execute("INSERT INTO current VALUES (?,?)", (source_id, source_rev))
                            for start, end, heading in chunks(text[body_start:]):
                                start, end = start + body_start, end + body_start
                                body = text[start:end]
                                cursor = self.db.execute("INSERT INTO chunks(source_id,revision,heading,start,end,start_line,end_line,text) VALUES (?,?,?,?,?,?,?,?)",
                                    (source_id, source_rev, heading, start, end, text.count("\n", 0, start) + 1,
                                     text.count("\n", 0, max(start, end - 1)) + 1, body))
                                self.db.execute("INSERT INTO search(rowid,title,heading,body) VALUES (?,?,?,?)",
                                    (cursor.lastrowid, " ".join(terms(title + " " + source_id + " " + meta["kind"] + " " + " ".join(meta["topics"] + meta["platforms"] + meta["architectures"]))),
                                     " ".join(terms(heading)), " ".join(terms(body))))
                        self.db.execute("INSERT OR REPLACE INTO metadata VALUES ('revision',?)", (revision,))
                self.error = None
            except (OSError, UnicodeError, ValueError, sqlite3.Error, yaml.YAMLError) as exc:
                # Transaction rollback preserves the last complete generation.
                self.error = str(exc)

    def status(self):
        with self.lock:
            self.refresh()
            return dict(api_version=API_VERSION, ok=self.error is None,
                        status="stale" if self.error else "success", backend="sqlite-fts5",
                        index_revision=self.revision(), documents=self.db.execute("SELECT count(*) FROM current").fetchone()[0],
                        chunks=self.db.execute("SELECT count(*) FROM chunks").fetchone()[0], error=self.error,
                        recovery="Correct the Markdown library; indexing retries on the next request after five seconds." if self.error else None)

    def search(self, data):
        query = string(data, "query")
        offset = integer(data, "offset", 0, 0, 100000000)
        limit = integer(data, "limit", 8, 1, 20)
        context_limit = integer(data, "context_limit", 0, 0, 20)
        tokens = terms(query)
        if len(tokens) > 512:
            raise RequestError("Query has more than 512 distinct terms. Search with a focused question or identifier.")
        with self.lock:
            self.refresh()
            if self.error:
                raise RequestError(f"Index refresh failed; repair the Markdown library and retry: {self.error}", 503)
            revision = self.revision()
            if offset and not data.get("index_revision"):
                raise RequestError("Pagination requires index_revision from the first page.")
            if data.get("index_revision", revision) != revision:
                raise RequestError("Index changed. Repeat the search at offset 0.", 409)
            where, args = "search MATCH ?", [" OR ".join('"' + t + '"' for t in tokens)]
            if data.get("source_id") is not None:
                where += " AND c.source_id=?"
                args.append(string(data, "source_id", maximum=1024))
            filters = data.get("filters", {})
            if not isinstance(filters, dict) or any(key not in ("kind", "topic", "platform", "architecture") for key in filters):
                raise RequestError("filters supports kind, topic, platform, architecture")
            for key in filters:
                value = string(filters, key, maximum=64).lower()
                if key == "kind":
                    where += " AND json_extract(m.metadata,'$.kind')=?"
                else:
                    plural = {"topic": "topics", "platform": "platforms", "architecture": "architectures"}[key]
                    where += f" AND EXISTS(SELECT 1 FROM json_each(m.metadata,'$.{plural}') WHERE value=?)"
                args.append(value)
            join = "search JOIN chunks c ON c.id=search.rowid JOIN source_metadata m ON m.source_id=c.source_id AND m.revision=c.revision"
            total, matches, context_matches = 0, [], []
            if tokens:
                total = self.db.execute(f"SELECT count(*) FROM {join} WHERE {where}", args).fetchone()[0]
                rows = self.db.execute(f"SELECT c.*, m.metadata, bm25(search,3,2,1) AS score FROM {join} WHERE {where} ORDER BY c.source_id,c.start LIMIT ? OFFSET ?", args + [limit, offset]).fetchall()
                for row in rows:
                    item = dict(row)
                    item.pop("id")
                    item["metadata"] = json.loads(item["metadata"])
                    item["citation"] = f"kb:{item['source_id']}@{item['revision']}:{item['start']}-{item['end']}"
                    matches.append(item)
                if context_limit:
                    # Complete search evidence remains available, but provisional
                    # learned notes must not silently become automatic guidance.
                    context_where = where + " AND NOT EXISTS(SELECT 1 FROM json_each(m.metadata,'$.topics') WHERE value='unreviewed')"
                    ranked = self.db.execute(f"SELECT c.*, m.metadata, bm25(search,3,2,1) AS score FROM {join} WHERE {context_where} ORDER BY score,c.source_id,c.start LIMIT ?", args + [context_limit]).fetchall()
                    # A limit is a ceiling, not a quota. Avoid padding a good
                    # match with much weaker passages just to fill the packet.
                    best_score = ranked[0]["score"] if ranked else 0
                    ranked = [row for position, row in enumerate(ranked)
                              if position < 2 or row["score"] <= best_score * 0.65]
                    for rank, row in enumerate(ranked, 1):
                        item = dict(row)
                        item.pop("id")
                        item["metadata"] = json.loads(item["metadata"])
                        item["rank"] = rank
                        item["citation"] = f"kb:{item['source_id']}@{item['revision']}:{item['start']}-{item['end']}"
                        context_matches.append(item)
                    context_matches.sort(key=lambda item: (item["source_id"], item["start"]))
            next_offset = offset + len(matches) if offset + len(matches) < total else None
            return dict(api_version=API_VERSION, ok=True, status="no_matches" if not total else "truncated" if next_offset is not None else "success",
                        index_revision=revision, query=query, query_terms=tokens, filters=filters, order="source_id,start",
                        score_note="BM25; lower scores indicate stronger lexical matches. Rows are in source order.",
                        collection_partial=False, total=total, offset=offset, returned=len(matches),
                        truncated=next_offset is not None, next_offset=next_offset, matches=matches,
                        context_selection={"method": "BM25: retain best two candidates, then require 65% of best score magnitude; exclude unreviewed; present in source order", "limit": context_limit,
                                           "protected_top_ranks": 2,
                                           "relative_score_floor": 0.65,
                                           "excluded_topic": "unreviewed",
                                           "selected": len(context_matches), "omitted": total - len(context_matches),
                                           "complete_evidence": "Page /search matches in source order; context_matches is a selected context packet, not the complete search result."},
                        context_matches=context_matches)

    def read(self, data):
        source_id = string(data, "source_id", maximum=1024)
        revision = string(data, "revision", maximum=64)
        offset = integer(data, "offset", 0, 0, 100000000)
        limit = integer(data, "limit", 6000, 1, 16000)
        with self.lock:
            row = self.db.execute("SELECT title,text FROM revisions WHERE source_id=? AND revision=?", (source_id, revision)).fetchone()
            if row is None:
                raise RequestError("Unknown source revision. Use /search to obtain an existing source_id and revision.", 404)
            if offset > len(row["text"]):
                raise RequestError("offset exceeds source length")
            text = row["text"][offset:offset + limit]
            meta = self.db.execute("SELECT metadata FROM source_metadata WHERE source_id=? AND revision=?", (source_id, revision)).fetchone()
            end = offset + len(text)
            return dict(api_version=API_VERSION, ok=True, status="truncated" if end < len(row["text"]) else "success",
                        source_id=source_id, revision=revision, title=row["title"], metadata=json.loads(meta[0]) if meta else {}, offset=offset,
                        returned=len(text), total=len(row["text"]), text=text, offset_unit="Unicode code points",
                        truncated=end < len(row["text"]), next_offset=end if end < len(row["text"]) else None,
                        citation=f"kb:{source_id}@{revision}:{offset}-{end}")


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def respond(self, status, body):
        encoded = json.dumps(body, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path not in ("/health", "/status"):
            self.respond(404, dict(api_version=1, ok=False, status="failed", error="Unknown endpoint"))
            return
        result = self.server.index.status()
        self.respond(200 if result["ok"] else 503, result)

    def do_POST(self):
        try:
            if self.path not in ("/search", "/read"):
                raise RequestError("Unknown endpoint", 404)
            length = self.headers.get("Content-Length", "")
            if not length.isdigit() or not 0 < int(length) <= 128000:
                raise RequestError("A Content-Length between 1 and 128000 bytes is required.", 413)
            data = json.loads(self.rfile.read(int(length)))
            if not isinstance(data, dict):
                raise RequestError("Expected a JSON object")
            result = self.server.index.search(data) if self.path == "/search" else self.server.index.read(data)
            self.respond(200, result)
        except (ValueError, UnicodeError) as exc:
            self.respond(400, dict(api_version=1, ok=False, status="failed", error=f"Invalid JSON: {exc}"))
        except RequestError as exc:
            self.respond(exc.status, dict(api_version=1, ok=False, status="failed", error=str(exc)))
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            return
        except Exception:
            self.respond(500, dict(api_version=1, ok=False, status="failed", error="Internal retrieval error; inspect the KB container logs."))
            raise


def serve(index, host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), Handler)
    server.index = index
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--documents", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    index = Index(args.documents, args.database)
    server = serve(index, args.host, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        index.close()


if __name__ == "__main__":
    main()
