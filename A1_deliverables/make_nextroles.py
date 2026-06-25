"""Generate the A1 Week-2 next-roles plan as a Word .docx AND a Word-style PDF
(Helvetica sans-serif via reportlab — looks like Word->PDF, not LaTeX)."""
import os
OUT = "/Users/keshavkrishnan/Claude/ASSIPPaper/A1_deliverables"
os.makedirs(OUT, exist_ok=True)
BLUE = (0x1f, 0x4e, 0x8c)

TITLE = "A1 Week 2 Plan"
SUB = ("General Carbon/Contracting Theory & Numerical Methods — "
       "closing the gap to a Management Science submission")

STATUS = ("Status. Week 1 delivered the spine: the capacity-substitution channel K*R > K°R, the exact "
    "net-carbon inequality (C), the distribution-free cutoffs, the closed-form thresholds (the FCL "
    "adoption threshold and the renewable-cost bounds, with the small-FCL widening), a 15/15 "
    "machine-precision audit, a 3-referee honesty pass, and a green four-role integration. An "
    "adversarial Management Science review puts us at ≈70–75% of the rigor bar. The gap is one "
    "keystone — a general-distribution, finite-optimum carbon theorem — plus robustness, a clean "
    "numerical narrative, and theory positioning.")
SCOPE = ("Scope (hard wall — A1 only). Every task below is general theory or numerical-method work on the "
    "FCL carbon model. Out of scope: real-data calibration/magnitudes (A2); reliability, welfare, "
    "social-vs-private optimum (B1); flexibility continuum, AI, storage, multi-grid, dynamics (B2). "
    "Roles stay in their own lane.")

ROLES = [
 ("Role 1 — General Carbon Theory  (lead; carries the heaviest load)",
  "Turn the headline from “conditional for general F” into a proved, finite-optimum, "
  "general-distribution theorem — the paper’s title depends on it.",
  [("Existence & uniqueness.","Prove coercivity of profit Π and a primitive condition on F (e.g. "
    "log-concave density) under which any interior critical point is the unique global maximizer."),
   ("Primitive shift-ratio condition.","Replace the endogenous-window “g(x)=F_{K_R}/f non-increasing” "
    "with a support-wide condition on F that implies it, and prove the implication."),
   ("General-F non-emptiness (keystone).","Under that primitive plus a tail/skew condition, prove carbon "
    "falls somewhere in C_R for any such F — upgrading the current conjecture to a theorem."),
   ("Finite-optimum carbon win.","Give a primitive condition under which carbon strictly falls at a finite, "
    "interior K*R (not the K*R=∞ corner)."),
   ("Main theorem + re-scope.","State the headline theorem, align the abstract/title to exactly what is "
    "proved, and write the economic intuition at journal quality.")]),
 ("Role 2 — Solver & Numerical Methods",
  "One coherent, reproducible numerical backbone demonstrating the theory at a finite interior optimum.",
  [("One carbon-sign narrative.","Replace the scattered “2/32” counts with a principled sweep over "
    "Role 1’s primitive condition on a curated family, showing carbon falls at a finite interior optimum."),
   ("Hessian certificate.","A reproducible check that the Hessian H is negative definite on the interior path for Role 1’s "
    "distribution class (backstops existence)."),
   ("Analytic-cofactor solver.","Replace finite-difference cofactors with analytic ones (removes the noisy "
    "knife-edge points); document tolerances."),
   ("One-command reproducibility.","A single reproduce harness covering the 15 exact-formula checks plus "
    "the carbon sweep.")]),
 ("Role 3 — Comparative Statics & Robustness",
  "Close the cross-distribution robustness layer Week 1 left at “fixed capacities,” and deliver the "
  "sharpness example.",
  [("Cross-F least-favorable.","Sign the capacity covariation dK*/dF along the shape class U, turning the "
    "fixed-capacity result into a genuine least-favorable-distribution theorem."),
   ("Robust certificate.","Make C_R ≤ C†R ⇒ Δ ≥ 0 hold for every F ∈ U, or prove "
    "the obstruction cleanly."),
   ("Reversed-channel counterexample.","Construct a realized F with g increasing ⇒ K*R < K°R — the "
    "sharpness example Week 1 could not produce."),
   ("Repair the limit.","Replace the E[fossil*] → 0 a.s.-corner step with a dominated-convergence / "
    "finite-K_R argument.")]),
 ("Role 4 — Theory Hardening, Regimes & Positioning",
  "Make the four pieces one manuscript a referee reads as a single, consistent paper.",
  [("Unify the manuscript.","One Assumption 1 (R > c + C_M) and one carbon decomposition (Role 1’s "
    "two-force split) everywhere; one notation table."),
   ("Complete the regime map.","Fold Role 1’s finite-optimum statement into the small-FCL / interior / "
    "full-coverage map plus the C_R boundedness axis, as one consistent theorem."),
   ("Theory positioning.","Write the related-work section and bibliography on the methods A1 uses — monotone "
    "comparative statics (Topkis/Milgrom–Shannon), interruptible/demand-response economics, and "
    "distributionally-robust / least-favorable-distribution analysis."),
   ("Assemble & edit.","Move all “verified to 10^−k” out of proof bodies into the numerical "
    "section; align every claim with its theorem.")]),
]
SEQ = ("Sequencing. All four start now and share only notation + the Week-1 closed forms. Role 1 delivers two "
   "primitives early — the primitive shift-ratio condition (unblocks Role 2’s sweep and Role 3’s "
   "class U) and the existence condition (unblocks Role 3’s covariation and Role 2’s Hessian check). "
   "Roles 2–4 hand Role 4 their final statements for assembly. Acceptance gate: a referee cannot reject "
   "on rigor once Role 1 (keystone) and Role 4 (consistency + positioning) land; Roles 2–3 turn "
   "acceptance into a strong one.")

# ---------------- DOCX ----------------
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
d = Document()
for s in d.sections:
    s.top_margin=s.bottom_margin=Inches(0.8); s.left_margin=s.right_margin=Inches(0.9)
st=d.styles['Normal']; st.font.name='Calibri'; st.font.size=Pt(11)
t=d.add_paragraph(); t.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=t.add_run(TITLE); r.bold=True; r.font.size=Pt(20); r.font.color.rgb=RGBColor(*BLUE)
su=d.add_paragraph(); su.alignment=WD_ALIGN_PARAGRAPH.CENTER
rr=su.add_run(SUB); rr.italic=True; rr.font.size=Pt(10.5)
def para(text, bold_lead=None):
    p=d.add_paragraph()
    if bold_lead:
        b=p.add_run(bold_lead+" "); b.bold=True
    p.add_run(text); return p
for blob in (STATUS, SCOPE):
    lead, rest = blob.split(". ",1)
    para(rest, bold_lead=lead+".")
for head, mandate, bullets in ROLES:
    h=d.add_paragraph(); h.paragraph_format.space_before=Pt(8)
    rh=h.add_run(head); rh.bold=True; rh.font.size=Pt(13); rh.font.color.rgb=RGBColor(*BLUE)
    m=d.add_paragraph(); mi=m.add_run("Mandate. "); mi.italic=True; mi.bold=True; m.add_run(mandate)
    for lead,body in bullets:
        bp=d.add_paragraph(style='List Bullet'); bl=bp.add_run(lead+" "); bl.bold=True; bp.add_run(body)
lead,rest=SEQ.split(". ",1); para(rest,bold_lead=lead+".")
docx_path=os.path.join(OUT,"A1_Week2_NextRoles.docx"); d.save(docx_path)
print("wrote",docx_path)

# ---------------- PDF (Word-style, Helvetica) ----------------
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
blue=Color(BLUE[0]/255,BLUE[1]/255,BLUE[2]/255)
ss=getSampleStyleSheet()
H1=ParagraphStyle('H1',fontName='Helvetica-Bold',fontSize=20,textColor=blue,alignment=1,spaceAfter=2)
SUBs=ParagraphStyle('SUB',fontName='Helvetica-Oblique',fontSize=10.5,alignment=1,spaceAfter=10)
BODY=ParagraphStyle('BODY',fontName='Helvetica',fontSize=10.5,leading=13.5,spaceAfter=5)
RH=ParagraphStyle('RH',fontName='Helvetica-Bold',fontSize=13,textColor=blue,spaceBefore=9,spaceAfter=2)
MAND=ParagraphStyle('MAND',fontName='Helvetica',fontSize=10.5,leading=13.5,spaceAfter=3)
BUL=ParagraphStyle('BUL',fontName='Helvetica',fontSize=10.5,leading=13)
pdf_path=os.path.join(OUT,"A1_Week2_NextRoles.pdf")
doc=SimpleDocTemplate(pdf_path,pagesize=letter,topMargin=0.7*inch,bottomMargin=0.7*inch,
                      leftMargin=0.9*inch,rightMargin=0.9*inch)
fl=[Paragraph(TITLE,H1),Paragraph(SUB,SUBs)]
def b(lead,text): return f"<b>{lead}</b> {text}"
for blob in (STATUS,SCOPE):
    lead,rest=blob.split(". ",1); fl.append(Paragraph(b(lead+".",rest),BODY))
for head,mandate,bullets in ROLES:
    fl.append(Paragraph(head,RH))
    fl.append(Paragraph("<b><i>Mandate.</i></b> "+mandate,MAND))
    items=[ListItem(Paragraph(b(lead,body),BUL),leftIndent=14) for lead,body in bullets]
    fl.append(ListFlowable(items,bulletType='bullet',start='•',leftIndent=12,spaceAfter=4))
lead,rest=SEQ.split(". ",1); fl.append(Spacer(1,4)); fl.append(Paragraph(b(lead+".",rest),BODY))
doc.build(fl)
print("wrote",pdf_path)
