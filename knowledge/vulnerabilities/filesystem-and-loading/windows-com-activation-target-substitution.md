---
id: vulnerability-windows-com-registration-activation-target-substitution
title: Windows COM registration and activation target substitution
kind: vulnerability
topics: [windows, com, activation, registry, loading, privilege-boundary]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows COM registration and activation target substitution

## Definition and violated invariant

Windows COM target substitution occurs when a less-trusted actor can influence the effective mapping for a class requested by a more-trusted client, causing COM to select an unapproved DLL, executable, service, surrogate or remote server. The invariant is that every activation resolves through configuration and files controlled by an authority permitted to choose code or an endpoint for that client. COM registration, a writable unrelated class and successful activation are normal capabilities; the vulnerability requires attacker influence over the mapping actually consumed at a security boundary.

This profile covers class-to-server selection. Caller authentication, launch and access permissions, interface marshaling and method authorization are separate COM contracts. Review them when they decide reachability or impact, but do not rename an authorization defect as registration hijacking.

## Conditions that establish target substitution

A finding requires a less-trusted actor who can modify an effective class mapping, activation manifest, selected server file, service configuration or path-resolution input; a target process with different authority that reaches activation for the affected CLSID or ProgID; evidence that COM selects the actor-controlled implementation; and a resulting code, data or operation capability beyond the initiating actor's authority.

Record the initiating actor, target process and token, requested class and context, selected server, protected operation and resulting authority. Without actual target activation and selection, the evidence supports a candidate configuration weakness. Without a greater or otherwise forbidden capability, it does not establish privilege escalation.

## Recover the effective activation path

Start with the exact client call. Recover requested CLSID or ProgID, requested IID, `CLSCTX` flags, result and returned interface use. ProgID-to-CLSID conversion and later CLSID activation are distinct selections. Multiple context bits permit alternatives and do not prove which server form succeeded.

An active activation context can supply registration-free COM mappings before registry lookup. Otherwise recover registry data visible to the caller, including per-user/per-machine merging and the applicable architecture view. Trace local `TreatAs` redirection when present. Identify the selected `InprocServer32` DLL, `LocalServer32` executable, `LocalService`, surrogate/AppID or remote server. Activation context, caller architecture, process state and configuration prevent one registry export from proving universal precedence.

## Prove attacker control and actual selection

For each effective input, identify who can change its value and replace the resolved object. Review the security descriptor of the effective registry key, manifest and selected executable or DLL path. For a local server, recover actual executable selection and command-line interpretation; an unquoted or partial path is only a candidate until the process-created image is established.

Static imports, GUID references and configuration establish a supported path, not observed activation. Confirmation can come from an authorized trace, process/module history or other evidence binding the request to the selected server and result. Preserve failures and fallbacks. Do not register or activate an untrusted component merely to test it in an analyst or production process.

## COM authority and direct impact

An actor-controlled in-process DLL loaded into the target runs with that process's authority, subject to the load succeeding and enforced code-integrity policy. A substituted local executable runs under the identity chosen by effective activation configuration; it does not inherit a privileged client token merely because the client requested it. A service, surrogate or remote server requires AppID, service identity, launch/access policy and observed process or endpoint evidence.

A substituted server may expose client data or receive delegated operations without increasing process privilege. Report that direct effect. Claim elevation only when a lower-authority actor controls the selected implementation and activation places it in, or grants it operations from, a demonstrably higher-authority context. Recurring activation can support persistence, but one load does not prove survival across reboot, repair or policy change.

## Evidence that does not establish the issue

A CLSID string, `CoCreateInstance` import, COM-capable binary, missing registration, writable unrelated registry key, adjacent DLL, `dllhost.exe`, exported `DllGetClassObject`, or analyst-triggered activation does not independently prove target substitution. A writable class mapping matters only when the target's effective lookup consumes it and selects actor-controlled content.

Do not assume per-user registration always overrides machine registration for every client, architecture and policy state. Do not infer server identity from context flags or effective security from AppID values alone: another server form may be selected, and programmatic security initialization can supersede registry settings. Scanner labels are leads requiring full selection, authority and effect evidence.

## Reverse-engineering representation

COM target substitution has no portable assembly signature. In native code, use the applicable ABI and data flow to recover class identifiers, interface identifiers, context flags, success checks and returned-interface use. A GUID-shaped constant or indirect call is only a lead because identifiers can be constructed dynamically and calls can pass through wrappers or factories.

```text
less-trusted actor
  -> controllable manifest, effective registry mapping, path or server file
  -> target client requests CLSID/ProgID under a specific activation context
  -> COM selects in-process/local/service/surrogate/remote implementation
  -> selected binary or endpoint runs under an established identity
  -> direct code, data or operation capability
  -> any additional authority required for escalation
```

## Constructed target-substitution example

Assume a lower-privileged user can write the effective mapping and referenced DLL below. A higher-authority helper later requests the class with `CLSCTX_INPROC_SERVER`, its activation context does not override the class, effective registry lookup consumes this mapping, and code-integrity policy permits the load.

```text
Effective Classes view
  CLSID\{EXAMPLE-CLSID}\InprocServer32 = C:\Users\Low\bridge.dll

Higher-authority helper
  CoCreateInstance({EXAMPLE-CLSID}, ..., CLSCTX_INPROC_SERVER, ...)
```

If evidence confirms those assumptions and `bridge.dll` is loaded, the result is in-process code execution in the helper's authority context. Registry text alone is only a candidate. If the helper ignores the user-controlled view, uses a protected registration-free mapping, rejects the DLL or never activates the class, the constructed chain does not apply.

## Related knowledge contracts

`reference-windows-com-activation-interface-evidence` owns CLSID/IID, context, factory and proxy interpretation. `reference-windows-com-rpc-authentication-impersonation` owns launch/access security and caller identity. `reference-windows-dll-plugin-resolution-activation` owns loader and activation-context evidence, and `reference-windows-wow64-layouts-views` owns registry views. The decisive target-selection and impact threshold is repeated here for isolated use.

## Primary sources and review limits

Reviewed 2026-10-09 against Microsoft documentation for [class registration](https://learn.microsoft.com/en-us/windows/win32/com/registering-a-class-at-installation), [registration-free COM](https://learn.microsoft.com/en-us/windows/win32/sbscs/creating-registration-free-com-objects), [merged `HKEY_CLASSES_ROOT`](https://learn.microsoft.com/en-us/windows/win32/sysinfo/merged-view-of-hkey-classes-root), [COM registry keys](https://learn.microsoft.com/en-us/windows/win32/com/com-registry-keys), [`InprocServer32`](https://learn.microsoft.com/en-us/windows/win32/com/inprocserver32), [`LocalServer32`](https://learn.microsoft.com/en-us/windows/win32/com/localserver32), [surrogate activation](https://learn.microsoft.com/en-us/windows/win32/com/registering-the-dll-server-for-surrogate-activation), [`TreatAs`](https://learn.microsoft.com/en-us/windows/win32/com/treatas), and [COM security](https://learn.microsoft.com/en-us/windows/win32/com/setting-processwide-security-through-the-registry). This profile does not assert one target's mapping, policy or exploitability; no component was registered or run.
