#!/usr/bin/env python3
"""
Script to generate gRPC protobuf files from .proto definitions
"""
import subprocess
import sys
from pathlib import Path


def generate_proto_files():
    """Generate Python gRPC files from protobuf definitions"""

    # Get the project root directory
    project_root = Path(__file__).parent.parent
    proto_dir = project_root / "proto"
    output_dir = project_root / "proto"

    # Ensure proto directory exists
    proto_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    # Find all .proto files
    proto_files = list(proto_dir.glob("*.proto"))

    if not proto_files:
        print("No .proto files found in proto/ directory")
        return False

    print(f"Found {len(proto_files)} proto files:")
    for proto_file in proto_files:
        print(f"  - {proto_file.name}")

    # Generate Python files for each proto file
    for proto_file in proto_files:
        print(f"\nGenerating files for {proto_file.name}...")

        try:
            # Run protoc command
            cmd = [
                sys.executable,
                "-m",
                "grpc_tools.protoc",
                f"--proto_path={proto_dir}",
                f"--python_out={output_dir}",
                f"--grpc_python_out={output_dir}",
                str(proto_file),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Successfully generated files for {proto_file.name}")

                # List generated files
                base_name = proto_file.stem
                generated_files = [output_dir / f"{base_name}_pb2.py", output_dir / f"{base_name}_pb2_grpc.py"]

                for gen_file in generated_files:
                    if gen_file.exists():
                        print(f"  - {gen_file.name}")
                    else:
                        print(f"  ⚠️  {gen_file.name} not found")

            else:
                print(f"❌ Failed to generate files for {proto_file.name}")
                print(f"Error: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error generating files for {proto_file.name}: {e}")
            return False

    # Create __init__.py file in proto directory
    init_file = output_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Generated gRPC protobuf files\n")
        print(f"\n✅ Created {init_file}")

    print("\n🎉 All proto files generated successfully!")
    return True


def main():
    """Main function"""
    print("🔧 Generating gRPC protobuf files...")

    # Check if grpc-tools is installed
    try:
        import grpc_tools  # noqa: F401

        print("✅ grpc-tools is installed")
    except ImportError:
        print("❌ grpc-tools is not installed")
        print("Please install it with: pip install grpcio-tools")
        return False

    # Generate files
    success = generate_proto_files()

    if success:
        print("\n📁 Generated files are ready to use in your gRPC services")
        print("💡 You can now import them in your Python code:")
        print("   from proto import voicebridge_pb2")
        print("   from proto import voicebridge_pb2_grpc")
    else:
        print("\n❌ Failed to generate proto files")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
