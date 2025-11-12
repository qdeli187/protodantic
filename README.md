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

## 💡 Examples

### Nested Messages

```python
class Contact(ProtoModel):
    id: bytes
    type: str
    value: str

class Person(ProtoModel):
    name: str
    contacts: list[Contact] = []

person = Person(
    name="Alice",
    contacts=[
        Contact(id=b'\x01', type="phone", value="555-1234"),
        Contact(id=b'\x02', type="email", value="alice@example.com")
    ]
)

data = person.model_dump_proto()
restored = Person.model_validate_proto(data)
```

### Optional Fields

```python
class User(ProtoModel):
    name: str
    middle_name: str | None = None
    age: int
    bio: str | None = None

user = User(name="Bob", age=25)  # middle_name and bio will be skipped
proto_bytes = user.model_dump_proto()
```

### Repeated Fields

```python
class Team(ProtoModel):
    name: str
    members: list[str] = []

team = Team(name="Dev Team", members=["Alice", "Bob", "Charlie"])
data = team.model_dump_proto()
```

## 🔍 How It Works

### Encoding Process

1. Iterate through each field in your model
2. For each non-None, non-default value:
   - Encode the **field tag** (field number + wire type)
   - Encode the **value** based on its type
3. Return the concatenated bytes

### Decoding Process

1. Read the binary stream sequentially
2. Extract the **field tag** to determine field number and wire type
3. Based on wire type, read the appropriate number of bytes
4. Map the value to the corresponding model field
5. Repeat until end of stream

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

## 📖 API Reference

### `ProtoModel.model_dump_proto() -> bytes`
Serialize the model instance to protobuf bytes.

### `ProtoModel.model_validate_proto(data: bytes) -> ProtoModel`
Deserialize protobuf bytes into a model instance.

## 🗺 Roadmap

### Items 

- [x] Basic scalar types (`int`, `float`, `bool`, `str`, `bytes`)
- [x] Nested messages (ProtoModel instances)
- [x] Repeated fields (lists)
- [x] Optional fields (Union with None)
- [x] Automatic field numbering (1-indexed based on field order)
- [x] Round-trip serialization/deserialization
- [x] Full Pydantic validation support
- [ ] Enum Support: Handle Python enums and protobuf enum types
- [ ] Additional Scalar Types: `int32`, `int64`, `uint32`, `uint64`, `sint32`, `sint64`, `fixed32`, `fixed64`, `sfixed32`, `sfixed64`, `double` precision support
- [ ] Oneof Fields: Support for protobuf's `oneof` pattern (mutually exclusive fields)
- [ ] Map Types: Handle `dict` types as protobuf map fields
- [ ] Field Number Configuration: Allow explicit field number specification via Pydantic Field metadata
- [ ] Circular Reference Handling: Better support for self-referencing and circular model dependencies
- [ ] Packed Encoding: Automatic packed encoding for repeated scalar fields
- [ ] Protoc plugin for this lib: Generate pydantic classes from `.proto` files
- [ ] Default Values: Proper handling of protobuf default values (current naive approach does work though)
- [ ] Unknown Field Handling: Gracefully handle fields in the binary data that don't exist in the model
- [ ] Streaming Support: Large message serialization/deserialization with streaming

### Milestones

- [ ] Support for all protobuf types and field indexes
- [ ] protoc plugin
- [ ] Rust encoding and decoding , similar to pydantic
- [ ] Proposing to merge these features onto pydantic (who knows 💪 ?!)


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Areas where help is needed:

- Implementing enum support
- Adding support for additional numeric types
- Implementing oneof fields
- Map type support
- Proto file generation

## 📄 License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

