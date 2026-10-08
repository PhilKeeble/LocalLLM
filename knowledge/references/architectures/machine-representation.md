---
id: architecture-machine-representation
title: Machine representation, endian decoding, extensions, alignment and bitfields
kind: reference
topics: [representation, endianness, signedness, extension, alignment, bitfields]
platforms: [windows, linux, macos, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Machine representation

## Scope: bytes, decoded values and source types are distinct

These are representation rules and investigative checks, not one universal ABI.
Examples assume 8-bit bytes and ordinary binary integers. Record byte order,
storage width, operation width, address space and consumer for each field.
Instruction semantics establish operations; language and ABI metadata constrain
types. A plausible decompiler type alone establishes neither. [1,2]

## Endianness belongs to each representation

Little-endian stores the least significant byte first; big-endian stores the most
significant first. This describes byte ordering, not the direction of shifts or
the numbering of bits in an integer. A file/protocol encoding need not match its
consumer's native order; different layers of a container can differ. [1]

Constructed example: bytes `01 00 00 80` decode as unsigned little-endian
`0x80000001` (2147483649), or big-endian `0x01000080` (16777344). A two's-complement
signed interpretation of the former is -2147483647. Preserve the raw bytes and
the selected decoding separately. A byteswap seen twice may belong to two
different representations; follow the actual value before calling it redundant.

## Extension and truncation preserve different information

For an N-bit two's-complement value widened to M bits, sign extension repeats
bit N-1; zero extension inserts zeros. Narrowing to the low N bits discards high
bits. These are bit operations; an instruction's use of them does not by itself
prove a source-language signed type. Current C++ integral-conversion rules use
the destination value congruent to the source modulo 2^N, where N is the
destination type's width, except conversions involving Boolean values;
older language editions need their own rules for out-of-range signed results. [2,3]

Constructed byte example: `0x80` zero-extends to `0x00000080` (128) and
sign-extends to `0xffffff80` (-128 as signed 32-bit). Both truncate back to
`0x80`; a round trip to the narrow representation therefore does not prove that
the two wider values are equivalent for bounds checks. Follow extensions at
loads, calls and comparisons, not just casts displayed by the decompiler.

## Alignment is not merely whether a memory access faults

Object alignment constrains placement in the C++ object model. Creating an
object in inadequately aligned storage is undefined behavior even if the CPU
accepts an unaligned access. Hardware behavior additionally depends on the
instruction, memory type and machine configuration. [4]

Investigative procedure: recover effective address, access width, required
alignment and object extent independently. A successful scalar load does not
validate a later vector/atomic access. A packed wire record is not automatically
a valid native object; identify actual byte decoding or the compiler's packed
access contract. See `reference-native-integer-size-buffer-arithmetic` for
checked alignment rounding; alignment alone does not establish sufficient size.

## Bitfields and masks do not reveal a portable C structure

C++ bitfield allocation and alignment are implementation-defined; fields may
straddle storage units, and allocation direction differs across implementations.
Do not derive a native bitfield layout solely from the CPU's endianness. [5]

Constructed decoding: `(word >> 5) & 7` extracts bits 5..7 of the already-decoded
integer. It does not reveal which byte was first in the input, whether adjacent
bits are reserved, or whether the original declaration used a bitfield. Record
the load width, byte conversion, mask, shift and validation separately. For a
signed packed field, locate its sign extension before interpreting its range.

## Pointer-looking values and address arithmetic

An integer matching a mapped address is not sufficient evidence of a usable
pointer. It may be a relative offset, index, tagged value or encoded fixup.
Identify base, scale, address space and any decoding before naming a field.
C++ pointer arithmetic is constrained by the corresponding array object,
including its one-past endpoint; numerical adjacency alone is insufficient. [6]

Investigation: preserve file offsets, module-relative offsets and runtime
addresses in separate columns. Test the full accessed range, permissions and
lifetime, not just whether its first byte is mapped. Pointer representation,
canonicality and authentication require architecture/platform-specific evidence.

## Sources and verification scope

Reviewed 2026-10-02. Current C++ working draft provides language facts, not a
claim that an unknown legacy target used that edition. Examples are constructed
arithmetic, not observed target behavior.

1. [Endian definitions](https://eel.is/c++draft/bit.endian).
2. [Fundamental integer representations](https://eel.is/c++draft/basic.fundamental).
3. [Integral conversions](https://eel.is/c++draft/conv.integral).
4. [Object alignment](https://eel.is/c++draft/basic.align).
5. [Bitfield allocation](https://eel.is/c++draft/class.bit).
6. [Pointer arithmetic](https://eel.is/c++draft/expr.add).
