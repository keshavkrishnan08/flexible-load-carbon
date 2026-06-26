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
 ("Role 1 — Optimal Contract & General Carbon Theory  (lead; carries the heaviest load)",
  "A1 mandate (1): existence + full characterization of the optimal demand-response contract under "
  "general distributions, with a necessary-and-sufficient emission-reduction condition. Turn the "
  "headline from “conditional for general F” into a proved, finite-optimum theorem — the title depends on it.",
  [("Existence, uniqueness & contract characterization.","Prove coercivity of profit Π and a primitive "
    "condition on F (e.g. log-concave density) under which the interior capacity optimum is unique; prove "
    "(not merely assert) that the contract d*(x)=min{(K_F−x)_+, K_M} is the unique optimal dispatch in the "
    "admissible policy class via the strict R>c ordering — together the full characterization, discharging "
    "the “interior optimum is assumed” gap and Condition 2 (H negative definite) from primitives."),
   ("Primitive shift-ratio condition.","Replace the endogenous-window “g(x)=F_{K_R}/f non-increasing” "
    "with a support-wide condition on F that implies it, and prove the implication."),
   ("Necessary-and-sufficient emission condition, general F (keystone).","Under that primitive plus a "
    "tail/skew condition, prove a sharp iff for carbon reduction at a finite interior optimum for any such "
    "F — upgrading condition (C) from an endogenous inequality and the current existence conjecture to a "
    "clean necessary-and-sufficient theorem in primitives. Exhibit a non-power-law F satisfying all three primitive conditions "
    "(log-concavity, shift-ratio, tail/skew) to certify the admissible class is non-vacuous and genuinely "
    "more general than power-law/uniform."),
   ("Complete the viability threshold.","Extend the C_R† window from the power-law family to general F (the "
    "strict fall occurs at a finite, interior K*R, not the K*R=∞ corner), and prove Δ(C_R) is single-"
    "crossing so {Δ≥0}=(C_R°, C_R†] is a genuine interval — i.e. carbon falls iff C_R < C_R†."),
   ("Main theorem + re-scope.","State the headline theorem, align the abstract/title to exactly what is "
    "proved, and write the economic intuition at journal quality.")]),
 ("Role 2 — Solver & Numerical Methods",
  "A1 mandate (4): build and document the numerical solver for d*(x) and k* the group relies on; deliver "
  "one coherent, reproducible backbone demonstrating the theory at a finite interior optimum.",
  [("General solver for d*(x) and k*.","Finalize and document the joint-capacity / dispatch solver for any "
    "residual-demand distribution — the validated backend every role builds on."),
   ("One carbon-sign narrative.","Replace the scattered “2/32” counts with a principled sweep over Role 1’s "
    "primitive condition on a curated family, showing carbon falls at a finite interior optimum."),
   ("Hessian / existence certificate.","A reproducible check that the Hessian H is negative definite on the "
    "interior path for Role 1’s distribution class (backstops existence & uniqueness)."),
   ("Analytic-cofactor solver + one-command reproducibility.","Replace finite-difference cofactors with "
    "analytic ones (removes the noisy knife-edge points); ship a single reproduce harness covering the 15 "
    "exact-formula checks plus the carbon sweep, with documented tolerances.")]),
 ("Role 3 — Comparative Statics & Robustness",
  "A1 mandate (2): prove, under general conditions, the correlation comparative static and that mining "
  "raises optimal renewable capacity; close the cross-distribution robustness layer and deliver the "
  "sharpness example.",
  [("Correlation & price comparative statics (general).","Prove the net-carbon sign is governed by the "
    "demand–supply association (the shift ratio g = E[S|x]); that mining raises optimal renewable capacity "
    "K*R > K°R (A1 mandate 2); and sign the monotonicities in the model’s key prices — ∂(carbon effect)/∂R "
    "(computing margin), ∂/∂β (blackout penalty), ∂/∂p (retail price) — which a theory referee always asks "
    "for and no Week-1 result covers."),
   ("Cross-F least-favorable & robust certificate.","Sign the capacity covariation dK*/dF along the shape "
    "class U so the least-favorable result holds across F, making C_R ≤ C†R ⇒ Δ ≥ 0 a genuine "
    "distributionally-robust certificate (or prove the obstruction cleanly)."),
   ("Reversed-channel counterexample.","Construct a realized F with g increasing ⇒ K*R < K°R — the "
    "sharpness example Week 1 could not produce (an algebraic sign-flip is not a realized example)."),
   ("Repair the limit-interchange.","Replace the E[fossil*] → 0 a.s.-corner step with a "
    "dominated-convergence / finite-K_R envelope argument.")]),
 ("Role 4 — Mechanism Design, Regimes & Positioning",
  "A1 mandate (3): strengthen the mechanism-design treatment (regulator as principal, utility as agent); "
  "plus regime consistency, an explicit limitations boundary, and theory positioning — so the four pieces "
  "read as one paper with no exposed flank.",
  [("Mechanism design (principal–agent, with IR & IC).","Cast the regulator as principal and the "
    "utility/miner as agent; write the agent’s participation (IR) and incentive-compatibility (IC) "
    "constraints and prove the price-based program implements d* optimally and, where feasible, uniquely "
    "(not merely as the principal’s first-best dispatch); state the conditions — price-taking / exogenous R "
    "— under which IR/IC are slack and the induced miner-demand result holds — A1 mandate (3)."),
   ("Unify & complete the regime map.","One Assumption 1 (R>c+C_M) and one carbon decomposition (Role 1’s "
    "two-force split) everywhere; fold Role 1’s finite-optimum statement and the C_R boundedness axis into "
    "a single consistent regime theorem with the Assumption-1 necessity pattern."),
   ("Limitations & scope boundary.","State explicitly what is assumed and what is deferred (real-data "
    "calibration → A2; reliability/welfare/social-vs-private → B1; flexibility continuum/storage/multi-grid/"
    "dynamics → B2), so no referee can reject on an unaddressed omission rather than an A1 error."),
   ("Positioning, bibliography & assembly.","Write the related-work section on the methods A1 uses (monotone "
    "comparative statics, interruptible/demand-response economics, distributionally-robust analysis), add "
    "the bibliography, move all “verified to 10^−k” out of proof bodies, and assemble one manuscript with a "
    "single notation table.")]),
]
COMPLETE = ("Why this is complete (acceptance gate). The four roles map one-to-one onto A1’s own four "
   "mandate items — optimal contract + necessary-and-sufficient emission condition (Role 1), numerical solver (Role 2), "
   "correlation comparative static + mining-raises-K_R (Role 3), mechanism design + miner-demand "
   "conditions (Role 4) — and additionally close every rigor gap an adversarial Management Science "
   "review raised: existence/uniqueness from primitives, a primitive (not endogenous) condition, a "
   "finite-optimum general-F theorem, single-crossing of the carbon set in C_R, a non-vacuous admissible "
   "class, comparative statics in the key prices R/β/p, an IR/IC mechanism (not just first-best dispatch), "
   "the cross-F robust certificate, the realized counterexample, the "
   "limit-interchange repair, a single consistent regime statement, an explicit limitations boundary, "
   "and literature positioning. With all of it landed there is no A1-scope angle — theory, rigor, "
   "robustness, mechanism, consistency, or positioning — left to reject on; anything beyond is, by "
   "construction, A2 or B-stream work.")
SEQ = ("Sequencing. All four start now and share only notation + the Week-1 closed forms. Role 1 delivers two "
   "primitives early — the primitive shift-ratio condition (unblocks Role 2’s sweep and Role 3’s "
   "class U) and the existence condition (unblocks Role 3’s covariation and Role 2’s Hessian check). "
   "Roles 2–4 hand Role 4 their final statements for assembly. Order of resolution: Role 1 (keystone) and "
   "Role 4 (mechanism + consistency) are gating; Roles 2–3 turn acceptance into a strong one.")

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
lead,rest=COMPLETE.split(". ",1); para(rest,bold_lead=lead+".")
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
lead,rest=COMPLETE.split(". ",1); fl.append(Spacer(1,4)); fl.append(Paragraph(b(lead+".",rest),BODY))
lead,rest=SEQ.split(". ",1); fl.append(Paragraph(b(lead+".",rest),BODY))
doc.build(fl)
print("wrote",pdf_path)
