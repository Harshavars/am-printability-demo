import streamlit as st
import trimesh
import numpy as np
from pathlib import Path
from printability_analyzer import PrintabilityAnalyzer, ProcessType, Decision
import tempfile

st.set_page_config(
    page_title="AM Printability Screening System",
    page_icon="🔧",
    layout="wide"
)

st.markdown("""
<style>
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

def main():
    st.markdown('<div style="font-size: 2.5rem; font-weight: 700; color: #1f77b4;">🔧 AM Printability Screening System</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Automated feasibility analysis for additive manufacturing</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        process_type = st.selectbox(
            "Manufacturing Process",
            ["PBF-LB (Laser Powder Bed)", "MEX (Material Extrusion)"]
        )
        
        process_map = {
            "PBF-LB (Laser Powder Bed)": ProcessType.PBF_LASER,
            "MEX (Material Extrusion)": ProcessType.MATERIAL_EXTRUSION
        }
        
        if process_map[process_type] == ProcessType.PBF_LASER:
            material = st.selectbox("Material", ["Ti-6Al-4V", "AlSi10Mg", "316L"])
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
        
        st.header("🧪 Quick Tests")
        st.info("Upload a file below to analyze")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📁 Upload CAD File")
        
        uploaded_file = st.file_uploader(
            "Choose STL or STEP file",
            type=['stl', 'step', 'stp'],
            help="Upload your CAD file for analysis"
        )
    
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
    
    if uploaded_file is not None:
        st.divider()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.stl') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = Path(tmp_file.name)
        
        analyzer = PrintabilityAnalyzer(
            process_type=process_map[process_type],
            material=material
        )
        
        with st.spinner("🔍 Analyzing geometry..."):
            result = analyzer.analyze_file(file_path)
        
        st.markdown("---")
        st.header("📋 Analysis Results")
        
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
        
        if result.geometric_features:
            st.subheader("📐 Geometric Features")
            
            col1, col2, col3, col4 = st.columns(4)
            
            gf = result.geometric_features
            bbox = gf.bounding_box_mm
            
            with col1:
                st.metric("Envelope (mm)", f"{bbox[0]:.1f} × {bbox[1]:.1f} × {bbox[2]:.1f}")
            
            with col2:
                st.metric("Volume", f"{gf.volume_mm3:,.0f} mm³")
            
            with col3:
                if gf.min_wall_thickness_mm:
                    st.metric("Min Wall Thickness", f"{gf.min_wall_thickness_mm:.2f} mm")
                else:
                    st.metric("Min Wall Thickness", "N/A")
            
            with col4:
                st.metric("Overhang Area", f"{gf.overhang_percentage:.1f}%")
        
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
        
        if result.recommendations:
            st.subheader("💡 Recommendations")
            for i, rec in enumerate(result.recommendations, 1):
                st.markdown(f"{i}. {rec}")
    
    else:
        st.info("👆 Upload a CAD file to begin analysis")
    
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p><strong>AM Printability Screening System v1.0</strong></p>
        <p>Prototype demonstration | Built with Python, Trimesh, Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
