---
id: reference-objc-dispatch-type-evidence
title: Objective-C selectors, message dispatch, method signatures and object evidence
kind: reference
topics: [objective-c, selectors, objc-msgsend, dynamic-dispatch, type-recovery, swizzling]
platforms: [macos, ios]
architectures: [x86, x64, arm, arm64]
---
# Objective-C dispatch and type evidence

## SEL identifies a message; IMP identifies executable code

An Objective-C selector (SEL) identifies a method name. The receiver's class and
method lookup determine the implementation (IMP). A method receives hidden self
(receiver) and _cmd (selector) parameters before its explicit arguments. The same
selector can lead to different implementations for different receivers. [1]

For a call graph, recover the receiver's possible classes and the implementation
selected on the relevant path. A selector string in a binary shows vocabulary,
not that the corresponding behavior executes. Distinguish an instance receiver
from a class object; a class method is not an instance method merely because the
selector spelling matches.

## objc_msgSend and direct IMP calls require the real method ABI

Apple's message.h requires casting message-send entry points to the appropriate
function-pointer type when calling them directly. A generic header declaration
is not the actual method prototype. Return handling is target-dependent:
objc_msgSend_stret is unavailable on arm64; its existence on another architecture
does not mean every structure return uses it. [2]

An IMP obtained through methodForSelector: can be called directly with the
correct return and argument types, including self and _cmd. [1] Such a call does
not perform a fresh selector lookup. Recover hidden result storage and aggregate
classification before treating an apparent extra pointer as attacker data.

## Super dispatch changes lookup, not receiver identity

For Apple's objc_msgSendSuper, objc_super contains the actual receiver and the
class at which lookup starts. The implementation still operates on that receiver;
there is not a separately allocated superclass instance. This specific start-class
rule must not be copied to differently named compiler/runtime entry points. [2]

In an override, follow the same object's fields through superclass code. Losing
receiver identity can hide validation performed by the superclass or wrongly
attribute a write to an unrelated object.

## Dynamic resolution, forwarding and method replacement add call edges

resolveInstanceMethod: and resolveClassMethod: can supply missing implementations,
including through class_addMethod, before forwarding is considered. A
respondsToSelector: query can itself give resolution an opportunity to run. [3]
In Foundation's full forwarding path, forwardInvocation: receives an invocation
containing the message and arguments; it may forward, transform or handle it. [4]
method_exchangeImplementations atomically swaps two methods' IMPs. [5]

Static method lists are therefore not a complete execution graph. Investigate
registration, replacement and forwarding before declaring an indirect destination
unreachable. Swizzling (replacing method implementations) is also used by benign
frameworks: identify who installs it, which inputs it intercepts and its effect.

## Type encodings constrain a prototype but do not validate an argument

Objective-C encodes method return and parameter types. Useful codes include v
(void), @ (object), # (class), : (selector), ^ followed by a type (pointer), and
braced structure encodings. The hidden receiver and selector account for @ and :
in ordinary method signatures; they are not two user-supplied parameters. [6]

Combine encoding, target ABI and actual call-site use. An object encoding does
not establish its concrete class, buffer length, ownership or caller authority.
Metadata obtained from a malformed image is itself untrusted evidence, not a
reason to perform unchecked reads while reconstructing a signature.

## Messaging nil can hide missing state without entering the method

An Objective-C message to nil performs no method body; an object-valued result
is nil and a BOOL result is NO. [7] This is not a guarantee for calling an arbitrary
IMP or C function with a null argument, nor a portable rule for every aggregate
return ABI.

Trace what a missing receiver means at a security decision. A skipped audit or
cleanup message may be significant even without a crash. Conversely, NO from a
permission check may correctly deny access. Establish the consuming branch;
nil messaging is neither automatically safe nor automatically a bypass.

## Tagged pointers and nonpointer isa invalidate naive object casts

Apple objc4 distinguishes tagged pointers from ordinary object addresses and
supports encoded/nonpointer isa representations, including target-dependent
class decoding and pointer-authentication handling. [8] This is implementation
evidence, not a portable fixed object layout.

Do not unconditionally dereference every apparent id or treat its first word as
a plain class pointer. Recover the target runtime representation before assigning
heap fields. An unfamiliar pointer pattern alone is not corruption, packing or
malware concealment; an unsafe decoder can manufacture all three impressions.

## Categories add dispatch candidates without creating a new subclass

Apple categories add methods to an existing class and its subclasses. Ordinary
categories cannot add instance variables. If category and existing methods clash,
Apple's language guide leaves the selected implementation undefined. [9]

Recover loaded category contributions and the actual resolved implementation;
the main class's static method list need not be the complete dispatch surface.
Do not infer a new object layout or guaranteed override order from a category
name. Category registration alone does not prove the method executed or intercepted
sensitive input. Block callback ownership remains in reference-objc-ownership-blocks.

## Primary sources and scope

Reviewed 2026-10-02. Apple runtime scope, not all Objective-C implementations.
Archived conceptual guides supply enduring messaging concepts; objc4 main-branch
headers/source supply API and implementation distinctions, not target-build proof.
Ownership and blocks: `reference-objc-ownership-blocks`.

1. [Apple: How Messaging Works](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtHowMessagingWorks.html): receiver lookup, hidden arguments and direct IMP calls (2009).
2. [Apple objc4 message.h](https://raw.githubusercontent.com/apple-oss-distributions/objc4/main/runtime/message.h): typed calls, super lookup and return variants.
3. [Apple: Dynamic Method Resolution](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtDynamicResolution.html): resolution before forwarding (2009).
4. [Apple: Message Forwarding](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtForwarding.html): invocation-based handling (2009).

## Sources for mutation, representation and categories

Apple-specific runtime evidence; editions and earlier review above remain applicable.

5. [Apple objc4 runtime.h](https://raw.githubusercontent.com/apple-oss-distributions/objc4/main/runtime/runtime.h): method_exchangeImplementations.
6. [Apple: Type Encodings](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtTypeEncodings.html): selected codes, not a complete current encoding grammar (2009).
7. [Apple: Working with Objects](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ProgrammingWithObjectiveC/WorkingwithObjects/WorkingwithObjects.html): nil messaging.
8. [Apple objc4 objc-object.h](https://raw.githubusercontent.com/apple-oss-distributions/objc4/main/runtime/objc-object.h): ISA/rawISA and tagged-pointer branches.
9. [Apple: Customizing Existing Classes](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ProgrammingWithObjectiveC/CustomizingExistingClasses/CustomizingExistingClasses.html): category methods, ivar restriction and name clashes; inspected 2026-10-08. Earlier source review retained.
