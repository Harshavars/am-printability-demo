#!/usr/bin/env python3
"""
Simple AM Printability Demo - Self-Contained Version
This single file demonstrates the core concept without external dependencies
"""

print("=" * 60)
print("AM PRINTABILITY SCREENING SYSTEM - SIMPLE DEMO")
print("=" * 60)
print()

# Simulated part analysis
parts = [
    {
        "name": "Small Bracket",
        "size": [45, 30, 25],  # X, Y, Z in mm
        "wall_thickness": 2.5,
        "overhang_percent": 12,
        "expected": "FEASIBLE"
    },
    {
        "name": "Large Housing",
        "size": [300, 300, 400],  # Exceeds build volume
        "wall_thickness": 3.0,
        "overhang_percent": 15,
        "expected": "REJECT"
    },
    {
        "name": "Complex Bracket",
        "size": [80, 60, 70],
        "wall_thickness": 0.8,  # Too thin
        "overhang_percent": 25,
        "expected": "NEEDS REVIEW"
    }
]

# Process constraints (PBF-LB with Ti-6Al-4V)
BUILD_VOLUME = [250, 250, 325]  # mm
MIN_WALL_THICKNESS = 1.0  # mm
MAX_OVERHANG_PERCENT = 20  # %

print("PROCESS: Powder Bed Fusion - Laser (PBF-LB)")
print("MATERIAL: Ti-6Al-4V")
print(f"BUILD VOLUME: {BUILD_VOLUME[0]} × {BUILD_VOLUME[1]} × {BUILD_VOLUME[2]} mm")
print(f"MIN WALL THICKNESS: {MIN_WALL_THICKNESS} mm")
print(f"MAX OVERHANG: {MAX_OVERHANG_PERCENT}%")
print()
print("-" * 60)

# Analyze each part
for i, part in enumerate(parts, 1):
    print(f"\nPART {i}: {part['name']}")
    print(f"  Size: {part['size'][0]} × {part['size'][1]} × {part['size'][2]} mm")
    print(f"  Wall Thickness: {part['wall_thickness']} mm")
    print(f"  Overhang: {part['overhang_percent']}%")
    print()
    
    violations = []
    risk_score = 0
    
    # Check build volume
    if (part['size'][0] > BUILD_VOLUME[0] or 
        part['size'][1] > BUILD_VOLUME[1] or 
        part['size'][2] > BUILD_VOLUME[2]):
        violations.append(f"❌ CRITICAL: Exceeds build volume ({part['size'][0]}×{part['size'][1]}×{part['size'][2]} > {BUILD_VOLUME[0]}×{BUILD_VOLUME[1]}×{BUILD_VOLUME[2]} mm)")
        risk_score += 30
    
    # Check wall thickness
    if part['wall_thickness'] < MIN_WALL_THICKNESS:
        violations.append(f"⚠️  WARNING: Wall thickness {part['wall_thickness']} mm below recommended {MIN_WALL_THICKNESS} mm")
        risk_score += 15
    
    # Check overhang
    if part['overhang_percent'] > MAX_OVERHANG_PERCENT:
        violations.append(f"⚠️  WARNING: High overhang area {part['overhang_percent']}% (requires support structures)")
        risk_score += 10
    
    # Make decision
    if any("CRITICAL" in v for v in violations):
        decision = "❌ REJECT"
        confidence = 95
    elif risk_score > 20:
        decision = "⚠️  NEEDS REVIEW"
        confidence = 65
    else:
        decision = "✅ FEASIBLE"
        confidence = 85
    
    # Print results
    print(f"  DECISION: {decision}")
    print(f"  CONFIDENCE: {confidence}%")
    print(f"  RISK SCORE: {risk_score}/100")
    
    if violations:
        print(f"\n  VIOLATIONS ({len(violations)}):")
        for violation in violations:
            print(f"    {violation}")
    else:
        print("\n  ✓ No violations detected")
    
    # Recommendations
    print(f"\n  RECOMMENDATIONS:")
    if "Exceeds build volume" in str(violations):
        print(f"    • Scale part by {BUILD_VOLUME[2]/part['size'][2]:.2f}× to fit build envelope")
    if part['wall_thickness'] < MIN_WALL_THICKNESS:
        print(f"    • Increase wall thickness to {MIN_WALL_THICKNESS} mm minimum")
    if part['overhang_percent'] > MAX_OVERHANG_PERCENT:
        print(f"    • Consider reorienting part to reduce overhangs")
        print(f"    • Budget for support removal and surface finishing")
    if not violations:
        print(f"    • Part appears printable with standard process parameters")
    
    print("\n" + "-" * 60)

print()
print("=" * 60)
print("DEMO COMPLETE")
print("=" * 60)
print()
print("WHAT THIS DEMONSTRATES:")
print("1. Geometry analysis (size, wall thickness, overhang)")
print("2. Constraint checking (build volume, material limits)")
print("3. Risk scoring (weighted by severity)")
print("4. Evidence-based decisions (shows WHY it passed/failed)")
print("5. Actionable recommendations (not just 'fix the design')")
print()
print("THE REAL SYSTEM:")
print("• Loads actual STL/STEP CAD files")
print("• Extracts geometry using 3D mesh processing")
print("• Runs 10+ validation rules")
print("• Shows interactive 3D visualization")
print("• Exports JSON reports")
print()
print("This simplified version shows the LOGIC without needing CAD files.")
print("=" * 60)
