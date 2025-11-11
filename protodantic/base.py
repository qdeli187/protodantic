from pydantic import BaseModel
from google.protobuf.internal.encoder import _EncodeVarint, _EncodeSignedVarint
from google.protobuf.internal.wire_format import WIRETYPE_VARINT, WIRETYPE_FIXED64, WIRETYPE_LENGTH_DELIMITED, WIRETYPE_FIXED32
from typing import get_args, get_origin, Union
from io import BytesIO
import struct
import types

class ProtoModel(BaseModel):

  @classmethod
  def get_wiretype_for_field(cls, field) -> int:
    """Get the wiretype for a given Pydantic field based on its annotation."""
    annotation = field.annotation
    origin = get_origin(annotation)
    
    # Handle Optional types
    if origin is Union or origin is types.UnionType:
      anns = get_args(annotation)
      anns = [ann for ann in anns if ann is not type(None)]
      if len(anns) != 1:
        raise ValueError(f"Unsupported Union type: {annotation}")
      annotation = anns[0]
      origin = get_origin(annotation)
    
    # Handle list types
    if origin is list:
      return WIRETYPE_LENGTH_DELIMITED
    
    if annotation in {int, bool}:
        return WIRETYPE_VARINT  # varint
    elif annotation == float:
        return WIRETYPE_FIXED64  # 64-bit
    elif annotation in {str, bytes}:
        return WIRETYPE_LENGTH_DELIMITED  # length-delimited
    elif isinstance(annotation, type) and issubclass(annotation, ProtoModel):
        return WIRETYPE_LENGTH_DELIMITED  # nested message
    else:
        raise ValueError(f"Unsupported field type: {annotation}")

  def _encode_value(self, value, annotation, output: BytesIO):
    """Encode a single value based on its type."""
    origin = get_origin(annotation)
    
    # Handle Optional types
    if origin is Union or origin is types.UnionType:
      anns = get_args(annotation)
      anns = [ann for ann in anns if ann is not type(None)]
      if len(anns) == 1:
        annotation = anns[0]
        origin = get_origin(annotation)
    
    # Handle list types
    if origin is list:
      inner_type = get_args(annotation)[0]
      # For repeated fields, encode the length-delimited data
      inner_buffer = BytesIO()
      for item in value:
        self._encode_value(item, inner_type, inner_buffer)
      data = inner_buffer.getvalue()
      _EncodeVarint(output.write, len(data))
      output.write(data)
      return
    
    if annotation == int:
      _EncodeVarint(output.write, value)
    elif annotation == bool:
      _EncodeVarint(output.write, 1 if value else 0)
    elif annotation == float:
      output.write(struct.pack('<d', value))  # little-endian double
    elif annotation == str:
      encoded = value.encode('utf-8')
      _EncodeVarint(output.write, len(encoded))
      output.write(encoded)
    elif annotation == bytes:
      _EncodeVarint(output.write, len(value))
      output.write(value)
    elif isinstance(annotation, type) and issubclass(annotation, ProtoModel):
      # Nested message
      nested_bytes = value.model_dump_proto()
      _EncodeVarint(output.write, len(nested_bytes))
      output.write(nested_bytes)
    else:
      raise ValueError(f"Unsupported value type: {annotation}")

  def model_dump_proto(self) -> bytes:
    """Serialize the Pydantic model to protobuf bytes."""
    output = BytesIO()
    field_number = 1
    
    for field_name, field in self.model_fields.items():
      value = getattr(self, field_name)
      
      # Skip None values for optional fields
      if value is None:
        field_number += 1
        continue
      
      # Skip default values for optional fields
      if not field.is_required() and value == field.default:
        field_number += 1
        continue
      
      wt = self.get_wiretype_for_field(field)
      key = (field_number << 3) | wt
      _EncodeVarint(output.write, key)
      
      # Encode the value
      self._encode_value(value, field.annotation, output)
      
      field_number += 1
    
    return output.getvalue()


# Example usage
if __name__ == "__main__":
  class Address(ProtoModel):
    street: str
    city: str
    zip_code: int
  
  class Person(ProtoModel):
    id: int
    name: str
    email: str | None = None
    age: int
    salary: float
    is_active: bool
    address: Address | None = None
    tags: list[str] | None = None
  
  address = Address(street="123 Main St", city="Springfield", zip_code=12345)
  person = Person(
    id=42,
    name="Alice",
    email="alice@example.com",
    age=30,
    salary=75000.50,
    is_active=True,
    address=address,
    tags=["engineer", "python"]
  )
  
  proto_bytes = person.model_dump_proto()
  print(f"Serialized bytes: {proto_bytes.hex()}")
  print(f"Length: {len(proto_bytes)} bytes")