# 🚀 Protodantic

A powerful Pydantic extension that brings **Protocol Buffers** serialization to your Python models. Combine the validation power of Pydantic with the efficiency of protobuf encoding.

## ✨ Features

- 🔄 **Seamless Integration**: Extend your Pydantic models with protobuf serialization
- ⚡ **Efficient Encoding**: Convert Python objects to compact protobuf bytes
- 🔀 **Bidirectional**: Serialize to bytes and deserialize back to Python objects
- 📦 **Type Support**: Handle primitives, strings, nested messages, and repeated fields
- ✅ **Validated**: Automatic validation with Pydantic
- 🎯 **Simple API**: Just inherit from `ProtoModel` instead of `BaseModel`

## 🛠️ Installation

```bash
pip install protodantic
```

## 📚 Quick Start

### Define Your Models

```python
from protodantic import ProtoModel

class Address(ProtoModel):
    street: str
    city: str
    zipcode: str

class Person(ProtoModel):
    name: str
    age: int
    email: str
    phone: str | None = None
    address: Address
    hobbies: list[str] = []
    is_active: bool
    salary: float | None = None
```

### Serialize to Protobuf

```python
# Create an instance
person = Person(
    name="John Doe",
    age=30,
    email="john@example.com",
    address=Address(
        street="123 Main St",
        city="Anytown",
        zipcode="12345"
    ),
    hobbies=["reading", "gaming"],
    is_active=True,
    salary=55000.50
)

# Convert to protobuf bytes
proto_bytes = person.model_dump_proto()
print(proto_bytes)  # b'\n\x08John Doe\x10\x1e...'
```

### Deserialize from Protobuf

```python
# Parse protobuf bytes back to Python object
restored_person = Person.model_validate_proto(proto_bytes)
assert restored_person == person  # ✅ Perfect match!
```

## 🎨 Supported Types

| Type | Wire Type | Example |
|------|-----------|---------|
| `int` | Varint | `age: 30` |
| `bool` | Varint | `is_active: True` |
| `float` | 64-bit | `salary: 55000.50` |
| `str` | Length-delimited | `name: "John"` |
| `bytes` | Length-delimited | `id: b'\x01\x02\x03'` |
| `ProtoModel` | Message | Nested objects |
| `list[T]` | Repeated | `hobbies: ["reading", "gaming"]` |
| `T \| None` | Optional | `phone: None` |

## 📄 License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.
