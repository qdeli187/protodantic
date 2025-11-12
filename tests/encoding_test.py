from protodantic.base import ProtoModel
from .proto.test_pb2 import Person as PBPerson, Address as PBAddress, Contact as PBContact

import pytest

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
    phone: str | None = None
    address: Address
    hobbies: list[str] = []
    is_active: bool
    salary: float | None = None
    contacts : list[Contact] = []

@pytest.fixture
def pb_contact():
    return PBContact(type="phone", value="123-456-7890", id=b'\x01\x02\x03')

@pytest.fixture
def pb_address():
    return PBAddress(street="123 Main St", city="Anytown", zip_code="12345")

@pytest.fixture
def pb_person(pb_address, pb_contact):
    person = PBPerson(
        name="John Doe",
        age=30,
        email="test@exmaple.com",
        address=pb_address,
        hobbies=["reading", "gaming"],
        is_active=True,
        salary=55000.50,
        contacts=[pb_contact]
    )
    return person

@pytest.fixture
def contact():
    return Contact(type="phone", value="123-456-7890", id=b'\x01\x02\x03')

@pytest.fixture
def address():
    return Address(street="123 Main St", city="Anytown", zipcode="12345")

@pytest.fixture
def person(address, contact):
    person = Person(
        name="John Doe",
        age=30,
        email="test@exmaple.com",
        address=address,
        hobbies=["reading", "gaming"],
        is_active=True,
        salary=55000.50,
        contacts=[contact]
    )
    return person

def test_contact_serialization(contact, pb_contact):
    encoded = contact.model_dump_proto()
    assert encoded == pb_contact.SerializeToString()

def test_address_serialization(address, pb_address):
    encoded = address.model_dump_proto()
    assert encoded == pb_address.SerializeToString()

def test_person_serialization(person, pb_person):
    encoded = person.model_dump_proto()
    expected = pb_person.SerializeToString()
    assert encoded == expected

def test_contact_1_2(contact):
    encoded = contact.model_dump_proto()
    pb_contact = PBContact()
    pb_contact.ParseFromString(encoded)
    assert pb_contact.type == contact.type
    assert pb_contact.value == contact.value
    assert pb_contact.id == contact.id

def test_address_1_2(address):
    encoded = address.model_dump_proto()
    pb_address = PBAddress()
    pb_address.ParseFromString(encoded)
    assert pb_address.street == address.street
    assert pb_address.city == address.city
    assert pb_address.zip_code == address.zipcode

def test_person_1_2(person):
    encoded = person.model_dump_proto()
    pb_person = PBPerson()
    pb_person.ParseFromString(encoded)
    assert pb_person.name == person.name
    assert pb_person.age == person.age
    assert pb_person.email == person.email
    assert pb_person.address.street == person.address.street
    assert pb_person.address.city == person.address.city
    assert pb_person.address.zip_code == person.address.zipcode
    assert pb_person.hobbies == person.hobbies
    assert pb_person.is_active == person.is_active
    assert pb_person.salary == person.salary
    assert len(pb_person.contacts) == len(person.contacts)
    for pb_contact, contact in zip(pb_person.contacts, person.contacts):
        assert pb_contact.type == contact.type
        assert pb_contact.value == contact.value
        assert pb_contact.id == contact.id

def test_auto_enc_contact(contact):
    encoded = contact.model_dump_proto()
    obj = Contact.model_validate_proto(encoded)
    assert obj == contact

def test_auto_enc_address(address):
    encoded = address.model_dump_proto()
    obj = Address.model_validate_proto(encoded)
    assert obj == address

def test_auto_enc_person(person):
    encoded = person.model_dump_proto()
    obj = Person.model_validate_proto(encoded)
    assert obj == person
