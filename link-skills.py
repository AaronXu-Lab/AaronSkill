#!/usr/bin/env python3
"""Link all top-level repository Skills into a global Skills directory."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target", type=Path, default=Path.home() / ".agents" / "skills",
        help="global Skills directory (default: ~/.agents/skills)",
    )
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    target = args.target.expanduser().absolute()
    skills = sorted(p.parent for p in root.glob("*/SKILL.md") if p.is_file())
    linked = existing = conflicts = 0
    try:
        if not args.dry_run:
            target.mkdir(parents=True, exist_ok=True)
        for source in skills:
            destination = target / source.name
            if destination.is_symlink() and destination.resolve() == source.resolve():
                existing += 1
                print(f"OK       {source.name}")
            elif destination.exists() or destination.is_symlink():
                conflicts += 1
                print(f"CONFLICT {destination} (preserved; not linked to {source})")
            else:
                if not args.dry_run:
                    destination.symlink_to(source, target_is_directory=True)
                linked += 1
                print(f"{'WOULD LINK' if args.dry_run else 'LINKED'}   {destination} -> {source}")
    except OSError as error:
        print(f"ERROR: {error}")
        return 1
    print(f"Total {len(skills)}: already linked {existing}, "
          f"{'missing' if args.dry_run else 'created'} {linked}, conflicts {conflicts}")
    return 1 if conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
