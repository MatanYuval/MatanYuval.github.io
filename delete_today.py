#!/usr/bin/env python3

import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()

def git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True
    ).stdout

# Make sure we're inside a git repository
try:
    git("rev-parse", "--show-toplevel")
except Exception:
    print("ERROR: Run this from inside your GitHub repository folder.")
    raise SystemExit(1)

# Files ADDED in commits made since local midnight
output = git(
    "log",
    "--since=midnight",
    "--diff-filter=A",
    "--name-only",
    "--pretty=format:"
)

files = sorted({
    line.strip()
    for line in output.splitlines()
    if line.strip()
})

# Keep only files that still currently exist in the repo
files = [f for f in files if (ROOT / f).exists()]

if not files:
    print("No currently existing files were added today.")
    raise SystemExit

print("\nFILES ADDED TODAY\n")
for f in files:
    print("  ", f)

print(f"\nTotal: {len(files)} files")
print("\nNothing has been deleted yet.")

answer = input(
    '\nType DELETE to remove ALL of these files from the repository: '
)

if answer != "DELETE":
    print("\nCancelled. Nothing changed.")
    raise SystemExit

# Create a backup branch at the current state
stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = f"backup-before-delete-{stamp}"

subprocess.run(
    ["git", "branch", backup],
    cwd=ROOT,
    check=True
)

print(f"\nBackup branch created: {backup}")

# Remove each file using git rm
for f in files:
    print("Deleting:", f)
    subprocess.run(
        ["git", "rm", "--", f],
        cwd=ROOT,
        check=True
    )

print("\nFiles removed locally and staged for commit.")
print("\nCheck everything with:")
print("  git status")
print()
print("If correct:")
print('  git commit -m "Remove files added today"')
print("  git push")
print()
print("If something is wrong, restore from:")
print(f"  {backup}")
