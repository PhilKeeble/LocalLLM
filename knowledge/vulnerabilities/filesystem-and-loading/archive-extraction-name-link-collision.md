---
id: vulnerability-filesystem-archive-extraction-name-link-collision
title: Archive extraction collision, case folding, or link-target escape
kind: vulnerability
topics: [filesystem, archives, extraction, collisions, case-folding, links]
platforms: [cross-platform]
architectures: [any]
---

# Archive extraction collision, case folding, or link-target escape

## Definition and violated invariant

An archive extraction filesystem vulnerability occurs when member names, duplicate selection, destination comparison rules, link entries, extraction order, overwrite behavior, or post-extraction resolution cause writes or later reads to target an object outside the intended tree or a different object than the verifier approved. Every member must map to one authorized destination object under the target filesystem and extraction sequence.

Archive-format names and filesystem names have different contracts. Rewriting separators or parent components can collapse distinct members; case-insensitive destinations can collide names distinct in the archive; duplicate lookup and iteration can choose different entries; extracted symlinks or hard links can redirect later members. Format conformance does not prove safe extraction.

## Conditions that establish the issue

Recover archive format and decoder, raw and decoded member names, duplicate records and order, normalization/rewriting, destination filesystem comparison and reserved-name rules, member type and link target, extraction root, directory and link creation, overwrite policy, permissions, sparse/data behavior, verifier/scanner member selection, final object identity, and downstream activation. Prove attacker-controlled archive structure changes a destination or validated-to-extracted object relation and reaches a security-relevant write or use.

For ordered link attacks, show that the extractor actually creates the link and that a later path traverses it under the selected options and platform. A link entry alone is not enough.

## Evidence that is not sufficient

A `../` member, absolute-looking name, duplicate, case variant, symlink entry, extraction warning, rewritten name, overwrite, or file outside the tree is not sufficient. The extractor may reject or safely rewrite the member, avoid following links, identify entries by record, or extract into an isolated tree never activated.

Successful extraction does not prove later execution or use. Connect the published object to its consumer.

## Investigation sequence

Create a member ledger containing record index, raw/decoded name, normalized destination, member type, link target, payload identity, verifier decision, extraction order and final object. Simulate collisions under the actual destination filesystem and record every overwrite or alias. Follow post-extraction moves, installation, loading and execution.

At binary level, recover name decoder, sanitization order, path join, filesystem calls, link branches and overwrite flags. Preserve separate central/local or header/data records where the archive format has them.

## Constructed ordered-link example

```text
member 1: type=symlink, name=cache, target=../../service-config
member 2: type=file,    name=cache/settings.conf, data=attacker_content
```

If the target extractor creates member 1 as a filesystem symlink and then opens member 2 through ordinary link-following resolution, the file write can leave the extraction root. The finding requires that exact ordering, link support, resolution behavior, permissions and successful write. Extractors that reject links, defer them safely, or constrain every component change the conclusion.

## Primitive and impact limits

The direct primitive is unintended filesystem object selection during extraction or verifier/extractor disagreement about a member. Consequences include overwrite, disclosure through replacement, configuration or dependency substitution, persistence, or later code execution. Extraction destination authority and downstream activation determine impact; an isolated unused tree narrows it.

## Related knowledge and primary sources

`reference-parser-archive-member-identity`, `reference-parser-archive-extraction-effects`, archive expansion references, and `vulnerability-parser-archive-extraction-boundary-violation` provide format and resource detail. This profile keeps destination filesystem collisions and ordered link effects local.

Reviewed 2026-10-09 against POSIX [pax archive interchange](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/pax.html), PKWARE [APPNOTE](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT), libarchive [`archive_write_disk` source manual](https://github.com/libarchive/libarchive/blob/master/libarchive/archive_write_disk.3), and Python [`tarfile`](https://docs.python.org/3/library/tarfile.html) and [`zipfile`](https://docs.python.org/3/library/zipfile.html) for scoped implementation examples. The member sequence is constructed; target options and behavior must be established.
