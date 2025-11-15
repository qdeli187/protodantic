Welcome! This hands-on guide will walk you through the core concepts of Protodantic using practical examples. We'll cover basic usage, lists (repeated fields), nested messages, and enums.

## 📦 Installation

```bash
pip install protodantic
```

## 🔰 Basic Example

Let's start with a simple example. Create a basic Pydantic model and extend it with Protodantic's `ProtoModel`:

```python
from protodantic import ProtoModel

class Person(ProtoModel):
    name: str
    age: int
    email: str

# Create an instance
person = Person(name="Alice", age=30, email="alice@example.com")

print(person)
# Output: name='Alice' age=30 email='alice@example.com'

# Serialize to Protocol Buffer bytes
encoded = person.model_dump_proto()
print(encoded)
# Output: b'\n\x05Alice\x10\x1e\x1a\x12alice@example.com'

# Deserialize back
decoded = Person.model_validate_proto(encoded)
print(decoded)
# Output: name='Alice' age=30 email='alice@example.com'
assert decoded == person
```

That's it! You now have automatic Protocol Buffer serialization with full Pydantic validation.

---

## 📋 Working with Lists (Repeated Fields)

Protodantic makes it easy to work with repeated fields (lists). Use Python's `list` type annotation:

```python
from protodantic import ProtoModel
from typing import List

class Person(ProtoModel):
    name: str
    hobbies: list[str]

# Create an instance with a list
person = Person(
    name="Bob",
    hobbies=["reading", "gaming", "coding"]
)

print(person.hobbies)
# Output: ['reading', 'gaming', 'coding']

# Serialize and deserialize
encoded = person.model_dump_proto()
decoded = Person.model_validate_proto(encoded)

print(decoded.hobbies)
# Output: ['reading', 'gaming', 'coding']

assert decoded == person
```

### Key Points about Lists:

- **Type Annotation**: Use `list[T]` to define repeated fields (works with any supported type)
- **Validation**: Pydantic validates that the field is actually a list
- **Empty Lists**: Empty lists are allowed by default
- **Any Type**: Lists can contain primitives, bytes, nested messages, or enums
- **Multiple Items**: Each item is encoded as a separate protobuf message field

**Example with multiple item types:**

```python
class Contact(ProtoModel):
    name: str
    phone_numbers: list[str]
    email_addresses: list[str]
    tags: list[int]

contact = Contact(
    name="Alice",
    phone_numbers=["+1-555-0100", "+1-555-0101"],
    email_addresses=["alice@example.com", "alice.work@example.com"],
    tags=[1, 2, 3, 4, 5]
)

print(contact.phone_numbers)
# Output: ['+1-555-0100', '+1-555-0101']

# Serialize
encoded = contact.model_dump_proto()

# Deserialize
decoded = Contact.model_validate_proto(encoded)
assert decoded == contact
```

---

## 🎨 Working with Enums

Enums provide type-safe enumeration values. Define them using Python's `IntEnum`:

```python
from enum import IntEnum
from protodantic import ProtoModel

class Status(IntEnum):
    UNKNOWN = 0
    ACTIVE = 1
    INACTIVE = 2
    PENDING = 3

class User(ProtoModel):
    username: str
    status: Status

# Create an instance with an enum
user = User(username="bob", status=Status.ACTIVE)

print(user.status)
# Output: <Status.ACTIVE: 1>

print(user.status.value)
# Output: 1

# Serialize and deserialize
encoded = user.model_dump_proto()
decoded = User.model_validate_proto(encoded)

print(decoded.status)
# Output: <Status.ACTIVE: 1>

assert decoded == user
```

!!! info "Enums in Protobuf"

    Protobuf established that the first value of an enum is always the default value. It is recommended to always set the first value of an Enum to **TYPE_UNKNOWN** or **TYPE_UNSET**

### Key Points about Enums:

- **Type Safety**: Enums ensure only valid values are accepted
- **Validation**: Pydantic validates enum values automatically
- **Integer Values**: Enums are serialized as their integer values in protobuf
- **Deserialization**: When deserializing, the integer is converted back to the enum
- **Error Handling**: Invalid enum values raise a validation error

**Example with enum validation:**

```python
# This will raise a validation error
try:
    invalid_user = User(username="bob", status="INVALID_STATUS")
except ValueError as e:
    print(f"Error: {e}")
    # The status field must be a valid Status enum value

# Correct usage
user = User(username="bob", status=Status.ACTIVE)  # ✓
```

---

## 🏗️ Nested Messages

Nested messages allow you to create complex, hierarchical data structures:

```python
from protodantic import ProtoModel

class Address(ProtoModel):
    street: str
    city: str
    zipcode: str

class Contact(ProtoModel):
    id: bytes
    type: str
    value: str

class Person(ProtoModel):
    name: str
    age: int
    email: str
    address: Address
    contacts: list[Contact]

# Create an instance with nested data
person = Person(
    name="John Doe",
    age=30,
    email="john@example.com",
    address=Address(
        street="123 Main St",
        city="Anytown",
        zipcode="12345"
    ),
    contacts=[
        Contact(id=b'\x01', type="phone", value="555-0100"),
        Contact(id=b'\x02', type="email", value="john@work.com")
    ]
)

print(person.address.city)
# Output: 'Anytown'

print(person.contacts[0].value)
# Output: '555-0100'

# Serialize and deserialize
encoded = person.model_dump_proto()
decoded = Person.model_validate_proto(encoded)

print(decoded.address.city)
# Output: 'Anytown'

print(len(decoded.contacts))
# Output: 2

assert decoded == person
```

### Key Points about Nested Messages:

- **Definition**: Nested models are defined as class attributes with type annotations
- **Access**: Access nested fields using dot notation (`person.address.city`)
- **Validation**: Pydantic validates nested structures recursively
- **Serialization**: Nested messages are automatically encoded as length-delimited protobuf messages
- **Deserialization**: Nested structures are properly reconstructed from bytes
- **Deep Nesting**: Nested messages can themselves contain nested messages

**Example with multiple levels of nesting:**

```python
class Country(ProtoModel):
    name: str
    code: str

class City(ProtoModel):
    name: str
    country: Country

class Address(ProtoModel):
    street: str
    city: City

class Person(ProtoModel):
    name: str
    address: Address

# Create deeply nested data
person = Person(
    name="Alice",
    address=Address(
        street="123 Main St",
        city=City(
            name="San Francisco",
            country=Country(name="USA", code="US")
        )
    )
)

# Access deeply nested fields
print(person.address.city.country.code)
# Output: 'US'

# Works seamlessly with serialization
encoded = person.model_dump_proto()
decoded = Person.model_validate_proto(encoded)
assert decoded == person
```

---

## 🗺️ Working with Maps

Maps (dictionaries) allow you to store key-value pairs with efficient serialization:

```python
from protodantic import ProtoModel

class Config(ProtoModel):
    name: str
    settings: dict[str, int]
    metadata: dict[str, str]

# Create an instance with maps
config = Config(
    name="app_config",
    settings={"timeout": 30, "retries": 3, "max_connections": 100},
    metadata={"version": "1.0", "author": "alice", "environment": "production"}
)

print(config.settings["timeout"])
# Output: 30

print(config.metadata["environment"])
# Output: 'production'

# Serialize and deserialize
encoded = config.model_dump_proto()
decoded = Config.model_validate_proto(encoded)

print(decoded.settings)
# Output: {'timeout': 30, 'retries': 3, 'max_connections': 100}

assert decoded == config
```

### Key Points about Maps:

- **Type Annotation**: Use `dict[K, V]` to define map fields (keys and values can be primitives or strings)
- **Key Types**: Supported key types are `str` and `int`
- **Value Types**: Supported value types are `str`, `int`, `float`, `bytes`, `bool`, and nested `ProtoModel` messages
- **Validation**: Pydantic validates that the field is actually a dict
- **Empty Maps**: Empty dicts are allowed by default
- **Unordered**: Maps are unordered by nature; entries may serialize in different orders
- **Efficient Encoding**: Maps use protobuf's map field encoding for efficiency


---

## 🔗 Complete Example: Combining Everything

Let's create a real-world example using lists, nested messages, enums, and optional fields together:

```python
from protodantic import ProtoModel
from enum import IntEnum
from typing import Optional

class Priority(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

class Tag(ProtoModel):
    name: str
    color: str

class Task(ProtoModel):
    title: str
    description: str
    priority: Priority
    tags: list[Tag]
    assigned_to: Optional[str] = None

class Project(ProtoModel):
    name: str
    tasks: list[Task]

# Create a complete project structure
project = Project(
    name="Website Redesign",
    tasks=[
        Task(
            title="Design mockups",
            description="Create UI mockups",
            priority=Priority.HIGH,
            tags=[
                Tag(name="design", color="#FF5733"),
                Tag(name="urgent", color="#FF0000")
            ],
            assigned_to="alice"
        ),
        Task(
            title="Implement frontend",
            description="Build components",
            priority=Priority.MEDIUM,
            tags=[
                Tag(name="frontend", color="#0066CC")
            ]
        ),
        Task(
            title="Write documentation",
            description="Document the API",
            priority=Priority.LOW,
            tags=[],
            assigned_to=None  # Optional field
        )
    ]
)

# Access nested data
print(f"Project: {project.name}")
print(f"First task priority: {project.tasks[0].priority}")  # Priority.HIGH
print(f"Second task tags: {project.tasks[1].tags}")
print(f"Third task assigned to: {project.tasks[2].assigned_to}")  # None

# Serialize
encoded = project.model_dump_proto()
print(f"Serialized size: {len(encoded)} bytes")

# Deserialize
decoded = Project.model_validate_proto(encoded)
assert decoded == project

print("✓ Serialization and deserialization successful!")
```

---

## 🔄 Serialization and Deserialization

### Encoding to Protocol Buffers

```python
from protodantic import ProtoModel

class Person(ProtoModel):
    name: str
    age: int

person = Person(name="Alice", age=30)

# Encode to protobuf bytes
encoded = person.model_dump_proto()
print(type(encoded))  # <class 'bytes'>
print(encoded)        # b'\n\x05Alice\x10\x1e'
```

### Decoding from Protocol Buffers

```python
# Decode from bytes
decoded = Person.model_validate_proto(encoded)
print(decoded)  # name='Alice' age=30
assert decoded == person
```

### Working with Files

```python
# Save to file
with open("person.pb", "wb") as f:
    f.write(encoded)

# Load from file
with open("person.pb", "rb") as f:
    data = f.read()

decoded = Person.model_validate_proto(data)
```

---

## ✅ Validation and Error Handling

Pydantic automatically validates your data when creating instances:

```python
from protodantic import ProtoModel
from enum import IntEnum

class Status(IntEnum):
    ACTIVE = 1
    INACTIVE = 0

class User(ProtoModel):
    name: str
    age: int
    status: Status

# Type validation
try:
    user = User(name="Bob", age="thirty", status=Status.ACTIVE)
except ValueError as e:
    print(f"Error: Invalid age type")

# Enum validation
try:
    user = User(name="Bob", age=30, status="INVALID")
except ValueError as e:
    print(f"Error: Invalid status enum value")

# Successful creation
user = User(name="Bob", age=30, status=Status.ACTIVE)  # ✓
print(user)
```

Happy coding with Protodantic! 🚀
