---
id: vulnerability-authentication-recovery-mfa-transition-bypass
title: Password reset, account recovery, or MFA transition bypass
kind: vulnerability
topics: [authentication, account-recovery, password-reset, mfa, state-machines, tokens]
platforms: [cross-platform]
architectures: [any]
---

# Password reset, account recovery, or MFA transition bypass

## Definition and violated invariant

An account-recovery or MFA-transition vulnerability occurs when a claimant can reset, replace, remove or add an authenticator, recover an account, or enter a higher-authenticated state without satisfying the assurance and account-binding policy for that transition. Recovery is an alternate authentication path and must bind proof, target account, requested transition, lifetime, use count and resulting session to one coherent state machine.

Password replacement while authenticated with another sufficient factor, loss-of-all-factor recovery, MFA enrollment, factor replacement and temporary bypass codes are different transitions. A valid recovery token does not authorize a different account or operation, and a successful reset does not automatically justify reusing an older authenticated session at higher assurance.

## Conditions that establish the issue

Recover initiation actor and session, target account source, proofing/recovery method, token generation and delivery, entropy, stored verifier, account/action binding, expiry, use count and atomic consumption, rate limits, notifications, outstanding-token invalidation, factor enrollment/removal, session issuance/rotation and final assurance. Prove an attacker can complete a transition without the required evidence or redirect valid evidence to another account/action.

Trace every alternate route: support/admin workflows, legacy endpoints, recovery contacts, backup codes, device migration, remembered browsers and API/mobile flows. Establish the effective policy rather than assuming all accounts require the same factors.

## Evidence that is not sufficient

A reset endpoint, emailed code, recovery token, support flow, missing password prompt, MFA removal, short code or automatic login is not sufficient. The transition may use another authorized factor, repeated identity proofing, bounded single use, trusted administration or a policy that intentionally permits the action.

A notification detects possible abuse but does not itself prevent unauthorized recovery. Conversely, absence of notification alone does not prove account takeover.

## Investigation sequence

Model states and transitions from unauthenticated through recovery pending, proof accepted, authenticator changed and session issued. For each transition record principal/account, proof, token generation, expiry/use state, transaction boundary and invalidated credentials/sessions. Compare web, API, mobile, support and retry/error paths.

At binary or managed-code level, follow token lookup and account identifiers into the update, then locate atomic consume/update behavior and session creation. Confirm the final account and assurance rather than relying on success messages.

## Constructed reset-token object-binding example

```text
record = recovery_tokens.find(hash(request.token))
if record.valid and not record.expired:
    accounts[request.account_id].replace_password(request.new_password)
    record.used = true
```

If the token record is bound to one account but the update uses an independently caller-controlled `request.account_id`, a valid token for one account can reset another. The finding requires the actual mismatched sources, reachable account update and inadequate later authorization. If the lookup returns the target account and the update uses only that bound identity, this example does not apply.

## Primitive and impact limits

The direct primitive is unauthorized authenticator or account-state transition. Consequences can include account takeover, MFA downgrade, attacker-factor enrollment and persistent session access. Recovery policy, account privileges, notifications, revocation, later authorization and existing factor requirements bound impact.

## Related knowledge and primary sources

Protocol authentication state, token binding, randomness and authorization/object-binding references provide the underlying contracts. This profile keeps account, action, proof and state transition together.

Reviewed 2026-10-09 against NIST [SP 800-63B section 4.2](https://pages.nist.gov/800-63-4/sp800-63b/account-recovery/) for account recovery methods and notification, section 4.1 for authenticator binding, and section 5 for resulting session binding. The example is constructed and does not impose NIST assurance levels on applications outside that profile.
