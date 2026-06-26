"""A1 Week 2 Plan — formatted exactly like A1_Week1_Plan (title, blue Role
headings, bold-lead bullets, no preamble). EVERY bullet is hard, load-bearing
math / theory / experiment work, strictly in A1 scope. Outputs Word .docx and a
Word-style (Helvetica) PDF."""
import os
OUT = "/Users/keshavkrishnan/Claude/ASSIPPaper/A1_deliverables"
os.makedirs(OUT, exist_ok=True)
BLUE = (0x1f, 0x56, 0x99)
TITLE = "A1 Week 2 Plan"

ROLES = [
 ("Role 1 (Optimal Contract and General Carbon Theory)", [
   ("Prove existence, uniqueness, and contract optimality.",
    "Prove the interior optimum is unique via the recursive FOC structure — the distribution-free cutoff "
    "F(K_F°)=φ° pins K_F* as a unique implicit function, then K_M*, then K_R* (a monotone-triangular / "
    "diagonal-dominance condition on the Hessian in primitives, not global concavity, which fails since Π is "
    "submodular in (K_R,K_F)); and prove d*(x)=min{(K_F−x)_+,K_M} is the unique optimal dispatch via strict R>c."),
   ("Make the shift-ratio condition uniform along the homotopy.",
    "Prove that support-wide monotonicity of g(x)=F_{K_R}/f implies the realized endpoint condition holds "
    "uniformly along the whole C_M-homotopy, even as the window (K_F*−K_M*, K_F*) moves — this is the actual "
    "content Theorem 1's 'integrate downward' step needs, beyond the pointwise condition."),
   ("Prove the emission condition for general F (keystone).",
    "Substitute the equilibrium map K*(C_R) into the exact inequality (C) to get the endogenous carbon "
    "condition, and prove a primitive sufficient condition (the endpoint shift-ratio condition plus a tail/skew "
    "bound) under which it holds at a finite interior optimum; exhibit a non-power-law F (e.g. truncated "
    "lognormal) satisfying it to prove the admissible class is non-vacuous."),
   ("Prove connectedness of the carbon-reduction set.",
    "Prove {C_R : Δ(C_R)≥0} is bounded above (large-cost anchor) and non-empty, and that it is a single interval "
    "under an explicit monotone-renewable-shadow-value condition on F — general F can cross zero twice, so "
    "identify and prove the condition that rules out the second crossing."),
   ("Prove the sharp channel condition and tight bounds.",
    "Establish the sharp necessary-and-sufficient condition for K_R*>K_R°: the realized two-point endpoint "
    "inequality g(K_F*)≥g(K_F*−K_M*) — monotone g is sufficient but NOT necessary — and prove the two-sided "
    "bounds on the carbon saving Δ are tight by exhibiting the attaining distributions."),
 ]),
 ("Role 2 (Solver and Numerical Methods)", [
   ("Build and validate the general solver.",
    "Implement the joint-capacity/dispatch solver for d*(x) and (K_R,K_F,K_M) under any residual-demand "
    "distribution, validated against the benchmarks to machine precision — including at least one non-power-law "
    "F with a semi-closed form, so the test set goes beyond the Week-1 uniform case."),
   ("Run the carbon-sign sweep at a finite optimum.",
    "Sweep over Role 1's primitive condition on a synthetic, theory-tied distribution family and show "
    "numerically that carbon falls at a finite interior optimum — one principled map replacing the scattered "
    "Week-1 counts."),
   ("Derive the analytic Hessian and certify negative-definiteness.",
    "Derive and implement the full analytic Hessian and comparative-statics cofactors (replacing the "
    "knife-edge-noisy finite differences), and on that analytic Hessian certify negative-definiteness along the "
    "interior path for Role 1's class."),
   ("Map the boundary of the regularity region.",
    "Exhibit distributions in the admitted class where the Hessian fails to be negative definite, delimiting "
    "Condition 2 sharply and complementing Role 1's uniqueness proof — a numerical map of where regularity holds."),
 ]),
 ("Role 3 (Comparative Statics and Robustness)", [
   ("Sign the price and adoption-margin comparative statics.",
    "Via the Hessian-cofactor identities, under the explicit interior-regime hypotheses (R inside the "
    "Assumption-1 bounds), sign ∂(carbon effect)/∂R, ∂/∂β, ∂/∂p, and ∂/∂C_M (the adoption margin), and prove "
    "mining raises K_R*>K_R° under the endpoint shift-ratio condition."),
   ("Prove the cross-distribution robust certificate.",
    "Along a specified one-parameter deformation within the shape class U (a mean-preserving-spread / "
    "likelihood-ratio path), sign the capacity covariation dK*/dt so the least-favorable result holds across "
    "the path — making C_R ≤ C_R† ⇒ Δ ≥ 0 a genuine robust certificate — or prove the obstruction."),
   ("Construct the reversed-channel counterexample.",
    "Construct a realized F violating the endpoint shift-ratio condition (g(K_F*)<g(K_F*−K_M*) at the realized "
    "thresholds) for which K_R*<K_R°, and solve it numerically — the sharpness witness Week 1 could not produce, "
    "certifying necessity of the endpoint condition (Role 1)."),
   ("Prove the limit-interchange rigorously.",
    "Replace the expected-fossil-to-zero a.s.-corner step with a dominated-convergence / finite-capacity "
    "envelope argument, so the threshold proof holds without the limit shortcut."),
 ]),
 ("Role 4 (Mechanism Design and Regimes)", [
   ("Prove a single-price implements the optimum.",
    "Prove the non-trivial instrument result: a single per-MWh price R (not a state-contingent transfer) "
    "uniquely implements the dispatch d* and pins the capacity vector, and characterize exactly when the price "
    "instrument is rich enough to do so — the regulator's instrument-design problem."),
   ("Prove the unified regime theorem.",
    "Compose the C_M coverage axis (no adoption / small-FCL / interior / full coverage) and the C_R boundedness "
    "axis into one theorem, and pin down the small-FCL/large-FCL crossover precisely as the parameter-space "
    "locus where K_M*=K_R° (left open in Week 1)."),
   ("Prove the necessity of Assumption 1.",
    "Upgrade the four parameter conditions from pressure-test to proof: prove each is necessary for the interior "
    "optimum or the sign it guards, and characterize the regime obtained when relaxed (full-coverage corner, no "
    "adoption, or perverse curtailment)."),
   ("Characterize the second-best contract under private information.",
    "Introduce genuine private information the principal cannot infer from observed demand — the agent privately "
    "knows the renewable factor S while only the demand D is observed, so residual demand is the agent's private signal — "
    "and derive the second-best screening contract and how its information rent shifts the emission outcome "
    "versus the full-information benchmark."),
 ]),
]

# ---------------- DOCX (Word, Calibri) ----------------
from docx import Document
from docx.shared import Pt, RGBColor, Inches
d = Document()
for s in d.sections:
    s.top_margin=Inches(1.0); s.bottom_margin=Inches(1.0); s.left_margin=s.right_margin=Inches(1.0)
st=d.styles['Normal']; st.font.name='Calibri'; st.font.size=Pt(11)
tt=d.add_paragraph(); rt=tt.add_run(TITLE); rt.bold=True; rt.font.size=Pt(20); rt.font.color.rgb=RGBColor(*BLUE)
for head, bullets in ROLES:
    h=d.add_paragraph(); h.paragraph_format.space_before=Pt(10)
    rh=h.add_run(head); rh.bold=True; rh.font.size=Pt(13); rh.font.color.rgb=RGBColor(*BLUE)
    for lead, body in bullets:
        bp=d.add_paragraph(style='List Bullet'); bl=bp.add_run(lead+" "); bl.bold=True; bp.add_run(body)
docx_path=os.path.join(OUT,"A1_Week2_NextRoles.docx"); d.save(docx_path); print("wrote",docx_path)

# ---------------- PDF (Word-style, Helvetica) ----------------
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
from reportlab.platypus import SimpleDocTemplate, Paragraph, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle
blue=Color(BLUE[0]/255,BLUE[1]/255,BLUE[2]/255)
H1=ParagraphStyle('H1',fontName='Helvetica-Bold',fontSize=20,textColor=blue,spaceAfter=10)
RH=ParagraphStyle('RH',fontName='Helvetica-Bold',fontSize=13,textColor=blue,spaceBefore=12,spaceAfter=4)
BUL=ParagraphStyle('BUL',fontName='Helvetica',fontSize=11,leading=14)
def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
pdf_path=os.path.join(OUT,"A1_Week2_NextRoles.pdf")
doc=SimpleDocTemplate(pdf_path,pagesize=letter,topMargin=1*inch,bottomMargin=1*inch,leftMargin=1*inch,rightMargin=1*inch)
fl=[Paragraph(TITLE,H1)]
for head,bullets in ROLES:
    fl.append(Paragraph(esc(head),RH))
    items=[ListItem(Paragraph(f"<b>{esc(lead)}</b> {esc(body)}",BUL),leftIndent=14,spaceAfter=5) for lead,body in bullets]
    fl.append(ListFlowable(items,bulletType='bullet',start='•',leftIndent=12))
doc.build(fl); print("wrote",pdf_path)
