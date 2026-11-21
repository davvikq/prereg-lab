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

Examples:
  python prereg.py freeze PREREGISTRATION.md --copy-to docs/e01
  python prereg.py manifest experiments/E01 -o docs/e01/E01_artifacts_manifest.sha256
  python prereg.py signtest --diffs 12.1 -3.4 5.5 0.2 --alternative greater
  python prereg.py holm 0.003 0.014 0.052
"""

import argparse
import hashlib
import itertools
import os
import random
import sys


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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
    ref = abs(obs) if alternative == "two" else obs
    if n <= 17:
        ge = sum(
            1
            for signs in itertools.product((1, -1), repeat=n)
            if abs(sum(s * x for s, x in zip(signs, diffs))) >= ref
        ) if alternative == "two" else sum(
            1
            for signs in itertools.product((1, -1), repeat=n)
            if sum(s * x for s, x in zip(signs, diffs)) >= ref
        )
        return ge / (2 ** n), "exact", n
    rng = random.Random(seed)
    ge = 0
    for _ in range(n_mc):
        s = sum(x * rng.choice((-1, 1)) for x in diffs)
        val = abs(s) if alternative == "two" else s
        if val >= ref:
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
    if any(p < 0 or p > 1 for p in ps):
        sys.exit("holm: p-values must be in [0, 1]")
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

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
