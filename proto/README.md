# Protocol Buffers (gRPC)

This directory contains Protocol Buffer definitions and generated code for gRPC services.

## Files

- `voicebridge.proto` - Protocol Buffer definition file
- `voicebridge_pb2.py` - Generated Python code (auto-generated)
- `voicebridge_pb2_grpc.py` - Generated gRPC Python code (auto-generated)

## Regenerating Code

If you modify the `.proto` file, regenerate the Python files using:

```bash
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. --proto_path=. voicebridge.proto
```

Or use the provided script:

```bash
python scripts/generate_proto.py
```

## Note

The `*_pb2.py` and `*_pb2_grpc.py` files are auto-generated and can be regenerated from the `.proto` file. They are included in the repository for convenience, but can be excluded from version control if preferred.
