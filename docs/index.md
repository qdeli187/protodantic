---
order: 0
---

# 🚀 Protodantic

**Bridge the gap between Protocol Buffers and Pydantic validation.**

Protodantic is a Python library that seamlessly integrates **Protocol Buffers** with **Pydantic**, giving you the best of both worlds: powerful data validation and efficient binary serialization.

## 🎯 Project Goal

Protodantic enables developers to:

- Use **Pydantic models** with proto files seamlessly
- Leverage **Pydantic's robust validation** framework
- Serialize and deserialize with **zero configuration**

Whether you're building microservices, APIs, or distributed systems, Protodantic makes it easy to work with validated, serializable data structures.

## End Goal

The end goal of this library is to be a plugin for protobuf compilers like grpcio-tools. Instead of generation protobuf message classes you would generate ProtoModels.

## But why Though ?

This Project emerged from a frustration while building an OPAMP server for opentelemetry agents with Fastapi. Pydantic and protobuf don't bode well together but it's a shame because pydantic can be used for Fastapi but only (sqlmodel for ORM , faststream for EDS and so on...)

!!! info

    I believe this library will be useful for developers building apps with both protobuf and the pydantic ecosystem (Fastapi, SqlModel, FastStream ...)

    But it can also be useful without proto files altogether , protobuf's encoding is more efficient than json. Two codebases sharing the same Protomodels can exchange data more efficiently

## ✨ Currently Supported Features

### Core Types
- ✅ **Primitive Types** - `int`, `str`, `float`, `bool`, `bytes`
- ✅ **Optional Fields** - `Optional[T]` and union types
- ✅ **Boolean & Numeric** - Full support for integers, floats, and booleans

### Advanced Structures
- ✅ **Nested Messages** - Complex hierarchical data models
- ✅ **Lists / Repeated Fields** - `list[T]` for repeated elements
- ✅ **Enumerations** - Type-safe enums with automatic validation
- ✅ **Custom Validators** - Full Pydantic validation support

### Serialization
- ✅ **Protocol Buffer Encoding** - `model_dump_proto()` method
- ✅ **Protocol Buffer Decoding** - `model_validate_proto()` method
- ✅ **Pydantic Integration** - Use all Pydantic features alongside protobuf

### Validation
- ✅ **Type Checking** - Automatic type validation on instantiation
- ✅ **Required/Optional** - Clear nullable/required field semantics
- ✅ **Custom Rules** - Support for Pydantic validators and field constraints
- ✅ **Nested Validation** - Recursive validation of nested structures

## 🚀 Quick Start

```python
from protodantic import ProtoModel

class Person(ProtoModel):
    name: str
    age: int
    email: str

# Create an instance
person = Person(name="Alice", age=30, email="alice@example.com")

# Serialize to Protocol Buffer bytes
encoded = person.model_dump_proto()

# Deserialize back
decoded = Person.model_validate_proto(encoded)
```
