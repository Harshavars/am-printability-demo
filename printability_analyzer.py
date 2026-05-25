import trimesh
import numpy as np
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Optional

class Decision(Enum):
    FEASIBLE = "✅ Feasible"
    NEEDS_REVIEW = "⚠️ Needs Review"
    REJECT = "❌ Reject"

class ProcessType(Enum):
    PBF_LASER = "Powder Bed Fusion - Laser (PBF-LB)"
    MATERIAL_EXTRUSION = "Material Extrusion (MEX/FDM)"

@dataclass
class GeometricFeatures:
    volume_mm3: float
    surface_area_mm2: float
    bounding_box_mm: Tuple[float, float, float]
    min_wall_thickness_mm: Optional[float]
    max_wall_thickness_mm: Optional[float]
    overhang_area_mm2: float
    overhang_percentage: float
    unsupported_spans_mm: List[float]
    aspect_ratio: float
    is_manifold: bool
    vertex_count: int
    face_count: int

@dataclass
class Violation:
    rule_id: str
    severity: str
    category: str
    message: str
    measured_value: float
    threshold_value: float
    evidence: str

@dataclass
class PrintabilityResult:
    decision: Decision
    confidence: float
    process_type: ProcessType
    material: str
    geometric_features: GeometricFeatures
    violations: List[Violation]
    risk_score: float
    recommendations: List[str]
    evidence_summary: str

class PrintabilityAnalyzer:
    def __init__(self, process_type=ProcessType.PBF_LASER, material="Ti-6Al-4V"):
        self.process_type = process_type
        self.material = material
        self.constraints = self._load_constraints()
    
    def _load_constraints(self):
        if self.process_type == ProcessType.PBF_LASER:
            if self.material == "Ti-6Al-4V":
                return {
                    "build_volume_mm": (250, 250, 325),
                    "min_wall_thickness_mm": 0.4,
                    "recommended_wall_thickness_mm": 1.0,
                    "max_overhang_angle_deg": 45,
                }
            elif self.material == "AlSi10Mg":
                return {
                    "build_volume_mm": (250, 250, 325),
                    "min_wall_thickness_mm": 0.3,
                    "recommended_wall_thickness_mm": 0.8,
                    "max_overhang_angle_deg": 45,
                }
            else:  # 316L
                return {
                    "build_volume_mm": (250, 250, 325),
                    "min_wall_thickness_mm": 0.4,
                    "recommended_wall_thickness_mm": 1.2,
                    "max_overhang_angle_deg": 45,
                }
        else:  # MEX
            return {
                "build_volume_mm": (220, 220, 250),
                "min_wall_thickness_mm": 0.8,
                "recommended_wall_thickness_mm": 2.0,
                "max_overhang_angle_deg": 60,
            }
    
    def analyze_file(self, file_path):
        try:
            mesh = trimesh.load(str(file_path))
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate([
                    geom for geom in mesh.geometry.values()
                    if isinstance(geom, trimesh.Trimesh)
                ])
        except Exception as e:
            return self._insufficient_data_result(f"Failed to parse geometry: {str(e)}")
        
        features = self._extract_features(mesh)
        violations = self._check_constraints(features)
        risk_score = self._calculate_risk_score(violations, features)
        decision, confidence = self._make_decision(violations, risk_score)
        recommendations = self._generate_recommendations(violations, features)
        evidence = self._generate_evidence(features, violations)
        
        return PrintabilityResult(
            decision=decision,
            confidence=confidence,
            process_type=self.process_type,
            material=self.material,
            geometric_features=features,
            violations=violations,
            risk_score=risk_score,
            recommendations=recommendations,
            evidence_summary=evidence
        )
    
    def _extract_features(self, mesh):
        volume = mesh.volume
        surface_area = mesh.area
        bounds = mesh.bounds
        bbox_size = bounds[1] - bounds[0]
        is_manifold = mesh.is_watertight
        aspect_ratio = bbox_size[2] / min(bbox_size[0], bbox_size[1]) if min(bbox_size[0], bbox_size[1]) > 0 else 0
        
        # Simple wall thickness estimate
        min_wall = min(bbox_size) if is_manifold else None
        max_wall = max(bbox_size) if is_manifold else None
        
        # Overhang detection
        normals = mesh.face_normals
        face_areas = mesh.area_faces
        z_axis = np.array([0, 0, 1])
        angles = np.arccos(np.clip(np.dot(normals, z_axis), -1, 1)) * 180 / np.pi
        overhang_mask = angles > 135
        overhang_area = np.sum(face_areas[overhang_mask])
        overhang_percentage = (overhang_area / mesh.area) * 100 if mesh.area > 0 else 0
        
        # Unsupported spans (simplified)
        unsupported_spans = [bbox_size[0], bbox_size[1]] if overhang_percentage > 10 else []
        
        return GeometricFeatures(
            volume_mm3=volume,
            surface_area_mm2=surface_area,
            bounding_box_mm=tuple(bbox_size),
            min_wall_thickness_mm=min_wall,
            max_wall_thickness_mm=max_wall,
            overhang_area_mm2=overhang_area,
            overhang_percentage=overhang_percentage,
            unsupported_spans_mm=unsupported_spans,
            aspect_ratio=aspect_ratio,
            is_manifold=is_manifold,
            vertex_count=len(mesh.vertices),
            face_count=len(mesh.faces)
        )
    
    def _check_constraints(self, features):
        violations = []
        
        # Build volume check
        build_vol = self.constraints.get("build_volume_mm")
        if build_vol:
            bbox = features.bounding_box_mm
            if bbox[0] > build_vol[0] or bbox[1] > build_vol[1] or bbox[2] > build_vol[2]:
                violations.append(Violation(
                    rule_id="R001",
                    severity="CRITICAL",
                    category="Build Volume",
                    message=f"Part exceeds build volume: {bbox[0]:.1f}×{bbox[1]:.1f}×{bbox[2]:.1f}mm > {build_vol[0]}×{build_vol[1]}×{build_vol[2]}mm",
                    measured_value=max(bbox[0]/build_vol[0], bbox[1]/build_vol[1], bbox[2]/build_vol[2]),
                    threshold_value=1.0,
                    evidence=f"Bounding box: {bbox[0]:.1f} × {bbox[1]:.1f} × {bbox[2]:.1f} mm"
                ))
        
        # Manifold check
        if not features.is_manifold:
            violations.append(Violation(
                rule_id="R004",
                severity="CRITICAL",
                category="Geometry",
                message="Mesh is not watertight (non-manifold geometry)",
                measured_value=0,
                threshold_value=1,
                evidence="Non-manifold edges or holes detected. Repair required before printing."
            ))
        
        # Overhang check
        overhang_threshold = 15.0
        if features.overhang_percentage > overhang_threshold:
            violations.append(Violation(
                rule_id="R005",
                severity="WARNING",
                category="Overhangs",
                message=f"High overhang area: {features.overhang_percentage:.1f}% of surface",
                measured_value=features.overhang_percentage,
                threshold_value=overhang_threshold,
                evidence=f"Requires extensive support structures ({features.overhang_area_mm2:.1f}mm² overhang area)"
            ))
        
        return violations
    
    def _calculate_risk_score(self, violations, features):
        score = 0.0
        for v in violations:
            if v.severity == "CRITICAL":
                score += 30
            elif v.severity == "WARNING":
                score += 10
        
        if features.overhang_percentage > 20:
            score += 10
        
        return min(score, 100)
    
    def _make_decision(self, violations, risk_score):
        critical_violations = [v for v in violations if v.severity == "CRITICAL"]
        
        if critical_violations:
            return Decision.REJECT, 0.95
        
        if risk_score > 20:
            return Decision.NEEDS_REVIEW, 0.70
        
        return Decision.FEASIBLE, 0.85
    
    def _generate_recommendations(self, violations, features):
        recommendations = []
        
        for v in violations:
            if v.rule_id == "R001":
                recommendations.append(f"Scale part to fit within {self.constraints['build_volume_mm']} mm build envelope")
            elif v.rule_id == "R004":
                recommendations.append("Repair mesh: close holes, remove duplicate vertices, fix normals")
            elif v.rule_id == "R005":
                recommendations.append("Consider reorienting part to minimize overhangs below 45° from vertical")
        
        if not recommendations:
            recommendations.append("Part appears printable with standard process parameters")
        
        return recommendations
    
    def _generate_evidence(self, features, violations):
        lines = []
        lines.append(f"Geometry: {features.bounding_box_mm[0]:.1f} × {features.bounding_box_mm[1]:.1f} × {features.bounding_box_mm[2]:.1f} mm")
        lines.append(f"Volume: {features.volume_mm3:.1f} mm³")
        lines.append(f"Overhang area: {features.overhang_percentage:.1f}% of surface")
        lines.append(f"Mesh quality: {'Manifold' if features.is_manifold else 'Non-manifold (ERRORS)'}")
        
        if violations:
            lines.append(f"\n{len(violations)} constraint violation(s) detected")
        
        return "\n".join(lines)
    
    def _insufficient_data_result(self, reason):
        return PrintabilityResult(
            decision=Decision.REJECT,
            confidence=0.0,
            process_type=self.process_type,
            material=self.material,
            geometric_features=None,
            violations=[],
            risk_score=100,
            recommendations=[f"Unable to analyze: {reason}"],
            evidence_summary=reason
        )
