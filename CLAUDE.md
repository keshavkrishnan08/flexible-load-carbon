# CLAUDE.md - ASSIPPaper

Token-efficient working rules. Analysis profile (research/reporting).
Source: github.com/drona23/claude-token-efficient
Prose deliverables (the paper itself) follow the global Writing Style Guide, not these.

---

## Output
- Lead with the finding. Context and methodology after.
- Tables and bullets over prose paragraphs.
- Numbers must include units. Never ambiguous values.

## Accuracy Rules
- Never state a number without a source or derivation.
- If data is missing: say so. Do not estimate silently.
- If confidence is low: state it explicitly with a reason.
- Do not round aggressively. Preserve meaningful precision.

## Hallucination Prevention (Critical for Research)
- Never fabricate data points, statistics, or citations.
- If a claim cannot be grounded in provided data or a real source: do not make it.
- Distinguish clearly between what the data shows and what is inferred.
- Label inferences explicitly: "Based on the trend..." not stated as fact.

## Working Output Format
- Summary first (3 bullets max).
- Supporting data second.
- Caveats and limitations last.
- No narrative fluff between sections.

## Formatting
- No em dashes, smart quotes, or decorative Unicode in working output.
- Plain hyphens and straight quotes only.
- Tables use plain pipe characters.
- Natural language characters (accented letters, CJK, etc.) are fine when content requires them.

## Override
- Explicit user instructions always win.
