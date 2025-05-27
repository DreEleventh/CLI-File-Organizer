# Enhanced File Organizer

A powerful command-line utility for automatically organizing files into categorized folders based on their file extensions. This enhanced version includes advanced features like recursive processing, pattern matching, undo functionality, and custom configurations.

## Features

### Core Functionality
- **Automatic File Categorization**: Organizes files into folders by type (Images, Documents, Videos, Audio, etc.)
- **Duplicate Handling**: Automatically renames files if duplicates exist
- **Multiple Operation Modes**: Move or copy files with full control

### Advanced Features
- **Recursive Processing**: Organize files in subdirectories
- **Pattern Matching**: Include/exclude files using regex patterns
- **Size Filtering**: Filter files by minimum/maximum size
- **Dry Run Mode**: Preview operations before executing
- **Undo Functionality**: Reverse previous operations with detailed logs
- **Custom Configurations**: Define your own file type categories
- **Comprehensive Logging**: Detailed operation tracking with configurable levels

### File Categories (Default)
- **Images**: .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .tiff, .ico
- **Documents**: .pdf, .docx, .txt, .rtf, .odt, .pages, .doc
- **Videos**: .mp4, .mov, .avi, .mkv, .wmv, .flv, .webm, .m4v
- **Audio**: .mp3, .wav, .flac, .aac, .ogg, .wma, .m4a
- **Archives**: .zip, .tar.gz, .rar, .7z, .tar, .gz, .bz2
- **Code**: .py, .js, .html, .css, .java, .cpp, .c, .h, .php, .rb
- **Spreadsheets**: .xlsx, .xls, .csv, .ods, .numbers
- **Presentations**: .pptx, .ppt, .odp, .key
- **Executables**: .exe, .msi, .dmg, .pkg, .deb, .rpm, .app
- **Fonts**: .ttf, .otf, .woff, .woff2, .eot

## Installation

### Requirements
- Python 3.6 or higher

### Setup
1. Clone or download the repository:
   ```bash
   git clone https://github.com/DreEleventh/CLI-File-Organizer.git
   cd enhanced-file-organizer
   ```

2. Make the script executable (optional):
   ```bash
   chmod +x organizer.py
   ```

3. Create a symbolic link for global access (optional):
   ```bash
   ln -s /path/to/organizer.py /usr/local/bin/organize-files
   ```

## Usage

### Basic Syntax
```bash
   python3 organizer.py [source_directory] [options]
```

### Command Line Options

#### Required Arguments
- `source` - Source directory to organize (not required when using `--undo`)

#### Destination
- `--dest DIRECTORY` - Destination directory (default: "organized")

#### Operation Modes
- `--dry-run` - Show what would be done without moving files
- `--copy` - Copy files instead of moving them
- `-r, --recursive` - Process subdirectories recursively

#### Filtering Options
- `--pattern REGEX` - Only process files matching this regex pattern
- `--exclude REGEX` - Exclude files matching this regex pattern
- `--min-size BYTES` - Minimum file size in bytes
- `--max-size BYTES` - Maximum file size in bytes

#### Configuration
- `--config FILE` - Load custom file type configuration from JSON file
- `--log-level LEVEL` - Set logging level (DEBUG, INFO, WARNING, ERROR)

#### Undo Functionality
- `--save-log FILE` - Save operation log for undo capability
- `--undo FILE` - Undo operations from specified log file

## Examples

### Basic Organization
```bash
  # Organize files from Downloads folder
python3 organizer.py ~/Downloads --dest ~/OrganizedFiles

# Dry run to see what would happen
python3 organizer.py ~/Downloads --dry-run
```

### Advanced Usage
```bash
  # Recursively organize with custom destination
python3 organizer.py ~/Documents --dest ~/Sorted --recursive

# Copy only PDF files larger than 1MB
python3 organizer.py ~/Files --copy --pattern ".*\.pdf$" --min-size 1048576

# Exclude temporary files and organize
python3 organizer.py ~/Project --exclude ".*\.tmp$|.*\.temp$"

# Organize with undo log
python3 organizer.py ~/MessyFolder --save-log operation_log.json
```

### Undo Operations
```bash
  # Undo previous organization
python3 organizer.py --undo operation_log.json

# Dry run undo to see what would be reversed
python3 organizer.py --undo operation_log.json --dry-run
```

### Custom Configuration
Create a JSON file with your custom file types:

**custom_config.json**
```json
{
  "Work Documents": [".docx", ".xlsx", ".pptx"],
  "Development": [".py", ".js", ".html", ".css", ".json"],
  "Media Files": [".mp4", ".mp3", ".jpg", ".png"],
  "Design": [".psd", ".ai", ".sketch", ".fig"]
}
```

Use the custom configuration:
```bash
   python3 organizer.py ~/Files --config custom_config.json
```

## File Organization Structure

After running the organizer, your files will be organized like this:

```
organized/
├── Images/
│   ├── photo1.jpg
│   ├── screenshot.png
│   └── diagram.svg
├── Documents/
│   ├── report.pdf
│   ├── notes.txt
│   └── presentation.docx
├── Videos/
│   └── tutorial.mp4
├── Code/
│   ├── script.py
│   └── website.html
└── Other/
    └── unknown_file.xyz
```

## Logging

The application provides detailed logging with the following levels:

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about operations (default)
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations

Set the logging level using `--log-level`:
```bash
   python3 organizer.py ~/Files --log-level DEBUG
```

## Undo Functionality

The organizer can save detailed logs of all operations, allowing you to undo changes:

1. **Save operations**: Use `--save-log filename.json`
2. **Review log**: The JSON file contains all file movements with timestamps
3. **Undo operations**: Use `--undo filename.json` to reverse changes
4. **Preview undo**: Add `--dry-run` to see what would be undone

**Note**: Undo only works for move operations. Copied files will be deleted during undo.

## Error Handling

The application handles various error conditions gracefully:

- **Missing source directory**: Clear error message with suggestions
- **Permission issues**: Logs errors and continues with other files
- **Duplicate files**: Automatically renames with incremental counters
- **Invalid patterns**: Warns about invalid regex and continues
- **Disk space issues**: Proper error reporting

## Tips and Best Practices

1. **Always test first**: Use `--dry-run` before organizing important files
2. **Keep undo logs**: Save operation logs when organizing important directories
3. **Use filters wisely**: Combine pattern matching and size filters for precise control
4. **Custom configurations**: Create project-specific file type definitions
5. **Backup important data**: While the tool includes undo functionality, backups are always recommended

## Troubleshooting

### Common Issues

**"Command not found"**
- Ensure Python 3.6+ is installed
- Use `python3` instead of `python`
- Check file permissions if using symbolic links

**"Permission denied"**
- Ensure you have read/write permissions for source and destination
- Use `sudo` if organizing system directories (not recommended)

**"No files found"**
- Check if source directory exists and contains files
- Verify your pattern filters aren't too restrictive

**Undo not working**
- Ensure the log file exists and is valid JSON
- Check that destination files haven't been moved/deleted
- Verify permissions for the original source locations

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

To be determined.

## Version History

- **v2.0** - Enhanced version with advanced features
- **v1.0** - Basic file organization functionality

## Author

Andre McKenzie - amckenzie58@gmail.com

## Support

For issues, questions, or feature requests, please:
- Open an issue on GitHub
- Check existing documentation
- Review the troubleshooting section