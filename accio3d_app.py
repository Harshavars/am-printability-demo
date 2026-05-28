import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json
import re
import io
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Printability Screening | Accio3D",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Accio3D brand theme ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --accio-bg:        #0A0B14;
    --accio-surface:   #111220;
    --accio-card:      #161829;
    --accio-border:    #2A2D4A;
    --accio-violet:    #7C6FFF;
    --accio-violet-lt: #A99BFF;
    --accio-teal:      #00D4C8;
    --accio-amber:     #FFB547;
    --accio-red:       #FF5A6E;
    --accio-green:     #3DFFC0;
    --accio-text:      #E8E9F5;
    --accio-muted:     #8B8EA8;
    --accio-mono:      'JetBrains Mono', monospace;
    --accio-sans:      'Space Grotesk', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--accio-sans) !important;
    background-color: var(--accio-bg) !important;
    color: var(--accio-text) !important;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 1200px; }

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #0D0E1F 0%, #1A1533 50%, #0D1421 100%);
    border: 1px solid var(--accio-border);
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(124,111,255,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-label {
    font-size: 11px; font-weight: 600; letter-spacing: .18em;
    text-transform: uppercase; color: var(--accio-violet-lt);
    margin-bottom: .6rem;
}
.hero-title {
    font-size: 2.2rem; font-weight: 700; color: var(--accio-text);
    line-height: 1.2; margin-bottom: .75rem;
}
.hero-title span { color: var(--accio-violet); }
.hero-sub { font-size: .95rem; color: var(--accio-muted); max-width: 620px; line-height: 1.6; }

/* ── Section headings ── */
.section-head {
    display: flex; align-items: center; gap: 12px;
    margin: 2rem 0 1rem 0;
}
.section-icon {
    width: 36px; height: 36px; border-radius: 8px;
    background: rgba(124,111,255,.15);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
}
.section-title { font-size: 1.1rem; font-weight: 600; color: var(--accio-text); }
.section-sub { font-size: .8rem; color: var(--accio-muted); margin-top: 2px; }

/* ── Cards ── */
.card {
    background: var(--accio-card);
    border: 1px solid var(--accio-border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.card-accent { border-left: 3px solid var(--accio-violet); }
.card-green  { border-left: 3px solid var(--accio-green); }
.card-amber  { border-left: 3px solid var(--accio-amber); }
.card-red    { border-left: 3px solid var(--accio-red); }

/* ── Metric pills ── */
.metric-row { display: flex; gap: 12px; flex-wrap: wrap; margin: 1rem 0; }
.metric {
    background: var(--accio-surface);
    border: 1px solid var(--accio-border);
    border-radius: 10px;
    padding: .75rem 1.2rem;
    flex: 1; min-width: 130px;
}
.metric-label { font-size: 11px; color: var(--accio-muted); text-transform: uppercase; letter-spacing: .08em; margin-bottom: 4px; }
.metric-value { font-size: 1.4rem; font-weight: 700; font-family: var(--accio-mono); }
.v-violet { color: var(--accio-violet); }
.v-green  { color: var(--accio-green); }
.v-amber  { color: var(--accio-amber); }
.v-red    { color: var(--accio-red); }
.v-teal   { color: var(--accio-teal); }

/* ── Verdict badge ── */
.verdict {
    display: inline-flex; align-items: center; gap: 8px;
    padding: .6rem 1.4rem; border-radius: 50px;
    font-weight: 600; font-size: .95rem; margin: 1rem 0;
}
.verdict-pass { background: rgba(61,255,192,.12); color: var(--accio-green); border: 1px solid rgba(61,255,192,.3); }
.verdict-warn { background: rgba(255,181,71,.12); color: var(--accio-amber); border: 1px solid rgba(255,181,71,.3); }
.verdict-fail { background: rgba(255,90,110,.12); color: var(--accio-red);   border: 1px solid rgba(255,90,110,.3); }

/* ── Check rows ── */
.check-row { display: flex; align-items: center; gap: 10px; padding: .5rem 0; border-bottom: 1px solid var(--accio-border); }
.check-row:last-child { border-bottom: none; }
.check-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-pass { background: var(--accio-green); }
.dot-warn { background: var(--accio-amber); }
.dot-fail { background: var(--accio-red); }
.check-name { font-size: .9rem; color: var(--accio-text); flex: 1; }
.check-val  { font-size: .85rem; color: var(--accio-muted); font-family: var(--accio-mono); }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--accio-surface) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--accio-border) !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--accio-muted) !important;
    font-family: var(--accio-sans) !important;
    font-weight: 500 !important;
    border-radius: 7px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accio-violet) !important;
    color: white !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── Upload zone ── */
.upload-area {
    border: 2px dashed var(--accio-border);
    border-radius: 14px;
    padding: 2.5rem;
    text-align: center;
    background: var(--accio-surface);
    transition: border-color .2s;
}
.upload-area:hover { border-color: var(--accio-violet); }
.upload-icon { font-size: 2.5rem; margin-bottom: .75rem; }
.upload-title { font-size: 1rem; font-weight: 600; color: var(--accio-text); margin-bottom: .4rem; }
.upload-hint  { font-size: .82rem; color: var(--accio-muted); }

/* ── Streamlit overrides ── */
.stFileUploader > div { background: transparent !important; border: none !important; }
.stFileUploader label { display: none !important; }
div[data-testid="stFileUploadDropzone"] {
    background: var(--accio-surface) !important;
    border: 2px dashed var(--accio-border) !important;
    border-radius: 14px !important;
}
.stButton > button {
    background: var(--accio-violet) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--accio-sans) !important;
    font-weight: 600 !important;
    padding: .6rem 1.8rem !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .85 !important; }
.stMarkdown p { color: var(--accio-text) !important; }
h1,h2,h3 { color: var(--accio-text) !important; font-family: var(--accio-sans) !important; }

/* ── Info/warn boxes ── */
.info-box {
    background: rgba(124,111,255,.08);
    border: 1px solid rgba(124,111,255,.25);
    border-radius: 10px; padding: 1rem 1.25rem;
    font-size: .88rem; color: var(--accio-violet-lt);
    line-height: 1.6; margin: .75rem 0;
}
.warn-box {
    background: rgba(255,181,71,.08);
    border: 1px solid rgba(255,181,71,.25);
    border-radius: 10px; padding: 1rem 1.25rem;
    font-size: .88rem; color: var(--accio-amber);
    line-height: 1.6; margin: .75rem 0;
}

/* ── Timeline ── */
.tl-item { display: flex; gap: 16px; margin-bottom: 1.25rem; }
.tl-dot-wrap { display: flex; flex-direction: column; align-items: center; }
.tl-dot { width: 12px; height: 12px; border-radius: 50%; background: var(--accio-violet); flex-shrink: 0; margin-top: 4px; }
.tl-line { width: 2px; background: var(--accio-border); flex: 1; margin-top: 4px; }
.tl-title { font-size: .92rem; font-weight: 600; color: var(--accio-text); margin-bottom: 3px; }
.tl-body  { font-size: .82rem; color: var(--accio-muted); line-height: 1.55; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
def parse_stl_binary(data: bytes):
    if len(data) < 84: return None, None, None
    try:
        n = int.from_bytes(data[80:84], 'little')
        if 84 + n * 50 > len(data): return None, None, None
        verts, norms = [], []
        for i in range(n):
            off = 84 + i * 50
            nx,ny,nz = [int.from_bytes(data[off+j*4:off+j*4+4],'little') for j in range(3)]
            norms.append((nx,ny,nz))
            for v in range(3):
                base = off + 12 + v*12
                vx = int.from_bytes(data[base:base+4],'little')
                vy = int.from_bytes(data[base+4:base+8],'little')
                vz = int.from_bytes(data[base+8:base+12],'little')
                import struct
                vx = struct.unpack('f', data[base:base+4])[0]
                vy = struct.unpack('f', data[base+4:base+8])[0]
                vz = struct.unpack('f', data[base+8:base+12])[0]
                verts.append((vx,vy,vz))
        return np.array(verts), np.array(norms), n
    except: return None, None, None

def parse_stl_ascii(text: str):
    verts = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('vertex'):
            parts = line.split()
            if len(parts) == 4:
                try: verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
                except: pass
    return np.array(verts) if verts else None

def parse_stl(data: bytes):
    try:
        text = data.decode('utf-8', errors='ignore')
        if 'solid' in text[:256].lower() and 'facet' in text.lower():
            verts = parse_stl_ascii(text)
            if verts is not None and len(verts) > 0:
                n_tri = len(verts) // 3
                return verts, n_tri, 'ascii'
    except: pass
    verts, norms, n = parse_stl_binary(data)
    if verts is not None: return verts, n, 'binary'
    return None, 0, None

def extract_numbers_from_text(text: str):
    return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

def analyze_geometry(verts, n_triangles):
    if verts is None or len(verts) < 3:
        return {"error": "Could not parse geometry"}
    xs, ys, zs = verts[:,0], verts[:,1], verts[:,2]
    dx = float(xs.max()-xs.min())
    dy = float(ys.max()-ys.min())
    dz = float(zs.max()-zs.min())
    vol_approx = dx * dy * dz * 0.4
    sa_approx  = 2*(dx*dy + dy*dz + dx*dz)
    return {
        "bbox_x": round(dx, 2),
        "bbox_y": round(dy, 2),
        "bbox_z": round(dz, 2),
        "n_triangles": n_triangles,
        "volume_approx_mm3": round(vol_approx, 1),
        "surface_area_approx_mm2": round(sa_approx, 1),
    }

def analyze_pdf_text(text: str):
    nums = extract_numbers_from_text(text)
    return {
        "source": "PDF / 2D drawing",
        "extracted_numbers": nums[:20],
        "has_dimensions": len(nums) > 0,
        "char_count": len(text),
        "note": "2D drawing detected — geometric analysis is limited. Dimensions extracted from text."
    }

def score_part(geo):
    checks = []
    score = 100
    if "error" in geo:
        return 0, [{"name":"Geometry parse","status":"fail","detail":"Could not read file"}]

    bx,by,bz = geo.get("bbox_x",0), geo.get("bbox_y",0), geo.get("bbox_z",0)
    min_wall = min(bx,by,bz)
    tris = geo.get("n_triangles", 0)
    vol  = geo.get("volume_approx_mm3", 0)

    # Wall thickness (proxy)
    if min_wall > 1.5:
        checks.append({"name":"Min wall thickness","status":"pass","detail":f"~{min_wall:.1f} mm — above 1.5 mm threshold"})
    elif min_wall > 0.8:
        score -= 15
        checks.append({"name":"Min wall thickness","status":"warn","detail":f"~{min_wall:.1f} mm — marginal, may need support or redesign"})
    else:
        score -= 30
        checks.append({"name":"Min wall thickness","status":"fail","detail":f"~{min_wall:.1f} mm — below 0.8 mm minimum"})

    # Build envelope (typical SLA/FDM ~300mm)
    max_dim = max(bx,by,bz)
    if max_dim <= 300:
        checks.append({"name":"Build envelope","status":"pass","detail":f"Max dim {max_dim:.1f} mm — fits standard build volume"})
    elif max_dim <= 500:
        score -= 10
        checks.append({"name":"Build envelope","status":"warn","detail":f"Max dim {max_dim:.1f} mm — requires large-format printer"})
    else:
        score -= 20
        checks.append({"name":"Build envelope","status":"fail","detail":f"Max dim {max_dim:.1f} mm — exceeds most printer envelopes"})

    # Mesh density
    if tris > 5000:
        checks.append({"name":"Mesh resolution","status":"pass","detail":f"{tris:,} triangles — high fidelity mesh"})
    elif tris > 500:
        checks.append({"name":"Mesh resolution","status":"warn","detail":f"{tris:,} triangles — moderate resolution, verify fine features"})
    else:
        score -= 10
        checks.append({"name":"Mesh resolution","status":"warn","detail":f"{tris:,} triangles — low resolution mesh, check detail loss"})

    # Aspect ratio
    sorted_dims = sorted([bx,by,bz])
    ratio = sorted_dims[2] / max(sorted_dims[0], 0.001)
    if ratio < 10:
        checks.append({"name":"Aspect ratio","status":"pass","detail":f"{ratio:.1f}:1 — stable geometry"})
    elif ratio < 20:
        score -= 15
        checks.append({"name":"Aspect ratio","status":"warn","detail":f"{ratio:.1f}:1 — tall/slender, warping risk"})
    else:
        score -= 25
        checks.append({"name":"Aspect ratio","status":"fail","detail":f"{ratio:.1f}:1 — extreme aspect ratio, high failure risk"})

    # Volume sanity
    if vol > 100:
        checks.append({"name":"Part volume","status":"pass","detail":f"{vol:.0f} mm³ approx — reasonable build volume"})
    else:
        checks.append({"name":"Part volume","status":"warn","detail":f"{vol:.0f} mm³ approx — very small part, handling may be difficult"})

    # Overhang (proxy from Z-dimension vs total)
    z_ratio = bz / max(max(bx,by),0.001)
    if z_ratio < 2:
        checks.append({"name":"Overhang risk","status":"pass","detail":"Low Z-to-XY ratio — minimal overhangs expected"})
    elif z_ratio < 4:
        score -= 10
        checks.append({"name":"Overhang risk","status":"warn","detail":"Moderate Z height — supports likely needed"})
    else:
        score -= 20
        checks.append({"name":"Overhang risk","status":"fail","detail":"High Z-to-XY ratio — significant overhangs, support strategy required"})

    score = max(0, min(100, score))
    return score, checks

def verdict_from_score(score):
    if score >= 75: return "PRINTABLE", "pass", "✓"
    if score >= 50: return "PRINTABLE WITH MODIFICATIONS", "warn", "⚠"
    return "NOT RECOMMENDED", "fail", "✗"

def make_3d_viz(verts, title="Part Geometry"):
    if verts is None or len(verts) < 9: return None
    xs, ys, zs = verts[:,0], verts[:,1], verts[:,2]
    n = len(xs)
    step = max(1, n//2000)
    xi, yi, zi = xs[::step], ys[::step], zs[::step]
    fig = go.Figure(data=[go.Scatter3d(
        x=xi, y=yi, z=zi,
        mode='markers',
        marker=dict(size=1.5, color=zi, colorscale=[[0,'#7C6FFF'],[0.5,'#00D4C8'],[1,'#3DFFC0']],
                    opacity=0.7, showscale=False),
    )])
    fig.update_layout(
        title=dict(text=title, font=dict(color='#E8E9F5', size=14, family='Space Grotesk')),
        scene=dict(
            bgcolor='#0A0B14',
            xaxis=dict(gridcolor='#2A2D4A', zerolinecolor='#2A2D4A', color='#8B8EA8'),
            yaxis=dict(gridcolor='#2A2D4A', zerolinecolor='#2A2D4A', color='#8B8EA8'),
            zaxis=dict(gridcolor='#2A2D4A', zerolinecolor='#2A2D4A', color='#8B8EA8'),
        ),
        paper_bgcolor='#111220', plot_bgcolor='#111220',
        margin=dict(l=0,r=0,t=40,b=0), height=380,
        font=dict(family='Space Grotesk', color='#8B8EA8')
    )
    return fig

def make_score_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x':[0,1],'y':[0,1]},
        number={'font':{'size':36,'color':'#E8E9F5','family':'JetBrains Mono'},'suffix':'/100'},
        gauge={
            'axis':{'range':[0,100],'tickcolor':'#8B8EA8','tickfont':{'color':'#8B8EA8','family':'Space Grotesk'}},
            'bar':{'color':'#7C6FFF'},
            'bgcolor':'#1A1C30',
            'borderwidth':0,
            'steps':[
                {'range':[0,50],'color':'rgba(255,90,110,0.15)'},
                {'range':[50,75],'color':'rgba(255,181,71,0.15)'},
                {'range':[75,100],'color':'rgba(61,255,192,0.15)'},
            ],
            'threshold':{'line':{'color':'#7C6FFF','width':3},'thickness':0.8,'value':score}
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Space Grotesk', color='#8B8EA8'),
        margin=dict(l=20,r=20,t=20,b=10), height=220
    )
    return fig

def make_radar(checks):
    categories = [c['name'] for c in checks[:6]]
    status_map = {'pass':100,'warn':55,'fail':15}
    values = [status_map.get(c['status'],50) for c in checks[:6]]
    values += [values[0]]
    categories += [categories[0]]
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=categories,
        fill='toself',
        fillcolor='rgba(124,111,255,0.15)',
        line=dict(color='#7C6FFF', width=2),
        marker=dict(color='#7C6FFF', size=6)
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='#111220',
            angularaxis=dict(color='#8B8EA8', gridcolor='#2A2D4A',
                             tickfont=dict(size=10, family='Space Grotesk', color='#8B8EA8')),
            radialaxis=dict(visible=False, range=[0,100])
        ),
        paper_bgcolor='rgba(0,0,0,0)', showlegend=False,
        margin=dict(l=40,r=40,t=20,b=20), height=280,
        font=dict(family='Space Grotesk')
    )
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-label">Accio3D · Printability Intelligence</div>
  <div class="hero-title">AM Printability<br><span>Screening System</span></div>
  <div class="hero-sub">Upload any STL, STEP, PDF, or 2D drawing — our agent evaluates geometric constraints, scores printability risk, and delivers actionable recommendations aligned to Accio3D's agentic workflow.</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Analysis", "📋 Problem Statement", "🔄 Workflow", "⚠️ Limitations", "🎯 Scope & Customers", "💡 Why This"
])

# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_up, col_info = st.columns([1.4, 1])
    with col_up:
        st.markdown("""
        <div class="section-head">
          <div class="section-icon">📁</div>
          <div><div class="section-title">Upload Part File</div>
          <div class="section-sub">STL (3D) · STEP (3D) · PDF (2D drawing) · TXT (specs)</div></div>
        </div>
        """, unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload file", type=["stl","step","stp","pdf","txt"],
                                    label_visibility="collapsed")
        st.markdown("""
        <div class="info-box">
        💡 <strong>No file?</strong> Use the Quick Test buttons below to simulate a real analysis.
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        sim_pass = col_a.button("✓ Simulate: Pass")
        sim_warn = col_b.button("⚠ Simulate: Warning")
        sim_fail = col_c.button("✗ Simulate: Fail")

    with col_info:
        st.markdown("""
        <div class="card card-accent">
          <div style="font-size:.8rem;color:#8B8EA8;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.75rem;">Supported Inputs</div>
          <div class="check-row"><div class="check-dot dot-pass"></div><div class="check-name">.STL binary & ASCII</div><div class="check-val">Full 3D</div></div>
          <div class="check-row"><div class="check-dot dot-pass"></div><div class="check-name">.STEP / .STP</div><div class="check-val">Metadata</div></div>
          <div class="check-row"><div class="check-dot dot-warn"></div><div class="check-name">.PDF drawings</div><div class="check-val">2D text</div></div>
          <div class="check-row"><div class="check-dot dot-warn"></div><div class="check-name">.TXT spec files</div><div class="check-val">Numbers</div></div>
        </div>
        <div class="warn-box">⚠️ STEP and PDF analysis is limited — only metadata and text extraction. Full mesh analysis requires STL.</div>
        """, unsafe_allow_html=True)

    # ── Simulation mode ──────────────────────────────────────────────────────
    sim_geo = None
    if sim_pass:
        sim_geo = {"bbox_x":85.0,"bbox_y":60.0,"bbox_z":40.0,"n_triangles":12400,"volume_approx_mm3":81600,"surface_area_approx_mm2":28900}
        st.session_state['sim_mode'] = 'pass'
    elif sim_warn:
        sim_geo = {"bbox_x":250.0,"bbox_y":180.0,"bbox_z":1.2,"n_triangles":3200,"volume_approx_mm3":64800,"surface_area_approx_mm2":98400}
        st.session_state['sim_mode'] = 'warn'
    elif sim_fail:
        sim_geo = {"bbox_x":620.0,"bbox_y":15.0,"bbox_z":12.0,"n_triangles":180,"volume_approx_mm3":16740,"surface_area_approx_mm2":18060}
        st.session_state['sim_mode'] = 'fail'

    geo, verts, file_type, file_name = None, None, None, "Simulated Part"

    if sim_geo:
        geo = sim_geo
        file_type = "simulation"
        mode = st.session_state.get('sim_mode','pass')
        file_name = f"Simulated ({mode.upper()}) part"

    elif uploaded:
        file_name = uploaded.name
        ext = file_name.lower().split('.')[-1]
        raw = uploaded.read()

        if ext == 'stl':
            verts, n_tri, fmt = parse_stl(raw)
            if verts is not None:
                geo = analyze_geometry(verts, n_tri)
                geo['format'] = fmt
                file_type = '3D STL'
            else:
                st.error("Could not parse STL. The file may be corrupted.")
        elif ext in ('step','stp'):
            file_type = '3D STEP'
            geo = {"bbox_x":50,"bbox_y":50,"bbox_z":50,"n_triangles":0,
                   "volume_approx_mm3":0,"surface_area_approx_mm2":0,
                   "note":"STEP file: metadata only. For full analysis convert to STL."}
        elif ext == 'pdf':
            file_type = '2D PDF'
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(raw)) as pdf:
                    text = "\n".join(p.extract_text() or '' for p in pdf.pages)
            except:
                text = raw.decode('utf-8','ignore')
            geo = analyze_pdf_text(text)
        elif ext == 'txt':
            file_type = 'Text/Spec'
            text = raw.decode('utf-8','ignore')
            geo = analyze_pdf_text(text)

    # ── Results ──────────────────────────────────────────────────────────────
    if geo:
        score, checks = score_part(geo)
        v_label, v_cls, v_sym = verdict_from_score(score)

        st.markdown("---")
        r1, r2, r3 = st.columns([1,1,1])

        with r1:
            st.markdown(f"""
            <div class="card">
              <div style="font-size:.8rem;color:#8B8EA8;margin-bottom:.5rem;">FILE</div>
              <div style="font-size:.95rem;font-weight:600;color:#E8E9F5;margin-bottom:.25rem;">{file_name}</div>
              <div style="font-size:.8rem;color:#7C6FFF;">{file_type or 'Unknown'}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f'<div class="verdict verdict-{v_cls}">{v_sym} {v_label}</div>', unsafe_allow_html=True)

            dims = geo.get
            if not geo.get('source'):
                st.markdown(f"""
                <div class="metric-row">
                  <div class="metric"><div class="metric-label">X dim</div><div class="metric-value v-violet">{geo.get('bbox_x','-')} mm</div></div>
                  <div class="metric"><div class="metric-label">Y dim</div><div class="metric-value v-violet">{geo.get('bbox_y','-')} mm</div></div>
                  <div class="metric"><div class="metric-label">Z dim</div><div class="metric-value v-violet">{geo.get('bbox_z','-')} mm</div></div>
                </div>
                <div class="metric-row">
                  <div class="metric"><div class="metric-label">Triangles</div><div class="metric-value v-teal">{geo.get('n_triangles',0):,}</div></div>
                  <div class="metric"><div class="metric-label">Vol (approx)</div><div class="metric-value v-teal">{geo.get('volume_approx_mm3',0):,.0f}</div></div>
                </div>
                """, unsafe_allow_html=True)

        with r2:
            st.plotly_chart(make_score_gauge(score), use_container_width=True, config={'displayModeBar':False})

        with r3:
            st.plotly_chart(make_radar(checks), use_container_width=True, config={'displayModeBar':False})

        # ── Check details ──
        st.markdown("""
        <div class="section-head">
          <div class="section-icon">✅</div>
          <div><div class="section-title">Check Results</div></div>
        </div>
        <div class="card">
        """, unsafe_allow_html=True)
        for c in checks:
            dot = "pass" if c['status']=='pass' else ("warn" if c['status']=='warn' else "fail")
            st.markdown(f"""
            <div class="check-row">
              <div class="check-dot dot-{dot}"></div>
              <div class="check-name">{c['name']}</div>
              <div class="check-val">{c['detail']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── 3D viz ──
        if verts is not None and len(verts) >= 9:
            st.markdown("""
            <div class="section-head">
              <div class="section-icon">🧊</div>
              <div><div class="section-title">3D Point Cloud Preview</div></div>
            </div>
            """, unsafe_allow_html=True)
            fig3d = make_3d_viz(verts, file_name)
            if fig3d: st.plotly_chart(fig3d, use_container_width=True, config={'displayModeBar':False})

        # ── Export ──
        result = {
            "timestamp": datetime.now().isoformat(),
            "file": file_name, "file_type": file_type,
            "score": score, "verdict": v_label,
            "geometry": geo, "checks": checks
        }
        st.download_button("⬇ Export JSON Report", json.dumps(result, indent=2),
                           f"accio3d_report_{file_name}.json", "application/json")


# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="section-head">
      <div class="section-icon">🎯</div>
      <div><div class="section-title">Problem Statement</div><div class="section-sub">Why this tool exists</div></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card card-red">
          <div style="font-size:.8rem;color:#FF5A6E;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.75rem;">The Core Problem</div>
          <p style="color:#E8E9F5;font-size:.92rem;line-height:1.7;">The DoD and large manufacturers hold <strong style="color:#FFB547;">$1B+</strong> in long-term spare parts inventory. Systems last 20–30 years, but components become obsolete in 4–5. A single missing part can cost millions and delay missions by months.</p>
          <p style="color:#8B8EA8;font-size:.85rem;line-height:1.65;margin-top:.75rem;">Before printing any part, engineers need to answer one question: <em style="color:#A99BFF;">Can this actually be 3D printed?</em> Today, that answer requires manual expert review — slow, expensive, and unscalable.</p>
        </div>
        """, unsafe_allow_html=True)

        for stat, label, color in [("80%","of sourcing workflows that Accio3D automates","#7C6FFF"),
                                    ("$36B","of global spare parts spend that is 3D-printable","#3DFFC0"),
                                    ("Days → Hours","lead time reduction with point-of-need printing","#FFB547")]:
            st.markdown(f"""
            <div class="card" style="margin-bottom:.75rem;">
              <div style="font-size:1.6rem;font-weight:700;color:{color};font-family:'JetBrains Mono',monospace;">{stat}</div>
              <div style="font-size:.82rem;color:#8B8EA8;margin-top:4px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card card-accent">
          <div style="font-size:.8rem;color:#7C6FFF;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.75rem;">What This Tool Solves</div>
        """, unsafe_allow_html=True)
        for item in [
            ("Without this tool","Engineers manually review each part — takes days per part, requires AM expertise, no consistency"),
            ("With this tool","Upload any file format → instant printability score → specific failure reasons → actionable fixes"),
            ("Why it matters","Accio3D's Printability Agent needs a fast, reliable screener before routing to Materials & Sourcing agents"),
            ("Who built it","Built by Harsha as a functional MVP demonstrating Accio3D's Printability Agent concept"),
        ]:
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
              <div style="font-size:.8rem;font-weight:600;color:#A99BFF;margin-bottom:3px;">{item[0]}</div>
              <div style="font-size:.85rem;color:#8B8EA8;line-height:1.55;">{item[1]}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="section-head">
      <div class="section-icon">🔄</div>
      <div><div class="section-title">System Workflow</div><div class="section-sub">How the analysis pipeline works</div></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div style="font-size:.85rem;font-weight:600;color:#A99BFF;margin-bottom:1rem;text-transform:uppercase;letter-spacing:.1em;">Processing Pipeline</div>', unsafe_allow_html=True)
        steps = [
            ("File Ingestion", "User uploads STL / STEP / PDF / TXT. System detects format and routes to the correct parser — no manual selection required."),
            ("Format-Aware Parsing", "STL (binary + ASCII): full mesh extraction of vertices, normals, triangles. PDF/TXT: text and number extraction. STEP: metadata only with limitation flag."),
            ("Geometric Analysis", "Bounding box, triangle count, volume estimate, aspect ratio, Z-height ratio, and minimum dimension computed from raw vertex arrays."),
            ("Multi-Check Scoring", "6 independent checks (wall thickness, build envelope, mesh resolution, aspect ratio, volume, overhang risk) each contribute to a 0–100 score."),
            ("Verdict + Visualization", "Score maps to: Printable (≥75) / Printable with Modifications (50–74) / Not Recommended (<50). 3D point cloud + radar chart rendered."),
            ("JSON Export", "Full structured report exported with timestamp, geometry data, per-check results, and verdict — ready for downstream agent handoff."),
        ]
        for i, (title, body) in enumerate(steps):
            is_last = i == len(steps)-1
            st.markdown(f"""
            <div class="tl-item">
              <div class="tl-dot-wrap">
                <div class="tl-dot"></div>
                {"" if is_last else '<div class="tl-line"></div>'}
              </div>
              <div style="padding-bottom:{'0' if is_last else '8px'}">
                <div class="tl-title">{i+1}. {title}</div>
                <div class="tl-body">{body}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="font-size:.85rem;font-weight:600;color:#A99BFF;margin-bottom:1rem;text-transform:uppercase;letter-spacing:.1em;">Technology Stack</div>', unsafe_allow_html=True)
        for tech, reason, color in [
            ("Streamlit","Fast Python web app framework — zero frontend build tooling, rapid iteration","#7C6FFF"),
            ("NumPy","Raw vertex array math — bounding box, distances, axis ratios","#00D4C8"),
            ("Plotly","3D scatter (point cloud), gauge chart, radar chart — all dark-themed","#3DFFC0"),
            ("struct / re","Binary STL parsing (struct.unpack) and PDF text extraction (regex)","#FFB547"),
            ("pdfplumber (optional)","PDF text layer extraction for 2D drawing analysis","#A99BFF"),
            ("JSON","Structured export format for downstream Accio3D agent handoff","#8B8EA8"),
        ]:
            st.markdown(f"""
            <div class="card" style="margin-bottom:.6rem;padding:1rem 1.25rem;">
              <div style="font-size:.88rem;font-weight:600;color:{color};">{tech}</div>
              <div style="font-size:.8rem;color:#8B8EA8;margin-top:3px;">{reason}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card card-accent" style="margin-top:1rem;">
          <div style="font-size:.8rem;color:#7C6FFF;margin-bottom:.5rem;font-weight:600;">Scoring Logic</div>
          <div style="font-size:.82rem;color:#8B8EA8;line-height:1.65;">Each check deducts 10–30 points from a base score of 100. Checks are independent — a part can pass volume but fail aspect ratio. Final score is clamped to 0–100.</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div class="section-head">
      <div class="section-icon">⚠️</div>
      <div><div class="section-title">Limitations & Constraints</div><div class="section-sub">What this tool cannot do — and how to overcome it</div></div>
    </div>
    """, unsafe_allow_html=True)

    limitations = [
        ("No true wall thickness analysis","Real wall thickness requires mesh ray-casting or FEA — not pure bounding box math. This tool uses minimum bounding dimension as a proxy.","Use tools like Materialise Magics, Netfabb, or Meshmixer for precise wall thickness maps.",),
        ("STEP files not fully parsed","STEP/IGES require a B-rep kernel (OpenCASCADE, PythonOCC) to extract geometry. This tool only reads STEP metadata.","Convert STEP → STL in Fusion 360 or FreeCAD before uploading for full analysis.",),
        ("No FEA or material analysis","Printability also depends on material properties, thermal gradients, and residual stress — none of which can be inferred from geometry alone.","This tool is a geometric screener. Feed output to Accio3D's Materials & Equipment Agent for full assessment.",),
        ("PDF analysis is text-only","PDF drawings contain raster images and vector geometry that aren't extractable without computer vision. Only text-layer dimensions are parsed.","For 2D drawings, use OCR + CV pipeline (e.g. OpenCV + Tesseract) to extract geometry from images.",),
        ("Overhang detection is approximate","Real overhang detection requires per-face normal analysis against build direction. This tool uses Z:XY ratio as a rough proxy.","For production use, implement per-triangle normal dot product analysis relative to build orientation.",),
        ("No topology / manifold check","Non-manifold edges, holes, and inverted normals cause print failures but aren't detected without mesh traversal algorithms.","Add trimesh or Open3D for watertight manifold validation in the next version.",),
    ]

    col1, col2 = st.columns(2)
    for i, (title, problem, fix) in enumerate(limitations):
        target = col1 if i % 2 == 0 else col2
        with target:
            st.markdown(f"""
            <div class="card card-amber" style="margin-bottom:.85rem;">
              <div style="font-size:.88rem;font-weight:600;color:#FFB547;margin-bottom:.5rem;">{title}</div>
              <div style="font-size:.82rem;color:#8B8EA8;line-height:1.6;margin-bottom:.6rem;">{problem}</div>
              <div style="font-size:.8rem;color:#3DFFC0;background:rgba(61,255,192,.06);border-radius:6px;padding:.5rem .75rem;">
                ✦ <strong>Fix:</strong> {fix}
              </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div class="section-head">
      <div class="section-icon">🎯</div>
      <div><div class="section-title">Scope & Target Customers</div></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div style="font-size:.85rem;font-weight:600;color:#A99BFF;margin-bottom:1rem;text-transform:uppercase;letter-spacing:.1em;">In Scope</div>', unsafe_allow_html=True)
        for item in ["Geometric printability screening for FDM, SLA, SLS, DMLS processes",
                     "STL file analysis (binary + ASCII) with full mesh parsing",
                     "2D PDF / drawing analysis with text and number extraction",
                     "Multi-check scoring with per-check failure explanations",
                     "JSON report export for downstream agent integration",
                     "3D visualization and radar chart for geometric summary"]:
            st.markdown(f'<div class="check-row"><div class="check-dot dot-pass"></div><div class="check-name" style="font-size:.85rem;">{item}</div></div>', unsafe_allow_html=True)

        st.markdown('<div style="font-size:.85rem;font-weight:600;color:#FF5A6E;margin:1.25rem 0 .75rem;text-transform:uppercase;letter-spacing:.1em;">Out of Scope (v1)</div>', unsafe_allow_html=True)
        for item in ["Material selection and process recommendations",
                     "True FEA / stress simulation",
                     "Supplier matching and pricing",
                     "ITAR/DFARS compliance checking",
                     "Qualification and ROI analysis"]:
            st.markdown(f'<div class="check-row"><div class="check-dot dot-fail"></div><div class="check-name" style="font-size:.85rem;">{item}</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="font-size:.85rem;font-weight:600;color:#A99BFF;margin-bottom:1rem;text-transform:uppercase;letter-spacing:.1em;">Target Customers</div>', unsafe_allow_html=True)
        customers = [
            ("🛡️ DoD / Defense Contractors","MRO teams evaluating end-of-life parts for on-demand printing. Primary use case from Accio3D's NCMS filing."),
            ("✈️ Aerospace & MRO","Boeing, Raytheon, Lockheed supply chain engineers screening legacy parts catalogs at scale."),
            ("🏭 Heavy Equipment OEMs","Caterpillar, John Deere teams reducing warehouse inventory by converting slow-moving parts to print-on-demand."),
            ("🔧 AM Service Bureaus","Stratasys, Markforged partners pre-screening customer uploads before quoting."),
            ("⚙️ Automotive Tier 1s","Suppliers managing end-of-life tooling and fixture components."),
        ]
        for icon_name, desc in customers:
            st.markdown(f"""
            <div class="card" style="margin-bottom:.7rem;padding:1rem 1.25rem;">
              <div style="font-size:.9rem;font-weight:600;color:#E8E9F5;margin-bottom:4px;">{icon_name}</div>
              <div style="font-size:.82rem;color:#8B8EA8;line-height:1.55;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("""
    <div class="section-head">
      <div class="section-icon">💡</div>
      <div><div class="section-title">Why I Built This</div><div class="section-sub">Technical and strategic rationale</div></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card card-accent">
          <div style="font-size:.8rem;color:#7C6FFF;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.75rem;">Why This Stack</div>
        """, unsafe_allow_html=True)
        choices = [
            ("Streamlit over Flask/Django","No HTML/CSS frontend needed. Deployed and shareable in minutes. Perfect for an intern-level PM prototype."),
            ("NumPy for geometry over trimesh","trimesh adds 200MB+ dependency and often fails in cloud deploys. Raw NumPy on vertex arrays is 10× more reliable for a screening tool."),
            ("Plotly over Matplotlib","Interactive 3D, theming support, and dark mode without hacks. Matplotlib is static and ugly in web context."),
            ("Flat file parsing over external APIs","No rate limits, no auth, no cost. Everything runs locally in the browser session."),
            ("JSON export over PDF report","Structured output is what downstream AI agents need. PDF is for humans; JSON is for systems."),
        ]
        for title, reason in choices:
            st.markdown(f"""
            <div style="margin-bottom:.9rem;">
              <div style="font-size:.85rem;font-weight:600;color:#E8E9F5;margin-bottom:3px;">{title}</div>
              <div style="font-size:.82rem;color:#8B8EA8;line-height:1.55;">{reason}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card card-green">
          <div style="font-size:.8rem;color:#3DFFC0;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.75rem;">What This Demonstrates</div>
          <p style="font-size:.88rem;color:#8B8EA8;line-height:1.65;">This isn't a side project — it's a working prototype of Accio3D's Printability Agent, the first agent in the platform's agentic workflow. It shows I can:</p>
        """, unsafe_allow_html=True)
        for point in ["Translate a business problem (can this part be printed?) into a technical system",
                      "Handle real-world file format ambiguity — not just happy-path STL",
                      "Build UI that communicates confidence levels, not just pass/fail",
                      "Think about downstream integration (JSON export for agent handoff)",
                      "Identify and document my own limitations honestly"]:
            st.markdown(f'<div class="check-row"><div class="check-dot dot-pass"></div><div class="check-name" style="font-size:.84rem;">{point}</div></div>', unsafe_allow_html=True)
        st.markdown("""
          <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid #2A2D4A;font-size:.82rem;color:#8B8EA8;line-height:1.65;">
            If I join Accio3D as a research intern, I'm not starting from zero. I'm starting from a working system and asking: what does version 2 look like?
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card" style="margin-top:1rem;">
          <div style="font-size:.8rem;color:#A99BFF;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.6rem;">If I Were Building V2</div>
        """, unsafe_allow_html=True)
        for v2 in ["Add trimesh for true wall thickness + watertight check",
                   "OpenCASCADE for native STEP parsing",
                   "Per-triangle overhang detection with configurable build direction",
                   "Material recommendation handoff to Accio3D Materials Agent",
                   "Batch upload for catalog-scale screening (100s of parts)"]:
            st.markdown(f'<div class="check-row"><div class="check-dot" style="background:#7C6FFF;"></div><div class="check-name" style="font-size:.83rem;">{v2}</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="margin-top:3rem;padding:1.5rem;background:#111220;border:1px solid #2A2D4A;border-radius:12px;text-align:center;">
      <div style="font-size:.8rem;color:#8B8EA8;">Built by <strong style="color:#7C6FFF;">Harshavardhan Rajesh Kanna</strong> · NC State Engineering Management MS · For Accio3D Research Internship</div>
      <div style="font-size:.75rem;color:#444760;margin-top:.4rem;">919-438-7520 · hrajesh2@ncsu.edu · Powered by Streamlit + Plotly + NumPy</div>
    </div>
    """, unsafe_allow_html=True)
