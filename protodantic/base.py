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
from pydantic.fields import FieldInfo
from pydantic.config import JsonDict

class ProtoModel(BaseModel):

  @classmethod
  def get_wiretype_for_annotation(cls, annotation) -> int:
    """Get the wiretype for a given Pydantic field based on its annotation."""
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
    # Handle dict types (maps)
    if origin is dict:
      return WIRETYPE_LENGTH_DELIMITED
    if annotation in {int, bool} or issubclass(annotation, IntEnum):
        return WIRETYPE_VARINT  # varint
    if annotation == float:
        return WIRETYPE_FIXED64  # 64-bit
    if annotation in {str, bytes}:
        return WIRETYPE_LENGTH_DELIMITED  # length-delimited
    if isinstance(annotation, type) and issubclass(annotation, ProtoModel):
        return WIRETYPE_LENGTH_DELIMITED  # nested message
    raise ValueError(f"Unsupported field type: {annotation}")

  def build_key(self, field_number: int, annotation) -> int:
    """Build the protobuf key from field number and wire type."""
    return (field_number << 3) | self.get_wiretype_for_annotation(annotation)

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

    # Handle list/dict types
    if origin is list :
      raise RuntimeError("list[list[T]] or dict[...,list[T]] not supported by protobuf")
    elif origin is dict:
      raise RuntimeError("list[dict[T]] or dict[...,dict[T]] not supported by protobuf")
    elif annotation == int:
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

  def encode_list(self,key, value, annotation, output: BytesIO):
    """Encode a list of values."""
    inner_type = get_args(annotation)[0]
    for item in value:
      _EncodeVarint(output.write, key)
      self._encode_value(item, inner_type, output)
    
  def endode_dict(self, key,  value, annotation, output: BytesIO):
    """Encode a dictionary of key-value pairs."""
    key_type, value_type = get_args(annotation)
    key_key = (1 << 3) | self.get_wiretype_for_annotation(key_type)
    value_key = (2 << 3) | self.get_wiretype_for_annotation(value_type)
    for dict_key, dict_value in value.items():
      _EncodeVarint(output.write, key)
      item_output = BytesIO()
      _EncodeVarint(item_output.write, key_key)
      self._encode_value(dict_key, key_type, item_output)
      _EncodeVarint(item_output.write, value_key)
      self._encode_value(dict_value, value_type, item_output)
      item_bytes = item_output.getvalue()
      _EncodeVarint(output.write, len(item_bytes))
      output.write(item_bytes)

  def encode_field(self, field_number: int, value, annotation, output: BytesIO):
    """Encode a single field with its key and value."""
    key = self.build_key(field_number, annotation)
    if get_origin(annotation) is list:
      self.encode_list(key, value, annotation, output)
    elif get_origin(annotation) is dict:
      self.endode_dict(key, value, annotation, output)
    else:
      _EncodeVarint(output.write, key)
      self._encode_value(value, annotation, output)

  @classmethod
  def create_proto_map(cls) -> dict[int, dict]:
    proto_map : dict[int,dict] = {}
    default_index = 1
    for field_name, field in cls.model_fields.items():
      if isinstance(field.json_schema_extra,dict):
        if (index_override := field.json_schema_extra.get("proto_index")) is not None:
          proto_map[index_override] = {"name":field_name,"infos":field} # type: ignore
      else:
        proto_map[default_index] = {"name":field_name,"infos":field}
      default_index += 1
    return proto_map

  def model_dump_proto(self) -> bytes:
    """Serialize the Pydantic model to protobuf bytes."""
    output = BytesIO()

    for field_number, field in self.create_proto_map().items():
      field_name , field = field['name'] , field['infos']
      value = getattr(self, field_name)

      # Skip None values for optional fields
      if value is None:
        continue

      # Skip default values for optional fields
      if not field.is_required() and value == field.default:
        continue
      self.encode_field(field_number, value, field.annotation, output)

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

      proto_map = cls.create_proto_map()
      if field_number not in proto_map:
        raise ValueError(f"Unknown field number: {field_number}")

      field_name = proto_map[field_number]['name']
      field = proto_map[field_number]['infos']
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
        elif origin is dict:
          # Map entry - parse key and value fields
          key_type, value_type = get_args(annotation)
          entry_stream = BytesIO(data_bytes)
          entry_key = None
          entry_value = None
          
          while entry_stream.tell() < len(data_bytes):
            entry_tag = cls._decode_varint(entry_stream)
            entry_field_number = entry_tag >> 3
            entry_wire_type = entry_tag & 0x07
            
            if entry_field_number == 1:  # Key field
              if entry_wire_type == WIRETYPE_VARINT:
                entry_key = cls._decode_varint(entry_stream)
              elif entry_wire_type == WIRETYPE_LENGTH_DELIMITED:
                key_length = cls._decode_varint(entry_stream)
                key_bytes = entry_stream.read(key_length)
                if key_type == str:
                  entry_key = key_bytes.decode('utf-8')
                else:
                  entry_key = key_bytes
            elif entry_field_number == 2:  # Value field
              if entry_wire_type == WIRETYPE_VARINT:
                entry_value = cls._decode_varint(entry_stream)
                if value_type == bool:
                  entry_value = bool(entry_value)
              elif entry_wire_type == WIRETYPE_FIXED64:
                entry_value = struct.unpack('<d', entry_stream.read(8))[0]
              elif entry_wire_type == WIRETYPE_LENGTH_DELIMITED:
                value_length = cls._decode_varint(entry_stream)
                value_bytes = entry_stream.read(value_length)
                if value_type == str:
                  entry_value = value_bytes.decode('utf-8')
                elif value_type == bytes:
                  entry_value = value_bytes
                elif isinstance(value_type, type) and issubclass(value_type, ProtoModel):
                  entry_value = value_type.model_validate_proto(value_bytes)
                else:
                  entry_value = value_bytes
          
          value = (entry_key, entry_value)
        elif isinstance(annotation, type) and issubclass(annotation, ProtoModel):
          value = annotation.model_validate_proto(data_bytes)
        else:
          value = data_bytes
      else:
        raise ValueError(f"Unsupported wire type: {wire_type}")

      # Handle repeated fields (lists and dicts)
      if origin is list:
        if field_name not in field_values:
          field_values[field_name] = []
        field_values[field_name].append(value)
      elif origin is dict:
        if field_name not in field_values:
          field_values[field_name] = {}
        entry_key, entry_value = value # type: ignore
        field_values[field_name][entry_key] = entry_value
      else:
        field_values[field_name] = value

    return cls(**field_values)