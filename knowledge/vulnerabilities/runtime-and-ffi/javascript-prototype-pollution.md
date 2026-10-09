---
id: vulnerability-runtime-javascript-prototype-pollution
title: JavaScript prototype pollution through attacker-selected property paths
kind: vulnerability
topics: [javascript, prototype-pollution, property-lookup, object-merge, authorization]
platforms: [cross-platform]
architectures: [any]
---

# JavaScript prototype pollution through attacker-selected property paths

## Definition and violated invariant

Prototype pollution occurs when less-trusted input changes a prototype object or causes a write to invoke prototype-changing semantics, so later property lookup observes attacker-selected inherited state. The invariant is that input intended to supply data properties must not mutate inheritance state or create inherited values that a security-sensitive consumer treats as trusted configuration.

Pollution is a state-corruption primitive, not an impact by itself. Establish the polluted object population and the later consumer; an accepted key named `__proto__`, `prototype`, or `constructor` alone does not prove either.

## Conditions that establish the issue

Trace the exact decoded keys and path segments into the final write operation, including recursive merge, property assignment, `Object.assign`, spread, descriptor definition, or library-specific handling. Determine whether the destination has an ordinary prototype, whether an inherited setter runs, which prototype is changed, and which subsequently created or accessed objects inherit the value.

Then prove a reachable consumer reads the property through the affected chain without requiring an own property and uses it for a security-sensitive decision or operation. Record process/request isolation and when polluted state is reset.

## Evidence that is not sufficient

A dynamic property write, prototype terminology, `Object.assign`, or the string `__proto__` is not sufficient. Own-property definition, a null-prototype dictionary, key rejection, immutable prototypes, or a consumer that requires own properties can prevent the chain. Object spread and assignment do not have identical setter behavior; inspect the actual operation.

Do not infer global `Object.prototype` pollution when only one ordinary object's prototype changes. Do not infer authorization bypass from a polluted `isAdmin` value unless the relevant consumer actually resolves and trusts that inherited property.

## Investigation sequence

Recover parsing and decoding before the merge, then follow every key through the write algorithm. Inspect the destination's current prototype and property descriptors. Snapshot own properties and prototype links before and after the candidate operation, and identify which later objects share or inherit from the modified prototype.

At the sink, distinguish own-property lookup, ordinary inherited lookup, destructuring/default behavior, and explicit membership tests. Preserve event, worker, realm, and request boundaries so a process-wide effect is not inferred from per-request state.

## Constructed JavaScript example

```javascript
function merge(dst, src) {
    for (const key of Object.keys(src)) {
        if (src[key] && typeof src[key] === "object") {
            if (!dst[key]) dst[key] = {};
            merge(dst[key], src[key]);
        } else {
            dst[key] = src[key];
        }
    }
}

const options = {};
merge(options, JSON.parse(attackerText));
if (requestOptions.isAdmin) performPrivilegedAction();
```

This is only a candidate until the parsed key path, the destination objects created or selected by recursion, the resulting prototype mutation, and `requestOptions` inheritance are established. The consumer also needs a real authorization role; a display preference with the same name would not establish security impact.

## Runtime representation

There is no portable JavaScript assembly signature for prototype pollution. At the language level, ordinary `[[Get]]` searches an object's own property and then its `[[Prototype]]` chain, while `Object.assign` obtains enumerable own source keys and performs `[[Set]]` on the target. Engine bytecode or optimized native code may inline these operations behind shape guards and fallback calls, so recover the selected property key, receiver, setter or prototype transition, and later lookup rather than matching one opcode sequence.

## Primitive and impact limits

The direct primitive is modification of a prototype or inherited property state visible to a defined object population. Impact depends on the consumer and can include policy changes, path or command selection, denial of service, or a later injection chain. Report remote code execution only when the polluted value reaches and controls an execution-capable sink under the required authority.

## Primary sources and scope

Reviewed 2026-10-09 against ECMA-262 [ordinary object internal methods](https://tc39.es/ecma262/#sec-ordinary-object-internal-methods-and-internal-slots), [`Object.assign`](https://tc39.es/ecma262/#sec-object.assign), and the normative-optional legacy [`Object.prototype.__proto__` accessor](https://tc39.es/ecma262/#sec-object.prototype.__proto__). The source is hypothetical; libraries can implement different merge semantics.
