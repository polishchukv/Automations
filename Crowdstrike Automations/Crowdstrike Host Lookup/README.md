# CrowdStrike Host Lookup Script

This repository contains a Python script for querying and reporting host details from CrowdStrike. The script reads a list of hostnames or Fully Qualified Domain Names (FQDNs) from a file, queries the CrowdStrike API to retrieve host details, and saves the results in a CSV file.

## Features

- Reads a list of hostnames/FQDNs from an input file.
- Queries CrowdStrike API using OAuth2 for authentication.
- Retrieves host details including OS, manufacturer, MAC address, first seen/last seen timestamps, local IP, domain, platform, AD site, and containment status.
- Stores the results in a CSV file.

## Prerequisites

- Python 3.x
- `requests` library
- `csv` library

You can install the required `requests` library using pip:

```sh
pip install requests
```

## Setup

1. Clone the repository to your local machine:

    ```sh
    git clone https://github.com/polishchukv/crowdstrike-host-lookup.git
    cd crowdstrike-host-lookup
    ```

2. Set up environment variables for your CrowdStrike API credentials. You can do this by adding them to your shell profile (e.g., `.bashrc`, `.zshrc`), or by manually exporting them each time you run the script:

    ```sh
    export CS_CLIENT_ID="your_client_id"
    export CS_CLIENT_SECRET="your_client_secret"
    ```

## Usage

1. Prepare the input file with the list of hostnames/FQDNs. Each entry should be on a new line. Save it as `computers.txt` in a directory of your choice (e.g., `C:/temp/computers.txt`).

2. Ensure the output directory exists (e.g., `C:/temp`).

3. Run the script:

    ```sh
    python3 host_lookup.py
    ```

4. The results will be saved in `cs-host-lookup-results.csv` in the specified directory (e.g., `C:/temp`).

## Script Overview

The following is a high-level overview of the script components and functionality:

### `obtain_oauth_token`

This function retrieves a 30-minute Bearer token using OAuth2 authentication.

### `main`

This function:
- Reads the list of hostnames/FQDNs from `computers.txt`.
- Queries the CrowdStrike API to check if hosts exist and retrieves their details.
- Writes the host details to `cs-host-lookup-results.csv`.

## Example

Input file (`computers.txt`):
```
hostname1.domain.com
hostname2
```

Output file (`cs-host-lookup-results.csv`):
```csv
Hostname,InCrowdstrike,OS,Manufacturer,MAC,FirstSeen,LastSeen,LocalIP,Domain,Platform,AD-Site,Containment
hostname1,YES,Windows 10,Dell Inc.,00:1A:2B:3C:4D:5E,2021-01-01T12:00:00Z,2021-07-01T12:00:00Z,192.168.1.1,domain.com,Laptop,Site1,Contained
hostname2,NO,-,-,-,-,-,-,-,-,-,-
```