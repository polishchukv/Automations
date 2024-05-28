# Qualys Reports Google Apps Script

This script is used to interact with the Qualys API to authenticate, list, download, and format reports. It is written in JavaScript and is intended to be used with Google Apps Script.

## Features

- **Authentication**: The script can start and end sessions with the Qualys API using the `startSession` and `killSession` functions respectively.
- **Report Listing**: The `listReport` function fetches a list of available reports from the Qualys API.
- **Report Downloading**: The `downloadReport` function downloads a specific report based on its ID.
- **Report Formatting**: The `formatNewSheet` function formats the downloaded report for better readability.
- **Updating Checkpoint Columns**: The `updateCheckpointColumnsChild` function updates checkpoint columns in the spreadsheet.

## Usage

1. Replace the `username` and `password` variables with your Qualys API credentials.
2. Replace the `PLACEHOLDER URL` in the `spreadsheet` variable with the URL of your Google Spreadsheet.
3. Replace the `REPORT NAME HERE` in the `listReport` function with the name of the report you want to download.
4. Call the `main` function to run the entire script.

## Functions

- `startSession()`: Starts a session with the Qualys API.
- `killSession(sessionID)`: Ends a session with the Qualys API.
- `listReport(sessionID)`: Lists all available reports from the Qualys API.
- `downloadReport(sessionID, targetReport)`: Downloads a specific report from the Qualys API.
- `updateCheckpointColumnsChild(sheetName, updateText)`: Updates checkpoint columns in the spreadsheet.
- `formatNewSheet(updateText)`: Formats the downloaded report for better readability.
- `main()`: Runs the entire script.

## Note

This script is intended to be used with Google Apps Script. Make sure to enable the necessary APIs and services in your Google Cloud Project to run this script successfully.