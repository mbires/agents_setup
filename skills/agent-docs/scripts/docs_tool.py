#!/usr/bin/env python3
"""Agent docs helper (stdlib only).

  init  [docs_dir]                   add frontmatter, doc ID and section IDs to md files that lack them
  new   <relpath> <title> [docs_dir] create a new doc stub with the next free ID
  index [docs_dir]                   rebuild INDEX.md from frontmatter (two levels above INDEX_SPLIT docs)
  lint  [docs_dir]                   check IDs, sizes, sections, code paths, references
  show  <ID[#sN]> [docs_dir]         print one doc or one section
  find  <words> [docs_dir]           print index rows whose id, path or summary contain all words
  stats [docs_dir]                   words, lines, rough token estimate per doc
"""
import re, sys, datetime
from pathlib import Path

MAX_LINES = 150
MAX_WORDS = 1200
INDEX_SPLIT = 40  # more docs than this: INDEX.md lists areas, each area gets <area>/INDEX.md
AREA_MARK = "# Index: "
SKIP = ("INDEX.md", "GLOSSARY.md")
STATUSES = ("draft", "stable", "deprecated")
ID_RE = r"[A-Z][A-Z0-9]*-\d{2,}"
FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)
SEC = re.compile(r"^## .*?\{#(s\d+)\}\s*$", re.M)
HEAD = re.compile(r"^## .*$", re.M)
REF = re.compile(rf"\b({ID_RE})(?:#(s\d+))?")


def parse_fm(text):
    m = FM.match(text)
    if not m:
        return None, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = re.sub(r"\s{2,}#.*$", "", v).strip()
    return meta, text[m.end():]


def load(d):
    out = []
    for p in sorted(d.rglob("*.md")):
        if p.name in SKIP:
            continue
        text = p.read_text(encoding="utf-8")
        meta, body = parse_fm(text)
        out.append((p, text, meta, body))
    return out


def code_list(v):
    return [x.strip() for x in v.strip("[]").split(",") if x.strip()]


def prefix_for(p, d):
    parts = p.relative_to(d).parts
    name = parts[0] if len(parts) > 1 else p.stem
    pre = re.sub(r"[^A-Za-z0-9]", "", name).upper()[:6] or "DOC"
    return pre if pre[0].isalpha() else "D" + pre


def next_id(docs, prefix):
    nums = [int(m.group(1)) for _, _, meta, _ in docs if meta and "id" in meta
            for m in [re.fullmatch(rf"{prefix}-(\d+)", meta["id"])] if m]
    return f"{prefix}-{max(nums, default=0) + 1:02d}"


def frontmatter(i, title, summary, code, status, updated):
    return (f"---\nid: {i}\ntitle: {title}\nsummary: {summary}\n"
            f"code: [{code}]\nstatus: {status}\nupdated: {updated}\n---\n\n")


def cmd_init(d):
    docs = load(d)
    done = 0
    for p, text, meta, body in docs:
        rel = p.relative_to(d).as_posix()
        if meta is not None:
            if "id" not in meta:
                print(f"skip {rel}: has frontmatter without id, fix by hand")
            continue
        lines = body.split("\n")
        title = p.stem.replace("-", " ").replace("_", " ").title()
        for n, ln in enumerate(lines[:10]):
            if ln.startswith("# "):
                title = ln[2:].strip()
                del lines[n]
                break
        body = "\n".join(lines).lstrip("\n")
        counter = [0]

        def add(m):
            counter[0] += 1
            return f"{m.group(0).rstrip()} {{#s{counter[0]}}}"

        body = re.sub(r"^## (?!.*\{#s\d+\}\s*$).*$", add, body, flags=re.M)
        if counter[0] == 0:
            print(f"warn {rel}: no '##' sections, add them by hand")
        i = next_id(load(d), prefix_for(p, d))
        upd = datetime.date.fromtimestamp(p.stat().st_mtime).isoformat()
        p.write_text(frontmatter(i, title, "TODO", "", "draft", upd) + body, encoding="utf-8")
        print(f"{i}  {rel}")
        done += 1
    print(f"init: {done} file(s)")
    return cmd_index(d)


def cmd_new(d, rel, title):
    p = d / rel
    if p.exists():
        print(f"exists: {rel}"); return 1
    p.parent.mkdir(parents=True, exist_ok=True)
    i = next_id(load(d), prefix_for(p, d))
    p.write_text(frontmatter(i, title, "TODO", "", "draft", datetime.date.today().isoformat())
                 + "## Purpose {#s1}\n\n", encoding="utf-8")
    print(f"{i}  {rel}")
    return cmd_index(d)


TABLE = ["id | path | summary | code", "--- | --- | --- | ---"]


def index_rows(d):
    rows = []
    for p, _, meta, _ in load(d):
        if meta and "id" in meta:
            rows.append((meta["id"], p.relative_to(d).as_posix(),
                         meta.get("summary", ""), meta.get("code", "").strip("[]")))
    return sorted(rows)


def cmd_index(d):
    rows = index_rows(d)
    for old in d.glob("*/INDEX.md"):
        if old.read_text(encoding="utf-8").startswith(AREA_MARK):
            old.unlink()
    if len(rows) <= INDEX_SPLIT:
        out = ["# Index", ""] + TABLE + [" | ".join(r) for r in rows]
        (d / "INDEX.md").write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"INDEX.md: {len(rows)} docs")
        return 0
    areas, top = {}, []
    for r in rows:
        if "/" in r[1]:
            areas.setdefault(r[1].split("/", 1)[0], []).append(r)
        else:
            top.append(r)
    out = ["# Index", "", f"Two levels: open the area index you need, or run `find <words>`.", "",
           "area | ID prefixes | docs | index", "--- | --- | --- | ---"]
    for a, rs in sorted(areas.items()):
        pre = ", ".join(sorted({r[0].rsplit("-", 1)[0] for r in rs}))
        out.append(f"{a} | {pre} | {len(rs)} | {a}/INDEX.md")
        sub = [f"{AREA_MARK}{a}", ""] + TABLE + [" | ".join(r) for r in rs]
        (d / a / "INDEX.md").write_text("\n".join(sub) + "\n", encoding="utf-8")
    if top:
        out += ["", "Docs outside areas:", ""] + TABLE + [" | ".join(r) for r in top]
    (d / "INDEX.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"INDEX.md: {len(rows)} docs in {len(areas)} area index(es)")
    return 0


def cmd_find(d, words):
    ws = [w.lower() for w in words]
    hits = [r for r in index_rows(d)
            if all(w in f"{r[0]} {r[1]} {r[2]}".lower() for w in ws)]
    print("\n".join(" | ".join(r) for r in hits) if hits else "no match")
    return 0 if hits else 1


def cmd_lint(d):
    root = d.parent
    errs, ids, sections = [], {}, {}
    docs = load(d)
    for p, text, meta, body in docs:
        rel = p.relative_to(d).as_posix()
        if not meta:
            errs.append(f"{rel}: no frontmatter, run init"); continue
        for k in ("id", "title", "summary", "code", "status", "updated"):
            if k not in meta:
                errs.append(f"{rel}: missing '{k}'")
        if not meta.get("summary") or meta["summary"] == "TODO":
            errs.append(f"{rel}: summary is empty or TODO")
        if "code" in meta and not re.fullmatch(r"\[.*\]", meta["code"]):
            errs.append(f"{rel}: code must be a bracketed path list")
        if "updated" in meta:
            try:
                datetime.date.fromisoformat(meta["updated"])
            except ValueError:
                errs.append(f"{rel}: updated must be an ISO date")
        if meta.get("status") and meta["status"] not in STATUSES:
            errs.append(f"{rel}: bad status '{meta['status']}'")
        i = meta.get("id")
        if i:
            if not re.fullmatch(ID_RE, i):
                errs.append(f"{rel}: bad id '{i}'")
            if i in ids:
                errs.append(f"{rel}: duplicate id {i} (also {ids[i]})")
            ids[i] = rel
        n, w = len(text.splitlines()), len(text.split())
        if n > MAX_LINES:
            errs.append(f"{rel}: {n} lines (max {MAX_LINES}), split or cut")
        if w > MAX_WORDS:
            errs.append(f"{rel}: {w} words (max {MAX_WORDS}), split or cut")
        found = SEC.findall(body)
        for s in set(found):
            if found.count(s) > 1:
                errs.append(f"{rel}: duplicate section id {s}")
        missing = len(HEAD.findall(body)) - len(found)
        if missing:
            errs.append(f"{rel}: {missing} '##' heading(s) without {{#sN}}")
        if i:
            sections[i] = set(found)
        for c in code_list(meta.get("code", "")):
            if not (root / c).exists():
                errs.append(f"{rel}: code path not found: {c}")
    known = {i.rsplit("-", 1)[0] for i in ids}
    for p, text, meta, body in docs:
        rel = p.relative_to(d).as_posix()
        for i, s in REF.findall(body):
            if i.rsplit("-", 1)[0] not in known:
                continue
            if i not in ids:
                errs.append(f"{rel}: unknown ref {i}")
            elif s and s not in sections.get(i, ()):
                errs.append(f"{rel}: unknown section {i}#{s}")
    idx = d / "INDEX.md"
    if not idx.exists():
        errs.append("INDEX.md missing, run index")
    else:
        t = "\n".join(x.read_text(encoding="utf-8") for x in [idx, *d.glob("*/INDEX.md")])
        for i in ids:
            if not re.search(rf"^{re.escape(i)} \|", t, re.M):
                errs.append(f"INDEX.md: {i} missing, run index")
    print("\n".join(errs) if errs else "ok")
    return 1 if errs else 0


def cmd_show(d, ref):
    i, _, s = ref.partition("#")
    for p, text, meta, body in load(d):
        if meta and meta.get("id") == i:
            if not s:
                print(text); return 0
            for part in re.split(r"(?m)^(?=## )", body):
                if re.match(rf"## .*\{{#{s}\}}\s*$", part.split("\n", 1)[0]):
                    print(part.rstrip()); return 0
            print(f"section {s} not found in {i}"); return 1
    print(f"{i} not found"); return 1


def cmd_stats(d):
    tl = tw = 0
    for p, text, meta, _ in load(d):
        n, w = len(text.splitlines()), len(text.split())
        tl += n; tw += w
        print(f"{(meta or {}).get('id', '-'):10} {w:6} words {n:5} lines  ~{int(w * 1.3):6} tokens  {p.relative_to(d).as_posix()}")
    print(f"{'total':10} {tw:6} words {tl:5} lines  ~{int(tw * 1.3):6} tokens (rough estimate)")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] not in ("init", "new", "index", "lint", "show", "find", "stats"):
        sys.exit(__doc__)
    c = a[0]
    if c == "find" and len(a) >= 2:
        has_dir = len(a) > 2 and Path(a[-1]).is_dir()
        sys.exit(cmd_find(Path(a[-1]) if has_dir else Path("docs"), a[1:-1] if has_dir else a[1:]))
    if c == "find":
        sys.exit(__doc__)
    if c == "show" and len(a) >= 2:
        sys.exit(cmd_show(Path(a[2] if len(a) > 2 else "docs"), a[1]))
    if c == "new" and len(a) >= 3:
        sys.exit(cmd_new(Path(a[3] if len(a) > 3 else "docs"), a[1], a[2]))
    if c in ("show", "new"):
        sys.exit(__doc__)
    d = Path(a[1] if len(a) > 1 else "docs")
    sys.exit({"init": cmd_init, "index": cmd_index, "lint": cmd_lint, "stats": cmd_stats}[c](d))
