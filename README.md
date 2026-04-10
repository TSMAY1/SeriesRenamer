# TV Batch Renamer

A Python script for batch renaming TV episode files into a clean, consistent format.

It is designed to be safer and more flexible than a one-off renaming script, with features like:

- preview mode by default
- interactive confirmation before renaming
- CSV logging of all planned changes
- rollback support using a previous log
- support for multiple filename styles
- conflict detection before changes are made

## Output Format

The script renames files into this format:

```text
Series Name - S01 - E01 - Episode Title.ext
```

Example:

```text
Star Trek The Next Generation - S01 - E01 - Encounter at Farpoint.avi
```

## Features

- Renames batches of episode files in a folder
- Works with common video formats:
    - .avi
    - .mkv
    - .mp4
    - .mov
    - .wmv
    - .m4v
- Supports several naming patterns, including:
    - Season 1 Episode 3 - Title
    - S1E03 - Title
    - 1x03 - Title
    - Episode 03 - Title
    - Ep 03 - Title
- Can infer the season number from the folder name
- Can recursively search subfolders
- Creates a CSV log before renaming
- Can roll back renames from a saved log
- Checks for filename conflicts before making changes
- Asks for confirmation before applying renames

## Requirements

- Python 3.10 or newer recommended
- No external libraries required

This script only uses Python standard library modules:

- argparse
- csv
- dataclasses
- datetime
- pathlib
- re
- sys

## Installation

1. Save the script as:

```text
tv_batch_renamer.py
```

2. Make sure Python is installed on your system.

To check:

```bash
python --version
```

or on some systems:

```bash
py --version
```

## Basic Usage

### Preview planned renames

By default, the script previews changes only and does not rename anything.

```bash
python tv_batch_renamer.py "D:\Living Room TV\Star Trek The Next Generation - Seasons 1-7\Season 1" --series "Star Trek The Next Generation"
```

This will:

- scan the folder
- show planned renames
- list skipped files
- detect conflicts
- create a CSV log
- stop without changing files

### Apply renames

To actually rename the files, add `--apply`:

```bash
python tv_batch_renamer.py "D:\Living Room TV\Star Trek The Next Generation - Seasons 1-7\Season 1" --series "Star Trek The Next Generation" --apply
```

The script will still ask for confirmation before doing anything:

```text
Proceed with 24 rename(s)? [y/N]:
```

Type:

- y or yes to continue
- anything else to cancel

## Command-Line Arguments

### Required argument

`directory`

The folder containing the files you want to rename.

Example:

```bash
python tv_batch_renamer.py "D:\Shows\Season 1"
```

### Optional arguments

`--series`

Overrides the series name used in the new filenames.

Example:

```bash
--series "Star Trek The Next Generation"
```

If omitted, the script will try to extract the series name from the existing filename.
If it cannot determine one, it will use:

```text
Unknown Series
```

---

`--season`

Forces a season number.

This is useful when filenames only include episode numbers, such as:

```text
Episode 03 - The Naked Now.avi
```

Example:

```bash
python tv_batch_renamer.py "D:\Shows\Season 1" --series "Star Trek The Next Generation" --season 1
```

---

`--recursive`

Searches subfolders as well as the main folder.

Example:

```bash
python tv_batch_renamer.py "D:\Shows" --series "Star Trek The Next Generation" --recursive
```

`--include-non-video`

Includes all files instead of filtering to common video file extensions only.

By default, only supported video files are processed.

Example:

```bash
python tv_batch_renamer.py "D:\Shows" --include-non-video
```

Use this carefully.

---

`--apply`

Actually performs the renames.

Without this flag, the script only previews changes.

Example:

```bash
python tv_batch_renamer.py "D:\Shows\Season 1" --series "My Show" --apply
```

---

`--preview-limit`

Limits how many planned renames are shown in the console preview.

Example:

```bash
python tv_batch_renamer.py "D:\Shows" --series "My Show" --preview-limit 10
```

This shows the first 10 planned renames and then summarizes the rest.

---

`--log`

Specifies a custom path for the CSV log file.

Example:

```bash
python tv_batch_renamer.py "D:\Shows\Season 1" --series "My Show" --log "D:\Logs\rename_log.csv"
```

If omitted, the script creates a timestamped log automatically in the target directory.

Example auto-generated filename:

```text
rename_log_20260409_221530.csv
```

---

`--rollback`

Uses a previously generated CSV log to reverse renames.

Example:

```bash
python tv_batch_renamer.py "D:\anything" --rollback "D:\Logs\rename_log.csv"
```

This runs in preview mode unless `--rollback-apply` is also included.

---

`--rollback-apply`

Actually performs the rollback instead of previewing it.

Example:

```bash
python tv_batch_renamer.py "D:\anything" --rollback "D:\Logs\rename_log.csv" --rollback-apply
```

The script will ask for confirmation before restoring filenames.

## Examples

### Example 1: Preview renames for one season

```bash
python tv_batch_renamer.py "D:\TV\Season 1" --series "Star Trek The Next Generation"
```
### Example 2: Apply renames for one season

```bash
python tv_batch_renamer.py "D:\TV\Season 1" --series "Star Trek The Next Generation" --apply
```

### Example 3: Force the season number

```bash
python tv_batch_renamer.py "D:\TV\Misc Episodes" --series "Star Trek The Next Generation" --season 1 --apply
```

### Example 4: Scan folders recursively

```bash
python tv_batch_renamer.py "D:\TV" --series "Star Trek The Next Generation" --recursive
```

### Example 5: Save the log in a custom folder

```bash
python tv_batch_renamer.py "D:\TV\Season 1" --series "Star Trek The Next Generation" --log "D:\RenameLogs\tng_s1.csv"
```

### Example 6: Preview a rollback

```bash
python tv_batch_renamer.py "D:\unused" --rollback "D:\RenameLogs\tng_s1.csv"
```

### Example 7: Apply a rollback

```bash
python tv_batch_renamer.py "D:\unused" --rollback "D:\RenameLogs\tng_s1.csv" --rollback-apply
```

## Supported Filename Patterns

The script currently recognizes these common patterns:

```text
Star Trek The Next Generation Season 1 Episode 3 - The Naked Now.avi
Star Trek The Next Generation S1E03 - The Naked Now.mkv
Star Trek The Next Generation 1x03 - The Naked Now.mp4
Episode 03 - The Naked Now.avi
Ep 03 - The Naked Now.avi
```

These can be renamed into:

```text
Star Trek The Next Generation - S01 - E03 - The Naked Now.avi
```

## How Season Detection Works

The script determines the season number in this order:

1. --season argument, if provided
2. season extracted from the filename
3. season inferred from the folder name, such as:
    - Season 1
    - Season_02
4. if no season can be determined, the file is skipped

## Log Files

Before renaming, the script writes a CSV log containing:

- original file path
- new file path
- series name
- season number
- episode number
- episode title
- timestamp

This log is used for rollback later.

Example CSV columns:

```text
old_path,new_path,series_name,season,episode,title,timestamp
```

Keep these log files if you may want to undo a rename later.

## Rollback Notes

Rollback reverses filenames using a previous CSV log.

It works best when:

- the renamed files are still in the same location
- the renamed files have not been manually renamed again
- the original filenames do not already exist

The script will skip rollback entries if:

- the current renamed file cannot be found
- the original target name already exists
- another filesystem error occurs

Always preview rollback before applying it.

## Skipped Files

Files are skipped when:

- the filename does not match any supported pattern
- the season number cannot be determined
- the file is already in the correct format

Skipped files are listed in the console output so you can review them.

## Conflict Detection

Before renaming, the script checks for problems such as:

- two files trying to rename to the same target
- a target filename already existing in the folder

If conflicts are found, the script will stop before applying any changes.

## Safety Tips

Before applying renames:

1. run a preview first
2. review the planned changes carefully
3. keep the CSV log
4. test on a small folder before using it on a large library

This script is meant to be cautious, but it is still smart to keep backups of important files.

## Troubleshooting

### Nothing is being renamed

Possible reasons:

- the filenames do not match any supported pattern
- the files are already in the target format
- the folder path is wrong
- only non-video files are present and --include-non-video was not used

---

### Files are being skipped

This usually means the current filename format does not match one of the built-in patterns.

Check whether your filenames look significantly different from the supported examples.

---

### The script says a target already exists

That means renaming a file would overwrite an existing file, or two planned renames would create the same filename.

Review the conflict list before trying again.

---

### Rollback is skipping files

This usually means:

- the renamed file no longer exists
- the file was moved
- the file was renamed manually after the script ran
- the original filename already exists again

## Future Improvement Ideas

Possible enhancements you may want to add later:

- support for dotted filenames such as:
    - Star.Trek.TNG.S01E03.The.Naked.Now
- interactive selection of the series name
- custom naming templates
- support for anime-style episode numbering
- GUI version for non-command-line use
- automatic metadata lookup from online databases

## License / Personal Use

Feel free to modify this script for your own media library and naming conventions.

## Quick Start

Preview:

```bash
python tv_batch_renamer.py "D:\TV\Season 1" --series "Star Trek The Next Generation"
```

Apply:

```bash
python tv_batch_renamer.py "D:\TV\Season 1" --series "Star Trek The Next Generation" --apply
```

Rollback preview:

```bash
python tv_batch_renamer.py "D:\unused" --rollback "D:\TV\Season 1\rename_log_20260409_221530.csv"
```

Rollback apply:

```bash
python tv_batch_renamer.py "D:\unused" --rollback "D:\TV\Season 1\rename_log_20260409_221530.csv" --rollback-apply
```
