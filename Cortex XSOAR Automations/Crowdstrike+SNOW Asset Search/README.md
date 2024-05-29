# QueryHelper Script

This repository contains a Python script that queries data from CrowdStrike Falcon and ServiceNow CMDB. The script is designed to fetch and process data based on given IP addresses, generate CSV reports, and output the results in a structured format.

## Table of Contents

- [QueryHelper Script](#queryhelper-script)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Environment Variables](#environment-variables)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Script Details](#script-details)
    - [Classes](#classes)
    - [Methods](#methods)
  - [License](#license)

## Overview

The script is structured to use classes two main classes: `QueryHelper` and `MainApp`. The `QueryHelper` class handles the querying logic, while the `MainApp` class orchestrates the overall process, including data processing and result generation.

## Features

- Queries CrowdStrike Falcon for device data based on IP addresses.
- Queries ServiceNow CMDB for configuration item data based on IP addresses.
- Generates CSV reports from the query results.
- Outputs results in a structured format using the Demisto SDK.

## Requirements

- Python 3.6+
- `demisto-sdk` package
- `xlsxwriter` package

## Environment Variables

The script uses the following environment variables:

- `SERVICENOW_INSTANCE`: The name of the ServiceNow instance to use for querying CMDB records. This should be set to the appropriate instance name.

## Installation

1. Clone this repository to your local machine:

   ```sh
   git clone https://github.com/polishchukv/query-helper.git
   cd query-helper
   ```

2. Install the required Python packages:

    ```sh
    pip install demisto-sdk xlsxwriter
    ```

3. Set necessary env variables:

    ```sh
    export SERVICENOW_INSTANCE='your_servicenow_instance'
    ```

## Usage

To use the script, provide the input data (IP addresses) through Demisto arguments and execute the script. The script will perform necessary queries, process the results, generate CSV reports, and output results.

1. Ensure that the environmental variable `SERVICENOW_INSTANCE` is set correctly

2. Run the script:

    ```sh
    python query_helper.py
    ```

## Script Details

### Classes

#### QueryHelper
A helper class to handle CrowdStrike and ServiceNow queries.

**Attributes**:
- `FIELD_MAPPING`: A dictionary mapping fields to their descriptions.
- `ip_pattern`: A regex pattern to match IP addresses.
- `checked_items`: A set to track queried items.
- `crowdstrike_results`: A list to store CrowdStrike query results.
- `crowdstrike_not_found`: A list to store items not found in CrowdStrike.
- `servicenow_results`: A list to store ServiceNow query results.
- `servicenow_not_found`: A list to store items not found in ServiceNow.
- `servicenow_instance`: The ServiceNow instance name, read from the environment variable.

#### MainApp
The main application class to orchestrate the data processing and querying.

**Attributes**:
- `helper`: An instance of the `QueryHelper` class.

### Methods

- `QueryHelper.cs_query_helper(filter_key, filter_value)`: Queries CrowdStrike Falcon for devices based on the filter key and value.
- `QueryHelper.snow_query_helper(filter_key, filter_value)`: Queries ServiceNow CMDB for records based on the filter key and value.
- `QueryHelper.query_crowdstrike(data_list)`: Performs CrowdStrike queries for each item in the data list.
- `QueryHelper.query_servicenow(data_list)`: Performs ServiceNow queries for each item in the data list.
- `QueryHelper.generate_csv(filename, data)`: Generates a CSV file from the given data and returns it as a string.
- `MainApp.main()`: The main method to execute the query and processing logic.
