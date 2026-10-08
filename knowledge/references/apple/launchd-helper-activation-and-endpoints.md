---
id: reference-apple-launchd-helper-authority
title: launchd job activation, endpoint ownership and privileged helper operations
kind: reference
topics: [launchd, helpers, services, activation, ipc, privilege, lifecycle]
platforms: [macos]
architectures: [x86, x64, arm64]
---
# Helper activation and service authority

## launchd configuration describes activation rather than completed execution

Apple's launchd model registers service resources and can launch a job when a
request arrives. Job property lists describe executable arguments and activation
policy. [1]

Bind a configuration to its applicable job/session domain, registration and
selected executable. A plist on disk, label string or KeepAlive key alone cannot
prove the job ran or persisted successfully. This reference describes activation
concepts; exact registration keys/defaults require the matching platform contract.

## Endpoint reachability and privileged operation authority are separate

For analysis, identify who owns the listener, who can obtain the endpoint and
which process handles each request. Activation can bring a helper into existence;
it does not supply authorization for every request after startup.

Recover authenticated peer, requested object/action and effective helper
credentials. A trusted main app does not prove every caller contacting its helper
is trusted. A privileged helper can legitimately broker operations: establish
the requester-to-effect relation before alleging malicious privilege use.
Use reference-apple-xpc-peer-request-authority for the message boundary.

## Helper generations need separate pending-operation and state evidence

launchd can relaunch an on-demand service after it exits and a later request
arrives. [1] For investigation, keep process/connection generation, pending
request, cached decisions and selected resources together.

Exit or restart does not prove all operations rolled back or that a retained
authorization still belongs to the new peer. Follow failure, retry and cleanup
without assuming exactly-once remote effects. Malware persistence interpretation
belongs in reference-malware-persistence-trigger-context; configuration presence
alone remains activation evidence.

## Source and scope

Reviewed 2026-10-08. [Apple: Creating launchd Jobs](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
[1], launch sequence/on-demand resources and property-list purpose. Archived
sample recipes, timing values, deployment directories and contemporary helper
installation APIs are not adopted. Workflow: playbook-apple-service-authority.
