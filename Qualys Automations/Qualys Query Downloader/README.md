# Qualys_Vuln_Asset_Query_API

This Python script is designed to interact with the Qualys Vulnerability Management API. It is specifically tailored to query for vulnerabilities and assets.

## Requirements

- Python 3.6+
- Alteryx Designer

## Installation

1. Clone or download this repository to your local machine.
2. Install the required Python packages by running `pip install -r requirements.txt` in your terminal.

## Usage

This script is intended to be run within an Alteryx workflow. To use it:

1. Open Alteryx Designer.
2. Drag and drop the Run Command tool onto the canvas.
3. In the Command section, navigate to the location of the Python script.
4. In the Write Source section, select the input data that will be passed to the script.
5. In the Read Results section, select where the output data should be written.
6. Connect the Run Command tool to the rest of your workflow as needed.

## Notes

- Ensure that your Qualys API credentials are correctly set in the script.
- The script queries for vulnerabilities and assets. Modify the script as needed to query for different data.
- The script is designed to handle API rate limiting by pausing and retrying when necessary.

## Running Qualys_Vuln_Asset_Query_API.py Outside of Alteryx

Follow these steps to run the script outside of Alteryx:

1. **Environment Setup**: Ensure that Python is installed on your machine. If not, download and install it from the [official Python website](https://www.python.org/downloads/). Also, install necessary Python packages using pip. The packages might include requests, pandas, etc. depending on the script.
2. **Script Modification**: Remove or comment out any Alteryx specific code. This might include any import statements like `import AlteryxPythonSDK as Sdk` or any function that uses Alteryx SDK.
3. **Input and Output**: If the script reads or writes data from/to an Alteryx workflow, you'll need to modify this to read/write from a different source/destination. This could be a local file, a database, an API, etc.
4. **Running the Script**: Open a terminal, navigate to the directory containing the script, and run `python Qualys_Vuln_Asset_Query_API.py`.