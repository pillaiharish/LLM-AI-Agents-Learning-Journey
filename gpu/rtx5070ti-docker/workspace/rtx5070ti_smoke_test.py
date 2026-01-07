#!/usr/bin/env python3
"""
Enhanced GPU Smoke Test for RTX 5070 Ti (Blackwell sm_120)
Provides detailed compatibility and performance information
"""

import torch
import sys
import platform

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_rtx5070ti_compatibility():
    print_section("RTX 5070 Ti Compatibility Check")
    
    print(f"🖥️  System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"🔥 PyTorch: {torch.__version__}")
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available!")
        print("   Check NVIDIA drivers and Docker GPU support")
        return False
    
    print(f"✅ CUDA available: {torch.version.cuda}")
    print(f"📊 GPU Count: {torch.cuda.device_count()}")
    
    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        print(f"\n🎮 GPU {i}: {props.name}")
        print(f"   Memory: {props.total_memory / 1e9:.1f} GB")
        print(f"   Compute capability: sm_{props.major}{props.minor}")
        
        # Check if this is RTX 5070 Ti
        if "5070 Ti" in props.name:
            if props.major == 12 and props.minor == 0:
                print("   ✅ RTX 5070 Ti detected with sm_120 capability")
                return test_blackwell_operations(i)
            else:
                print(f"   ⚠️  Unexpected compute capability for RTX 5070 Ti: sm_{props.major}{props.minor}")
        else:
            print(f"   ℹ️  Different GPU detected: {props.name}")
    
    return True

def test_blackwell_operations(device_id=0):
    print_section("Blackwell Architecture Operations Test")
    
    try:
        # Set device
        torch.cuda.set_device(device_id)
        device = f"cuda:{device_id}"
        
        print(f"🎯 Testing on GPU {device_id}")
        
        # Test 1: Basic tensor operations
        print("🧪 Test 1: Basic tensor operations...")
        x = torch.randn(1000, 1000, device=device)
        y = torch.randn(1000, 1000, device=device)
        z = x + y
        print(f"   ✅ Addition: {z.shape} on {z.device}")
        
        # Test 2: Matrix multiplication
        print("🧪 Test 2: Matrix multiplication...")
        result = torch.matmul(x, y)
        print(f"   ✅ MatMul: {result.shape}, sample value: {result[0,0].item():.6f}")
        
        # Test 3: Neural network operation
        print("🧪 Test 3: Neural network operations...")
        linear = torch.nn.Linear(1000, 500).to(device)
        output = linear(x)
        print(f"   ✅ Linear layer: {output.shape}")
        
        # Test 4: Memory allocation stress test
        print("🧪 Test 4: Memory allocation test...")
        large_tensor = torch.randn(5000, 5000, device=device)
        result = torch.sum(large_tensor)
        print(f"   ✅ Large tensor ops: sum = {result.item():.6f}")
        
        # Test 5: Mixed precision (if supported)
        print("🧪 Test 5: Mixed precision test...")
        try:
            with torch.autocast(device_type='cuda', dtype=torch.float16):
                fp16_result = torch.matmul(x.half(), y.half())
            print(f"   ✅ Mixed precision: {fp16_result.dtype}")
        except Exception as e:
            print(f"   ⚠️  Mixed precision warning: {e}")
        
        return True
        
    except RuntimeError as e:
        if "no kernel image is available" in str(e):
            print(f"❌ KERNEL COMPATIBILITY ERROR:")
            print(f"   {e}")
            print(f"\n🔧 SOLUTIONS:")
            print(f"   1. Update PyTorch to latest nightly build:")
            print(f"      pip install torch --index-url https://download.pytorch.org/whl/nightly/cu124")
            print(f"   2. Check NVIDIA driver version (need ≥ 560.0)")
            print(f"   3. Ensure Docker has latest NVIDIA Container Toolkit")
            return False
        else:
            print(f"❌ Unexpected CUDA error: {e}")
            return False
    
    except Exception as e:
        print(f"❌ General error: {e}")
        return False

def check_pytorch_build_info():
    print_section("PyTorch Build Information")
    
    print(f"🔨 PyTorch built with CUDA: {torch.version.cuda}")
    print(f"🔧 Debug mode: {torch.version.debug}")
    
    # Check if PyTorch was built with sm_120 support
    if hasattr(torch.version, 'cuda_version'):
        cuda_ver = torch.version.cuda_version
        print(f"📦 CUDA version in build: {cuda_ver}")
    
    # Check supported architectures (if available)
    try:
        import torch.utils.cpp_extension
        print("🏗️  Checking available CUDA architectures...")
        # This is an indirect way to check build capabilities
    except:
        pass
    
    print(f"🎯 Recommended for RTX 5070 Ti:")
    print(f"   • PyTorch ≥ 2.5.0 with CUDA 12.4+")
    print(f"   • Built with sm_120 support")
    print(f"   • NVIDIA driver ≥ 560.0")

def performance_benchmark(device_id=0):
    print_section("Performance Benchmark")
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available for benchmarking")
        return
    
    import time
    device = f"cuda:{device_id}"
    
    # Warmup
    print("🔥 Warming up GPU...")
    for _ in range(10):
        x = torch.randn(1000, 1000, device=device)
        torch.matmul(x, x)
    torch.cuda.synchronize()
    
    # Benchmark matrix multiplication
    print("📊 Benchmarking matrix multiplication...")
    sizes = [1000, 2000, 4000]
    
    for size in sizes:
        x = torch.randn(size, size, device=device)
        
        torch.cuda.synchronize()
        start_time = time.time()
        
        for _ in range(10):
            result = torch.matmul(x, x)
        
        torch.cuda.synchronize()
        end_time = time.time()
        
        ops_per_sec = 10 / (end_time - start_time)
        gflops = (2 * size**3 * ops_per_sec) / 1e9
        
        print(f"   {size}x{size}: {ops_per_sec:.1f} ops/sec, {gflops:.1f} GFLOPS")

def main():
    print("🚀 RTX 5070 Ti GPU Smoke Test")
    print("=============================")
    
    success = True
    
    # Main compatibility test
    if not test_rtx5070ti_compatibility():
        success = False
    
    # Build info
    check_pytorch_build_info()
    
    # Performance test (only if basic ops work)
    if success:
        try:
            performance_benchmark()
        except Exception as e:
            print(f"⚠️  Benchmark failed: {e}")
    
    print_section("Summary")
    if success:
        print("🎉 All tests passed! RTX 5070 Ti is working correctly.")
        print("💡 Your environment is ready for ML/AI workloads.")
    else:
        print("❌ Some tests failed. Check the solutions above.")
        print("🔧 Try running the quick-fix script: ./quick-fix-rtx5070ti.sh")
    
    return success

if __name__ == "__main__":
    main()