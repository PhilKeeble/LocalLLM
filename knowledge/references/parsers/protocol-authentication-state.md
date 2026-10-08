---
id: reference-parser-protocol-authentication-state
title: LDAP, SSH and SASL authentication completion and identity transitions
kind: reference
topics: [protocols, authentication, authorization, state-machines, ldap, ssh, sasl]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Protocol authentication state

## LDAP rebind removes the previous authorization identity

RFC 4513 says an LDAP session begins anonymous. Receipt of a Bind request
immediately moves it to anonymous authorization; successful binding establishes
the resulting state, while failure leaves it anonymous. [1]

Investigative inference: trace identity, authorization flags and cached grants
together through a rebind, not just the BindResponse code. A connection pool that
retains the old user's grant after a failed new bind can disagree with this rule.
Anonymous does not mean no operations are permitted: recover the server's actual
anonymous-access policy before describing an accepted operation as a bypass.
Do not transfer LDAP's rebind reset rule to every authentication protocol.

## LDAP simple Bind success need not authenticate the supplied name

For LDAP simple Bind, an empty name and empty password request anonymous access.
A nonempty name with an empty password requests the unauthenticated mechanism,
also establishing anonymous authorization if accepted. That name is for tracing,
not authorization. RFC 4513 recommends servers reject this latter mode by default.
[1]

Investigative inference: in software using Bind as a password-check service,
follow empty-password handling and the client-side decision after success.
Checking only resultCode can mistake accepted anonymous access for proof of the
claimed user's credentials. Establish the actual server behavior; the protocol
allows rejection and acceptance cannot be assumed. A valid nonempty password path
does not establish the empty-input path's semantics.

## LDAP Bind sequencing differs from ordinary concurrent operations

RFC 4511 requires outstanding operations to complete or be abandoned before a
BindRequest is processed. Clients must wait for its BindResponse before sending
further LDAP PDUs; servers should not process other requests during binding. [2]

Investigative inference: recover queues, callbacks and the identity captured by
outstanding work. A response arriving later does not alone prove it ran with the
new identity. Multi-step binding also requires distinguishing saslBindInProgress
from final success. Keep an operation's execution identity separate from whichever
name the connection object contains when a log or response is produced.

## LDAP authorization state and an installed SASL layer are separate

An established LDAP SASL integrity/confidentiality layer remains until replaced
by another such layer; a failed or non-SASL Bind does not remove it. A newly
negotiated layer starts after the final successful BindResponse. [1]

Investigative inference: the continued ability to decode protected messages does
not prove the old user remains authorized after a failed rebind. Conversely,
resetting a user flag does not imply subsequent bytes are unprotected. Model
authentication identity, effective authorization and wire protection separately;
confusing them can misidentify both parser boundaries and security checks.

## SSH partial success is not USERAUTH_SUCCESS

SSH_MSG_USERAUTH_FAILURE can carry partial success when a method succeeded but
the full authentication sequence is incomplete. SSH_MSG_USERAUTH_SUCCESS denotes
completed authentication, not every successful factor. [3]

Investigative inference: follow which message/return value opens service dispatch.
Do not map every successful credential-helper result to logged_in=true. Recover
the required sequence and which factor evidence belongs to which attempt. For a
claimed bypass, show the sensitive service accepts work before its full policy is
satisfied, rather than treating the presence of partial success as a defect.

## SSH public-key acceptance probes do not prove private-key possession

SSH publickey authentication permits a no-signature query answered with
SSH_MSG_USERAUTH_PK_OK. Actual authentication checks both acceptable key and
signature; additional authentication methods may still be required. [3]

Investigative inference: distinguish key lookup, algorithm acceptance, signature
verification and final authorization when naming recovered functions. A server
saying a key is acceptable is not proof the peer authenticated with it. A client
can send a signed request directly, so absence of a preliminary probe is not
automatically an invalid sequence. This describes dispatch/completion evidence,
not a cryptographic signature-verification implementation recipe.

## SSH user or service changes invalidate accumulated authentication state

SSH authentication requests repeat user and service names. RFC 4252 requires
checking them each time and clearing accumulated authentication state when either
changes; a server unable to clear it must disconnect. [3]

Constructed investigation: factor one succeeds for A, a new request selects B,
and factor two is credited to B while retaining A's factor-one flag. Trace the
actual identity comparison and state reset before reporting this sequence as
reachable. The same numeric connection slot is not evidence of the same attempted
identity. User/service names stored only for logging do not establish enforcement.

## SASL authentication identity and requested authorization identity differ

SASL credentials establish an authentication identity. A client can separately
request an authorization identity, meaning the identity it wants to act as.
An absent or empty authorization identity requests the identity associated with
the credentials. The server must verify both credentials and permission to assume
the requested identity; either failure makes the exchange fail. [4]

Investigative inference: identify both values in callback arguments and effective
session state. Verifying A's password is not sufficient to authorize requested B.
Conversely, an intentional proxy/delegation policy can permit different identities.
Use reference-logic-authorization-object-binding for the subsequent per-operation
subject/object decision; successful SASL alone does not establish that decision.

## Sources and scope

Reviewed 2026-10-02. These are named protocol contracts, not observations of a
specific library or server. Application policy, protocol extensions and upstream
identity enforcement require separate evidence. Historical algorithm recommendations
in these RFCs are not adopted here as current cryptographic guidance.

1. [RFC 4513](https://www.rfc-editor.org/rfc/rfc4513.html): §§4, 5.1.1-5.1.2 and 5.2.1.4, LDAP authorization and SASL layer transitions.
2. [RFC 4511](https://www.rfc-editor.org/rfc/rfc4511.html#section-4.2.1): LDAP Bind sequencing.
3. [RFC 4252](https://www.rfc-editor.org/rfc/rfc4252.html): §§5-5.1 and 7, SSH identity, partial success and publickey exchange.
4. [RFC 4422](https://www.rfc-editor.org/rfc/rfc4422.html): §§2 and 3.4.1, SASL identities and verification.

Workflow: playbook-re-protocol-security-state.
