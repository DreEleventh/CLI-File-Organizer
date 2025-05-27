#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File organizer CLI application - Automatically organize files

This script organizes files into specific folders based on file type. Moving files from a source directory
to a destination directory.

Author: Andre McKenzie
Version: 1.0
"""

import argparse
import os
import shutil
from pathlib import Path

FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".docx", ".txt", ".rtf", ".odt", ".pages"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
    "Archives": [".zip", ".tar.gz", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c"],
    "Spreadsheets": [".xlsx", ".xls", ".csv", ".ods"],
    "Presentations": [".pptx", ".ppt", ".odp"],
}

def organize(src, dest, dry_run):
    src_path = Path(src)
    dest_path = Path(dest)

    if not src_path.exists():
        raise FileNotFoundError(f"Source directory '{src}' does not exist.")
    if not src_path.is_dir():
        raise NotADirectoryError(f"Source '{src}' is not a directory.")

    for file in src_path.iterdir():
        if file.is_file():
            ext = file.suffix.lower()
            category = next((cat for cat, exts in FILE_TYPES.items() if ext in exts), "Other")
            target_dir = dest_path / category
            target_file = target_dir / file.name

            if dry_run:
                print(f"[Dry Run] Would move {file} -> {target_file}")
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), str(target_file))
                print(f"Move {file.name} to {category}")

def main():
    parser = argparse.ArgumentParser(description="Organize files in a directory by type.")
    parser.add_argument("source", help="Source directory")
    parser.add_argument("--dest", help="Destination directory", default="organized")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without moving files")

    args = parser.parse_args()
    organize(args.source, args.dest, args.dry_run)


if __name__ == '__main__':
    main()


