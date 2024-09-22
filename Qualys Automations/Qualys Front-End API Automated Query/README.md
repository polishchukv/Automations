# Script Overview

This script interfaces with a third-party API to gather data about operating systems and their end-of-life (EOL) status. The script establishes a session with the API, retrieves relevant data, processes it, and writes the results to output using the `Alteryx.write` function.

## Functionality

### Key Features

- **Authentication**: Uses session-based authentication to connect to the API.
- **Data Retrieval**: Retrieves data related to EOL status of operating systems.
- **Data Processing**: The script processes JSON data into a flattened DataFrame for easier analysis.
- **Deduplication**: Removes duplicate records based on specific columns.
- **Integration with Alteryx**: Outputs the final processed data using `Alteryx.write`.

### Important Functions

#### `start_session(username, password, auth_url)`
- Establishes an authenticated session using provided credentials.
- Retries up to 15 times in case of server errors or connectivity issues.

#### `kill_session(session_id, auth_url)`
- Ends the session to release resources.

#### `assetview_query(session_id, offset, limit, sendResponse, assetview_url, query, query_param)`
- Queries the asset view API to retrieve data about operating systems.

#### `format(data)`
- Converts raw JSON data into a structured pandas DataFrame.

#### `deduplicate(df)`
- Removes duplicate records based on 'Asset ID' and 'Host ID'.

#### `main(username, password, auth_url, assetview_url)`
- Main function that orchestrates the entire process.

### How to Run the Script

1. Replace the placeholder values in the script (`"USERNAME"`, `"PASSWORD"`, `"{AUTH_URL}"`, `"{ASSETVIEW_URL}"`) with actual values before execution.
2. Ensure all necessary Python packages are installed:
    - `requests`
    - `pandas`
    - `json`
    - `datetime`
3. Make sure to fill out all of the queries and query paramaters, depending on what you're searching for.
4. Execute the script using Python: `python script.py`

### Configuration

- **Credentials**: The script requires a valid `username` and `password` for authentication.
- **API URLs**: The script uses `auth_url` and `assetview_url` to communicate with the API.

### Error Handling

- Implements retry logic for network requests with exponential backoff in case of server errors.
- Prints clear error messages for different HTTP status codes.

### Dependencies

- `requests`
- `pandas`
- `datetime`
- `Alteryx` (proprietary integration)

### Security Considerations

- Never hard-code sensitive information like credentials in the script. Use environment variables or configuration files with appropriate access controls.
- Replace placeholder values with actual credentials in a secure manner (like .env file).
