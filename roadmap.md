# 🗺 Roadmap

Here is the roadmap for this project. We are open to make changes based on community suggestions

## Items

- [x] Basic scalar types (`int`, `float`, `bool`, `str`, `bytes`)
- [x] Nested messages (ProtoModel instances)
- [x] Repeated fields (lists)
- [x] Optional fields (Union with None)
- [x] Automatic field numbering (1-indexed based on field order)
- [x] Round-trip serialization/deserialization
- [x] Full Pydantic validation support
- [x] Enum Support: Handle Python enums and protobuf enum types
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

## Milestones

- [ ] Support for all protobuf types and field indexes
- [ ] protoc plugin
- [ ] Rust encoding and decoding , similar to pydantic
- [ ] Proposing to merge these features onto pydantic (who knows 💪 ?!)
