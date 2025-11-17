from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[Status]
    ACTIVE: _ClassVar[Status]
    INACTIVE: _ClassVar[Status]
    PENDING: _ClassVar[Status]
UNKNOWN: Status
ACTIVE: Status
INACTIVE: Status
PENDING: Status

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
    __slots__ = ("name", "age", "email", "address", "phone", "hobbies", "is_active", "salary", "contacts", "status", "skills")
    class SkillsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    HOBBIES_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    CONTACTS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SKILLS_FIELD_NUMBER: _ClassVar[int]
    name: str
    age: int
    email: str
    address: Address
    phone: str
    hobbies: _containers.RepeatedScalarFieldContainer[str]
    is_active: bool
    salary: float
    contacts: _containers.RepeatedCompositeFieldContainer[Contact]
    status: Status
    skills: _containers.ScalarMap[str, int]
    def __init__(self, name: _Optional[str] = ..., age: _Optional[int] = ..., email: _Optional[str] = ..., address: _Optional[_Union[Address, _Mapping]] = ..., phone: _Optional[str] = ..., hobbies: _Optional[_Iterable[str]] = ..., is_active: bool = ..., salary: _Optional[float] = ..., contacts: _Optional[_Iterable[_Union[Contact, _Mapping]]] = ..., status: _Optional[_Union[Status, str]] = ..., skills: _Optional[_Mapping[str, int]] = ...) -> None: ...

class Contact(_message.Message):
    __slots__ = ("id", "type", "value")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    id: bytes
    type: str
    value: str
    def __init__(self, id: _Optional[bytes] = ..., type: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
