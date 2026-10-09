---
id: vulnerability-config-insecure-bootstrap-default-identity-policy
title: Insecure bootstrap, first-run or default identity and policy
kind: vulnerability
topics: [configuration, default-credentials, bootstrap, enrollment, first-run]
platforms: [cross-platform]
architectures: [any]
---

# Insecure bootstrap, first-run or default identity and policy

## Definition and violated invariant

This vulnerability occurs when initial deployment, enrollment, reset, recovery, or first-run state accepts shared or predictable credentials, exposes unauthenticated setup, grants overly broad default authority, or leaves bootstrap capability reachable after ownership is established. The invariant is that initial authority must be unique or securely established, limited to enrollment, and irreversibly or explicitly retired before normal sensitive operation.

A documented default is not automatically vulnerable if exposure and mandatory enrollment controls match the threat model. Prove the unauthorized actor can reach and benefit from it.

## Conditions that establish the issue

Recover factory/default state, credential derivation, setup endpoint reachability, physical/network assumptions, ownership claim, reset/recovery paths, state persistence, race between claimants, and retirement of bootstrap accounts/tokens. Prove an actor outside the intended enrollment role can authenticate, claim ownership, or invoke a sensitive operation.

Check cloned images and backups for duplicated device identity or bootstrap secrets. Determine whether reset restores a shared secret or reopens setup while retaining protected user data.

## Evidence that is not sufficient

A username such as `admin`, sample password, first-run wizard, enrollment API, uninitialized database field, or reset button is not sufficient. Credentials may be per-device, setup may require physical proof or a one-time secret, the endpoint may be isolated, or normal operation may be blocked until ownership is established.

## Investigation sequence

Build the lifecycle from manufacture/install through first boot, enrollment, steady state, update, backup restore, reset and recovery. At each state record accepted identities, credential source, reachable interfaces, permitted operations, and transition persistence. Trace how the system distinguishes an unclaimed device from a transient failure to read enrollment state.

At binary level, identify default-object creation and credential comparison but confirm the state predicate and data source. A compiled fallback constant can be dead, diagnostic-only, or gated by hardware presence.

## Primary sources and scope

Reviewed 2026-10-09 against NISTIR 8259A [IoT Device Cybersecurity Capability Core Baseline](https://csrc.nist.gov/pubs/ir/8259/a/final), NIST SP 800-63B [authenticator lifecycle guidance](https://pages.nist.gov/800-63-4/sp800-63b.html), and ETSI EN 303 645 [consumer IoT security provisions](https://www.etsi.org/deliver/etsi_en/303600_303699/303645/). Apply the product's intended enrollment and recovery threat model; the standards do not establish a particular deployment defect.
