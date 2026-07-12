# Committee Pack

Turns a structured data file into a single, self-contained, interactive HTML
committee pack — dashboards, KPI tiles, a risk heatmap, sortable tables and
trend charts — that can be attached to an email and opened by any committee
member in a browser. No server, no install, no internet connection required
to view it.

Built for an Enterprise Risk Committee that also feeds into an Audit and Risk
Committee, but the structure is generic enough for any committee that
receives a Risk Management, Compliance Management, Business Continuity
Management, Whistleblowing and Project Risk report each cycle, plus a
rotating set of policies, procedures and one-off items.

## How it works

1. **You edit `data/pack.yaml`** — this is the only place numbers and words
   come from. The dashboard never parses PDFs for figures itself; it only
   renders what a human typed into this file. That keeps every number a
   committee member sees traceable to a person, which matters for a
   risk/compliance pack.
2. **You drop source PDFs into `source/`** (optional) — matching the
   `source_file` paths referenced in the data file. If a PDF isn't there yet,
   the pack still builds; that report just shows "source document not
   attached" instead of a download link.
3. **You run the generator**, which embeds any found PDFs as base64 and
   produces one HTML file:

   ```bash
   pip install -r requirements.txt
   python build/generate_pack.py data/pack.yaml dist/committee-pack.html
   ```

4. **You attach `dist/committee-pack.html` to an email.** Recipients
   double-click it and it opens in their browser — tabs, search, sortable
   tables, dark mode, and a print/PDF button all work offline.

## Structure of the data file

- `meeting` — committee name, what it feeds into, entity, cycle label, date,
  location, confidentiality banner.
- `key_information` — the "things the Committee needs to know" callouts on
  the Overview tab, each tagged `For Noting` / `For Decision` / `For
  Approval`.
- `reports` — a **fixed list of five standing reports** (Risk Management,
  Compliance Management, Business Continuity Management, Whistleblowing,
  Project Risk). These always appear as tabs, cycle to cycle, even if one
  wasn't tabled a given quarter (set `tabled: false` and it renders as "not
  tabled this cycle" instead of disappearing — so the navigation never
  reshuffles on committee members). **Do not add or remove entries from this
  list.**
  - Within a report, `sections` is a **free-form ordered list** — add,
    rename, drop or reorder sections as needed each cycle. This is
    deliberate: which sub-headings matter (e.g. "Matters Requiring the
    Committee's Attention", "Emerging Risk Themes") changes quarter to
    quarter, and the tool should not fight that. Each section can carry a
    `body` (prose), a `table` (generic columns/rows), a `risk_matrix` (5×5
    heatmap) and/or a `bar_chart`.
- `other_items` — the **rotating bucket** for whatever else is tabled this
  cycle: policies, procedures, assessments, memos, an internal audit survey.
  Nothing here is expected to recur in the same shape next cycle. Add/remove
  freely.
- `trends` — one chart definition per metric you want to track over time.
  Append a new data point each cycle; a chart with only one point shows an
  explanatory empty state instead of a misleading single-dot line.

## Why data-driven ratings, not computed ones

The risk heatmap colors and rating pills use whatever `rating` value is in
the data file for that item, not a value recalculated from
`likelihood × impact`. Real registers sometimes label two same-scoring risks
differently for qualitative reasons — the tool preserves what the Committee
was actually shown rather than silently "correcting" it.

## Repository layout

```
data/pack.yaml            sample/template data file (safe to commit)
data/private/              real cycle data — gitignored, never committed automatically
source/                    source PDFs referenced by source_file (optional)
build/generate_pack.py    the generator
build/template/            the dashboard's HTML/CSS/JS
dist/                      generated output
```

`data/private/` and any `dist/*.private.html` are gitignored on purpose —
real committee content (names, figures, findings) should only be committed
after a deliberate decision to do so, separate from the tool itself.
