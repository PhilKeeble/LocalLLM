---
id: reference-jvm-serialization-construction-and-graphs
title: Java object deserialization construction, callbacks, graph identity and failures
kind: reference
topics: [jvm, java, deserialization, object-streams, constructors, callbacks, object-graphs]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# Java object deserialization

## Scope: ObjectInputStream is an object-reconstruction boundary

Reviewed 2026-10-02 against Java SE/JDK 25 serialization contracts. These rules
concern Java Object Serialization, not arbitrary JSON/XML libraries, Kryo,
Android parceling or a universal JVM object layout. Untrusted Java object
deserialization is explicitly discouraged by the Serializable API. [1]

Filter evidence: reference-jvm-serialization-filters. Investigation:
playbook-re-jvm-deserialization-boundary. Loader/type identity:
reference-jvm-loading-and-reflection. A class name or Serializable marker is
not evidence of safe values, allowed application actions or a reachable defect.

## Identify a stream without executing its object graph

The standard header is AC ED 00 05. Wire handles begin at 0x7E0000 and restart
after reset; they are stream identities, not native pointers. Strings have
modified-UTF-8 byte lengths: TC_STRING uses unsigned 16-bit length and
TC_LONGSTRING signed 64-bit length. [2]

Investigation: preserve transport/framing/decompression and the exact bytes
handed to the parser. Header resemblance is a format lead, not authentication
or proof of a complete valid stream. Track handle-table epochs across resets;
joining the same numeric handle across epochs can invent aliasing. Use a bounded
structural reader, not ObjectInputStream on unknown input merely to list types.
Custom stream subclasses and legacy external-data formats require their actual
grammar. Encoding details: reference-jvm-class-file-evidence.

## Ordinary Serializable constructors do not establish restored invariants

For ordinary Serializable classes, deserialization bypasses their constructors
and field initializers, but invokes the first nonserializable superclass's
no-argument constructor. [3] Default field restoration covers nonstatic,
nontransient fields. [1]

Investigation: a validating public constructor or setter is not proof that
restored fields were checked. Follow the actual readObject/defaultReadObject
path, including private fields and later consumers. A transient field's source
initializer is not evidence of its restored value. Static state is not ordinary
per-object serialized field state; do not infer that deserializing an instance
resets a class's static variables. Exclude records and Externalizable objects
before applying this constructor-bypass rule.

## Externalizable runs a constructor and then its own restoration code

Externalizable requires a public no-argument constructor; readExternal controls
restoration, including coordination with superclass state. [4]

Investigation: successful construction is only an intermediate state. Trace
subsequent assignments, length checks, nested reads and side effects in
readExternal. It may overwrite values the constructor initialized safely.
Because this is a public entry, inspect whether the application can invoke it
again on an existing object; do not assume only fresh instances reach it.
Do not decode an external custom layout as ordinary default serialized fields.

## Records and enums are not ordinary Serializable construction

Records use their canonical constructor with restored component values;
absent components receive type defaults. Their readObject/readExternal hooks
are ignored, but readResolve can replace the result. Record serialVersionUID
matching is waived. Enums restore by name and ignore custom serialization hooks. [4]

Investigation: inspect a record's actual canonical constructor, including
null/default acceptance and side effects before a throwing validation. Do not
credit an ignored private readObject as a record guard or assume ordinary
constructor bypass. Resolve enum type and name separately from application
authorization; a valid constant may still request an impermissible operation.
These are Java serialization contracts, not general data-binding-library rules.

## Serialized fields and missing data need their actual restoration path

serialPersistentFields can define a serial form differing from physical fields. [4]
readObjectNoData handles a locally present serializable superclass absent from
the stream; otherwise its fields receive defaults. [1,3]

Investigation: recover each class's hook descriptor and access, stream fields,
optional data and mapping into live fields. Do not identify a serialization
hook by method name alone. A missing field, explicit zero/null and an omitted
class segment can take different checks. Inspect GetField.defaulted and caller
defaults where used. Version evolution is a possible cause of absent data;
absence alone does not establish tampering. Identify the effective invariant
after all relevant superclass/subclass restoration, not only one method.

## Callback execution precedes return and can expose partial state

Class-specific readObject can run during graph reconstruction. Overridable calls
from restoration code dispatch on the actual object type even before restoration
finishes. Registered validation occurs after graph reconstruction, before return;
higher priorities run first. [3]

Investigation: map every feasible callback from input to side effect, including
collection reconstruction, virtual calls and application hooks. A cast after
readObject returns cannot prevent earlier callback effects. A class name from a
known gadget list is only a lead: establish the installed class version, allowed
graph, reached method chain, controlled values and actual consequence. Graph
validation is not a retroactive barrier against earlier work; inspect whether
partially restored objects escape through callbacks or shared state.

## Serialization hooks require matching descriptors and access

Ordinary Serializable hook forms include private void
readObject(java.io.ObjectInputStream), private void readObjectNoData(), and
Object readResolve() with the applicable accessibility/inheritance rules. [1]
Externalizable uses public void readExternal(java.io.ObjectInput). [4]

Investigation: preserve parameter and return descriptors plus access/static flags.
An overload named readObject with a different parameter is not this hook.
Throws declarations do not add parameters to the JVM method descriptor.
Inspect superclass hooks and the actual record/enum special case before assigning
a call edge. Do not treat every same-named method as invoked during restoration.

## Default class resolution does not simply use the context class loader

JDK 25 ObjectInputStream.resolveClass uses Class.forName(name, false, loader).
Its default loader is the first stack loader excluding the platform loader and
its ancestors, or the platform loader if none qualifies. Proxy descriptors use
the distinct resolveProxyClass path; subclasses can override resolution. [5]

Investigation: record the resolved Class and defining loader, not merely a thread
context-loader setting or stream class name. initialize=false is not a passive
loader sandbox; reference-jvm-loading-and-reflection retains that distinction.
Follow proxy interfaces and the invocation handler to actual callback bodies.
An override restricting ordinary class descriptors is not automatically evidence
of equivalent restrictions on proxy resolution or nested streams.

## Aliases, cycles and replacement change the validated object

Ordinary graph handles preserve sharing/cycles. Cycles targeting a record from
its components are not preserved while that record is being constructed. [4]
readResolve runs after reconstruction; existing internal references to the
original need not be rewritten to the replacement. [3]

Investigation: record identity edges, not merely recursively equal values.
Check whether two fields alias one mutable object and whether validation applies
to the object later used. A replacement is not automatically a sanitized deep
copy. For a record cycle, do not import ordinary-object cycle assumptions or
diagnose a resulting null link as a memory-corruption artifact. Inspect both
original and replacement callback paths before accepting an invariant claim.

## readUnshared does not promise a deep, uniquely owned graph

readUnshared invalidates the returned object's wire handle for later references,
but substitution or enum/Class identity can still return an externally shared
object. A readResolve-returned array is shallow-cloned. [3]

Investigation: distinguish the root's stream-handle rule from ownership of
reachable children. A shallow array clone does not clone mutable elements.
Compare identity at each security-relevant edge before assuming independent
validation, tenant state or mutation. No observed root alias is not proof that
its nested graph lacks shared nodes.

## Compatibility and parse failure are not authenticity or rollback

serialVersionUID is a serialization compatibility identifier; an ordinary class
mismatch rejects with InvalidClassException. [1] A deserialization exception can
leave ObjectInputStream unusable. [3]

Investigation: matching UID does not authenticate a sender, prove identical
bytecode or validate fields. Preserve the exact failure and when it occurred:
format, resolution, compatibility, filter, constructor, hook and application
checks are different stages. A rejection does not prove earlier callbacks or
external writes were undone. Do not continue parsing the same damaged stream
and interpret subsequent errors as independent clean tests.

## Primary sources and inspected sections

1. [Serializable, JDK 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/Serializable.html): warning, default fields, hook signatures, missing superclass data and UID compatibility.
2. [Serialization protocol](https://docs.oracle.com/en/java/javase/25/docs/specs/serialization/protocol.html): sections 6.2 and 6.4, handles, encodings, grammar and constants.
3. [Serialization input specification](https://docs.oracle.com/en/java/javase/25/docs/specs/serialization/input.html): sections 3.1-3.7, construction, validation, hooks, replacement and failure.
4. [Serialization architecture](https://docs.oracle.com/en/java/javase/25/docs/specs/serialization/serial-arch.html): sections 1.5 and 1.11-1.14, persistent fields, Externalizable, enums, records and cycles.
5. [ObjectInputStream, JDK 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/ObjectInputStream.html): resolveClass and resolveProxyClass loader behavior.
