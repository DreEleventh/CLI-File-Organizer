#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced File Organizer - Automatically organize files by type with advanced features

This script organizes files into categorized folders based on their extensions,
with support for dry-run mode, recursive processing, custom configurations,
logging, and undo functionality.

Author: Andre McKenzie
Version: 2.0
"""

import argparse
import shutil
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


# Default file type mappings
DEFAULT_FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"],
    "Documents": [".pdf", ".docx", ".txt", ".rtf", ".odt", ".pages", ".doc"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Archives": [".zip", ".tar.gz", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".php", ".rb"],
    "Spreadsheets": [".xlsx", ".xls", ".csv", ".ods", ".numbers"],
    "Presentations": [".pptx", ".ppt", ".odp", ".key"],
    "Executables": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".app"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
}


class FileOrganizer:
    """Enhanced file organizer with comprehensive features."""

    def __init__(self, file_type: Dict[str, List[str]] = None, log_level: str = "INFO"):
        """
        Initialize the FileOrganizer.

        Args:
            file_type: Custom file type mappings
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = None
        self.file_types = file_type or DEFAULT_FILE_TYPES.copy()
        self.operations_log = []
        self.setup_logging(log_level)

    def setup_logging(self, level: str):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self, config_file: str) -> bool:
        """
        Load file type configuration from JSON file.

        Args:
            config_file: Path to JSON configuration file

        Returns:
            True if config loaded successfully, False otherwise
        """

        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.file_types = json.load(f)
                self.logger.info(f"Loading configuration file {config_file}")
                return True
            else:
                self.logger.warning(f"Configuration file {config_file} not found")
                return False
        except (json.JSONDecoder, IOError) as e:
            self.logger.error(f"Error loading configuration: {e}")
            return False

    def get_category(self, file_extension: str) -> str:
        """
        Get the category for a given file extension.

        Args:
            file_extension: File extension (with dot)

        Returns:
            Category name or 'Other' if not found
        """

        ext_lower = file_extension.lower()
        for category, extensions in self.file_types.items():
            if ext_lower in [e.lower() for e in extensions]:
                return category
        return "Other"

    @staticmethod
    def get_unique_filename(target_path: Path) -> Path:
        """
        Generate a unique filename if the target already exists.

        Args:
            target_path: Original target path

        Returns:
            Unique path with counter if necessary
        """

        if not target_path.exists():
            return target_path

        counter = 1
        stem = target_path.stem
        suffix = target_path.suffix
        parent = target_path.parent

        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    def matches_pattern(self, filename: str, pattern: Optional[str]) -> bool:
        """
          Check if filename matches the given pattern.

          Args:
              filename: Name of the file
              pattern: Regex pattern to match

          Returns:
              True if matches or no pattern provided
        """

        if not pattern:
            return True
        try:
            return bool(re.search(pattern, filename, re.IGNORECASE))
        except re.error:
            self.logger.warning(f"Invalid regex pattern: {pattern}")
            return True

    @staticmethod
    def check_file_size(file_path: Path, min_size: Optional[int], max_size: Optional[int]) -> bool:
        """
        Check if file size is within specified limits.

        Args:
            file_path: Path to the file
            min_size: Minimum size in bytes
            max_size: Maximum size in bytes

        Returns:
            True if file size is within limits
        """

        try:
            file_size = file_path.stat().st_size
            if min_size is not None and file_size < min_size:
                return False
            if max_size is not None and file_size > max_size:
                return False
            return True
        except OSError:
            return True # If we can't get size, assume it's okay

    def organize_files(self, source: str, destination: str, **options) -> Tuple[int, int]:
        """
        Organize files from source to destination directory.

        Args:
            source: Source directory path
            destination: Destination directory path
            **options: Organization options

        Returns:
            Tuple of (files_processed, files_moved)

        Raises:
            FileNotFoundError: If source directory doesn't exist
            NotADirectoryError: If source is not a directory
        """

        # Validate input
        src_path = Path(source).resolve()
        dest_path = Path(destination).resolve()

        if not src_path.exists():
            raise FileNotFoundError(f"Source directory '{source}' does not exist.")
        if not src_path.is_dir():
            raise NotADirectoryError(f"Source '{source}' is not a directory.")

        # Extract options
        dry_run = options.get('dry_run', False)
        recursive = options.get('recursive', False)
        copy_files = options.get('copy_files', False)
        pattern = options.get('pattern')
        exclude_pattern = options.get('exclude_pattern')
        min_size = options.get('min_size')
        max_size = options.get('max_size')

        # Get files to process
        if recursive:
            files = [f for f in src_path.rglob("*") if f.is_file()]
        else:
            files = [f for f in src_path.iterdir() if f.is_file()]

        self.logger.info(f"Found {len(files)} files to process")

        files_processed = 0
        files_moved = 0

        for file_path in files:
            try:
                # Apply filters
                if not self.matches_pattern(file_path.name, pattern):
                    continue
                if exclude_pattern and self.matches_pattern(file_path.name, exclude_pattern):
                    continue
                if not self.check_file_size(file_path, min_size, max_size):
                    continue

                files_processed += 1

                # Determine category and target
                file_extension = file_path.suffix
                file_category = self.get_category(file_extension)
                target_dir = dest_path / file_category
                target_file = self.get_unique_filename(target_dir / file_path.name)

                if dry_run:
                    action = "copy" if copy_files else "move"
                    print(f"[Dry Run] Would {action}: {file_path} -> {target_file}")
                    self.logger.debug(f"Dry run: {action} {file_path} to {target_file}")
                else:
                    # Create target directory
                    target_dir.mkdir(parents=True, exist_ok=True)

                    # Perform operation
                    if copy_files:
                        shutil.copy2(str(file_path), str(target_file))
                        operation = "copied"
                    else:
                        shutil.move(str(file_path), str(target_file))
                        operation = "moved"

                    # Log the operation
                    self.operations_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'operation': 'copy' if copy_files else 'move',
                        'source': str(file_path),
                        'destination': str(target_file),
                        'category': file_category
                    })

                    files_moved += 1
                    print(f"{operation.capitalize()} {file_path.name} to {file_category}/")
                    self.logger.info(f"{operation.capitalize()} {file_path} to {target_file}")

            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")

        return files_processed, files_moved


    def save_undo_log(self, log_file: str):
        """
        Save operations log for potential undo functionality.

        Args:
            log_file: Path to save the undo log
        """

        if not self.operations_log:
            return

        try:
            log_data = {
                'session_info':{
                    'timestamp': datetime.now().isoformat(),
                    'total_operations': len(self.operations_log)
                },
                'operations': self.operations_log
            }

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2)

            self.logger.info(f"Undo log saved to {log_file}")
            print(f"Undo log saved to {log_file}")

        except IOError as e:
            self.logger.error(f"Error saving undo log: {e}")


    def undo_operations(self, log_file: str, dry_run: bool = False) -> int:
        """
        Undo operations based on log file.

        Args:
            log_file: Path to the undo log file
            dry_run: If True, only show what would be undone

        Returns:
            Number of operations undone
        """
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)

            operations = log_data.get('operations', [])
            undone_count = 0

            # Process operations in reverse order
            for operation in reversed(operations):
                source = operation['source']
                destination = operation['destination']
                op_type = operation['operation']

                if dry_run:
                    print(f"[Dry Run] Would undo: {destination} -> {source}")
                else:
                    try:
                        if op_type == 'move' and Path(destination).exists():
                            # Move back to original location
                            Path(source).parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(destination, source)
                            print(f"Undone: {Path(destination).name} -> {Path(source).parent}")
                            undone_count += 1
                        elif op_type == 'copy' and Path(destination).exists():
                            # Remove the copied file
                            Path(destination).unlink()
                            print(f"Removed copy: {destination}")
                            undone_count += 1
                    except Exception as e:
                        self.logger.error(f"Error undoing operation: {e}")

            if not dry_run:
                self.logger.info(f"Undone {undone_count} operations")

            return undone_count

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Error reading undo log: {e}")
            return 0


def main():
    """Main function to handle command-line interface."""
    parser = argparse.ArgumentParser(
        description="Enhanced file organizer with advanced features.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
                %(prog)s /path/to/messy/folder --dest /path/to/organized
                %(prog)s /downloads --dry-run --recursive
                %(prog)s /documents --pattern "*.pdf" --copy
                %(prog)s --undo operations.json
        """
    )

    # Main arguments
    parser.add_argument("source", nargs='?', help="Source directory to organize")
    parser.add_argument("--dest", default="organized",
                        help="Destination directory (default: organized)")

    # Operation modes
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without moving files")
    parser.add_argument("--copy", action="store_true",
                        help="Copy files instead of moving them")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Process subdirectories recursively")

    # Filtering options
    parser.add_argument("--pattern", help="Only process files matching this regex pattern")
    parser.add_argument("--exclude", help="Exclude files matching this regex pattern")
    parser.add_argument("--min-size", type=int, help="Minimum file size in bytes")
    parser.add_argument("--max-size", type=int, help="Maximum file size in bytes")

    # Configuration and logging
    parser.add_argument("--config", help="Custom file type configuration (JSON file)")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        default="INFO", help="Set logging level")
    parser.add_argument("--save-log", help="Save undo log to specified file")

    # Undo functionality
    parser.add_argument("--undo", help="Undo operations from log file")

    args = parser.parse_args()

    # Handle undo mode
    if args.undo:
        organizer = FileOrganizer(log_level=args.log_level)
        count = organizer.undo_operations(args.undo, args.dry_run)
        print(f"{'Would undo' if args.dry_run else 'Undone'} {count} operations")
        return None

    # Validate source directory for organize mode
    if not args.source:
        parser.error("Source directory is required unless using --undo")

    # Initialize organizer
    organizer = FileOrganizer(log_level=args.log_level)

    # Load custom configuration if provided
    if args.config:
        organizer.load_config(args.config)

    try:
        # Organize files
        options = {
            'dry_run': args.dry_run,
            'recursive': args.recursive,
            'copy_files': args.copy,
            'pattern': args.pattern,
            'exclude_pattern': args.exclude,
            'min_size': args.min_size,
            'max_size': args.max_size,
        }

        files_processed, files_moved = organizer.organize_files(
            args.source, args.dest, **options
        )

        # Print summary
        if args.dry_run:
            print(f"\n[Dry Run] Found {files_processed} files that would be organized")
        else:
            print(f"\nOrganization complete!")
            print(f"Files processed: {files_processed}")
            print(f"Files {'copied' if args.copy else 'moved'}: {files_moved}")

            # Save undo log if requested
            if args.save_log and files_moved > 0:
                organizer.save_undo_log(args.save_log)

    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
