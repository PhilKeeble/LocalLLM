---
id: reference-parser-protocol-upgrade-negotiation
title: STARTTLS, SMTP AUTH and ALPN parser-selection boundaries
kind: reference
topics: [protocols, negotiation, starttls, smtp, sasl, alpn, downgrade, state-machines]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Protocol upgrades and negotiation

## SMTP STARTTLS readiness is not a completed TLS handshake

After a 220 response to STARTTLS, the SMTP client must negotiate TLS before
sending another SMTP command. STARTTLS must be last in a pipelined command group.
[1] The reply announces readiness to start negotiation, not authenticated
completion of that negotiation.

Investigative inference: locate the transition from plaintext command parsing
to handshake processing, including bytes already buffered in the same read.
Trace whether queued plaintext commands are incorrectly carried forward as
protected input. Do not assume one read equals one command or one TLS message.
Attribute each byte to the actual parser/protection epoch in which it was received,
not just the connection's flag at the time its callback runs.

## SMTP STARTTLS resets previously learned capability state

After the TLS handshake, SMTP resets to its initial state. Each peer discards
knowledge acquired before TLS rather than from the negotiation itself, including
EHLO information. A new EHLO is recommended; advertised extensions can differ. [1]

Investigative inference: recover capability caches and the next dispatch decision.
A pre-upgrade AUTH list is not evidence of what is available on the protected
connection. Follow actual state reset, not just the call that installs encryption.
A reset need not destroy the transport object; fields can be cleared in place.
This SMTP rule must not be generalized to every in-place protocol upgrade.

## SMTP AUTH challenge, cancellation and completion are different states

SMTP AUTH uses 334 for challenges and 235 for successful completion. A client
line containing only '*' cancels the exchange and receives 501. An initial
response '=' means present but empty, unlike omission. AUTH during a mail
transaction or after successful AUTH in the same session must be rejected. [2]

Investigative inference: recover the mode deciding whether a line is an SMTP
command or SASL response. Challenge receipt is not a logged-in transition.
On cancellation or malformed response, follow the reset to command parsing and
retained principal/transaction fields. A name, Base64 decoder or successful line
parse alone does not prove any credential or authorization check completed.

## SMTP SASL security-layer activation has a precise byte boundary

When SMTP AUTH negotiates a SASL security layer, client transmission switches
after the CRLF ending its final response; server transmission switches after the
CRLF ending its success reply. Enabling that layer resets SMTP state and discards
prior capability knowledge; this reset is conditional on a layer being enabled.
If both layers apply, sending uses SASL encoding before TLS. [2]

Investigative inference: do not treat every successful AUTH as installation of a
new record layer. Recover mechanism outcome, framing lengths and buffers at each
direction's activation boundary. Using the wrong decoder after a transition can
make valid traffic appear corrupt or expose a parser-state disagreement. Keep
the final success response itself distinct from bytes protected by the new layer.

## ALPN selection binds the application parser to a negotiated protocol

ALPN advertises nonempty opaque protocol-name byte strings. Its server selection
contains one protocol; an ALPN-selecting server with no supported offered protocol
must fail with no_application_protocol. The selected protocol determines application-data
interpretation, rather than allowing a different protocol after selection. [3]

Investigative inference: trace counted-byte comparison, selected value and actual
parser dispatch. A substring match, guessed port or recognizable payload is not
equivalent to the negotiated selection. Absence of ALPN is a separate path whose
policy depends on the application protocol; do not describe every such fallback
as forbidden. Verify policy before labeling supported compatibility a downgrade.

## TLS 1.3 carries server ALPN in EncryptedExtensions

RFC 7301's original ALPN flow uses ServerHello. TLS 1.3 instead permits the ALPN
extension in ClientHello and EncryptedExtensions. [3][4]

Investigative inference: a dissector expecting the selection only in ServerHello
can report missing negotiation incorrectly. Match the TLS version and visibility
of decrypted handshake content. Failure to observe encrypted ALPN is not evidence
that no protocol was selected, and an advertised client list is not the server's
decision. Keep transport negotiation evidence separate from application-user
authentication and authorization.

## Negotiation failure is a policy decision before compatibility fallback

Constructed state model: peer proposal → supported intersection → local policy
check → committed mode → selected parser. A failure branch that retries with a
different mode must satisfy the same required security policy, or an explicitly
permitted alternative. No universal ordering makes every larger version number
or differently named mechanism stronger.

Record who can influence proposals, the integrity of the exchange, effective
minimum policy and the point at which permissions or parser flags change. To
establish a downgrade defect, show a reachable below-policy mode and its effect;
legacy code or an intentional compatibility option is only a lead. Related
effective-setting rules: reference-logic-configuration-quotas-fallbacks.

## Sources and scope

Reviewed 2026-10-02. RFCs specify SMTP/ALPN transition contracts; implementation
buffers, callbacks, enabled mechanisms and deployment policy require target evidence.
No historical cipher-suite recommendations or universal plaintext-fallback policy
are inferred from these sources.

1. [RFC 3207](https://www.rfc-editor.org/rfc/rfc3207.html): §§4-4.2, SMTP STARTTLS sequencing and reset.
2. [RFC 4954](https://www.rfc-editor.org/rfc/rfc4954.html#section-4): AUTH responses, cancellation, empty input, restrictions and security-layer activation.
3. [RFC 7301](https://www.rfc-editor.org/rfc/rfc7301.html): §§3.1-3.2, ALPN names and selection.
4. [RFC 8446 §4.2](https://www.rfc-editor.org/rfc/rfc8446.html#section-4.2): TLS 1.3 extension locations.

Workflow: playbook-re-protocol-security-state.
