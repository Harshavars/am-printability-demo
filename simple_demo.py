#!/usr/bin/env python3
"""Simple AM Printability Demo"""

print("=" * 60)
print("AM PRINTABILITY SCREENING SYSTEM - SIMPLE DEMO")
print("=" * 60)
print()

# Simulated part analysis
parts = [
    {"name": "Small Bracket", "size": [45, 30, 25], "wall_thickness": 2.5, "overhang_percent": 12},
    {"name": "Large Housing", "size": [300, 300, 400], "wall_thickness": 3.0, "overhang_percent": 15},
    {"name": "Complex Bracket", "size": [80, 60, 70], "wall_thickness": 0.8, "overhang_percent": 25}
]

BUILD_VOLUME = [250, 250, 325]
MIN_WALL_THICKNESS = 1.0
MAX_OVERHANG_PERCENT = 20

print("PROCESS: Powder Bed Fusion - Laser (PBF-LB)")
print("MATERIAL: Ti-6Al-4V")
print(f"BUILD VOLUME: {BUILD_VOLUME[0]} × {BUILD_VOLUME[1]} × {BUILD_VOLUME[2]} mm")
print()

for i, part in enumerate(parts, 1):
    print(f"\nPART {i}: {part['name']}")
    print(f"  Size: {part['size'][0]} × {part['size'][1]} × {part['size'][2]} mm")
    print(f"  Wall Thickness: {part['wall_thickness']} mm")
    
    violations = []
    risk_score = 0
    
    if max(part['size']) > max(BUILD_VOLUME):
        violations.append("❌ CRITICAL: Exceeds build volume")
        risk_score += 30
    
    if part['wall_thickness'] < MIN_WALL_THICKNESS:
        violations.append(f"⚠️  WARNING: Wall too thin ({part['wall_thickness']} mm)")
        risk_score += 15
    
    if part['overhang_percent'] > MAX_OVERHANG_PERCENT:
        violations.append(f"⚠️  WARNING: High overhang ({part['overhang_percent']}%)")
        risk_score += 10
    
    if any("CRITICAL" in v for v in violations):
        decision = "❌ REJECT"
    elif risk_score > 20:
        decision = "⚠️  NEEDS REVIEW"
    else:
        decision = "✅ FEASIBLE"
    
    print(f"\n  DECISION: {decision}")
    print(f"  RISK SCORE: {risk_score}/100")
    
    if violations:
        print(f"\n  VIOLATIONS:")
        for v in violations:
            print(f"    {v}")

print("\n" + "=" * 60)
