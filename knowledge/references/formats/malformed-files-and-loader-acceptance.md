---
id: format-malformed-files-loader-acceptance
title: Malformed executable metadata, overlapping mappings and loader acceptance
kind: reference
topics: [binary-parsing, loaders, malformed-input, checked-arithmetic, overlaps, evidence]
platforms: [windows, linux, android, freebsd, macos, ios]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Binary parser and loader acceptance

## Parser output, format validity, loader acceptance and executed behavior
Reviewed 2026-10-02. Keep these claims separate: a tool displayed a structure;
the bytes satisfy a stated format rule; a particular loader accepted the image;
the investigated execution reached the relevant code or data. None automatically
proves the next. LLVM readobj, for example, describes file headers, sections,
symbols and relocations; those inspection outputs are not execution traces. [1]

A permissive parser may recover a useful partial view while a loader rejects
the image. A loader may ignore data used by a debugger or preview handler. Name
the actual consumer: a malformed PDB can reach a symbol parser without the
associated executable ever being launched. Record version, options, diagnostics,
input hash and acceptance boundary instead of labeling the file simply valid.

## Bounded table arithmetic
For a table at byte offset o with entry count c and byte stride s (distance
between entries) in a file of byte length F, first establish nonnegative values
in the parser's domain, o <= F and s > 0.
Then c <= (F - o) / s proves table extent without overflowing c*s. Check format-
required entry sizes separately. Each referenced payload needs its own bound;
a bounded directory does not validate its child offsets or strings.

Constructed case: an eight-byte directory record fits, but its claimed payload
starts beyond F. Accepting the record is not permission to dereference that
payload. Apply checked arithmetic again after alignment, decompression, coordinate
translation and count-to-byte conversion. See
`reference-native-integer-size-buffer-arithmetic` for width/unit mismatches.

## Traversal, termination and resource bounds
Binary format readers must distinguish a specified terminator from reaching the
end of available input. For variable records, prove the next step progresses and
remains bounded; for offset graphs, account for revisits, cycles and depth. Keep
string termination, table-index bounds and record-kind validation separate.

These are investigation obligations, not a claim that every format forbids
shared references or every repeated offset is malicious. A permitted shared node
can require memoization rather than rejection. A tiny input can request enormous
allocation, expansion or traversal work even if every individual read is in bounds.
Trace the consumer's actual resource policy and failure path before claiming DoS.

## Overlaps and competing interpretations
Distinguish overlapping file extents, overlapping virtual byte ranges and merely
shared page-alignment coverage. They are not interchangeable observations. ELF
loading describes file/memory sizes and page alignment; PE defines separate raw
and virtual section coordinates. [2][3]

For an ambiguous address, collect every candidate mapping with its source fields
and full-range checks. Do not choose the first table entry solely because the
analysis tool did. Compare the relevant loader's ordering, page granularity and
reject/overwrite behavior using versioned evidence. Overlap alone proves neither
exploitability nor universal rejection. Preserve alternate interpretations if
loader behavior is unknown; never merge conflicting bytes into one asserted image.

## Pinned Linux executable-loader example
Linux v6.18 fs/binfmt_elf.c load_elf_phdrs requires e_phentsize to equal the
compiled elf_phdr size and rejects a program-header table whose computed size
is zero or greater than 65536 bytes. It reads exactly that table through elf_read;
short reads fail. [4] This is an implementation observation, not the generic ELF
format's maximum and not a promise about every Linux loader or compatibility path.

Constructed inference: a file-inspection tool displaying a larger program-header
table does not establish acceptance by this executable-loading function. Other
checks, including architecture, interpreter and mappings, still apply after the
table passes. Format-level extended counts must not be treated as automatically
supported by this particular code path.

## Evidence needed for a parser defect
A malformed input is a candidate, not itself a vulnerability finding. Identify
the consuming component, attacker-controlled bytes, parse path, broken invariant
and consequence. A graceful rejection can be the intended behavior. A tool crash
needs its own root cause; it does not prove the target application crashes too.

Prefer static bounds and versioned implementation inspection first. Any permitted
dynamic reproduction belongs in an isolated analysis environment with explicit
input provenance; loading a specimen in a production process is not a neutral
format check. Preserve unsupported features and parser disagreement as unknowns
rather than changing metadata until a tool silently produces a convenient view.

## Malformed executable metadata and suspected analysis evasion
Investigation guidance: retain each tool's interpretation of an ambiguous range,
then identify which interpretation the actual consumer uses. Connect any hidden
or misidentified bytes to a feasible decode/load/control-flow path before calling
them concealed executable behavior. A parser disagreement alone does not establish
deliberate evasion: unsupported features, damaged files and tool defects remain
alternative explanations.

Separate two findings: an analysis tool omitted relevant behavior, and a target
parser violated a security invariant. The first can matter in malware analysis
without proving the second. Neither a malformed header nor successful loading
alone establishes malicious intent. See `format-disk-versus-loaded-image` when
disk and captured memory disagree.

## Sources and scope
Reviewed 2026-10-02. Arithmetic/traversal rules above are derived investigation
checks; the concrete Linux acceptance rule is pinned to the inspected release.

1. [LLVM readobj manual](https://llvm.org/docs/CommandGuide/llvm-readobj.html): inspection options, not an OS loading contract.
2. [ELF program loading](https://gabi.xinuos.com/elf/07-pheader.html): segment sizes, alignment and loading view.
3. [Microsoft PE format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format): file/image coordinates and structures.
4. [Linux v6.18 ELF loader](https://raw.githubusercontent.com/torvalds/linux/v6.18/fs/binfmt_elf.c): load_elf_phdrs, elf_read and load_elf_binary.
