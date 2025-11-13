from __future__ import annotations

import struct
import types
from enum import IntEnum
from io import BytesIO
from typing import Union, get_args, get_origin

from google.protobuf.internal.decoder import _DecodeVarint  # type: ignore
from google.protobuf.internal.encoder import _EncodeVarint  # type: ignore
from google.protobuf.internal.wire_format import (WIRETYPE_FIXED32,
                                                  WIRETYPE_FIXED64,
                                                  WIRETYPE_LENGTH_DELIMITED,
                                                  WIRETYPE_VARINT)
from pydantic import BaseModel


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

    if annotation in {int, bool} or issubclass(annotation, IntEnum):
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
      return

    if annotation == int:
      _EncodeVarint(output.write, value)
    elif issubclass(annotation, IntEnum):
      _EncodeVarint(output.write, value.value)
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

      if get_origin(field.annotation) is list:
        inner_type = get_args(field.annotation)[0]
        for item in value:
          _EncodeVarint(output.write, key)
          self._encode_value(item, inner_type, output)
      else:
        _EncodeVarint(output.write, key)
        self._encode_value(value, field.annotation, output)

      field_number += 1

    return output.getvalue()

  @classmethod
  def _decode_varint(cls, stream: BytesIO) -> int:
    """Decode a varint from the stream."""
    result = 0
    shift = 0
    while True:
      byte_data = stream.read(1)
      if not byte_data:
        break
      byte = byte_data[0]
      result |= (byte & 0x7f) << shift
      if not (byte & 0x80):
        break
      shift += 7
    return result

  @classmethod
  def model_validate_proto(cls, data: bytes):
    """Deserialize protobuf bytes into the Pydantic model."""
    stream = BytesIO(data)
    field_values = {}

    while stream.tell() < len(data):
      # Read field tag
      tag = cls._decode_varint(stream)
      field_number = tag >> 3
      wire_type = tag & 0x07

      # Get field name from field number (1-indexed)
      field_names = list(cls.model_fields.keys())
      if field_number - 1 >= len(field_names):
        raise ValueError(f"Unknown field number: {field_number}")

      field_name = field_names[field_number - 1]
      field = cls.model_fields[field_name]
      annotation = field.annotation
      origin = get_origin(annotation)

      # Unwrap Optional
      if origin is Union or origin is types.UnionType:
        anns = get_args(annotation)
        anns = [ann for ann in anns if ann is not type(None)]
        if len(anns) == 1:
          annotation = anns[0]
          origin = get_origin(annotation)

      # Parse based on wire type
      if wire_type == WIRETYPE_VARINT:
        value = cls._decode_varint(stream)
        if annotation == bool:
          value = bool(value)
      elif wire_type == WIRETYPE_FIXED64:
        value = struct.unpack('<d', stream.read(8))[0]
      elif wire_type == WIRETYPE_LENGTH_DELIMITED:
        length = cls._decode_varint(stream)
        data_bytes = stream.read(length)

        if annotation == str:
          value = data_bytes.decode('utf-8')
        elif annotation == bytes:
          value = data_bytes
        elif origin is list:
          # Nested message or repeated field
          inner_type = get_args(annotation)[0]
          if isinstance(inner_type, type) and issubclass(inner_type, ProtoModel):
            value = inner_type.model_validate_proto(data_bytes)
          else:
            value = data_bytes
        elif isinstance(annotation, type) and issubclass(annotation, ProtoModel):
          value = annotation.model_validate_proto(data_bytes)
        else:
          value = data_bytes
      else:
        raise ValueError(f"Unsupported wire type: {wire_type}")

      # Handle repeated fields
      if origin is list:
        if field_name not in field_values:
          field_values[field_name] = []
        field_values[field_name].append(value)
      else:
        field_values[field_name] = value

    return cls(**field_values)
