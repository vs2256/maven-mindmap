"""
build.py — Multi-mindmap generator
Usage:
  py build.py                                    # interactive
  py build.py --folder maven                     # all JSONs in data/maven/
  py build.py --folder maven --files intro,deep-dive
  py build.py --all                              # every JSON in every folder
  py build.py --all --out custom/
"""
import json
import os
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Jinja2 not found. Install with: pip install jinja2")
    raise SystemExit(1)

TEMPLATE_FILE = "template.html"
DATA_DIR      = "data"
OUT_DIR       = "dist"


# ── Data transforms (logic preserved from original build.py) ─────────────────

def to_markmap(node, depth=0):
    return {
        "content": node["text"],
        "children": [to_markmap(c, depth + 1) for c in node.get("children", [])],
        "payload": {"fold": 1 if depth >= 1 else 0}
    }

def collect_explanations(node, acc):
    if "explanation" in node:
        acc[node["text"]] = node["explanation"]
    for c in node.get("children", []):
        collect_explanations(c, acc)

def collect_quizzes(node, acc):
    if "quiz" in node:
        acc[node["text"]] = node["quiz"]
    for c in node.get("children", []):
        collect_quizzes(c, acc)


# ── Core builder ─────────────────────────────────────────────────────────────

def build_one(folder, json_stem, data_dir, out_dir, jinja_template):
    src = Path(data_dir) / folder / f"{json_stem}.json"
    with open(src, encoding="utf-8") as f:
        data = json.load(f)

    meta         = data["meta"]
    root         = to_markmap(data["root"])
    explanations = {}; collect_explanations(data["root"], explanations)
    quizzes      = {}; collect_quizzes(data["root"], quizzes)
    glossary     = data.get("glossary", {})

    inline_vars = (
        f"var APP_META         = {json.dumps(meta,         ensure_ascii=False)};\n"
        f"var APP_ROOT         = {json.dumps(root,         ensure_ascii=False)};\n"
        f"var APP_EXPLANATIONS = {json.dumps(explanations, ensure_ascii=False)};\n"
        f"var APP_QUIZZES      = {json.dumps(quizzes,      ensure_ascii=False)};\n"
        f"var APP_GLOSSARY     = {json.dumps(glossary,     ensure_ascii=False)};"
    )
    data_script = f"<script>\n{inline_vars}\n</script>"

    html = jinja_template.render(data_script=data_script)

    dest = Path(out_dir) / folder / f"{json_stem}.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)

    return str(dest)


# ── Discovery helpers ─────────────────────────────────────────────────────────

def discover_folders(data_dir):
    base = Path(data_dir)
    return sorted(
        d.name for d in base.iterdir()
        if d.is_dir() and any(d.glob("*.json"))
    )

def discover_files(data_dir, folder):
    return sorted(p.stem for p in (Path(data_dir) / folder).glob("*.json"))


# ── Batch runner ──────────────────────────────────────────────────────────────

def run_builds(tasks, data_dir, out_dir, jinja_template):
    max_workers = min(32, (os.cpu_count() or 1) + 4)
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(build_one, folder, stem, data_dir, out_dir, jinja_template): (folder, stem)
            for folder, stem in tasks
        }
        for fut in as_completed(futures):
            folder, stem = futures[fut]
            try:
                print(f"  ✓ {fut.result()}")
            except Exception as e:
                print(f"  ✗ {folder}/{stem}: {e}")

    elapsed = time.perf_counter() - start
    print(f"\nBuilt {len(tasks)} map(s) in {elapsed:.2f}s")


# ── Interactive mode ──────────────────────────────────────────────────────────

def _resolve_folder(choice, folders):
    if choice.isdigit():
        idx = int(choice) - 1
        return folders[idx] if 0 <= idx < len(folders) else None
    return choice if choice in folders else None

def _resolve_stems(choice, stems):
    parts = [p.strip() for p in choice.split(",")]
    result = []
    for p in parts:
        if p.isdigit():
            idx = int(p) - 1
            if 0 <= idx < len(stems):
                result.append(stems[idx])
            else:
                return None
        elif p in stems:
            result.append(p)
        else:
            return None
    return result or None

def interactive(data_dir, out_dir, jinja_template):
    folders = discover_folders(data_dir)
    if not folders:
        print(f"No topic folders found in '{data_dir}/'.")
        return

    print("\nAvailable folders:")
    for i, name in enumerate(folders, 1):
        stems = discover_files(data_dir, name)
        print(f"  [{i}] {name}  ({len(stems)} file(s): {', '.join(stems)})")

    choice = input("\nWhich folder? (number, name, or 'all'): ").strip()

    if choice.lower() == "all":
        tasks = [(f, s) for f in folders for s in discover_files(data_dir, f)]
    else:
        folder = _resolve_folder(choice, folders)
        if folder is None:
            print("Invalid selection."); return

        stems = discover_files(data_dir, folder)
        print(f"\nFiles in '{folder}':")
        for i, s in enumerate(stems, 1):
            print(f"  [{i}] {s}.json")

        file_choice = input("\nWhich files? (number, name, comma-list, or 'all'): ").strip()
        if file_choice.lower() == "all":
            selected_stems = stems
        else:
            selected_stems = _resolve_stems(file_choice, stems)
            if selected_stems is None:
                print("Invalid selection."); return

        tasks = [(folder, s) for s in selected_stems]

    out = input(f"\nOutput root [{out_dir}]: ").strip() or out_dir
    print()
    run_builds(tasks, data_dir, out, jinja_template)


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Build self-contained mindmap HTML files from JSON data."
    )
    parser.add_argument("--folder", help="Folder name inside data/ (e.g. maven)")
    parser.add_argument("--files",  help="Comma-separated JSON stems (e.g. intro,deep-dive)")
    parser.add_argument("--all",    action="store_true", help="Build every JSON in every folder")
    parser.add_argument("--out",    default=OUT_DIR, metavar="DIR", help=f"Output root (default: {OUT_DIR})")
    parser.add_argument("--data",   default=DATA_DIR, metavar="DIR", help=f"Data root (default: {DATA_DIR})")
    args = parser.parse_args()

    env = Environment(loader=FileSystemLoader("."), autoescape=False)
    jinja_template = env.get_template(TEMPLATE_FILE)

    if not args.folder and not args.all:
        interactive(args.data, args.out, jinja_template)
        return

    if args.all:
        folders = discover_folders(args.data)
        tasks = [(f, s) for f in folders for s in discover_files(args.data, f)]
    else:
        stems = [s.strip() for s in args.files.split(",")] if args.files else discover_files(args.data, args.folder)
        tasks = [(args.folder, s) for s in stems]

    if not tasks:
        print("No tasks found. Check folder/file names.")
        return

    print(f"Building {len(tasks)} map(s) → {args.out}/\n")
    run_builds(tasks, args.data, args.out, jinja_template)


if __name__ == "__main__":
    main()
