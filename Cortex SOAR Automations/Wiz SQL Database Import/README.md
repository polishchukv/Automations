# Wiz SQL Import

This Python script is designed to import data from a file into a SQL table. It is part of the `demisto_sdk` package and is used to interact with the Demisto platform.

## Features

- **Debug Logging**: The script maintains a debug log, which is useful for tracking the execution flow and troubleshooting issues.

- **Argument Fetching**: It fetches arguments such as the database table name and the file location from the Demisto platform.

- **Table Management**: The script can drop an existing table in the database and create a new one.

- **File Processing**: It processes the file to be imported, handling both CSV and XLSX formats. For XLSX files, it converts them to CSV before processing.

- **Data Import**: The script reads the data from the file, processes it, and then imports it into the SQL table.

- **Report Processing**: If a 'wizReport' argument is provided, the script fetches the report, processes its content, and saves it as a file.

- **Table Building**: It builds a new SQL table with the processed data.

- **Record Counting**: After the import, the script counts the total number of records in the table.

- **Result Output**: Finally, it outputs the results, including the total number of records imported and the debug log.

## Usage

To use this script, create an instance of the `DataImporter` class and call the `execute` method. This method orchestrates the entire process, from fetching arguments to outputting results.

```python
dataImporter = DataImporter()
dataImporter.execute()