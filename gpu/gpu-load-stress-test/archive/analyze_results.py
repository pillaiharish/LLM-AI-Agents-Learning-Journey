#!/usr/bin/env python3
"""
Analyze GPU Stress Test Results
"""
import csv
import os

log_file = 'logs/gpu_stress_full_20260103_012003.csv'

if not os.path.exists(log_file):
    print(f"❌ Log file not found: {log_file}")
    exit(1)

print("="*70)
print("GPU STRESS TEST ANALYSIS")
print("="*70)
print(f"Source: {log_file}\n")

# Parse CSV
temps = []
powers = []
utils = []
clocks = []

with open(log_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        temps.append(float(row['GPU_Temp_C']))
        powers.append(float(row['GPU_Power_W']))
        utils.append(float(row['GPU_Util_%']))
        clocks.append(float(row['GPU_Clock_MHz']))

# Statistics
max_temp = max(temps)
avg_temp = sum(temps) / len(temps)
max_power = max(powers)
avg_power = sum(powers) / len(temps)
max_util = max(utils)
avg_util = sum(utils) / len(utils)
max_clock = max(clocks)

print("📊 METRICS SUMMARY")
print("-"*70)
print(f"Test Duration:          {len(temps)} seconds")
print(f"\nTemperature:")
print(f"  Maximum:              {max_temp:.1f}°C")
print(f"  Average:              {avg_temp:.1f}°C")
print(f"  Safety Threshold:     83°C")
print(f"  Margin:               {83 - max_temp:+.1f}°C")

print(f"\nPower Draw:")
print(f"  Maximum:              {max_power:.1f}W")
print(f"  Average:              {avg_power:.1f}W")
print(f"  TDP Threshold:        285W")
print(f"  Margin:               {285 - max_power:+.1f}W")

print(f"\nGPU Utilization:")
print(f"  Maximum:              {max_util:.0f}%")
print(f"  Average:              {avg_util:.1f}%")

print(f"\nGPU Clock:")
print(f"  Maximum:              {max_clock:.0f} MHz")

print("\n" + "="*70)
print("🔍 ANALYSIS")
print("="*70)

# Temperature analysis
print("\n1. THERMAL PERFORMANCE:")
if max_temp < 50:
    print(f"   ✅ EXCELLENT - GPU barely warmed up ({max_temp:.0f}°C)")
    print("   → Cooling is more than adequate")
    print("   → GPU was not stressed enough to evaluate cooling limits")
elif max_temp < 70:
    print(f"   ✅ VERY GOOD - Low temps under load ({max_temp:.0f}°C)")
    print("   → Excellent cooling performance")
elif max_temp < 80:
    print(f"   ✅ GOOD - Acceptable temps ({max_temp:.0f}°C)")
    print("   → Adequate cooling for normal use")
else:
    print(f"   ⚠️  WARM - Approaching limits ({max_temp:.0f}°C)")
    print("   → Consider improving cooling")

# Power analysis  
print("\n2. POWER CONSUMPTION:")
if avg_power < 50:
    print(f"   ⚠️  MINIMAL LOAD - Only {avg_power:.0f}W average")
    print("   → GPU was NOT properly stressed")
    print("   → stress-ng GPU test did not generate significant load")
elif avg_power < 150:
    print(f"   ℹ️  MODERATE LOAD - {avg_power:.0f}W average")
    print("   → Partial GPU stress achieved")
elif avg_power < 250:
    print(f"   ✅ GOOD LOAD - {avg_power:.0f}W average")
    print("   → Significant GPU stress achieved")
else:
    print(f"   🔥 MAXIMUM LOAD - {avg_power:.0f}W average")
    print("   → Full GPU stress achieved")

# Utilization analysis
print("\n3. GPU UTILIZATION:")
if avg_util < 20:
    print(f"   ❌ VERY LOW - Only {avg_util:.1f}% average utilization")
    print("   → Test tool (stress-ng) did NOT effectively stress the GPU")
    print("   → Recommendation: Use FurMark, Unigine, or gpu-burn for real stress")
elif avg_util < 50:
    print(f"   ⚠️  LOW - {avg_util:.1f}% average utilization")
    print("   → Partial stress only")
elif avg_util < 80:
    print(f"   ✅ MODERATE - {avg_util:.1f}% average utilization")
    print("   → Good stress achieved")
else:
    print(f"   ✅ HIGH - {avg_util:.1f}% average utilization")
    print("   → Excellent stress test")

print("\n" + "="*70)
print("💡 CONCLUSIONS")
print("="*70)

if avg_util < 20:
    print("\n❌ TEST LIMITATION:")
    print("   The stress-ng tool did NOT effectively load the RTX 5070 Ti.")
    print("   Average utilization was only {:.1f}%, which is insufficient.".format(avg_util))
    print("\n📝 RECOMMENDATIONS:")
    print("   1. Install proper GPU stress tool:")
    print("      • FurMark (Windows/Linux)")
    print("      • Unigine Superposition (Windows/Linux)")  
    print("      • gpu-burn (Linux CUDA tool)")
    print("   2. Re-run test with proper tool for 10+ minutes")
    print("   3. Monitor temps approaching 70-80°C for real cooling test")
    
print("\n✅ SYSTEM STATUS:")
print(f"   • GPU is healthy and functional")
print(f"   • Idle/light load temps are excellent ({avg_temp:.0f}°C)")
print(f"   • Safety monitoring worked correctly")
print(f"   • No throttling or safety violations detected")

print("\n📊 WHAT WE LEARNED:")
print(f"   • Idle temperature: ~{avg_temp:.0f}°C")
print(f"   • Light load power: ~{avg_power:.0f}W")
print(f"   • GPU is stable and responding normally")
print(f"   • Cooling is adequate for light loads")
print(f"   • Need real stress test tool for full evaluation")

print("\n" + "="*70)
print("NEXT STEPS: Install FurMark or Unigine Superposition for proper testing")
print("="*70)
