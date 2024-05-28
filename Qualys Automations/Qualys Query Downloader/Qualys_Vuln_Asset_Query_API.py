from ayx import Alteryx
import requests
import time
import json
import datetime
import pandas as pd

# Initialize the session
def start_session(username, password, auth_url):
    max_retries = 5
    retries = 0

    payload = {
        "action": "login",
        "username": username,
        "password": password
    }
    headers = {
        "X-Requested-With": "Python requests",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    while retries <= max_retries:
        try:
            response = requests.post(auth_url, data=payload, headers=headers)
            response_cookies = response.cookies
            response_id = None
            for cookie in response_cookies:
                if 'QualysSession' in cookie.name:
                    response_id = f"QualysSession={cookie.value}"
                    break
            if response.status_code == 200:
                print(f"HTTP 200 - Qualys Authentication Successful")
                return response_id
            elif response.status_code == 400:
                print(f"HTTP 400 - Bad Request. The server could not understand the request due to invalid syntax.")
                break
            elif response.status_code == 401:
                print(f"HTTP 401 - Unauthorized. Authentication is required and has failed or has not yet been provided.")
                break
            elif response.status_code == 403:
                print(f"HTTP 403 - Forbidden. The client does not have access rights to the content.")
                break
            elif response.status_code == 404:
                print(f"HTTP 404 - Not Found. The server can not find the requested resource.")
                break
            elif response.status_code >= 500:
                print(f"HTTP {response.status_code} - Server Error.")
                wait = 2 ** retries
                time.sleep(wait)
                retries += 1
            else:
                print(f"Unexpected error. HTTP {response.status_code}")
                break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            wait = 2 ** retries
            time.sleep(wait)
            retries += 1

# End the session
def kill_session(session_id, auth_url):
    max_retries = 5
    retries = 0

    payload = {
        "action": "logout"
    }
    headers = {
        "X-Requested-With": "Python requests",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": session_id
    }

    while retries <= max_retries:
        try:
            response = requests.post(auth_url, data=payload, headers=headers)
            if response.status_code == 200:
                print(f"HTTP 200 - Logout successful.")
                return
            elif response.status_code >= 500:
                print(f"HTTP {response.status_code} - Server Error. Retrying...")
                wait = 2 ** retries
                time.sleep(wait)
                retries += 1
            else:
                print(f"Unexpected error. HTTP {response.status_code}")
                break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            wait = 2 ** retries
            time.sleep(wait)
            retries += 1

# Format the JSON data and save it to a file
def format(data):

    # Initialize the flattened_data list
    flattened_data = []

    # Iterate over the data and rename the fields
    for sublist in data:
        for item in sublist:
            # Create a new dictionary with only the fields you're interested in
            new_item = {
                'Asset ID': item.get('assetId', 'N/A'),
                'Asset Name': item.get('name', 'N/A'),
                'Host ID': item['host'].get('qgHostId', 'N/A'),
                'Netbios Name': item['host'].get('netbiosName', 'N/A'),
                'IPV4 Addresses': item['host'].get('address', 'N/A').lstrip('/'),  # Remove leading "/"
                'Operating System Category': item['host']['os'].get('category1', 'N/A') + ' / ' + item['host']['os'].get('category2', 'N/A'), # Concatenate the two category fields
                'OS': item['host']['os'].get('name', 'N/A'),
                'Operating System Version': item['host']['os'].get('version', 'N/A'),
                'Operating System Lifecycle Stage': 'Not Applicable' if item['host']['os'].get('version', '-') == '-' and item['host']['os'].get('name', 'N/A') not in ['VMware vCenter Server Appliance 6.7.0 build 22509751'] else 'EOL', 
                # If the version is '-' and the name is not in the exemption list, set to 'Not Applicable', otherwise set to 'EOL'
                'Hardware Category': 'N/A',
                'Activity': datetime.datetime.strptime(item.get('updatedAt', 'N/A'), "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%m/%d/%Y"), # Convert the date to a more readable format
                'Tags': ' | '.join([tag.get('name', 'N/A') for tag in item.get('tags', [])]) # Join the tag names into a single string
            }

            # Add the new item to the flattened data list
            flattened_data.append(new_item)

    # Convert the flattened data to a pandas DataFrame
    df = pd.DataFrame(flattened_data)

    print("JSON file created successfully")

    return df

# General query function + total count getter
def assetview_query(session_id, offset, limit, sendResponse, assetview_url, query, query_param):
    print(query)
    params = {
        'limit': limit,
        'offset': offset,
        'fields': 'assetId,name,host.qgHostId,host.netbiosName,host.address,host.os.category1,host.os.category2,host.os.name,host.os.version,updatedAt,tags.name',
        'query': query,
        'groupByPivot': 'Asset',
        'havingQuery': query_param,
        'order': '-updatedAt'
    }
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://qualysguard.qualys.com/portal-front/rest/assetview/1.0/assets',
        'Accept': '*/*',
        'Content-Type': 'text/plain',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Origin': 'https://qualysguard.qg1.apps.qualys.com',
        'Cookie': session_id
    }

    response = requests.get(assetview_url, params=params, headers=headers)
    #print(response.text)
    if sendResponse == 1:
        return response
    elif sendResponse == 0:       
        count = int(response.headers.get("Total-Count"))
        return count

# Pull current EOL OS query
def currentEOLQuery(session_id, assetview_url):
    # Initialize the offset and json_string variables
    offset = 0
    pull_size = 150
    json_data = []
    max_retries = 5
    eol_query = 'not ((operatingSystem:"Windows Server 2022" or operatingSystem:"Windows Server 2019" or operatingSystem:"Windows Server 2016") or (operatingSystem:"Windows 10 Enterprise 19045" or operatingSystem:"Windows 10 Enterprise 22H2") or (operatingSystem:"Windows 11 Enterprise 22631" or operatingSystem:"Windows 11 22H2" or operatingSystem:"Windows 11 23H2") or (operatingSystem:"Red Hat Enterprise Linux Server 7") or (operatingSystem:"Ubuntu Linux 16.04.5" or operatingSystem:"Ubuntu Linux 18.04.6") or (operatingSystem:"VMware ESXi 7.0.3" or operatingSystem:"VMware vCenter Server Appliance 7.0.3"))'
    eol_query_param = '(vulnerabilities.vulnerability.title:"EOL/Obsolete Operating System") and (vulnerabilities.disabled: FALSE and vulnerabilities.ignored: FALSE)'

    # Get the initial response to retrieve the count, using offset 0, limit 1, and sendResponse 0
    count = assetview_query(session_id, offset, 1, 0, assetview_url, eol_query, eol_query_param)

    # Print out the count (for testing)
    print(f"Total number of records: {count}")

    print("Starting pagination...")

    # Call the assetview_query function and increment the offset by either 100 or (if different between offset and count is less than 200) the difference between offset and count
    while offset < count:
        increment = min(pull_size, count - offset)
        retries = 0

        while retries <= max_retries:
            try:
                response = assetview_query(session_id, offset, pull_size, 1, assetview_url, eol_query, eol_query_param)
                # If the request is successful, break the retry loop
                json_data.append(json.loads(response.text))
                print(f"Now trying: {str(offset)}")
                offset += increment
                break
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                wait = 2 ** retries
                time.sleep(wait)
                retries += 1
        
        # If the maximum number of retries is exceeded, break the main loop
        if retries > max_retries:
            print("Maximum number of retries exceeded. Stopping pagination...")
            break

        # Sleep for 5 seconds to avoid rate limiting
        time.sleep(5)

    return json_data

# Pull future EOL OS query
def futureEOLQuery(session_id, assetview_url):
    # Initialize the offset and json_string variables
    offset = 0
    pull_size = 150
    json_data = []
    max_retries = 5
    os_query = '(operatingSystem:"Ubuntu" and operatingSystem.version:"23.10") or (operatingSystem:"CentOS 7") or (operatingSystem:"Alpine" and operatingSystem.version:"3.16") or (operatingSystem:"Alpine" and operatingSystem.version: "3.17") or (operatingSystem:"Red Hat Enterprise" and operatingSystem.version:"7") or (operatingSystem:"Debian" and operatingSystem.version:"11") or (operatingSystem:"Oracle Linux 7") or (operatingSystem:"SUSE" AND operatingSystem.name:"12 SP5") or (operatingSystem:"Windows 11 Pro" AND operatingSystem.version:"22H2") or (operatingSystem:"Windows 11 Enterprise" and operatingSystem.name:"21H2") or (operatingSystem:"Windows 10 Enterprise" and operatingSystem.name:"21H2")'
    os_query_param = 'vulnerabilities.disabled: FALSE and vulnerabilities.ignored: FALSE'

    # Get the initial response to retrieve the count, using offset 0, limit 1, and sendResponse 0
    count = assetview_query(session_id, offset, 1, 0, assetview_url, os_query, os_query_param)

    # Print out the count (for testing)
    print(f"Total number of records: {count}")

    print("Starting pagination...")

    # Call the assetview_query function and increment the offset by either 100 or (if different between offset and count is less than 200) the difference between offset and count
    while offset < count:
        increment = min(pull_size, count - offset)
        retries = 0

        while retries <= max_retries:
            try:
                response = assetview_query(session_id, offset, pull_size, 1, assetview_url, os_query, os_query_param)
                # If the request is successful, break the retry loop
                json_data.append(json.loads(response.text))
                print(f"Now trying: {str(offset)}")
                offset += increment
                break
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                wait = 2 ** retries
                time.sleep(wait)
                retries += 1
        
        # If the maximum number of retries is exceeded, break the main loop
        if retries > max_retries:
            print("Maximum number of retries exceeded. Stopping pagination...")
            break

        # Sleep for 5 seconds to avoid rate limiting
        time.sleep(5)

    return json_data

# Run direct, w/o options
def main(username, password, auth_url, assetview_url):
    # Establish Qualys session
    try:
        session_id = start_session(username,password,auth_url)
    except Exception as e:
        print(f"An error occurred while starting the session: {str(e)}")
        exit()

    # Pull / format current EOL OS data
    try:
        currentEOLData = format(currentEOLQuery(session_id, assetview_url))
    except Exception as e:
        print(f"An error occurred during EOL QID query: {str(e)}")
        exit()

    # Pull future EOL OS data
    try:
        futureEOLData = format(futureEOLQuery(session_id, assetview_url))
    except Exception as e:
        print(f"An error occurred during EOL OS query: {str(e)}")
        exit()

    # Return the data, current EOL to output #1 and future EOL to output #2
    Alteryx.write(currentEOLData,1)
    Alteryx.write(futureEOLData,2)

    try:
        # Terminate the session
        kill_session(session_id, auth_url)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    username="placeholder"
    password="placeholder"
    auth_url="https://qualysapi.qualys.com/api/2.0/fo/session/"
    assetview_url="https://qualysguard.qualys.com/portal-front/rest/assetview/1.0/assets"
    main(username, password, auth_url, assetview_url)