# Script Overview

This script processes Excel files from various directories. It collects all matching folders, validates and un-hides data from Excel sheets, and then unions all data into a single output.

## Functionality

### Key Features

- **File Locking/Unlocking**: The script locks files using `msvcrt` to prevent concurrent modification.
- **Data Extraction**: Extracts data from Excel sheets, un-hiding any hidden rows/columns.
- **Data Union**: Combines data from multiple sources into a unified DataFrame.
- **Temporary File Handling**: Creates temporary local copies of Excel files if read/write access is restricted.
- **Integration with Alteryx**: The script outputs the final unified DataFrame using the `Alteryx.write` function.

### Important Functions

#### `lock_file(file_path)`
Locks the specified file to prevent concurrent access.

#### `unlock_file(fd)`
Unlocks the previously locked file.

#### `get_matching_folders(root_dir, match_format)`
Searches for folders within a specified root directory that match a given format and returns them as a DataFrame.

#### `validate_excel_file(file_path, sheet_name)`
Validates and reads an Excel sheet. Returns an empty DataFrame if the sheet is not found.

#### `unhide_hidden(file_path)`
Un-hides hidden rows and columns in the specified Excel file.

#### `ensure_read_access(file_path)`
Checks if the file has read access. If not, creates a temporary copy.

#### `ensure_write_access(file_path)`
Checks if the file has write access. If not, creates a temporary copy.

#### `union_all_excel_files(df)`
Processes Excel files from given paths, unlocking, un-hiding, and validating them, and unions all data into a single DataFrame.

#### `copy_files_to_local(df)`
Copies Excel files from remote locations to a local directory.

### Running the Script

1. The script identifies the current date and determines the matching folder format (`YYYY-MM`).
2. The script identifies folders within the directories for Tech EOL and Streaming EOL using the matching format.
3. Local copies are made of the matching files.
4. Data from all matching files is read and combined into a single DataFrame.
5. The final DataFrame is written to an output destination using `Alteryx.write`.

### Configuration and Variables

- **Directories**: Defined using the `os.path.join` method with `USERPROFILE` and organization-specific placeholders.
  - `root_dir_techeol`: `"{ORGANIZATION_PATH_TECH_EOL}"`
  - `root_dir_streamingeol`: `"{ORGANIZATION_PATH_STREAMING_EOL}"`
  - `local_dir`: `"{LOCAL_COPY_DIR}"`

### Dependencies

- `ctypes`
- `os`
- `shutil`
- `pandas`
- `openpyxl`
- `glob`
- `tempfile`
- `msvcrt`
- `datetime`

### Notes

- The script is meant to run as part of an Alteryx workflow.
- The script is designed to run on Windows, utilizing `msvcrt` for file locking.
- Replace placeholder values (e.g., `"{ORGANIZATION_PATH_TECH_EOL}"`) with actual paths before running in production.