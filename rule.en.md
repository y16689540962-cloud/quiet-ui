# Interface copy rules

Six lines. Paste them into `AGENTS.md`, `CLAUDE.md` or a project-level agent config, and the agent stops adding defensive explanation to interfaces. Installing [`quiet-ui`](skills/quiet-ui/SKILL.md) makes this step unnecessary.

```
Interface copy rules:
- Page text may only be: headings, field labels, button verbs, real data, error messages, empty states, legally required text.
- No subtitles, captions, helper text, tip boxes or eyebrow labels. Express meaning with hierarchy, grouping, whitespace and icons.
- No greetings, footer credits (Made with / Powered by), "Demo data" tags, summaries at the bottom of the page.
- Do not chain fragments together with "·" "•" "|".
- Keep aria-label, image alt text and visible input labels.
- Output the page only; reply in one or two sentences, no explanatory paragraphs.
```

The rule was measured across 6 interfaces and 3 configurations; numbers are in the [README](README.en.md). `audit_copy.py` checks whether it is being followed.

For existing pages, clean up afterwards with [unslop-ui](https://github.com/felipebasurto/unslop-ui).
