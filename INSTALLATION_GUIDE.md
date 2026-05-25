# Complete Installation & Usage Guide

## What You Have: Complete Working Prototype

This portfolio includes:
1. **Web-based interactive demo** (runs in browser)
2. **Command-line analysis tool** (for automation)
3. **Comprehensive documentation** (45+ pages)
4. **Test files and sample outputs**

---

## Installation (5 Minutes)

### Prerequisites
- Python 3.10 or higher
- 500MB disk space
- Internet (for initial package install only)

### Step 1: Install Dependencies
```bash
pip install streamlit plotly trimesh numpy scipy rtree
```

OR if you don't have pip permissions:
```bash
pip install --user streamlit plotly trimesh numpy scipy rtree
```

### Step 2: Verify Installation
```bash
python3 --version  # Should be 3.10+
python3 -c "import streamlit; print('✓ Streamlit installed')"
python3 -c "import trimesh; print('✓ Trimesh installed')"
```

---

## Running the Interactive Web Demo

### Option 1: Use the Launcher Script (Easiest)
```bash
chmod +x run_demo.sh
./run_demo.sh
```

The browser will automatically open to http://localhost:8501

### Option 2: Run Manually
```bash
streamlit run app_printability_demo.py
```

### Option 3: Specify Custom Port
```bash
streamlit run app_printability_demo.py --server.port 8080
```

---

## Using the Web Interface

### Quick Demo Flow (2 Minutes)

1. **Open browser** to http://localhost:8501
2. **Click sidebar**: "🔴 Reject Part" (tests oversized component)
3. **See result**: ❌ Reject, Risk 50/100, "Exceeds build volume"
4. **View 3D model**: Interactive rotating view with bounding box
5. **Check violations**: Expandable cards with evidence
6. **Download report**: JSON export button

### Upload Your Own Files

1. Click "Choose STL or STEP file"
2. Select any CAD file from your computer
3. Analysis runs automatically
4. Results appear with:
   - Decision (✅/⚠️/❌)
   - Risk score
   - Geometric measurements
   - Violation list
   - 3D visualization
   - Recommendations

### Change Process/Material

1. **Sidebar** → "Manufacturing Process"
2. Select: PBF-LB (Laser Powder Bed) or MEX (Material Extrusion)
3. **Sidebar** → "Material"
4. Select: Ti-6Al-4V, AlSi10Mg, 316L (for PBF-LB)
5. Re-analyze to see different constraints

---

## Running the Command-Line Tool

### Basic Analysis
```bash
python3 demo_analysis.py
```

**Output:**
- Analyzes 5 test parts
- Prints decisions and violations to terminal
- Generates JSON reports in current directory

### Analyze a Specific File
```python
from printability_analyzer import PrintabilityAnalyzer, ProcessType

analyzer = PrintabilityAnalyzer(
    process_type=ProcessType.PBF_LASER,
    material="Ti-6Al-4V"
)

result = analyzer.analyze_file("your_part.stl")

print(result.decision.value)
print(f"Risk: {result.risk_score}/100")

for violation in result.violations:
    print(f"  - {violation.message}")
```

---

## File Structure

```
am_printability_portfolio/
│
├── app_printability_demo.py        # 🌐 Web interface (main demo)
├── printability_analyzer.py        # 🔧 Analysis engine
├── demo_analysis.py                # ⌨️  Command-line tool
├── run_demo.sh                     # 🚀 Launcher script
│
├── WEB_APP_GUIDE.md                # 📖 Web app usage
├── README.md                       # 📚 Technical documentation
├── RISK_ANALYSIS.md                # ⚠️  Failure modes
├── case_study_thin_rib_failure.md  # 🔍 Failure case study
├── EXECUTIVE_SUMMARY.md            # 📊 Interview guide
├── PORTFOLIO_INVENTORY.md          # 📋 Complete inventory
├── QUICK_START_GUIDE.md            # ⚡ Interview flow
│
├── test_cube_50mm.stl              # Test files
├── test_thin_wall.stl
├── test_oversized.stl
├── test_overhang.stl
├── test_nonmanifold.stl
│
└── test_*_report.json              # Sample outputs
```

---

## For Your Interview

### Before the Interview

**5-Minute Prep:**
1. Run `./run_demo.sh` to test everything works
2. Open `QUICK_START_GUIDE.md` for talking points
3. Have browser window ready at http://localhost:8501
4. Keep `EXECUTIVE_SUMMARY.md` open for reference

### During Screen Share

**Option A: Web Demo (Recommended)**
1. Show the web interface
2. Click "🟢 Feasible Part" → explain decision
3. Click "🔴 Reject Part" → show violations
4. Upload a file live (if you have one)
5. Show 3D visualization and JSON export
6. **Time:** 5 minutes

**Option B: Code Walkthrough**
1. Open `printability_analyzer.py` in editor
2. Show constraint database (lines 90-120)
3. Explain wall thickness algorithm (lines 220-250)
4. Show decision logic (lines 350-380)
5. Run command-line demo: `python3 demo_analysis.py`
6. **Time:** 7 minutes

**Option C: Documentation Focus**
1. Show `RISK_ANALYSIS.md` (top 3 risks)
2. Walk through `case_study_thin_rib_failure.md`
3. Discuss metrics and detection (failure rate tracking)
4. Show web demo as "proof of execution"
5. **Time:** 10 minutes

### Key Talking Points

**When showing the web app:**
> "This is a working prototype you can use right now. Upload any STL file and get analysis in seconds. It's not mockups or slides — it's real code processing real geometry."

**When they ask about accuracy:**
> "80% on synthetic test data. To reach production-grade 90%+, I need to tune thresholds on your historical successful builds. That's 2 weeks of validation work."

**When they ask about deployment:**
> "This runs locally for the demo. For production, I'd deploy on Streamlit Cloud (free), AWS ECS (scalable), or integrate as an API endpoint in your quote system. 2-3 days integration work."

**When they ask about next steps:**
> "Week 1: Validate on 100 real quote requests from your system. Week 2-3: Two engineers label results, measure agreement. Week 4: Tune thresholds and retrain. Week 6: Deploy in shadow mode (engineers see results but make final calls). Week 12: Full automation with override tracking."

---

## Deployment Options

### Option 1: Local Demo (Interview Only)
- Run on your laptop
- Show via screen share
- No deployment needed
- **Pros:** Full control, offline works
- **Cons:** Can't share link afterward

### Option 2: Streamlit Community Cloud (Free)
```bash
# Push to GitHub
git init
git add .
git commit -m "AM Printability Screening System"
git push origin main

# Deploy at streamlit.io/cloud
# Get URL: https://yourapp.streamlit.app
```
- **Pros:** Free, public URL to share
- **Cons:** Must be public repo, slower load times

### Option 3: Cloud Deployment (Production)
```bash
# AWS, GCP, Azure
docker build -t am-printability .
docker push your-registry/am-printability
kubectl apply -f deployment.yaml
```
- **Pros:** Full control, fast, scalable
- **Cons:** Costs $20-50/month

---

## Customization

### Update Your Contact Info
Edit `app_printability_demo.py` line 468:
```python
<p>📧 Contact: <a href='mailto:YOUR_EMAIL'>YOUR_EMAIL</a></p>
```

### Add Your Own Test Parts
1. Copy STL files to the directory
2. Update sidebar buttons in `app_printability_demo.py` lines 93-99:
```python
if st.button("🟢 My Part", use_container_width=True):
    st.session_state['test_file'] = 'my_part.stl'
```

### Change Constraints
Edit `printability_analyzer.py` lines 90-130 to add materials:
```python
"Your-Material": {
    "build_volume_mm": (300, 300, 400),
    "min_wall_thickness_mm": 0.5,
    # ... etc
}
```

---

## Troubleshooting

### Web app won't start
```bash
# Check if port 8501 is busy
lsof -i :8501
# Kill process or use different port
streamlit run app_printability_demo.py --server.port 8080
```

### "No module named 'streamlit'"
```bash
pip install streamlit plotly trimesh numpy scipy rtree
# Or with --user flag if no admin rights
pip install --user streamlit plotly trimesh numpy scipy rtree
```

### "Cannot load STL file"
- Check file path is correct
- Verify STL is valid (open in MeshLab or Blender first)
- Try smaller file (<10MB)

### 3D visualization blank
- Update browser (Chrome, Firefox, Edge)
- Disable ad blockers
- Check browser console (F12) for WebGL errors

### Analysis takes too long
- Simplify mesh: reduce face count to <50k
- Use command-line tool instead (faster, no 3D rendering)
- Optimize ray-casting by reducing sample points

---

## Testing Before Interview

### Quick Validation (5 Minutes)

```bash
# 1. Launch web app
./run_demo.sh

# 2. In browser, click each Quick Test button:
#    - 🟢 Feasible Part → Should show ✅
#    - 🟡 Review Needed → Should show ⚠️
#    - 🔴 Reject Part → Should show ❌

# 3. Upload test_oversized.stl manually
#    Should see: ❌ Reject, "Exceeds build volume"

# 4. Download JSON report
#    Open in text editor, verify structure

# 5. Rotate 3D visualization
#    Should show bounding box overlay
```

If all 5 steps work → **You're ready**

---

## Support & Resources

### Documentation
- **Technical Details:** README.md
- **Risk Analysis:** RISK_ANALYSIS.md
- **Case Study:** case_study_thin_rib_failure.md
- **Interview Guide:** QUICK_START_GUIDE.md

### Code Reference
- **Main Engine:** printability_analyzer.py (21KB, 500 lines)
- **Web Interface:** app_printability_demo.py (17KB, 470 lines)
- **CLI Demo:** demo_analysis.py (6KB, 150 lines)

### Example Outputs
- JSON reports: `test_*_report.json`
- Test geometry: `test_*.stl` (5 files)

---

## What to Emphasize in Interview

### 1. It's Real and Working
"This isn't a proposal or mockup. It's running code. You can upload a file right now and get results."

### 2. Evidence-Based Decisions
"Every decision shows: which rule was violated, measured vs. threshold values, specific recommendations. Not just 'this won't work' — shows exactly why and how to fix it."

### 3. Built for Production
"Risk analysis identifies 10 failure modes. Instrumented detection metrics. Closed feedback loop architecture. Not just a prototype — designed for deployment."

### 4. Domain Knowledge Encoded
"Process-specific constraints (PBF-LB vs. MEX). Material-specific thresholds (Ti-6Al-4V vs. AlSi10Mg). Physics-based rules (thermal distortion, aspect ratio). Not generic ML — engineered for AM."

### 5. Validated Improvements
"Case study shows: algorithm missed thin junctions → redesigned sampling → false negative rate dropped 40% to 10%. Demonstrates systematic debugging."

---

## Post-Interview Follow-Up

### Send Within 24 Hours

**Email Template:**
```
Subject: AM Printability Screening System - Demo & Code

Hi Kunal,

Thanks for the conversation today. As discussed, here's the working prototype:

🌐 Live Demo: [Streamlit Cloud URL if deployed]
💻 Code: [GitHub repo link]
📦 Download: [Zip file attachment or Dropbox link]

Key files:
- WEB_APP_GUIDE.md — How to run the demo
- README.md — Technical documentation
- RISK_ANALYSIS.md — Failure modes & mitigation

To run locally:
1. pip install streamlit plotly trimesh numpy scipy rtree
2. ./run_demo.sh
3. Open http://localhost:8501

Happy to discuss next steps or make any modifications you'd find useful.

Best,
[Your Name]
```

---

## Success Metrics

You'll know this worked if:
- ✅ Kunal engages with the technical details (asks about algorithms)
- ✅ He tests the live demo during the interview
- ✅ He asks about deployment timeline (means he's thinking about using it)
- ✅ He challenges your assumptions (means he's evaluating fit, not just politeness)
- ✅ He asks you to modify something (means he wants to see how you respond to feedback)

---

**You have everything you need. Web demo works. Documentation is comprehensive. Go show them what you built.**
