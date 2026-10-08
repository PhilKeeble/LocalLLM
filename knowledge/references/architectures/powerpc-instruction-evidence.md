---
id: architecture-powerpc-instruction-evidence
title: PowerPC conditions, r0 operands, rotate masks, reservations and VLE decoding
kind: reference
topics: [powerpc, instruction-semantics, condition-registers, bitfields, vle, atomics]
platforms: [linux, aix, firmware]
architectures: [powerpc]
---
# Selected PowerPC instruction evidence

## Decode the actual core and encoding, not a generic PowerPC label
Reviewed 2026-10-02. This reference uses classic 32-bit PowerPC instruction
semantics and separately scoped e200 VLE evidence. It does not define all later
POWER extensions, 64-bit instruction behavior, console ABIs or privileged state.
Record core revision, byte order, address mode, instruction encoding and memory
map before interpreting a raw firmware region. See
`abi-powerpc64-descriptors-toc-entry` for ELF linkage, not instruction semantics.

Freescale AN4648 describes e200 implementations with 16/32-bit VLE and, on
applicable cores, standard Book E pages. The selected page/region matters; its
example uses MAS2[VLE] to distinguish them. [1] A fixed four-byte sweep can skip
a valid VLE instruction or decode two short operations as one. Do not infer
instruction length solely from the CPU family's register width.

## CMP and CMPL update a selected CR field with different signedness
PowerPC CMP compares signed values; CMPL compares unsigned values. BF chooses
the condition-register field rather than always updating CR0. [2][3]

Constructed 32-bit values 0xffffffff and 1 compare less-than under signed CMP
but greater-than under unsigned CMPL. If the compare writes CR2, a later branch
testing CR0 does not consume that comparison unless an intervening operation
transfers/recomputes the needed condition. Recover the exact field and bit read,
not merely the closest compare mnemonic. Also distinguish word from doubleword
forms on a 64-bit target; this numeric case is deliberately 32-bit.

## ADDI's zero-base r0 encoding does not make r0 a zero register
In the inspected classic PowerPC ADDI form, selecting r0 for the RA operand
means a zero base; the signed immediate becomes the result. ADDI does not
update CR0. [4]

Constructed live r0=0x1000 does not make addi r3,r0,8 produce 0x1008: it produces
8. This is an operand-encoding rule, not permission to replace every r0 read
with zero. Inspect each operation's definition and source/destination positions.
While following an address or a guard, do not assume ADDI refreshed a preceding
comparison's CR bits. An apparent dependency through r0 can be a decoder/model
error rather than a hidden application address calculation.

## RLWINM is rotate then mask; its dot form changes condition evidence
For the classic 32-bit form, RLWINM rotates left by SH and ANDs with the mask
selected by MB/ME; mask ranges may wrap. The dot form updates CR0, the undotted
form does not. [5] PowerPC mask numbering here counts from the most significant
bit: MB=24, ME=31 selects the low byte. [6]

Constructed source 0x12345678 with SH=8, MB=24, ME=31 yields 0x12: rotation
first gives 0x34567812, then the mask keeps 0x12. Treating it as just source&0xff
would produce 0x78 and misidentify a message field. With the undotted form, a
following CR0 test need not describe this result. Do not generalize this 32-bit
example to all wrapping-mask behavior in 64-bit implementations without checking
the selected ISA's word replication and result-width rules.

## Branch conditions, link values and indirect targets need separate tracking
For the inspected classic PowerPC branch forms, BO selects condition/CTR tests,
BI selects a CR bit, and LK requests a link. BCLR targets LR; BCCTR targets CTR.
Classic four-byte linking branches use the following instruction address, not a
MIPS-style PC+8 delay-slot return. [6][7]

Constructed linking branch at 0x2000 gives link 0x2004. A BCLR using a recently
loaded LR is not necessarily a return to this function's caller. Trace the LR or
CTR producer, condition fields and link bit before classifying return, tail call,
callback or jump table. Do not assume every CTR-using branch decrements CTR:
the specific BO encoding and instruction's allowed forms matter.

## STWCX. reports store success through CR0, not through the stored value
For the inspected MPC82x reservation sequence using the matching address,
LWARX establishes a reservation and STWCX. conditionally stores. CR0[EQ]=1 means
store success; without a reservation the store does not occur and EQ=0. [6]

Investigation inference: the BNE retry after STWCX. tests reservation success,
not whether the new integer equals the old integer. Distinguish it from an
earlier comparison implementing a compare-and-swap value check. Record address,
access size, reservation lifetime, CR producer and surrounding barriers. A
conditional store alone does not demonstrate release publication, full ordering
or object lifetime safety. Do not assign a successful store to a mismatched
load-reserve/store-conditional address pair from the mnemonic alone.

## Sources and limits
Reviewed 2026-10-02. Constructed examples are numeric/control-flow reasoning,
not processor tests. Primary vendor references; selected classic forms only.

1. [Freescale AN4648 revision 1, March 2013](https://www.nxp.com/docs/en/application-note/AN4648.pdf): sections 3-5, e200/Book E/VLE distinction; not a universal exception-recovery recipe.
2. [IBM AIX 7.2 CMP](https://www.ibm.com/docs/en/aix/7.2.0?topic=set-cmp-compare-instruction): signed compare and BF.
3. [IBM AIX 7.2 CMPL](https://www.ibm.com/docs/en/aix/7.2.0?topic=set-cmpl-compare-logical-instruction): unsigned compare and BF; inspected indexed primary-page text.
4. [IBM AIX 7.1 ADDI](https://www.ibm.com/docs/en/aix/7.1.0?topic=is-addi-add-immediate-cal-compute-address-lower-instruction): zero-base RA and unchanged CR0.

## Further instruction sources
Reviewed 2026-10-02. Vendor entries below support the rotate, branch and
reservation sections. The historical MPC82x extract has no clear revision on
its title page; scope is its named instruction entries, not current Power ISA.

5. [IBM AIX 7.2 RLWINM](https://www.ibm.com/docs/en/aix/7.2.0?topic=is-rlwinm-rlinm-rotate-left-word-immediate-then-mask-instruction): mask and record variants; inspected indexed primary-page text.
6. [Freescale MPC82x instruction-set extract](https://www.nxp.com/docs/en/reference-manual/MPC82XINSET.pdf): PDF pp. 1-4 notation, 24-27 BCCTR/BCLR, 115-116 RLWINM and 137 STWCX.
7. [IBM AIX BCLR](https://www.ibm.com/docs/nl/aix/7.2?topic=set-bclr-bcr-branch-conditional-link-register-instruction): BO/BI/LK and link behavior; English indexed primary-page text at the locale URL.
