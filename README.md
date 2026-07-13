# Committee Pack

Turns a structured data file into a single, self-contained, interactive HTML
committee pack — dashboards, KPI tiles, a risk heatmap, sortable tables and
trend charts — that can be attached to an email and opened by any committee
member in a browser. No server, no install, no internet connection required
to view it.

Built for an Enterprise Risk Committee that also feeds into an Audit and Risk
Committee, but the structure is generic enough for any committee that
presents a Matters Arising tracker before five standing reports — Risk
Management, Compliance Management, Business Continuity Management,
Whistleblowing and Project Risk — each cycle, plus a rotating set of
policies, procedures and one-off items.

The shell (sidebar nav, splash screen, colours, logo) is branded per
deployment. To rebrand: swap the two embedded `data:image/png;base64,...`
sources on the `.sp-logo` and `.logo-badge` `<img>` tags in
`build/template/pack_template.html`, and update the `--brand-navy` /
`--brand-navy-2` / `--brand-orange` CSS variables. Everything is still one
self-contained file: no CDN fonts, no PDF.js, no external calls — native
browser rendering only (including for the inline source-PDF viewer), so it
opens identically online or off.

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
   double-click it and it opens in their browser — sidebar navigation, a
   branded splash screen, search, sortable tables, an inline viewer for any
   attached source PDF (native browser PDF rendering, no PDF.js), a
   "Present" mode that zooms in for showing on a screen, dark mode, and a
   print/PDF button — all work offline.

## Admin Mode — adjusting Noting/Decision/Approval without re-running Python

Every generated pack has a "🔒 Admin Mode" button in the header. Turning it
on makes every `For Noting` / `For Decision` / `For Approval` tag clickable
— click one to cycle it — and reveals an "Export updated pack" button.
Export rebuilds a brand-new, fully working standalone HTML file with those
edits baked in, entirely in the browser (no Python needed for a quick tag
change); that export is what you'd send on to committee members. Edits only
exist in that open browser tab until exported — closing without exporting
discards them (the browser will warn you if you try).

This is a soft convenience, not an access-control system: anyone who can
open the file can turn Admin Mode on, since there is no server to enforce a
real permission boundary in a file that's emailed around. Keep the "admin"
copy of a pack somewhere only preparers can get to, and only distribute the
already-finalised export to the full committee.

Admin Mode currently only edits tags. If you want more fields editable
in-browser (e.g. KPI values, whether a report was tabled), that's a
reasonable next step — just ask.

## Ask the pack — offline search assistant

Every pack has a "💬 Ask the pack" button (bottom-right). It searches every
KPI, section, risk register row, table and other item in the pack and jumps
you straight to the matching tab and card. This is plain client-side text
search over the pack's own data, not a conversational LLM — deliberately,
since the pack is a single file emailed around with no server behind it, and
embedding a live API key in that file would let anyone who receives it
extract and misuse it. If you want true conversational Q&A later, that needs
a backend (auth, rate limiting, key management) — a much bigger build than
the pack generator itself.

## Starting the next cycle

There is no background/automated ingestion tool — that is a deliberate
choice (see "Why data-driven ratings, not computed ones" below). What *is*
automated is not having to remember the schema from scratch each quarter:

```bash
python build/new_cycle.py data/pack.yaml data/pack.q3-2026.yaml
```

This copies the previous file forward, keeps the five report ids/labels and
the `trends` chart definitions (so you only append one new point per chart),
and blanks out everything that's expected to change: dates, key information,
each report's KPIs/sections, and the `other_items` bucket.

## Structure of the data file

- `meeting` — committee name, what it feeds into, entity, cycle label, date,
  location, confidentiality banner.
- `key_information` — the "things the Committee needs to know" callouts,
  each tagged `For Noting` / `For Decision` / `For Approval`. Shown on the
  Overview tab always; add `applies_to: [report_id, ...]` to also surface an
  item at the top of that specific report's tab (e.g. a "For Approval" item
  about BCM shows on both Overview and the Business Continuity tab), so a
  committee member who jumps straight to one report doesn't miss it.
- `matters_arising` — a **standalone standing tab**, presented before the
  five reports at every sitting, tracking resolutions from prior meetings
  across every category. It is not part of any one report — don't fold its
  rows back into a report's `sections`. Has its own `kpis` and a `groups`
  list (each group is a heading + table — e.g. "General matters arising" vs
  "Matters arising — ERMC reports"). Omit the whole key in a cycle with
  nothing to carry forward; the tab still shows with an empty state.
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
