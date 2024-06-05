# TableManager Script

## Overview

This script provides functionality to manage SQL table operations such as creating and dropping tables. It is designed to be modular, using a class-based structure to ensure maintainability and extensibility. The script includes argument validation, dynamic column typing, and robust error handling to prevent SQL command execution.

## Features

- **Validation of Arguments**: Ensures that required arguments, such as table name and headers, are provided for the appropriate SQL commands.
- **Dynamic Column Types**: Allows users to specify different data types for columns dynamically.
- **Logging**: Integrated logging for tracing the execution of SQL queries.
- **Error Handling**: Robust error handling to catch and log exceptions, providing meaningful error messages.
- **Configuration Management**: Prepared for easy configuration of database connection settings and other execution parameters.
- **Support for Multiple SQL Commands**: Currently supports `CREATE TABLE` and `DROP TABLE` commands, with the possibility to extend for more SQL operations.

## Usage

### Prerequisites

Ensure you have the following dependencies installed:
- Python 3.x
- Any necessary external libraries (e.g., `demisto-sdk`, if applicable)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/TableManagerScript.git
    ```

2. Navigate to the project directory:
    ```sh
    cd TableManagerScript
    ```

### Execution

1. **Arguments**:
    - `tableName` (required): The name of the table to create or drop.
    - `headers` (required for CREATE): A comma-separated list of column definitions (e.g., `id INT, name VARCHAR(255)`).
    - `command` (optional): The SQL command to execute (`CREATE` or `DROP`). Defaults to `CREATE`.

2. **Example Arguments**:
    ```json
    {
        "tableName": "employees",
        "headers": "id INT, name VARCHAR(255), role VARCHAR(100)",
        "command": "CREATE"
    }
    ```

### Explanation of Code

- **TableManager Class**: Encapsulates all functionality for table management. This ensures modularity and makes the codebase easier to maintain.
- **Argument Validation**: The `validate_arguments` method checks if essential parameters are present.
- **Header Parsing**: The `parse_headers` method splits and processes headers to include their data types. Defaults to `varchar(255)` if not specified.
- **SQL Query Generation**: Methods `generate_create_query` and `generate_drop_query` build the respective SQL commands.
- **Execution and Error Handling**: Executes the generated SQL query and handles any exceptions, logging relevant error messages.