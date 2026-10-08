---
id: reference-native-binary-protocol-framing-deserialization
title: Binary protocol framing and deserialization boundaries
kind: reference
topics: [serialization, deserialization, framing, parsers, length-fields, type-confusion]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# Binary protocol framing and deserialization boundaries

## TCP receive boundaries do not define application message boundaries

TCP is a byte stream: application writes, TCP segments and receiving read buffers
do not have guaranteed one-to-one boundaries. [1] A parser needs its application
framing rule independently of the socket's successful return.

Recover actual bytes available and buffered state, not merely the requested read
size. One read can contain part of a message or bytes from several messages.
Preserve the distinction between transport completion, frame completion and
object decoding; success at an earlier layer does not establish the next one.

## Winsock datagram truncation is not a resumable TCP short read

For message-oriented sockets, Winsock recv reports WSAEMSGSIZE when the message
exceeds the supplied buffer. Its UDP excess is lost; for reliable protocols the
provider retains excess data under the documented receive contract. [2]

Do not generalize one API's partial-message behavior to all transports. In a
Windows UDP parser, another recv does not recover the discarded remainder of
that datagram. In a framing finding, name the socket type, return/error handling
and exact buffered bytes that reach the consumer.

## Encoded lengths must agree with the data actually consumed

CWE-130 identifies inconsistent length parameters and associated data as a parser
weakness. [3] An input length is a claim, not evidence of available storage.

Compare validation, allocation, indexing and copying in the same unit and width.
A length bounded before conversion can still disagree with a later narrowed,
expanded or differently interpreted value. Grammar facts and examples are in
reference-parser-wire-fields-lengths-tags; nested boundaries and checksum scope
are in reference-parser-container-boundaries-integrity. Follow the procedure in
playbook-re-parser-grammar rather than treating a familiar header as a full schema.

## Object deserialization can cross type and behavior boundaries

CWE-502 concerns untrusted data deserialized without adequate assurance that the
resulting data is valid. [4] The reachable behavior depends on the actual
serializer's type-resolution and object-construction contracts.

Recover concrete type, nested graph, constructors, setters, callbacks and later
consumers rather than trusting a display name or a claimed internal client.
Keep operations performed before rejection separate from successful completion;
an exception alone does not establish rollback of earlier effects. For .NET,
use playbook-re-dotnet-deserialization-boundary and
reference-dotnet-serializer-type-and-state-boundaries for specific contracts.
For Java, Python, YAML and Serde, use
playbook-re-object-reconstruction-boundary to select the corresponding factual
reference; no single constructor or type-filter rule covers all those mechanisms.

## A BinaryFormatter binder does not make untrusted deserialization safe

Microsoft states that BinaryFormatter deserialization risks cannot be made safe
through a SerializationBinder or configuration switch; specifically, its denial-
of-service risk cannot be mitigated this way. [5]

This is not a generic claim about all serializers. Conversely, generic advice
to review type allowlists is not a safety recipe for BinaryFormatter. Establish
which API is reachable and what bytes control it before applying a serializer-
specific conclusion. Merely finding an unused import does not establish exposure.

## Evidence limits

A dangerous serializer/API identifies a review surface, not a vulnerability.
Establish attacker control, configuration/type resolution, reachable callback or
sink, and security consequence. Conversely, a bounded parser test that does not
trigger a defect does not clear untested message shapes or state sequences.

## Sources and scope

Reviewed 2026-10-02. TCP and Winsock contracts are scoped explicitly; serializers
have distinct contracts. CWE entries classify weaknesses, not observed target bugs.

1. [RFC 9293 TCP](https://www.rfc-editor.org/rfc/rfc9293.html), section 3.7: stream segmentation and application buffers.
2. [Winsock recv](https://learn.microsoft.com/en-us/windows/win32/api/winsock/nf-winsock-recv): message-size errors and retained/discarded excess.
3. [CWE-130 length inconsistency](https://cwe.mitre.org/data/definitions/130.html).
4. [CWE-502 untrusted deserialization](https://cwe.mitre.org/data/definitions/502.html).
5. [Microsoft BinaryFormatter security guide](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide).
