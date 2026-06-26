"""A1 Week 2 Plan — formatted to match A1_Week1_Plan exactly:
title, then Role headings (blue) each with bold-lead bullets. No preamble.
Outputs an editable Word .docx and a Word-style (Helvetica) PDF."""
import os
OUT = "/Users/keshavkrishnan/Claude/ASSIPPaper/A1_deliverables"
os.makedirs(OUT, exist_ok=True)
BLUE = (0x1f, 0x56, 0x99)

TITLE = "A1 Week 2 Plan"

ROLES = [
 ("Role 1 (Optimal Contract and General Carbon Theory)", [
   ("Establish existence, uniqueness, and the optimal contract.",
    "Prove coercivity of expected profit and a primitive condition on F (e.g. a log-concave density) under "
    "which the interior capacity optimum is unique, and prove that the dispatch contract "
    "d*(x)=min{(K_F−x)_+, K_M} is the unique optimal policy via the strict R>c ordering. This discharges the "
    "currently-assumed interior optimum and supplies the negative-definite-Hessian condition from primitives."),
   ("Promote the shift-ratio condition to a primitive.",
    "Replace the endogenous-window condition g(x)=F_{K_R}/f non-increasing with a support-wide condition on F "
    "that implies it, and prove the implication."),
   ("Prove the necessary-and-sufficient emission condition for general F.",
    "Under that primitive plus a tail/skew condition, prove a sharp iff for carbon reduction at a finite "
    "interior optimum, upgrading the endogenous inequality (C) and the current existence conjecture to a clean "
    "condition in primitives. Exhibit a non-power-law F satisfying all three conditions to certify the class "
    "is non-vacuous and genuinely more general than the power-law/uniform case."),
   ("Complete the viability threshold.",
    "Extend the renewable-cost window from the power-law family to general F, with the strict fall at a finite "
    "interior K_R* rather than the unbounded corner, and prove the carbon-reduction set is an interval "
    "(single-crossing in C_R) so carbon falls if and only if C_R is below the threshold."),
   ("State the main theorem and re-scope.",
    "State the headline theorem, align the abstract and title to exactly what is proved, and write the economic "
    "intuition at journal quality."),
 ]),
 ("Role 2 (Solver and Numerical Methods)", [
   ("Build and document the general solver.",
    "Finalize the joint-capacity and dispatch solver for d*(x) and the capacities under any residual-demand "
    "distribution — the validated backend the rest of the group relies on."),
   ("Deliver one carbon-sign narrative.",
    "Replace the scattered counts with a principled sweep over Role 1's primitive condition on a curated "
    "distribution family, showing carbon falls at a finite interior optimum."),
   ("Provide a Hessian / existence certificate.",
    "A reproducible check that the Hessian is negative definite on the interior path for Role 1's distribution "
    "class, backstopping existence and uniqueness."),
   ("Harden the solver and ship reproducibility.",
    "Replace finite-difference cofactors with analytic ones to remove the noisy knife-edge points, and ship a "
    "single command that reproduces the exact-formula checks and the carbon sweep, with documented tolerances."),
 ]),
 ("Role 3 (Comparative Statics and Robustness)", [
   ("Prove the correlation and price comparative statics.",
    "Show the net-carbon sign is governed by the demand–supply association (the shift ratio g = E[S | x]); that "
    "mining raises optimal renewable capacity K_R* > K_R°; and sign the monotonicities in the computing margin "
    "R, the blackout penalty β, and the retail price p, under general conditions."),
   ("Establish the cross-distribution robust certificate.",
    "Sign the capacity covariation along the shape class U so the least-favorable result holds across F, making "
    "the renewable-cost condition a genuine distributionally-robust certificate, or prove the obstruction cleanly."),
   ("Construct the reversed-channel counterexample.",
    "Build a realized F with g increasing so that K_R* < K_R° — the sharpness example Week 1 could not produce, "
    "since an algebraic sign-flip is not a realized example."),
   ("Repair the limit-interchange.",
    "Replace the expected-fossil-to-zero corner step with a dominated-convergence or finite-capacity envelope "
    "argument."),
 ]),
 ("Role 4 (Mechanism Design, Regimes, and Positioning)", [
   ("Strengthen the mechanism-design treatment.",
    "Cast the regulator as principal and the utility/miner as agent; write the participation and "
    "incentive-compatibility constraints and prove the price-based demand-response program implements d* "
    "optimally and, where feasible, uniquely — not merely as the principal's first-best dispatch; state the "
    "conditions (price-taking, exogenous R) under which those constraints are slack and the induced "
    "miner-demand result holds."),
   ("Unify and complete the regime map.",
    "Use one Assumption 1 and one carbon decomposition throughout; fold the finite-optimum statement and the "
    "renewable-cost boundedness axis into a single consistent regime theorem with the Assumption-1 necessity "
    "pattern."),
   ("State the limitations and scope boundary.",
    "State explicitly what is assumed and what is deferred to the companion workstreams (calibration; "
    "reliability, welfare, and pricing; the flexibility continuum and dynamics), so no referee can reject on an "
    "unaddressed omission rather than an error in scope."),
   ("Position and assemble.",
    "Write the related-work section on the methods used — monotone comparative statics, interruptible and "
    "demand-response load economics, and distributionally-robust analysis — add the bibliography, and assemble "
    "the pieces into one manuscript with a single notation table."),
 ]),
]

# ---------------- DOCX (Word, Calibri) ----------------
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
d = Document()
for s in d.sections:
    s.top_margin=Inches(1.0); s.bottom_margin=Inches(1.0); s.left_margin=s.right_margin=Inches(1.0)
st=d.styles['Normal']; st.font.name='Calibri'; st.font.size=Pt(11)
tt=d.add_paragraph()
rt=tt.add_run(TITLE); rt.bold=True; rt.font.size=Pt(20); rt.font.color.rgb=RGBColor(*BLUE)
for head, bullets in ROLES:
    h=d.add_paragraph(); h.paragraph_format.space_before=Pt(10)
    rh=h.add_run(head); rh.bold=True; rh.font.size=Pt(13); rh.font.color.rgb=RGBColor(*BLUE)
    for lead, body in bullets:
        bp=d.add_paragraph(style='List Bullet')
        bl=bp.add_run(lead+" "); bl.bold=True; bp.add_run(body)
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
pdf_path=os.path.join(OUT,"A1_Week2_NextRoles.pdf")
doc=SimpleDocTemplate(pdf_path,pagesize=letter,topMargin=1*inch,bottomMargin=1*inch,
                      leftMargin=1*inch,rightMargin=1*inch)
def esc(s): return s.replace("&","&amp;")
fl=[Paragraph(TITLE,H1)]
for head,bullets in ROLES:
    fl.append(Paragraph(esc(head),RH))
    items=[ListItem(Paragraph(f"<b>{esc(lead)}</b> {esc(body)}",BUL),leftIndent=14,spaceAfter=5)
           for lead,body in bullets]
    fl.append(ListFlowable(items,bulletType='bullet',start='•',leftIndent=12))
doc.build(fl); print("wrote",pdf_path)
