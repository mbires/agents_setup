#!/usr/bin/env python3
"""_Claude kit: project skeleton and skill distribution (stdlib only).

  new    <project_dir> [--no-git]     create the skeleton (dirs, AGENTS.md stub, settings, .gitignore, git init)
  add    <project_dir> <item>...      install skills (by name) and/or `agents` (Claude subagents)
  check  <project_dir>                compare installed skills/agents with the kit
  update <project_dir> [--force]      re-copy outdated skills/agents; --force also overwrites local edits
  pack   [skill]...                   zip skills to dist/<name>.skill for upload in the Claude app (all if none named)

Skills go to both .claude/skills/<name> (Claude Code) and .agents/skills/<name> (Codex, Antigravity).
Project-specific files (AGENTS.md, .agents/spec-writing.md, .claude/settings.json) are never touched by add/update.
"""
import filecmp, hashlib, re, shutil, subprocess, sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
SKILLS = KIT / "skills"
AGENTS = KIT / "agents"
SKILL_DIRS = (".claude/skills", ".agents/skills")
NO_INSTALL = {"project-setup"}  # used from the kit directly, never copied into projects


def version(skill_dir):
    m = re.search(r"^version:\s*(\S+)", (skill_dir / "SKILL.md").read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "?"


def digest(path):
    h = hashlib.sha256()
    for f in sorted(p for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        h.update(f.relative_to(path).as_posix().encode())
        h.update(f.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()


def kit_skills():
    return sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").exists() and p.name not in NO_INSTALL)


def copy_skill(name, proj):
    for base in SKILL_DIRS:
        dst = proj / base / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(SKILLS / name, dst, ignore=shutil.ignore_patterns("__pycache__"))
    print(f"skill {name} {version(SKILLS / name)} -> {', '.join(SKILL_DIRS)}")


def copy_agents(proj):
    dst = proj / ".claude/agents"
    dst.mkdir(parents=True, exist_ok=True)
    for f in AGENTS.glob("*.md"):
        shutil.copy2(f, dst / f.name)
    print(f"agents -> .claude/agents ({', '.join(f.stem for f in AGENTS.glob('*.md'))})")


def cmd_new(proj, git=True):
    if proj.exists() and any(proj.iterdir()):
        print(f"{proj} is not empty; new only creates fresh projects"); return 1
    shutil.copytree(KIT / "project", proj, dirs_exist_ok=True)
    for d in ("docs", "specification/phase", "specification/feat", "specification/fix", ".agents/skills"):
        (proj / d).mkdir(parents=True, exist_ok=True)
    for d in ("specification/phase", "specification/feat", "specification/fix"):
        (proj / d / ".gitkeep").touch()
    a = proj / "AGENTS.md"
    a.write_text(a.read_text(encoding="utf-8").replace("{{PROJECT}}", proj.name)
                 .replace("{{KIT}}", KIT.as_posix()), encoding="utf-8")
    if git and shutil.which("git"):
        subprocess.run(["git", "init", "-q", str(proj)], check=True)
        print("git init done (no remote, no commit)")
    print(f"skeleton ready: {proj}\nnext: open the project with an agent; AGENTS.md tells it to run project-setup")
    return 0


def cmd_add(proj, items):
    known = kit_skills()
    for it in items:
        if it == "agents":
            copy_agents(proj)
        elif it in known:
            copy_skill(it, proj)
        else:
            print(f"unknown item {it}; skills: {', '.join(known)}, or agents"); return 1
    return 0


def status(proj):
    """Yield (kind, name, state, detail). state: ok | outdated | modified | missing-copy."""
    for name in kit_skills():
        copies = [proj / b / name for b in SKILL_DIRS]
        present = [c for c in copies if (c / "SKILL.md").exists()]
        if not present:
            continue
        kit_v, kit_d = version(SKILLS / name), digest(SKILLS / name)
        for c in copies:
            rel = c.relative_to(proj).as_posix()
            if c not in present:
                yield "skill", name, "missing-copy", rel; continue
            if digest(c) == kit_d:
                yield "skill", name, "ok", f"{rel} {kit_v}"
            elif version(c) != kit_v:
                yield "skill", name, "outdated", f"{rel} {version(c)} < kit {kit_v}"
            else:
                yield "skill", name, "modified", f"{rel} {kit_v}: edited in project, differs from kit"
    adir = proj / ".claude/agents"
    for f in AGENTS.glob("*.md"):
        if (adir / f.name).exists():
            same = filecmp.cmp(f, adir / f.name, shallow=False)
            yield "agent", f.stem, "ok" if same else "outdated", f".claude/agents/{f.name}"


def cmd_check(proj):
    rows = list(status(proj))
    if not rows:
        print("no kit skills or agents installed"); return 0
    for kind, name, state, detail in rows:
        print(f"{state:12} {kind:5} {name:24} {detail}")
    return 0 if all(r[2] == "ok" for r in rows) else 1


def cmd_update(proj, force=False):
    todo, agents = set(), False
    for kind, name, state, detail in status(proj):
        if state == "ok":
            continue
        if state == "modified" and not force:
            print(f"skip {detail} (use --force to overwrite, or move the change into the kit first)"); continue
        if kind == "agent":
            agents = True
        else:
            todo.add(name)
    for name in sorted(todo):
        copy_skill(name, proj)
    if agents:
        copy_agents(proj)
    if not todo and not agents:
        print("nothing to update")
    return 0


def cmd_pack(names):
    import zipfile
    names = names or kit_skills() + sorted(NO_INSTALL)
    (KIT / "dist").mkdir(exist_ok=True)
    for name in names:
        src = SKILLS / name
        if not (src / "SKILL.md").exists():
            print(f"unknown skill {name}"); return 1
        out = KIT / "dist" / f"{name}.skill"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(p for p in src.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
                z.write(f, f"{name}/{f.relative_to(src).as_posix()}")
        print(f"{out.relative_to(KIT).as_posix()}  {version(src)}")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["pack"]:
        sys.exit(cmd_pack(a[1:]))
    flags = {x for x in a if x.startswith("--")}
    a = [x for x in a if not x.startswith("--")]
    if len(a) < 2 or a[0] not in ("new", "add", "check", "update") or (a[0] == "add" and len(a) < 3):
        sys.exit(__doc__)
    proj = Path(a[1]).resolve()
    if a[0] != "new" and not proj.is_dir():
        sys.exit(f"not a directory: {proj}")
    sys.exit({"new": lambda: cmd_new(proj, "--no-git" not in flags),
              "add": lambda: cmd_add(proj, a[2:]),
              "check": lambda: cmd_check(proj),
              "update": lambda: cmd_update(proj, "--force" in flags)}[a[0]]())
