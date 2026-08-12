# StudyMind — Interactive Mind Map

An interactive, offline mind map for studying **any topic**. All content is stored in a plain JSON file, so you can add, edit, or extend notes without touching any HTML or JavaScript. The bundled sample dataset covers Maven for Java developers, but you can replace it with notes on any subject.

---

## Project Structure

```
maven-mindmap/
├── template.html         # Jinja2 template — do not open directly
├── build.py              # Multi-map generator
├── requirements.txt      # Python dependencies
├── .gitignore
├── data/
│   └── <folder>/
│       └── <name>.json   # Source content — edit this file
├── dist/                 # Generated output — tracked in git
│   └── <folder>/
│       └── <name>.html   # Open this in a browser
└── venv/                 # Local Python venv — gitignored (not tracked)
```

---

## Setup

### 1. Create the virtual environment

```bash
py -m venv venv
venv\Scripts\pip install -r requirements.txt
```

### 2. Build a mindmap

```bash
venv\Scripts\python build.py --folder maven
```

Then open `dist/maven/maven.html` in your browser.

---

## How to Use the Mind Map

1. Open any generated `.html` from `dist/<folder>/` in any modern browser (Chrome, Edge, Firefox).
2. No server or internet connection is needed — the file is fully self-contained (all data is inlined at build time).

### Navigation

| Action | How |
|---|---|
| Pan | Click and drag on the canvas |
| Zoom | Scroll wheel |
| Fit to screen | Click **Fit** button or press `F` |
| Fullscreen study mode | Click **⛶ Fullscreen** (hides header and status bar; `Esc` exits) |
| Expand one level | Click a node |
| Expand all | Click **+ Expand All** |
| Collapse all | Click **- Collapse All** |
| Zoom in / out | Click **+** / **-** buttons |
| Toggle dark mode | Click the moon/sun icon |

### Search

| Action | How |
|---|---|
| Search nodes | Type in the search box |
| Next match | `Enter` or click ↓ |
| Previous match | `Shift+Enter` or click ↑ |
| Clear search | `Escape` or click **✕ Clear** |

When you search, the matched node, all its children, and all ancestor nodes are highlighted. Everything else is dimmed.

### Node Action Menu (the + button)

Nodes that have any actions (an explanation, a quiz, etc.) show a single gold **+** button to the left of their label.

- Click the **+** to expand the menu — it rotates to **×** and the action icons slide out to the left.
- Click any action icon to open it, or click the **+** / canvas / press `Escape` to close the menu.
- Only one node's menu is open at a time.

### Detail Dialog (Info Panel)

The **i** action icon (inside the **+** menu) appears on nodes that have a detailed explanation.

- Click the **i** icon to open a full-page detail panel.
- The panel contains a summary, section-by-section explanation, code examples, a tip, and an analogy.
- Close by clicking **✕**, pressing `Escape`, or clicking outside the panel.

### Quiz Dialog (Knowledge Check)

The green **t** action icon (inside the **+** menu) appears on nodes that have a quiz configured.

- Click the **t** icon to start a quiz on that topic.
- Questions are picked **randomly** from the topic's question pool every time you open it, so no two attempts are identical.
- Answer one question at a time using **Previous** / **Next**, then click **Submit** (enabled once all questions are answered).
- The results screen shows:
  - Your score and a pass/fail verdict (pass is 60% or higher).
  - Two D3 charts — a score donut and a correct-vs-incorrect bar chart.
  - A full per-question review with your answer, the correct answer, and an explanation.
- Click **↻ Retake** to try a fresh random set, or **⬇ Download PDF** to export.

#### Downloading the PDF report

1. Click **⬇ Download PDF**.
2. Enter your **name** and **email** (email is validated).
3. Click **Generate PDF**. The report — stamped with your name, email, date, topic, and score — downloads as `StudyMind-Quiz-<Topic>-<Date>.pdf`.

### Text Selection vs Drag Mode

By default the canvas is in **Drag Mode** — you can pan freely without accidentally selecting text.

Click the **✦ Drag Mode** button in the toolbar to switch to **Select Mode** if you want to copy text from the map.

---

## How to Edit Content

Each mindmap is a JSON file inside `data/<folder>/`. Create as many folders and JSON files as you need — one JSON file per mindmap. After every edit, run the build script to write the updated HTML to `dist/`, then open or refresh it in the browser.

### Step 1 — Edit your JSON file

The file has two top-level keys: `meta` and `root`.

#### meta

```json
"meta": {
  "title": "StudyMind",
  "subtitle": "Interactive Mind Map",
  "source": "Notes & Study Guide",
  "version": "1.0",
  "lastUpdated": "2026-07-17"
}
```

Change any of these fields to update the header displayed in the mind map.

#### root — node structure

Every node follows this shape:

```json
{
  "text": "Node label shown on the map",
  "children": [ ...child nodes... ]
}
```

Nodes can be nested to any depth. The root node is whatever top-level subject you choose (for example `"text": "Maven"` in the sample dataset).

#### Adding a new topic

Find the `"children"` array of the parent where you want to add the topic, then append a new object:

```json
{
  "text": "🔌 Plugin System",
  "children": [
    { "text": "Plugins execute goals" },
    { "text": "Goals are bound to lifecycle phases" },
    { "text": "Example: maven-compiler-plugin" }
  ]
}
```

Leaf nodes (no children) are just `{ "text": "..." }`.

### Step 2 — Add an explanation (optional)

Any node can have an optional `"explanation"` object. This enables the **ⓘ** icon and fills the detail dialog when clicked.

```json
{
  "text": "🔌 Plugin System",
  "explanation": {
    "summary": "One or two sentences describing the concept.",
    "sections": [
      {
        "heading": "What it is",
        "body": "Detailed paragraph. Can be as long as needed."
      },
      {
        "heading": "Why it matters",
        "body": "Second section body."
      }
    ],
    "code": {
      "lang": "xml",
      "snippet": "<plugin>\n  <groupId>org.apache.maven.plugins</groupId>\n  <artifactId>maven-compiler-plugin</artifactId>\n</plugin>"
    },
    "tip": "What to say about this topic.",
    "analogy": "A plain-English comparison to something familiar."
  },
  "children": [ ... ]
}
```

All `explanation` fields are optional except `summary` — you can include any combination of `sections`, `code`, `tip`, and `analogy`.

| Field | Type | Purpose |
|---|---|---|
| `summary` | string | Bold card shown at the top of the dialog |
| `sections` | array | Heading + body pairs — unlimited |
| `code.lang` | string | Language label shown above the code block (e.g. `xml`, `bash`) |
| `code.snippet` | string | Raw code text — use `\n` for line breaks |
| `tip` | string | Amber callout box — key takeaway |
| `analogy` | string | Green callout box — plain-English comparison |

### Step 2b — Add a quiz (optional)

Any node can have an optional `"quiz"` object. This enables the green **t** icon and powers the quiz dialog.

```json
{
  "text": "What is Maven?",
  "explanation": { ... },
  "quiz": {
    "count": 5,
    "questions": [
      {
        "q": "What is Maven primarily used for?",
        "options": ["Memory management", "Project management and build automation", "Thread scheduling", "Database indexing"],
        "answer": 1,
        "explain": "Maven is a project management and build automation tool."
      }
    ]
  },
  "children": [ ... ]
}
```

| Field | Type | Purpose |
|---|---|---|
| `count` | number | (Optional) How many questions to show per attempt. Falls back to `meta.quizDefaultCount` if omitted. |
| `questions` | array | The question pool. Questions are picked randomly each attempt. |
| `questions[].q` | string | The question text |
| `questions[].options` | array | 2–6 answer choices |
| `questions[].answer` | number | **0-based** index of the correct option (`0` = first option) |
| `questions[].explain` | string | (Optional) Explanation shown in the results review |

Notes:
- `answer` is **zero-based**: for `["A", "B", "C"]`, the correct answer `B` is `1`.
- Put **more** questions in the pool than `count` so each attempt shows a different random subset.
- Set a global default for all quizzes with `"quizDefaultCount"` in the `meta` block.

### Step 2c — Add glossary terms (optional)

Define hard words once in a top-level `glossary` map (a sibling of `meta` and `root`), then wrap any occurrence of that word in `[[term]]` inside node text or explanation text. A small **?** badge appears next to the word; clicking it opens a popup with the definition.

```json
{
  "meta": { ... },
  "glossary": {
    "SNAPSHOT": "A mutable, in-development version. Maven re-downloads SNAPSHOT artifacts on each build; released versions are immutable.",
    "artifact": "Any file produced or used by a build — typically a JAR, WAR, or EAR."
  },
  "root": { ... }
}
```

Then reference terms anywhere in text:

```json
{ "text": "<version> — project version (e.g. 1.0-[[SNAPSHOT]])" }
```

Notes:
- The word inside `[[...]]` must match a `glossary` key **exactly** (case-sensitive).
- Badges work both on mind map node labels and inside the info dialog (summary, section bodies, tip, analogy).
- Terms with no matching glossary key still render (badge shows "No definition available.").

### Step 3 — Run the build script

Requires Python 3 and Jinja2. Use the project venv (see [Setup](#setup)).

```bash
# Build all JSON files in a folder:
venv\Scripts\python build.py --folder maven

# Build specific files only:
venv\Scripts\python build.py --folder maven --files intro,deep-dive

# Build every JSON in every folder in parallel:
venv\Scripts\python build.py --all
```

| Flag | Description |
|---|---|
| `--folder <name>` | Folder inside `data/` to build |
| `--files <a>,<b>` | Comma-separated JSON stems (requires `--folder`) |
| `--all` | Build every JSON in every folder |
| `--out <dir>` | Output root directory (default: `dist`) |

Expected output:

```
Building 1 map(s) → dist/

  ✓ dist\maven\maven.html

Built 1 map(s) in 0.01s
```

### Step 4 — Open the generated file

Open `dist/<folder>/<name>.html` in any browser. The file is fully self-contained — open it directly from the file system, no server needed.

---

## Common Workflows

### Add a new leaf bullet point

1. Open the relevant `data/<folder>/<name>.json`.
2. Find the parent node by its `"text"` value.
3. Add `{ "text": "Your new bullet" }` to its `"children"` array.
4. Run `venv\Scripts\python build.py --folder <folder>` and refresh.

### Add a new section with sub-topics

1. Add a new object with `"text"` and `"children"` inside the relevant parent's `"children"` array.
2. Optionally add an `"explanation"` to enable the detail panel.
3. Run `venv\Scripts\python build.py --folder <folder>` and refresh.

### Extend an existing explanation

1. Find the node by its `"text"` in the relevant JSON file.
2. Edit or add fields inside its `"explanation"` object.
3. Run `venv\Scripts\python build.py --folder <folder>` and refresh.

### Add a new mindmap

1. Create a JSON file in any `data/<folder>/` directory (e.g. `data/java/collections.json`).
2. Give it the same schema as an existing file — `meta`, `root`, and optionally `glossary`.
3. Run `venv\Scripts\python build.py --folder java` to generate `dist/java/collections.html`.

---

## Requirements

| Requirement | Details |
|---|---|
| Python | 3.7 or later |
| Jinja2 | ≥ 3.0 (see `requirements.txt`) |
| Browser | Chrome 90+, Edge 90+, Firefox 88+ |
| Internet | Only for CDN libraries on first load |

---

## File Reference

### `data/<folder>/<name>.json` — content source

The files you edit. Each JSON file becomes one mindmap. Organize by topic folder (e.g. `data/maven/intro.json`, `data/java/core.json`). Controls every node label, child relationship, explanation, quiz, and glossary entry.

### `build.py` — multi-map generator

Reads JSON files from `data/` and writes self-contained HTML files to `dist/`. It:
- Converts the `{text, children}` tree into markmap's `{content, children, payload}` format.
- Sets all nodes beyond depth 0 to start folded (`payload.fold = 1`).
- Collects all `explanation` objects into a flat `APP_EXPLANATIONS` lookup keyed by node text.
- Collects all `quiz` objects into a flat `APP_QUIZZES` lookup keyed by node text.
- Emits the top-level `glossary` map as `APP_GLOSSARY` (empty object if omitted).
- Inlines all five JS globals into the HTML via Jinja2 — no external data file needed.
- Uses `ThreadPoolExecutor` for parallel builds when processing multiple files.

Run it every time you change a JSON file. See [Step 3](#step-3--run-the-build-script) for CLI usage.

### `template.html` — Jinja2 template

The application shell containing all HTML, CSS, and JavaScript for the interactive mindmap. Do not open this file directly in a browser — it contains an unresolved `{{ data_script | safe }}` placeholder. Only edit it if you need to change the UI, color theme, or application behavior.

The five JS globals injected at build time are:

- `APP_META` — header metadata (including `quizDefaultCount`)
- `APP_ROOT` — the full node tree in markmap format
- `APP_EXPLANATIONS` — flat lookup of node text → explanation object
- `APP_QUIZZES` — flat lookup of node text → quiz object
- `APP_GLOSSARY` — flat lookup of glossary term → definition string

#### Adding a new node action icon

Node icons (i, t) are driven by a single registry, `NODE_ACTIONS`, in the inline script of `template.html`. To add a new icon to the **+** menu, add one entry:

```javascript
const NODE_ACTIONS = [
  { id:'info', sym:'i', cls:'nd-act-info', has:k => !!APP_EXPLANATIONS[k], on:k => openDialog(k, APP_EXPLANATIONS[k]) },
  { id:'quiz', sym:'t', cls:'nd-act-quiz', has:k => !!APP_QUIZZES[k],      on:k => openQuiz(k, APP_QUIZZES[k]) },
  // Add your action here:
  { id:'note', sym:'n', cls:'nd-act-note', has:k => !!MY_DATA[k],          on:k => openMyThing(k, MY_DATA[k]) },
];
```

- `sym` — the single character shown in the icon circle.
- `cls` — a CSS class for coloring; add matching `.nd-act-note .nd-action-circle` / `.nd-action-text` rules (and dark-mode variants) next to the existing `.nd-act-info` / `.nd-act-quiz` rules.
- `has(key)` — returns true if the node (by its text) should show this action.
- `on(key)` — runs when the icon is clicked.

The FAB layout, slide-out animation, and single-open behavior all work automatically for any number of actions.
