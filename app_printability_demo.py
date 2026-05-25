#!/usr/bin/env python3
"""
Interactive AM Printability Screening Demo
Web-based UI for analyzing CAD files
"""

import streamlit as st
import trimesh
import numpy as np
from pathlib import Path
import json
import plotly.graph_objects as go
from printability_analyzer import PrintabilityAnalyzer, ProcessType, Decision
import tempfile

# Page config
st.set_page_config(
    page_title="AM Printability Screening System",
    page_icon="🔧",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .danger-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def create_3d_visualization(mesh, violations=None):
    """Create interactive 3D visualization of the mesh"""
    
    vertices = mesh.vertices
    faces = mesh.faces
    
    # Create mesh plot
    fig = go.Figure(data=[
        go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            color='lightblue',
            opacity=0.7,
            name='Part Geometry'
        )
    ])
    
    # Add bounding box
    bounds = mesh.bounds
    bbox_points = np.array([
        [bounds[0][0], bounds[0][1], bounds[0][2]],
        [bounds[1][0], bounds[0][1], bounds[0][2]],
        [bounds[1][0], bounds[1][1], bounds[0][2]],
        [bounds[0][0], bounds[1][1], bounds[0][2]],
        [bounds[0][0], bounds[0][1], bounds[1][2]],
        [bounds[1][0], bounds[0][1], bounds[1][2]],
        [bounds[1][0], bounds[1][1], bounds[1][2]],
        [bounds[0][0], bounds[1][1], bounds[1][2]],
    ])
    
    # Bounding box edges
    edges = [
        [0,1], [1,2], [2,3], [3,0],  # Bottom
        [4,5], [5,6], [6,7], [7,4],  # Top
        [0,4], [1,5], [2,6], [3,7]   # Vertical
    ]
    
    for edge in edges:
        fig.add_trace(go.Scatter3d(
            x=[bbox_points[edge[0]][0], bbox_points[edge[1]][0]],
            y=[bbox_points[edge[0]][1], bbox_points[edge[1]][1]],
            z=[bbox_points[edge[0]][2], bbox_points[edge[1]][2]],
            mode='lines',
            line=dict(color='red', width=2, dash='dash'),
            showlegend=False
        ))
    
    fig.update_layout(
        scene=dict(
            xaxis_title='X (mm)',
            yaxis_title='Y (mm)',
            zaxis_title='Z (mm)',
            aspectmode='data'
        ),
        height=500,
        margin=dict(l=0, r=0, b=0, t=30)
    )
    
    return fig

def main():
    # Header
    st.markdown('<div class="main-header">🔧 AM Printability Screening System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automated feasibility analysis for additive manufacturing</div>', unsafe_allow_html=True)
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        process_type = st.selectbox(
            "Manufacturing Process",
            ["PBF-LB (Laser Powder Bed)", "MEX (Material Extrusion)"],
            help="Select the additive manufacturing process"
        )
        
        process_map = {
            "PBF-LB (Laser Powder Bed)": ProcessType.PBF_LASER,
            "MEX (Material Extrusion)": ProcessType.MATERIAL_EXTRUSION
        }
        
        if process_map[process_type] == ProcessType.PBF_LASER:
            material = st.selectbox(
                "Material",
                ["Ti-6Al-4V", "AlSi10Mg", "316L"],
                help="Select build material"
            )
        else:
            material = "PLA"
            st.info("Material: PLA (default for MEX)")
        
        st.divider()
        
        st.header("📊 System Info")
        st.markdown(f"""
        **Process:** {process_type}  
        **Material:** {material}  
        **Version:** 1.0  
        **Algorithm:** Rule-based + Geometry Analysis
        """)
        
        st.divider()
        
        # Quick test buttons
        st.header("🧪 Quick Tests")
        if st.button("🟢 Feasible Part", use_container_width=True):
            st.session_state['test_file'] = 'test_thin_wall.stl'
        if st.button("🟡 Review Needed", use_container_width=True):
            st.session_state['test_file'] = 'test_overhang.stl'
        if st.button("🔴 Reject Part", use_container_width=True):
            st.session_state['test_file'] = 'test_oversized.stl'
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📁 Upload CAD File")
        
        uploaded_file = st.file_uploader(
            "Choose STL or STEP file",
            type=['stl', 'step', 'stp'],
            help="Upload your CAD file for analysis"
        )
        
        # Handle quick test buttons
        if 'test_file' in st.session_state:
            test_path = Path(f'/home/claude/{st.session_state["test_file"]}')
            if test_path.exists():
                uploaded_file = test_path
                st.info(f"Testing with: {st.session_state['test_file']}")
            del st.session_state['test_file']
    
    with col2:
        st.subheader("ℹ️ About This System")
        st.markdown("""
        This prototype analyzes CAD geometry and applies manufacturing constraints to determine printability.
        
        **Analysis includes:**
        - Build envelope validation
        - Wall thickness measurement
        - Overhang detection
        - Thermal distortion risk
        - Support structure requirements
        """)
    
    # Analysis section
    if uploaded_file is not None:
        st.divider()
        
        # Save uploaded file temporarily
        if isinstance(uploaded_file, Path):
            file_path = uploaded_file
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.stl') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                file_path = Path(tmp_file.name)
        
        # Initialize analyzer
        analyzer = PrintabilityAnalyzer(
            process_type=process_map[process_type],
            material=material
        )
        
        # Run analysis
        with st.spinner("🔍 Analyzing geometry..."):
            result = analyzer.analyze_file(file_path)
        
        # Display results
        st.markdown("---")
        st.header("📋 Analysis Results")
        
       # Decision banner
decision_value = result.decision.value
if "Feasible" in decision_value:
    decision_class = "success-box"
elif "Review" in decision_value:
    decision_class = "warning-box"
else:
    decision_class = "danger-box"

st.markdown(
    f'<div class="{decision_class}">'
    f'<h2>{decision_value}</h2>'
    f'<p><strong>Confidence:</strong> {result.confidence:.0%} | '
    f'<strong>Risk Score:</strong> {result.risk_score:.0f}/100</p>'
    f'</div>',
    unsafe_allow_html=True
)
        
        # Metrics row
        if result.geometric_features:
            st.subheader("📐 Geometric Features")
            
            col1, col2, col3, col4 = st.columns(4)
            
            gf = result.geometric_features
            bbox = gf.bounding_box_mm
            
            with col1:
                st.metric(
                    "Envelope (mm)",
                    f"{bbox[0]:.1f} × {bbox[1]:.1f} × {bbox[2]:.1f}"
                )
            
            with col2:
                st.metric(
                    "Volume",
                    f"{gf.volume_mm3:,.0f} mm³"
                )
            
            with col3:
                if gf.min_wall_thickness_mm:
                    st.metric(
                        "Min Wall Thickness",
                        f"{gf.min_wall_thickness_mm:.2f} mm"
                    )
                else:
                    st.metric("Min Wall Thickness", "N/A")
            
            with col4:
                st.metric(
                    "Overhang Area",
                    f"{gf.overhang_percentage:.1f}%"
                )
            
            # Additional metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Surface Area", f"{gf.surface_area_mm2:,.0f} mm²")
            with col2:
                st.metric("Aspect Ratio", f"{gf.aspect_ratio:.2f}:1")
            with col3:
                st.metric("Mesh Quality", "✓ Manifold" if gf.is_manifold else "✗ Non-manifold")
            with col4:
                st.metric("Faces", f"{gf.face_count:,}")
        
        # Violations section
        if result.violations:
            st.subheader(f"⚠️ Constraint Violations ({len(result.violations)})")
            
            for violation in result.violations:
                severity_emoji = {
                    "CRITICAL": "🔴",
                    "WARNING": "⚠️",
                    "INFO": "ℹ️"
                }
                
                with st.expander(
                    f"{severity_emoji[violation.severity]} [{violation.rule_id}] {violation.message}",
                    expanded=(violation.severity == "CRITICAL")
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Category:** {violation.category}")
                        st.markdown(f"**Severity:** {violation.severity}")
                    with col2:
                        st.markdown(f"**Measured:** {violation.measured_value:.2f}")
                        st.markdown(f"**Threshold:** {violation.threshold_value:.2f}")
                    
                    st.markdown(f"**Evidence:** {violation.evidence}")
        else:
            st.success("✅ No constraint violations detected")
        
        # Recommendations
        if result.recommendations:
            st.subheader("💡 Recommendations")
            for i, rec in enumerate(result.recommendations, 1):
                st.markdown(f"{i}. {rec}")
        
        # 3D Visualization
        st.subheader("🎨 3D Geometry Visualization")
        
        try:
            mesh = trimesh.load(str(file_path))
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate([
                    geom for geom in mesh.geometry.values()
                    if isinstance(geom, trimesh.Trimesh)
                ])
            
            fig = create_3d_visualization(mesh, result.violations)
            st.plotly_chart(fig, use_container_width=True)
            
            # Add build volume reference
            constraints = analyzer.constraints
            if constraints and 'build_volume_mm' in constraints:
                bv = constraints['build_volume_mm']
                st.caption(f"📦 Build Volume Reference: {bv[0]} × {bv[1]} × {bv[2]} mm (shown as red dashed box)")
        
        except Exception as e:
            st.warning(f"Could not render 3D visualization: {str(e)}")
        
        # Export options
        st.divider()
        st.subheader("💾 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON export
            report_data = {
                "decision": result.decision.value,
                "confidence": result.confidence,
                "risk_score": result.risk_score,
                "violations": len(result.violations),
                "recommendations": result.recommendations
            }
            
            st.download_button(
                label="📄 Download JSON Report",
                data=json.dumps(report_data, indent=2),
                file_name=f"printability_report_{file_path.stem}.json",
                mime="application/json"
            )
        
        with col2:
            # Summary text
            summary = f"""
PRINTABILITY ANALYSIS REPORT
=============================

Decision: {result.decision.value}
Confidence: {result.confidence:.0%}
Risk Score: {result.risk_score}/100

VIOLATIONS: {len(result.violations)}
{chr(10).join([f"- {v.message}" for v in result.violations[:5]])}

RECOMMENDATIONS:
{chr(10).join([f"{i}. {r}" for i, r in enumerate(result.recommendations[:5], 1)])}
"""
            st.download_button(
                label="📝 Download Text Summary",
                data=summary,
                file_name=f"printability_summary_{file_path.stem}.txt",
                mime="text/plain"
            )
    
    else:
        # Landing state
        st.info("👆 Upload a CAD file or use Quick Test buttons in the sidebar to begin analysis")
        
        # Show example results
        st.divider()
        st.subheader("📊 Example Analysis Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="success-box">
                <h4>✅ Feasible Example</h4>
                <p><strong>Part:</strong> Thin-walled cylinder</p>
                <p><strong>Risk:</strong> 20/100</p>
                <p>Standard build parameters. Ready to quote.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="warning-box">
                <h4>⚠️ Review Example</h4>
                <p><strong>Part:</strong> L-bracket with overhang</p>
                <p><strong>Risk:</strong> 40/100</p>
                <p>Needs support structures. Engineer review recommended.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="danger-box">
                <h4>❌ Reject Example</h4>
                <p><strong>Part:</strong> Oversized component</p>
                <p><strong>Risk:</strong> 50/100</p>
                <p>Exceeds build volume. Cannot manufacture as-is.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p><strong>AM Printability Screening System v1.0</strong></p>
        <p>Prototype demonstration | Built with Python, Trimesh, Streamlit</p>
        <p>📧 Contact: <a href='mailto:your.email@example.com'>your.email@example.com</a> | 
        📁 GitHub: <a href='#'>github.com/yourname/am-printability</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
