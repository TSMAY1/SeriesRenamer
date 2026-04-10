import csv
import re
import sys
import argparse
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


VIDEO_EXTENSIONS = {".avi", ".mkv", ".mp4", ".mov", ".wmv", ".m4v"}


PATTERNS = [
    # Star Trek The Next Generation Season 1 Episode 3 - The Naked Now
    re.compile(
        r"""
        ^.*?
        Season\W*(?P<season>\d{1,2})
        \W+
        Episode\W*(?P<episode>\d{1,3})
        \W*[-–—]\W*
        (?P<title>.+?)
        $
        """,
        re.IGNORECASE | re.VERBOSE,
    ),

    # Star Trek The Next Generation S1E03 - The Naked Now
    re.compile(
        r"""
        ^.*?
        S(?P<season>\d{1,2})
        E(?P<episode>\d{1,3})
        \W*[-–—]\W*
        (?P<title>.+?)
        $
        """,
        re.IGNORECASE | re.VERBOSE,
    ),

    # Star Trek The Next Generation 1x03 - The Naked Now
    re.compile(
        r"""
        ^.*?
        (?P<season>\d{1,2})x(?P<episode>\d{1,3})
        \W*[-–—]\W*
        (?P<title>.+?)
        $
        """,
        re.IGNORECASE | re.VERBOSE,
    ),

    # Episode 03 - The Naked Now
    re.compile(
        r"""
        ^.*?
        Episode\W*(?P<episode>\d{1,3})
        \W*[-–—]\W*
        (?P<title>.+?)
        $
        """,
        re.IGNORECASE | re.VERBOSE,
    ),

    # Ep 03 - The Naked Now
    re.compile(
        r"""
        ^.*?
        Ep\W*(?P<episode>\d{1,3})
        \W*[-–—]\W*
        (?P<title>.+?)
        $
        """,
        re.IGNORECASE | re.VERBOSE,
    ),
]


@dataclass
class RenamePlan:
    old_path: Path
    new_path: Path
    series_name: str
    season: int
    episode: int
    title: str


def clean_title(title: str) -> str:
    """Normalize title text and remove invalid Windows filename characters."""
    title = title.strip()
    title = re.sub(r'[<>:"/\\|?*]', "", title)
    title = re.sub(r"\s+", " ", title)
    title = title.rstrip(" .")
    return title


def infer_season_from_folder(directory: Path) -> int | None:
    for candidate in [directory.name, directory.parent.name]:
        match = re.search(r"Season\W*(\d{1,2})", candidate, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def parse_filename(file_path: Path, default_season: int | None = None) -> tuple[int, int, str] | None:
    """Return (season, episode, title) if matched, else None."""
    stem = file_path.stem

    for pattern in PATTERNS:
        match = pattern.search(stem)
        if not match:
            continue

        groups = match.groupdict()
        season_text = groups.get("season")
        episode_text = groups.get("episode")
        title = groups.get("title")

        season = int(season_text) if season_text else default_season
        episode = int(episode_text) if episode_text else None

        if season is None or episode is None or not title:
            continue

        return season, episode, clean_title(title)

    return None


def extract_series_name_from_filename(file_path: Path) -> str | None:
    stem = file_path.stem

    patterns = [
        r"^(?P<series>.+?)\s+Season\W*\d{1,2}\W+Episode\W*\d{1,3}\W*[-–—]",
        r"^(?P<series>.+?)\s+S\d{1,2}E\d{1,3}\W*[-–—]",
        r"^(?P<series>.+?)\s+\d{1,2}x\d{1,3}\W*[-–—]",
    ]

    for p in patterns:
        match = re.search(p, stem, re.IGNORECASE)
        if match:
            series = match.group("series").strip()
            series = re.sub(r"\s+", " ", series)
            return series

    return None


def build_new_filename(series_name: str, season: int, episode: int, title: str, suffix: str) -> str:
    return f"{series_name} - S{season:02d} - E{episode:02d} - {title}{suffix.lower()}"


def get_files(directory: Path, recursive: bool = False, video_only: bool = True) -> list[Path]:
    if recursive:
        files = [p for p in directory.rglob("*") if p.is_file()]
    else:
        files = [p for p in directory.iterdir() if p.is_file()]

    if video_only:
        files = [p for p in files if p.suffix.lower() in VIDEO_EXTENSIONS]

    return sorted(files, key=lambda p: p.name.lower())


def create_rename_plan(
    directory: Path,
    series_name: str | None = None,
    season_override: int | None = None,
    recursive: bool = False,
    video_only: bool = True,
) -> tuple[list[RenamePlan], list[Path]]:
    plans: list[RenamePlan] = []
    skipped: list[Path] = []

    inferred_season = season_override if season_override is not None else infer_season_from_folder(directory)

    for file_path in get_files(directory, recursive=recursive, video_only=video_only):
        parsed = parse_filename(file_path, default_season=inferred_season)

        if not parsed:
            skipped.append(file_path)
            continue

        season, episode, title = parsed

        resolved_series = series_name or extract_series_name_from_filename(file_path) or "Unknown Series"
        resolved_series = re.sub(r"\s+", " ", resolved_series).strip()

        new_name = build_new_filename(
            series_name=resolved_series,
            season=season,
            episode=episode,
            title=title,
            suffix=file_path.suffix,
        )
        new_path = file_path.with_name(new_name)

        if file_path.name == new_name:
            continue

        plans.append(
            RenamePlan(
                old_path=file_path,
                new_path=new_path,
                series_name=resolved_series,
                season=season,
                episode=episode,
                title=title,
            )
        )

    return plans, skipped


def detect_conflicts(plans: list[RenamePlan]) -> list[str]:
    errors: list[str] = []
    target_map: dict[str, Path] = {}

    for plan in plans:
        target_key = str(plan.new_path).lower()

        if target_key in target_map:
            errors.append(
                f"Duplicate target: '{plan.new_path.name}' "
                f"(from '{target_map[target_key].name}' and '{plan.old_path.name}')"
            )
        else:
            target_map[target_key] = plan.old_path

        if plan.new_path.exists() and plan.old_path.resolve() != plan.new_path.resolve():
            errors.append(f"Target already exists: '{plan.new_path.name}'")

    return errors


def write_log(plans: list[RenamePlan], log_path: Path) -> None:
    with log_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["old_path", "new_path", "series_name", "season", "episode", "title", "timestamp"]
        )
        timestamp = datetime.now().isoformat(timespec="seconds")

        for plan in plans:
            writer.writerow(
                [
                    str(plan.old_path),
                    str(plan.new_path),
                    plan.series_name,
                    plan.season,
                    plan.episode,
                    plan.title,
                    timestamp,
                ]
            )


def confirm_action(prompt: str) -> bool:
    response = input(f"{prompt} [y/N]: ").strip().lower()
    return response in {"y", "yes"}


def apply_renames(plans: list[RenamePlan]) -> tuple[int, int]:
    renamed = 0
    failed = 0

    for plan in plans:
        try:
            plan.old_path.rename(plan.new_path)
            print(f"Renamed: {plan.old_path.name} -> {plan.new_path.name}")
            renamed += 1
        except Exception as e:
            print(f"Failed: {plan.old_path.name} -> {plan.new_path.name} | {e}")
            failed += 1

    return renamed, failed


def rollback_from_log(log_path: Path, dry_run: bool = True) -> tuple[int, int]:
    if not log_path.exists():
        print(f"Log file not found: {log_path}")
        return 0, 0

    with log_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reversed_rows = list(reader)

    reversed_rows.reverse()

    restored = 0
    failed = 0

    for row in reversed_rows:
        old_path = Path(row["old_path"])
        new_path = Path(row["new_path"])

        print(f"Rollback: {new_path.name} -> {old_path.name}")

        if dry_run:
            continue

        try:
            if not new_path.exists():
                print(f"  Skipped: current file missing: {new_path}")
                failed += 1
                continue

            if old_path.exists():
                print(f"  Skipped: original target already exists: {old_path}")
                failed += 1
                continue

            new_path.rename(old_path)
            restored += 1
        except Exception as e:
            print(f"  Failed: {e}")
            failed += 1

    return restored, failed


def print_preview(
    plans: list[RenamePlan],
    skipped: list[Path],
    conflicts: list[str],
    max_preview: int | None = None,
) -> None:
    print("\nPlanned renames:\n")

    preview_items = plans[:max_preview] if max_preview else plans

    if not preview_items:
        print("No files need renaming.")
    else:
        for plan in preview_items:
            print(f"{plan.old_path.name}")
            print(f"  -> {plan.new_path.name}")

    if max_preview and len(plans) > max_preview:
        print(f"\n... plus {len(plans) - max_preview} more planned rename(s).")

    if skipped:
        print("\nSkipped files:")
        for file_path in skipped:
            print(f" - {file_path.name}")

    if conflicts:
        print("\nConflicts detected:")
        for c in conflicts:
            print(f" - {c}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch rename TV episode files into a standard format."
    )

    parser.add_argument("directory", type=Path, help="Directory containing files to rename")
    parser.add_argument("--series", type=str, help="Override series name")
    parser.add_argument("--season", type=int, help="Override season number")
    parser.add_argument("--recursive", action="store_true", help="Search subfolders too")
    parser.add_argument("--include-non-video", action="store_true", help="Include all files, not just video files")
    parser.add_argument("--apply", action="store_true", help="Actually rename files")
    parser.add_argument("--preview-limit", type=int, default=None, help="Limit preview output")
    parser.add_argument("--log", type=Path, help="CSV log path")
    parser.add_argument("--rollback", type=Path, help="Rollback using a previous CSV log")
    parser.add_argument("--rollback-apply", action="store_true", help="Actually perform rollback")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.rollback:
        dry_run = not args.rollback_apply
        restored, failed = rollback_from_log(args.rollback, dry_run=dry_run)

        if dry_run:
            print("\nRollback preview complete. No files were changed.")
            return 0

        if not confirm_action("Proceed with rollback?"):
            print("Rollback cancelled.")
            return 0

        restored, failed = rollback_from_log(args.rollback, dry_run=False)
        print(f"\nRollback complete. Restored: {restored}, Failed: {failed}")
        return 0

    directory = args.directory

    if not directory.exists() or not directory.is_dir():
        print(f"Invalid directory: {directory}")
        return 1

    plans, skipped = create_rename_plan(
        directory=directory,
        series_name=args.series,
        season_override=args.season,
        recursive=args.recursive,
        video_only=not args.include_non_video,
    )

    conflicts = detect_conflicts(plans)
    print_preview(plans, skipped, conflicts, max_preview=args.preview_limit)

    if conflicts:
        print("\nFix conflicts before applying renames.")
        return 1

    if not plans:
        return 0

    log_path = args.log
    if log_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = directory / f"rename_log_{timestamp}.csv"

    write_log(plans, log_path)
    print(f"\nLog written to: {log_path}")

    if not args.apply:
        print("\nPreview only. No files were renamed.")
        print("Run again with --apply to perform the renames.")
        return 0

    if not confirm_action(f"Proceed with {len(plans)} rename(s)?"):
        print("Rename cancelled.")
        return 0

    renamed, failed = apply_renames(plans)
    print(f"\nRename complete. Renamed: {renamed}, Failed: {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())