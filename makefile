.PHONY: proto proto-clean help

# Variables
PROTO_DIR := tests/proto
PROTO_FILES := $(wildcard $(PROTO_DIR)/*.proto)
PYTHON_OUT := $(PROTO_DIR)

help:
	@echo "Protodantic Makefile Targets:"
	@echo "  make proto       - Generate Python code from .proto files using grpcio-tools"
	@echo "  make proto-clean - Remove generated protobuf Python files"

# Generate Python protobuf files from .proto files
proto: $(PROTO_FILES)
	python -m grpc_tools.protoc \
		-I$(PROTO_DIR) \
		--python_out=$(PYTHON_OUT) \
		--grpc_python_out=$(PYTHON_OUT) \
		--pyi_out=$(PYTHON_OUT) \
		$(PROTO_FILES)

# Clean generated protobuf files
proto-clean:
	rm -f $(PROTO_DIR)/*_pb2.py $(PROTO_DIR)/*_pb2.pyi $(PROTO_DIR)/*_pb2_grpc.py
	find $(PROTO_DIR) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.DEFAULT_GOAL := help
