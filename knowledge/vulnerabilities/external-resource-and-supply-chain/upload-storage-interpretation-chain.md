---
id: vulnerability-external-upload-storage-interpretation-chain
title: Untrusted upload stored or interpreted under unsafe authority
kind: vulnerability
topics: [file-upload, storage, content-type, filename, handler, code-execution]
platforms: [cross-platform]
architectures: [any]
---

# Untrusted upload stored or interpreted under unsafe authority

## Definition and violated invariant

This vulnerability occurs when less-trusted uploaded bytes, names, metadata, or replacement rights cause storage outside the intended object boundary or later interpretation by an unsafe handler or authority. The invariant is that upload acceptance, object identity, storage location, replacement policy, content classification, serving policy, and every later interpreter must remain bound to the intended data-only use.

Uploading an executable format is not itself code execution. Prove which component later selects and interprets the stored bytes.

## Conditions that establish the issue

Recover multipart or protocol framing, decoded filename and fields, server-generated identifier, path/object resolution, create/replace semantics, permissions, quotas, content checks, archive processing, metadata persistence, serving headers, handler selection, and activation. Prove attacker influence reaches a protected object or an interpreter with a security-sensitive effect.

Check asynchronous scanners and converters: acceptance may precede quarantine, or a failure path may publish the original. Bind every decision to the exact stored generation so replacement cannot swap bytes after validation.

## Evidence that is not sufficient

An upload endpoint, original filename, executable extension, MIME type, magic bytes, antivirus call, or web-accessible location is not sufficient. Filenames and media types can be ignored or rewritten; content can be served as inert attachment; an interpreter may be absent; or policy may isolate the object.

No single extension, declared type, or signature proves benignness or maliciousness. Polyglot and container formats require the actual downstream parser/handler contract.

## Investigation sequence

Follow one upload generation from transport bytes through temporary storage, validation, move/copy, database identity, object-store key, publication, replacement and final read. Record which actor can mutate each location and whether opens are object-relative and race-resistant. Enumerate every consumer, including preview, indexing, conversion, import, plugin, template, archive and web serving.

For execution claims, identify the exact handler, configuration, invocation arguments, process identity and reachable trigger. For overwrite claims, prove the final resolved object and replacement rights rather than relying on filename text.

## Constructed application example

```text
accepted filename: ../../plugins/report.so
stored path:       upload_root + "/" + decoded_filename
later action:      plugin scanner loads every .so below plugin_root
```

This becomes a chain only if path resolution escapes or aliases into the actual plugin directory, creation/replacement succeeds, the scanner selects the stored bytes, loading occurs, and the scanner's authority matters. If the service replaces the client name with an opaque object key and serves bytes only as attachment, the shown text does not establish the issue.

## Primary sources and scope

Reviewed 2026-10-09 against RFC 7578 [multipart form data](https://www.rfc-editor.org/rfc/rfc7578), RFC 9110 [content metadata semantics](https://www.rfc-editor.org/rfc/rfc9110), WHATWG [MIME sniffing](https://mimesniff.spec.whatwg.org/), and POSIX [`open`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html) and [`rename`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html) contracts. Storage, handler and object-store semantics remain product-specific.
