---
id: reference-crypto-password-verifier-binding
title: Password verifier inputs, salts, cost parameters and acceptance behavior
kind: reference
topics: [cryptography, passwords, verifiers, salts, cost-parameters, authentication, normalization]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Password-verifier and accepted-input evidence

## A password verifier has a defined input and cost model

NIST describes password-hashing schemes using password, salt and cost inputs
to make offline guesses more expensive. RFC 9106's Argon2 model includes salt
and memory/pass parameters. These are distinct from a plain fast content digest.
[1][2]

For investigation, identify actual construction, stored algorithm/parameter
metadata, salt and verification result. A 'hash' field or crypto library import
does not establish a suitable password verifier. A salt is not a secret key or
encryption of the password. No fixed tuning value or current algorithm ranking
is adopted; the claim must reflect actual inputs and selected implementation.

## Enrollment and verification must bind the same password representation

For analysis, follow text encoding, normalization, case handling, NUL treatment,
truncation and length units from submitted input to the verifier at enrollment
and authentication. Preserve the user/account association and actual bytes.

One normalized display does not prove the two consumers see the same value.
Conversely, deliberate normalization under a defined policy is not automatically
a defect. Identify a mismatch or violated acceptance invariant with its context,
using the shared text/parser references. A successful low-level comparison cannot
authenticate a different account or a caller-controlled stored verifier record.

## Stored verifier parameters need bounded parsing and trusted selection

For investigation, trace how algorithm identifier, salt, work/memory settings
and output extent are parsed and selected. RFC 9106 makes these explicit inputs
to its defined function. [2]

Malformed or untrusted parameters can select unexpected failure/work paths;
the actual implementation's handling is required before claiming an effect.
A stored cost label is not evidence that the selected call applied it. Preserve
limits, allocation results and migration paths. Do not infer weak storage from
a parameter value without the construction, policy and runtime context, or treat
an expensive verifier as protection against every authentication failure.

## Offline verifier exposure and online acceptance are different boundaries

NIST distinguishes offline resistance of stored verifiers from online authentication
and its other controls. [1]

For investigation, bind exposed record/material to the actual account and active
verification path. A database read does not by itself establish recovered passwords
or successful login. Rate limits, lockout, multi-factor state and failure handling
need their own evidence; they cannot retroactively strengthen a stolen verifier's
offline cost. Report storage, input selection and authorized acceptance separately,
without a password-cracking recipe or invented success rate.

## Sources and scope

Reviewed 2026-10-08. NIST SP 800-63B-4, Password Verifiers and offline/online
discussion; RFC 9106 section 3.1 for defined inputs/resource cost. Editions
are source provenance; numerical tuning requirements are not imported.

1. [NIST authentication guidance](https://pages.nist.gov/800-63-4/sp800-63b.html): salted costed verifiers and distinct authentication boundaries.
2. [RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html): Argon2 input/parameter scope, not every password scheme.

Workflow: playbook-crypto-operation-evidence. Generic caller/object authorization
and representation rules remain in their existing primary homes.
