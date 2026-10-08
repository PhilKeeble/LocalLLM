---
id: reference-parser-python-object-reconstruction
title: Python pickle reconstruction, external buffers and JSON decoding hooks
kind: reference
topics: [parsers, deserialization, python, pickle, json, callbacks, object-invariants]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Python object reconstruction boundaries

## Pickle loading is execution-capable, not passive data inspection

Python warns that unpickling untrusted data can execute arbitrary code.
Unpickler.find_class resolves functions as well as classes and can import a
module. Reduction data can specify a callable and arguments used to reconstruct
an object. [1]

Investigative inference: recover the reachable load/loads/Unpickler call, its
subclass and the actual resolved objects. A module/name pair is not code embedded
in the stream; interpretation depends on the consumer's environment. Do not load
an unknown pickle merely to discover its type. A find_class restriction is a
specific resolution control, not evidence that permitted callbacks, resource
use or application operations are safe. A post-load isinstance check occurs too
late to prevent effects during reconstruction.

## Pickle instance restoration need not run __init__

Ordinary instance unpickling usually bypasses __init__. State restoration can
invoke __setstate__ or populate the instance dictionary; a reduction's None state
does not invoke __setstate__. A supplied state-updating callable can take priority
over __setstate__. [1]

Investigative inference: locate the actual construction and state-update path
rather than crediting a validating __init__ that is not reached. Check whether
an accepted initial state is overwritten later. Follow nested callbacks and
consumers before asserting that a returned instance satisfies its normal class
invariant. An exception after an external effect does not establish rollback.
Do not generalize these rules to every custom reduction callable.

## Pickle persistent IDs resolve through application code

Unpickler.persistent_load resolves persistent IDs through a caller-defined hook;
its default rejects them. Pickle does not define the external object's identity
scheme. [1]

Investigative inference: recover how a persistent ID selects an object, under
whose authority, and whether an earlier validation binds that exact object.
Input containing an identifier is not proof of ownership. Record nested loads as new
deserialization boundaries with their own configuration.

## Pickle load success does not establish whole-input consumption

Python pickle load/loads ignore bytes following the first pickled representation.
[1]

Investigative inference: compare the consumed object extent with the enclosing
transport or file extent. Success does not prove that trailing bytes were examined.
Recover whether another consumer parses the suffix, whether several objects share
a stream, and where parser state resets. Preserve the original representation;
re-pickling the returned object cannot account for discarded trailing content.

## Pickle protocol 5 can depend on separately supplied buffers

Protocol 5 supports out-of-band buffers consumed in stream-reference order.
These buffers can be writable or read-only. Passing buffer views within one
process can reconstruct an object sharing the original backing storage rather
than a deep copy. [2]

Investigative inference: preserve the main stream plus each supplied buffer's
identity, ordering, extent and ownership. Hashing only the main stream does not
identify all input data. Compare dimensions and element widths with actual buffer
capacity; keep metadata validation separate from buffer mutability. If the later
consumer depends on stable contents, identify whether another alias can change
them after validation. Out-of-band does not mean authenticated or immutable.

## pickletools disassembly does not execute pickle bytecode

Python documents pickletools' command-line disassembly as nonexecuting, unlike
loading an object with the pickle module. Its output identifies encoded operations;
memo preservation is a separate option across disassemblies. [3]

Use bounded structural inspection to recover references and construction requests.
Successful disassembly does not establish harmless callbacks or sufficient resource
limits in the real consumer. Avoid adding an inspection step that imports target
modules or calls methods on reconstructed objects. Preserve unsupported or truncated
regions as unresolved evidence, not empty or benign content.

## Python JSON object hooks replace ordinary dictionary results

Python json decoding normally produces built-in values. object_hook can replace
each decoded object's dictionary; object_pairs_hook instead receives ordered
pairs and takes precedence when both hooks are supplied. parse_int, parse_float
and parse_constant provide separate numeric conversion hooks. [4]

Investigative inference: the word JSON does not imply that an application's
binding layer is behavior-free. Follow installed hooks, class hints and factories
before assigning a type-selection or validation contract. Conversely, a type-like
key in plain JSON is not itself arbitrary object activation. Preserve original
pairs when duplicate handling matters; a dictionary can hide an earlier occurrence.
Rejection after a hook returns does not undo the hook's earlier effects.

## Sources and scope

Reviewed 2026-10-02 against Python 3.14.8 documentation and PEP 574. These are
standard-library contracts; third-party serializers and custom subclasses need
their own implementation evidence. No payload was loaded or executed.
Workflow: `playbook-re-object-reconstruction-boundary`.

1. [Python pickle](https://docs.python.org/3/library/pickle.html): security warning, find_class, restoration, reduction, persistent_load and trailing data.
2. [PEP 574](https://peps.python.org/pep-0574/): protocol 5 buffer ordering, mutability and sharing.
3. [pickletools](https://docs.python.org/3/library/pickletools.html): disassembly versus loading and memo scope.
4. [Python json](https://docs.python.org/3/library/json.html): built-in conversion and object/numeric hooks.
