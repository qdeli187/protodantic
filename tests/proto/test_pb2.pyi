from __future__ import annotations

from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class Address(_message.Message):
    __slots__ = ("street", "city", "zip_code")
    STREET_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    ZIP_CODE_FIELD_NUMBER: _ClassVar[int]
    street: str
    city: str
    zip_code: str
    def __init__(self, street: _Optional[str] = ..., city: _Optional[str] = ..., zip_code: _Optional[str] = ...) -> None: ...

class Person(_message.Message):
    __slots__ = ("name", "age", "email", "phone", "address", "hobbies", "is_active", "salary", "contacts")
    NAME_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    HOBBIES_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    CONTACTS_FIELD_NUMBER: _ClassVar[int]
    name: str
    age: int
    email: str
    phone: str
    address: Address
    hobbies: _containers.RepeatedScalarFieldContainer[str]
    is_active: bool
    salary: float
    contacts: _containers.RepeatedCompositeFieldContainer[Contact]
    def __init__(self, name: _Optional[str] = ..., age: _Optional[int] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., address: _Optional[_Union[Address, _Mapping]] = ..., hobbies: _Optional[_Iterable[str]] = ..., is_active: bool = ..., salary: _Optional[float] = ..., contacts: _Optional[_Iterable[_Union[Contact, _Mapping]]] = ...) -> None: ...

class Contact(_message.Message):
    __slots__ = ("id", "type", "value")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    id: bytes
    type: str
    value: str
    def __init__(self, id: _Optional[bytes] = ..., type: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
