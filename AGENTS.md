# Repository guidance

Before adding, editing, moving or deleting knowledge documents, or changing the RAG service, its retrieval behavior, tests or integration, read [`kb/LIBRARY.md`](kb/LIBRARY.md) in full.

`kb/LIBRARY.md` is the source of truth for the knowledge-base design, folder responsibilities, content quality, document structure, metadata, external-review workflow and validation. Apply its requirements to every future knowledge edit: the result must be accurate, useful during investigation and concise enough for each retrieved passage to stand alone with its necessary scope and caveats.

Never hard-wrap prose at a character or column limit. Keep each Markdown prose paragraph and each individual list item on one physical line; use line breaks only for Markdown structure or intentional semantic separation.

Verify factual claims against primary sources, favor durable concepts and review affected sections in isolation before accepting the change. Summarize the actual source/content/static review and its limits; do not claim retrieval effectiveness from documentation checks. Follow the detailed rules in `kb/LIBRARY.md` rather than maintaining a second rule set here. If an authorized change alters the library design, update `kb/LIBRARY.md` in the same change.
