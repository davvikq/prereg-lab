#!/usr/bin/env python3
"""prereg-lab deterministic helpers (stdlib only).

Every experiment hashes and tests with this script rather than improvising
equivalents, so numbers come from the same code path across runs.

Commands:
  freeze FILE [--copy-to DIR] [--name NAME]
      sha256 of FILE; writes a frozen copy (never overwrites an existing one).
  manifest DIR [-o FILE]
      sha256 manifest of every file under DIR (stable order, sha256sum format).
  signtest (--diffs D1 D2 ... | --file FILE) [--alternative two|greater|less]
      [--mc N] [--seed S]
      Monte Carlo sign-flip randomization test for paired/block differences.
      Exact enumeration when N <= 17.
  holm P1 P2 ...
      Holm step-down adjusted p-values for one preregistered family.
  decide REGISTRY "decision" --evidence "fact"
      Append a DECISIONS.md row with a mechanical UTC timestamp and the next
      D-number. Call at decision time - backfilled rows have unverifiable times.
  install [--source DIR] [--dir PATH]... [--update] [--dry-run]
      Copy the skill into every detected agent skills directory. The canonical
      shared dir ~/.agents/skills is always installed; existing harness dirs
      (~/.claude/skills, OpenCode, project-local) are picked up automatically;
      pass --dir for anything custom. Without --update, an already-installed
      different version is skipped, never silently replaced.

Examples:
  python prereg.py freeze PREREGISTRATION.md --copy-to docs/e01
  python prereg.py manifest experiments/E01 -o docs/e01/E01_artifacts_manifest.sha256
  python prereg.py signtest --diffs 12.1 -3.4 5.5 0.2 --alternative greater
  python prereg.py holm 0.003 0.014 0.052
"""

import argparse
import hashlib
import itertools
import math
import os
import random
import re
import shutil
import sys
from datetime import datetime, timezone


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_decide(args):
    path = args.registry
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = (
        "# DECISIONS\n\n"
        "Append-only registry. One row per decision, written at decision time\n"
        "(use prereg.py decide so the timestamp is mechanical). Never rewrite;\n"
        "a reversed decision gets status SUPERSEDED with a pointer.\n\n"
        "| ID | Date | Decision | Evidence |\n"
        "|----|------|----------|----------|\n"
    )
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            content = f.read()
        numbers = [int(x) for x in re.findall(r"\bD-(\d+)\b", content)]
        n = (max(numbers) + 1) if numbers else 1
    else:
        content = ""
        n = 1
    def cell(text):
        return text.replace("|", "\\|")  # keep the markdown table intact

    row = f"| D-{n:03d} | {stamp} | {cell(args.decision)} | {cell(args.evidence)} |\n"
    with open(path, "a", encoding="utf-8", newline="") as f:
        if not content.strip():
            if content:
                f.write("\n")
            f.write(header)
        elif not content.endswith("\n"):
            f.write("\n")
        f.write(row)
    print(f"appended: {row.strip()}")
    print(f"registry sha256: {sha256_file(path)}")


SKILL_FILES = (
    "SKILL.md", "templates.md", "statistics.md", "case-studies.md",
    "prereg.py", "LICENSE",
)


def cmd_install(args):
    source = os.path.abspath(args.source or os.path.dirname(os.path.abspath(__file__)))
    missing = [f for f in SKILL_FILES if not os.path.isfile(os.path.join(source, f))]
    if missing:
        sys.exit(f"install: {source} is missing skill files: {', '.join(missing)}")

    targets = [os.path.expanduser(os.path.join("~", ".agents", "skills"))]
    home = os.path.expanduser("~")
    for candidate in (
        os.path.join(home, ".claude", "skills"),
        os.path.join(home, ".config", "opencode", "skills"),
        os.path.join(home, ".opencode", "skills"),
        os.path.join(os.getcwd(), ".agents", "skills"),
        os.path.join(os.getcwd(), ".claude", "skills"),
        os.path.join(os.getcwd(), ".opencode", "skills"),
    ):
        if os.path.isdir(candidate) and os.path.abspath(candidate) not in targets:
            targets.append(os.path.abspath(candidate))
    for d in args.dir or []:
        targets.append(os.path.abspath(os.path.expanduser(d)))

    if args.dry_run:
        print("dry run - would install into:")
        for t in targets:
            print(f"  {os.path.join(t, 'prereg-lab')}")
        return

    src_hash = {f: sha256_file(os.path.join(source, f)) for f in SKILL_FILES}
    installed, skipped, current = [], [], 0
    for target in targets:
        dest = os.path.join(target, "prereg-lab")
        if os.path.abspath(dest) == os.path.abspath(source):
            current += 1
            continue
        dest_skill_md = os.path.join(dest, "SKILL.md")
        if os.path.isfile(dest_skill_md):
            dest_complete = all(
                os.path.isfile(os.path.join(dest, f))
                and sha256_file(os.path.join(dest, f)) == src_hash[f]
                for f in SKILL_FILES
            )
            if dest_complete:
                current += 1
                print(f"up to date: {dest}")
                continue
            if not args.update:
                skipped.append(dest)
                print(f"SKIPPED (different or incomplete version, use --update): {dest}")
                continue
        os.makedirs(dest, exist_ok=True)
        for f in SKILL_FILES:
            shutil.copy2(os.path.join(source, f), os.path.join(dest, f))
        installed.append(dest)
        print(f"installed: {dest}  (SKILL.md sha256 {src_hash['SKILL.md'][:16]}...)")

    print(f"\n{len(installed)} installed, {len(skipped)} skipped, {current} already current.")
    print("Agents that read ~/.agents/skills pick the skill up automatically; "
          "for anything else pass --dir /path/to/skills.")


def cmd_freeze(args):
    path = args.file
    if not os.path.isfile(path):
        sys.exit(f"freeze: no such file: {path}")
    digest = sha256_file(path)
    stem, ext = os.path.splitext(os.path.basename(path))
    frozen_name = args.name or f"{stem}_frozen{ext}"
    if args.copy_to:
        os.makedirs(args.copy_to, exist_ok=True)
        target = os.path.join(args.copy_to, frozen_name)
        if os.path.exists(target):
            sys.exit(
                f"freeze: {target} already exists. Do NOT overwrite - the change "
                f"protocol is append-only addenda ('changed after start, reason')."
            )
        with open(path, "rb") as src, open(target, "wb") as dst:
            dst.write(src.read())
        copy_digest = sha256_file(target)
        print(f"original: {path}")
        print(f"sha256:   {digest}")
        print(f"frozen:   {target}")
        print(f"sha256:   {copy_digest}")
    else:
        print(f"original: {path}")
        print(f"sha256:   {digest}")
        print("frozen copy skipped (no --copy-to given)")


def cmd_manifest(args):
    root = args.dir
    if not os.path.isdir(root):
        sys.exit(f"manifest: no such directory: {root}")
    rels = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            rels.append(rel)
    rels.sort()
    lines = [f"{sha256_file(os.path.join(root, rel))}  {rel}" for rel in rels]
    payload = "\n".join(lines) + ("\n" if lines else "")
    if args.output:
        if os.path.exists(args.output):
            sys.exit(
                f"manifest: {args.output} exists. Manifests are immutable - "
                f"write a new one for the new state instead."
            )
        with open(args.output, "w", newline="\n") as f:
            f.write(payload)
        print(f"{len(rels)} files -> {args.output}")
        print(f"manifest sha256: {sha256_file(args.output)}")
    else:
        sys.stdout.write(payload)
        print(f"# {len(rels)} files", file=sys.stderr)


def sign_flip_p(diffs, alternative="two", n_mc=99999, seed=1337):
    n = len(diffs)
    if n == 0:
        sys.exit("signtest: no differences given")
    obs = sum(diffs)

    def exceeds(s):
        if alternative == "two":
            return abs(s) >= abs(obs)
        if alternative == "greater":
            return s >= obs
        if alternative == "less":
            return s <= obs
        sys.exit(f"signtest: unknown alternative {alternative!r}")

    if n <= 17:
        ge = sum(
            1
            for signs in itertools.product((1, -1), repeat=n)
            if exceeds(sum(s * x for s, x in zip(signs, diffs)))
        )
        return ge / (2 ** n), "exact", n
    rng = random.Random(seed)
    ge = 0
    for _ in range(n_mc):
        s = sum(x * rng.choice((-1, 1)) for x in diffs)
        if exceeds(s):
            ge += 1
    return (ge + 1) / (n_mc + 1), f"monte-carlo(n_mc={n_mc}, seed={seed})", n


def cmd_signtest(args):
    if bool(args.diffs) == bool(args.file):
        sys.exit("signtest: pass exactly one of --diffs or --file")
    if args.diffs:
        try:
            diffs = [float(x) for x in args.diffs]
        except ValueError as e:
            sys.exit(f"signtest: bad number: {e}")
    else:
        with open(args.file) as f:
            diffs = [float(line) for line in f.read().split()]
    p, method, n = sign_flip_p(diffs, args.alternative, args.mc, args.seed)
    print(f"n diffs:        {n}")
    print(f"mean diff:      {sum(diffs) / n:.6g}")
    print(f"observed stat:  {sum(diffs):.6g}")
    print(f"alternative:    {args.alternative}")
    print(f"method:         {method}")
    print(f"p-value:        {p:.6g}")


def cmd_holm(args):
    ps = args.pvalues
    if not ps:
        sys.exit("holm: no p-values given")
    if any(not math.isfinite(p) or p < 0 or p > 1 for p in ps):
        sys.exit("holm: p-values must be finite and in [0, 1]")
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * ps[idx])
        adjusted[idx] = min(1.0, running)
    print(f"family size m = {m} (declare this in the preregistration)")
    print(f"{'index':>5}  {'p_raw':>10}  {'p_holm':>10}")
    for i in range(m):
        print(f"{i:>5}  {ps[i]:>10.4g}  {adjusted[i]:>10.4g}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("freeze", help="sha256 + frozen copy of the preregistration")
    p.add_argument("file")
    p.add_argument("--copy-to", default=None)
    p.add_argument("--name", default=None)
    p.set_defaults(func=cmd_freeze)

    p = sub.add_parser("manifest", help="sha256 manifest of a directory")
    p.add_argument("dir")
    p.add_argument("-o", "--output", default=None)
    p.set_defaults(func=cmd_manifest)

    p = sub.add_parser("signtest", help="sign-flip randomization test")
    p.add_argument("--diffs", nargs="+", default=None)
    p.add_argument("--file", default=None)
    p.add_argument("--alternative", choices=["two", "greater", "less"], default="two")
    p.add_argument("--mc", type=int, default=99999)
    p.add_argument("--seed", type=int, default=1337)
    p.set_defaults(func=cmd_signtest)

    p = sub.add_parser("holm", help="Holm step-down adjusted p-values")
    p.add_argument("pvalues", nargs="+", type=float)
    p.set_defaults(func=cmd_holm)

    p = sub.add_parser("decide", help="append a registry row with a mechanical UTC timestamp")
    p.add_argument("registry")
    p.add_argument("decision")
    p.add_argument("--evidence", default="")
    p.set_defaults(func=cmd_decide)

    p = sub.add_parser("install", help="install the skill into detected agent skills directories")
    p.add_argument("--source", default=None, help="skill source dir (default: this file's directory)")
    p.add_argument("--dir", action="append", default=[], help="extra skills directory (repeatable)")
    p.add_argument("--update", action="store_true", help="overwrite already-installed different versions")
    p.add_argument("--dry-run", action="store_true", help="show targets without installing")
    p.set_defaults(func=cmd_install)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
