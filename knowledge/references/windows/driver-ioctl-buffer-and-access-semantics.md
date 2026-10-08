---
id: reference-windows-driver-ioctl-buffer-access
title: Windows driver IOCTL access and buffer semantics
kind: reference
topics: [windows, drivers, ioctl, irp, method-neither, user-pointers, device-security]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows driver IOCTL access and buffer semantics

## Device-control request reachability and access

An IOCTL (I/O control code) selects a driver-defined or system-defined operation;
its presence is not evidence that a caller can invoke that operation. An IOCTL's
security surface depends on the device object's security descriptor,
the access bits encoded in the IOCTL, the handle's granted access, and any
driver authorization. `FILE_ANY_ACCESS` is not inherently a vulnerability, but
it requires deliberate review for privileged operations. Device-interface or
DOS-link discoverability is not the same as authorization.

Device permissions, IOCTL access bits and operation-specific authorization are
different checks. A reachable device name does not establish a usable handle.

## IOCTL encoding and complete dispatch comparison

For a 32-bit IOCTL value c, CTL_CODE encodes DeviceType in bits 31..16,
Access in 15..14, Function in 13..2 and Method in 1..0. Decode as
`(c >> 16) & 0xffff`, `(c >> 14) & 3`, `(c >> 2) & 0xfff`, `c & 3`.
Vendor DeviceType 0x8000..0xffff includes the Common bit; vendor Function
0x800..0xfff includes the Custom bit. Do not discard these bits as padding.
Dispatch must compare the complete IOCTL, not just its function field. [1,2]

Access 0 is FILE_ANY_ACCESS; 1 requires read, 2 write, 3 both on the handle.
ANY_ACCESS does not bypass opening the device. Method 0/1/2/3 denotes BUFFERED,
IN_DIRECT, OUT_DIRECT, NEITHER. IOCTL method bits select transfer behavior;
DO_BUFFERED_IO/DO_DIRECT_IO select read/write-request buffering instead. [1,4]

## Additional access validation and request origin

IoValidateDeviceIoControlAccess can require stricter read/write handle access
than the IOCTL encodes. Its documented implementation checks UserMode requests;
KernelMode requests receive STATUS_SUCCESS without that user access test. The
supported major functions are DEVICE_CONTROL and FILE_SYSTEM_CONTROL, not
arbitrary IRPs. Check the returned NTSTATUS before the sensitive operation. [5]

Inference: a kernel-created replacement request containing user-controlled
operands is not authenticated merely because this helper succeeds. Original
caller identity and IoBuildDeviceIoControlRequest's KernelMode default are
covered in reference-windows-wdm-irp-ownership. Driver-local authorization still
depends on the operation and trust boundary.

## Buffered IOCTL: allocation is not initialized input

METHOD_BUFFERED uses AssociatedIrp.SystemBuffer for both directions. Allocation
size is max(InputBufferLength, OutputBufferLength), but initialized input is
bounded by InputBufferLength and output capacity by OutputBufferLength. [3]
Constructed example: input 8, output 64 gives 64 bytes of storage, not 64 bytes
of supplied input. Reading a 16-byte header is unjustified; returning 64 bytes
after writing eight can expose a tail if those bytes cross the boundary.

In-place output can overwrite input still needed by later validation. Copying
the outer structure does not capture a pointee named by an embedded address;
that is a separate pointer/lifetime boundary. These are data-flow consequences,
not claims that the I/O manager recursively validates driver-defined objects.

## Direct IOCTL: two buffers with separate extents

METHOD_IN_DIRECT and METHOD_OUT_DIRECT use SystemBuffer for the first buffer,
bounded by InputBufferLength. MdlAddress describes the second, whose extent is
OutputBufferLength in both methods. IN_DIRECT checks read access for data the
driver receives there; OUT_DIRECT checks write access for data it produces. [3]
The name OutputBufferLength alone does not establish the second buffer's role.

A system-address mapping can fail or be absent for a zero-length buffer; a
driver must not dereference a NULL mapping result. [2] MDL page locking is not
content immutability. Mapping ownership and deferred-use limits are in
reference-windows-driver-mdl-lifetimes.

## Neither IOCTL: addresses are not captured buffers

METHOD_NEITHER supplies input at Type3InputBuffer and output at UserBuffer,
with their separate stack lengths. The I/O manager supplies neither a system
buffer nor an MDL and does not validate/map these user addresses. [3]
Raw caller virtual addresses require the correct process context; deferring
them to an arbitrary worker is not safe simply because dispatch probed them.
The driver must establish its own appropriate capture or locked-page lifetime.
Lower drivers cannot assume they execute in the original caller's context. [4]

## ProbeForRead and ProbeForWrite do not freeze memory

ProbeForRead checks user address range and requested alignment for nonzero
length; Length=0 performs no address check. It can raise exceptions, requires
IRQL <= APC_LEVEL, and belongs inside exception handling along with subsequent
user-buffer accesses. Do not apply a user-address probe to SystemBuffer's kernel
address. Probing neither locks pages nor captures stable field values. [6]

Microsoft currently discourages ProbeForWrite and recommends ProbeForRead for
new validation code. ProbeForWrite additionally tests initial writability and
writes to pages, with overhead and concurrent-buffer hazards; protection can
still change afterward. ProbeForRead does not test initial writability. Thus
absence of ProbeForWrite is not itself a defect: the subsequent access,
exception handling, capture and request context determine the result. [7]

## Completion counts and actually delivered output

IoStatus.Information is ULONG_PTR and its meaning depends on the request. [8]
For a byte-returning IOCTL, the claimed count must fit output capacity and the
defined response bytes. Input allocation size is not an output authorization.
Inspect structure versions, checked offsets/counts and every completion path.

DeviceIoControl returning FALSE does not always mean zero output: asynchronous
work may be pending, and some operations return partial results with
ERROR_MORE_DATA. Conversely, an arbitrary failure status does not guarantee
buffered copy-back. Establish final status, transfer method, actual count and
delivered bytes before asserting disclosure. [9] Direct/neither-buffer writes
must also be traced at the write itself; completion status is not a rollback.
Shared initialization evidence is in
reference-windows-response-structures-initialization.

WOW64 does not automatically translate the driver-defined buffer contents.
The conversion, original-request identity and layout checks have their primary
home in `reference-windows-wow64-layouts-views`.

## Sources

Reviewed 2026-10-02 against Microsoft DDI buffer, access and completion contracts.
Constructed examples illustrate independent extents, not a tested target driver.

Request ownership and completion are in reference-windows-wdm-irp-ownership
and reference-windows-kmdf-request-ownership. Deferred memory access and MDL
release duties are in reference-windows-driver-mdl-lifetimes; execution/pool
constraints are in reference-windows-driver-irql-pool. Device-state rundown is
in reference-windows-driver-pnp-power-rundown. Use
playbook-re-driver-request-rundown to join these facts for one investigation.

- [1. Defining I/O Control Codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/defining-i-o-control-codes): complete encoding and access fields.
- [2. Security Issues for I/O Control Codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/security-issues-for-i-o-control-codes): full-code comparison, lengths and mapping failures.
- [3. Buffer Descriptions for I/O Control Codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/buffer-descriptions-for-i-o-control-codes): per-method locations and lengths.
- [4. Using Neither Buffered Nor Direct I/O](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-neither-buffered-nor-direct-i-o): execution context and buffering selection.
## Access, probing and completion sources

Reviewed 2026-10-02; API-specific qualifications support the sections above.

- [5. WdmlibIoValidateDeviceIoControlAccess](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdmsec/nf-wdmsec-wdmlibiovalidatedeviceiocontrolaccess): UserMode/KernelMode distinction and supported majors.
- [6. ProbeForRead](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-probeforread): nonzero length, exceptions and IRQL.
- [7. ProbeForWrite](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-probeforwrite): current recommendation versus historical behavior.
- [8. IO_STATUS_BLOCK](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_io_status_block): status and pointer-sized request-dependent Information.
- [9. DeviceIoControl](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-deviceiocontrol): pending and partial-result contracts.
