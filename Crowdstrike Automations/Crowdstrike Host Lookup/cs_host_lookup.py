import requests
import csv
import os

def obtain_oauth_token(client_id, client_secret):
    """
    Obtain a 30-minute Bearer token using OAuth2.

    Args:
    - client_id (str): Client ID for OAuth2.
    - client_secret (str): Client secret for OAuth2.

    Returns:
    - str: Bearer token.
    """
    token_url = "https://api.crowdstrike.com/oauth2/token"
    payload = f"client_id={client_id}&client_secret={client_secret}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_url, headers=headers, data=payload)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json().get('access_token')

def main():
    # File paths for input (FQDN list) and output (CSV report)
    input_file_path = "C:/temp/computers.txt"
    output_file_path = "C:/temp/cs-host-lookup-results.csv"

    # Environment variables (or securely stored parameters) for sensitive information
    client_id = os.getenv('CS_CLIENT_ID', 'your_client_id')
    client_secret = os.getenv('CS_CLIENT_SECRET', 'your_client_secret')

    # Obtaining the OAuth2 Bearer token
    token = obtain_oauth_token(client_id, client_secret)

    # Base headers for API requests
    base_headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    with open(input_file_path, 'r') as input_file, open(output_file_path, 'w', newline='') as output_file:
        # Read the list of FQDNs
        fqdn_list = input_file.readlines()

        # CSV setup for writing the report
        field_names = ['Hostname', 'InCrowdstrike', 'OS', 'Manufacturer', 'MAC', 'FirstSeen', 'LastSeen', 'LocalIP', 'Domain', 'Platform', 'AD-Site', 'Containment']
        csv_writer = csv.DictWriter(output_file, fieldnames=field_names)
        csv_writer.writeheader()

        # Process each FQDN
        for fqdn in fqdn_list:
            hostname = fqdn.strip().split('.')[0]  # Extract hostname by removing the domain part
            device_query_url = f"https://api.crowdstrike.com/devices/queries/devices/v1?filter=hostname:'{hostname}'"

            # Querying the device by hostname
            response = requests.get(device_query_url, headers=base_headers)
            response.raise_for_status()  # Raise an error for bad status codes
            query_result = response.json()

            # Check if the hostname is found in CrowdStrike
            if query_result['meta']['pagination'].get('total', 0) == 1:
                asset_id = query_result['resources'][0]
                device_details_url = f"https://api.crowdstrike.com/devices/entities/devices/v1?ids={asset_id}"

                # Querying the detailed device info by asset ID
                response = requests.get(device_details_url, headers=base_headers)
                response.raise_for_status()
                device_details = response.json()['resources'][0]

                # Recording found details
                report_entry = {
                    "Hostname": hostname,
                    "InCrowdstrike": "YES",
                    "OS": device_details.get('os_version', '-'),
                    "Manufacturer": device_details.get('system_manufacturer', '-'),
                    "MAC": device_details.get('mac_address', '-'),
                    "FirstSeen": device_details.get('first_seen', '-'),
                    "LastSeen": device_details.get('last_seen', '-'),
                    "LocalIP": device_details.get('local_ip', '-'),
                    "Domain": device_details.get('machine_domain', '-'),
                    "Platform": device_details.get('product_type_desc', '-'),
                    "AD-Site": device_details.get('site_name', '-'),
                    "Containment": device_details.get('status', '-')
                }
            else:
                # Entry if the hostname is not found
                report_entry = {
                    "Hostname": hostname,
                    "InCrowdstrike": "NO",
                    "OS": "-",
                    "Manufacturer": "-",
                    "MAC": "-",
                    "FirstSeen": "-",
                    "LastSeen": "-",
                    "LocalIP": "-",
                    "Domain": "-",
                    "Platform": "-",
                    "AD-Site": "-",
                    "Containment": "-"
                }

            # Write the entry to the CSV report
            csv_writer.writerow(report_entry)

if __name__ == "__main__":
    main()