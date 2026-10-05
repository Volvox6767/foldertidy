#!/usr/bin/env python3
"""
foldertidy — clean up your Downloads/Messy folder in seconds.

  * sorts files into Pictures / Videos / Documents / Music / Archives / ...
  * finds duplicate files and moves them to a _duplicates folder (never deletes)
  * dry-run by default: nothing moves until you pass --apply

Single file, zero dependencies, works offline.

  python foldertidy.py                    # organize ~/Downloads (preview)
  python foldertidy.py ~/Downloads --apply
  python foldertidy.py ./Photos --by-month --apply
  python foldertidy.py ./Messy --dedupe --apply

Author : Ahmet Gedik  (https://www.instagram.com/ahmetgedik67)
License: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

__version__ = "1.0.0"
AUTHOR = "Ahmet Gedik"
INSTAGRAM = "https://www.instagram.com/ahmetgedik67"

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ---------------------------------------------------------------- categories
CATEGORIES: dict[str, tuple[str, ...]] = {
    "Pictures": (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic", ".heif",
                 ".svg", ".ico", ".tiff", ".tif", ".raw", ".cr2", ".nef", ".arw", ".dng"),
    "Videos": (".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".ts", ".wmv", ".flv",
               ".3gp", ".mpeg", ".mpg"),
    "Documents": (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt",
                  ".ods", ".odp", ".rtf", ".txt", ".md", ".csv", ".epub", ".mobi"),
    "Music": (".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".opus"),
    "Archives": (".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".cab"),
    "Programs": (".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".appimage", ".apk"),
    "Code": (".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".java", ".c",
             ".cpp", ".cs", ".go", ".rs", ".rb", ".php", ".sh", ".bat", ".ps1", ".ipynb"),
    "Fonts": (".ttf", ".otf", ".woff", ".woff2"),
    "Torrents": (".torrent",),
}
EXT_TO_CAT = {ext: cat for cat, exts in CATEGORIES.items() for ext in exts}
SKIP_DIRS = {"_duplicates", "previews", ".git", "__pycache__", "node_modules"}
# files that belong together with what made them (crdownload/part = downloading now)
TRANSIENT = (".crdownload", ".part", ".tmp", ".download")


def banner() -> str:
    return (
        "\n  foldertidy — organize messy folders & find duplicates\n"
        f"  by {AUTHOR}  |  {INSTAGRAM}\n"
        "  ------------------------------------------------------\n"
    )


def category_of(path: Path) -> str | None:
    ext = path.suffix.lower()
    if ext in TRANSIENT:
        return None
    return EXT_TO_CAT.get(ext)


def target_dir(root: Path, f: Path, by_month: bool, by_date: bool) -> Path:
    cat = category_of(f) or "Others"
    d = root / cat
    if by_month and cat == "Pictures":
        d = d / datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m")
    elif by_date:
        d = d / datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
    return d


def unique_path(dst: Path) -> Path:
    if not dst.exists():
        return dst
    for i in range(2, 10_000):
        cand = dst.with_name(f"{dst.stem} ({i}){dst.suffix}")
        if not cand.exists():
            return cand
    return dst.with_name(f"{dst.stem} (dup){dst.suffix}")


# ---------------------------------------------------------------- organize
def plan_organize(root: Path, by_month: bool, by_date: bool) -> list[tuple[Path, Path]]:
    moves: list[tuple[Path, Path]] = []
    for f in sorted(root.rglob("*")):
        if not f.is_file() or any(part in SKIP_DIRS for part in f.relative_to(root).parts[:-1]):
            continue
        if f.parent != root:      # already in a subfolder
            continue
        if f.suffix.lower() in TRANSIENT:   # still downloading — leave alone
            continue
        if category_of(f) is None and not f.suffix:
            continue              # extensionless junk we don't understand (e.g. desktop.ini)
        dst_dir = target_dir(root, f, by_month, by_date)
        dst = unique_path(dst_dir / f.name)
        if dst != f:
            moves.append((f, dst))
    return moves


# ---------------------------------------------------------------- duplicates
def file_hash(path: Path, quick: bool = False) -> bytes:
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        if quick:                      # first 64 KB + file size: fast pre-filter
            h.update(fh.read(65_536))
        else:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    return h.digest()


def plan_dedupe(root: Path) -> tuple[list[tuple[Path, Path]], int]:
    """Return (moves, wasted_bytes). Keeps the oldest copy, moves the rest."""
    by_size: dict[int, list[Path]] = defaultdict(list)
    for f in sorted(root.rglob("*")):
        if f.is_file() and not any(part in SKIP_DIRS for part in f.relative_to(root).parts):
            by_size[f.stat().st_size].append(f)

    wasted = 0
    dup_groups: list[list[Path]] = []
    for size, files in by_size.items():
        if size == 0 or len(files) < 2:
            continue
        by_quick: dict[bytes, list[Path]] = defaultdict(list)
        for f in files:
            by_quick[file_hash(f, quick=True)].append(f)
        for cand in by_quick.values():
            if len(cand) < 2:
                continue
            full: dict[bytes, list[Path]] = defaultdict(list)
            for f in cand:
                full[file_hash(f)].append(f)
            for group in full.values():
                if len(group) >= 2:
                    group.sort(key=lambda p: p.stat().st_mtime)
                    dup_groups.append(group)
                    wasted += size * (len(group) - 1)

    moves: list[tuple[Path, Path]] = []
    for group in dup_groups:
        for f in group[1:]:
            rel = f.relative_to(root)
            dst = unique_path(root / "_duplicates" / rel)
            moves.append((f, dst))
    return moves, wasted


# ---------------------------------------------------------------- runner
def human(n: float) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{int(n)} B" if u == "B" else f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} GB"


def apply_moves(moves: list[tuple[Path, Path]], dry: bool, root: Path | None = None) -> tuple[int, int]:
    done = errors = 0
    for src, dst in moves:
        if root is not None:
            rel = dst.relative_to(root)
            print(f"  {'[dry] ' if dry else ''}{src.relative_to(root)}  →  {rel}")
        else:
            print(f"  {'[dry] ' if dry else ''}{src.name}  →  {dst}")
        if dry:
            done += 1
            continue
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.replace(src, dst)
            done += 1
        except OSError as e:
            print(f"    ✘ {e}")
            errors += 1
    return done, errors


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="foldertidy",
        description="Organize a messy folder (Downloads!) into categories and move duplicate files out — safely, offline.",
        epilog=f"by {AUTHOR} — {INSTAGRAM}",
    )
    ap.add_argument("folder", nargs="?", default=str(Path.home() / "Downloads"),
                    help="folder to tidy (default: ~/Downloads)")
    ap.add_argument("--apply", action="store_true",
                    help="actually move files (default is a dry-run preview)")
    ap.add_argument("--by-month", action="store_true",
                    help="also sort Pictures into YYYY-MM subfolders")
    ap.add_argument("--by-date", action="store_true",
                    help="sort ALL files into YYYY-MM-DD subfolders")
    ap.add_argument("--dedupe", action="store_true",
                    help="find duplicates and move them to _duplicates/")
    ap.add_argument("--version", action="version", version=f"foldertidy {__version__}")
    args = ap.parse_args()

    root = Path(args.folder).expanduser().resolve()
    if not root.is_dir():
        print(f"folder not found: {root}")
        return 1

    print(banner())
    if not args.dedupe:
        moves = plan_organize(root, args.by_month, args.by_date)
        mode = f"organize{' + photos by month' if args.by_month else ''}{' + by date' if args.by_date else ''}"
        print(f"📁 {root}   ({mode})")
        if not moves:
            print("  ✔ already tidy — nothing to move.")
        else:
            done, errors = apply_moves(moves, not args.apply, root)
            print(f"\n  {'PREVIEW:' if not args.apply else 'moved:'} {done} file(s)"
                  + (f", {errors} error(s)" if errors else ""))
            if not args.apply:
                print("  👍 looks right? run again with --apply")
        if not args.dedupe:
            return 0

    print(f"\n🔎 duplicates in {root}")
    moves, wasted = plan_dedupe(root)
    if not moves:
        print("  ✔ no duplicates found.")
        return 0
    done, errors = apply_moves(moves, not args.apply, root)
    print(f"\n  {len(moves)} duplicate file(s), {human(wasted)} reclaimable")
    if not args.apply:
        print("  👍 looks right? run again with --apply  (copies go to _duplicates/, nothing is deleted)")
    else:
        print(f"  moved {done} to {root / '_duplicates'}" + (f", {errors} error(s)" if errors else ""))
    print(f"\nmade with ❤ by {AUTHOR} — {INSTAGRAM}")
    return 0 if errors == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
