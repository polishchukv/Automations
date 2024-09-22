from ayx import Alteryx
import requests
import time
import json
import datetime
import pandas as pd
import sys

# Initialize the session
def start_session(username, password, auth_url):
    max_retries = 15
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
    max_retries = 15
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

    # Define the header names, for use when incoming json data is empty
    headers = [
        'Asset ID', 'Asset Name', 'Host ID', 'Netbios Name', 'IPV4 Addresses',
        'Operating System Category', 'OS', 'Operating System Version',
        'Operating System Lifecycle Stage', 'Hardware Category', 'Activity',
        'Tags', 'Qualys - External Facing'
    ]

    # Check if the data is empty
    if not data:
        # Create an empty DataFrame with only the header names
        df = pd.DataFrame(columns=headers)
        print("Data is empty, returning header-only dataframe...")
        return df

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
            'Tags': ' | '.join([tag.get('name', 'N/A') for tag in item.get('tags', [])]), # Join the tag names into a single string
            # Check if the 'External BU' or 'Internet Facing Assets' tags are present and set the 'Qualys - External Facing' field accordingly (true or false)
            'Qualys - External Facing': 'True' if ('[EXTERNAL]' or '[external]' or 'EXTERNAL' or 'external') in [tag.get('name', '') for tag in item.get('tags', [])] else 'False'
            }

            # Add the new item to the flattened data list
            flattened_data.append(new_item)

    # Convert the flattened data to a pandas DataFrame
    df = pd.DataFrame(flattened_data)

    print("Converted to dataframe, returning...")

    return df

# Deduplicate the DataFrame
def deduplicate(df):
    # Drop duplicates based on 'Asset ID' and 'Host ID' columns
    df_deduplicated = df.drop_duplicates(subset=['Asset ID', 'Host ID'])
    print(f"Data deduplicated. Reduced from {len(df)} to {len(df_deduplicated)} rows.")
    return df_deduplicated

# General query function + total count getter
def assetview_query(session_id, offset, limit, sendResponse, assetview_url, query, query_param):
    #print(query)
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

# Combined normal current EOL query and temp
def combinedEOLQuery(session_id, assetview_url):
    # Run temp query first
    temp_data = currentEOLQuerytemp(session_id, assetview_url)

    time.sleep(5)

    # Run normal query second
    current_data = currentEOLQuery(session_id, assetview_url)

    # Combine the two data sets
    combined_data = temp_data + current_data

    # Print the combined JSON data before returning
    #print("Final combined JSON data:", combined_data)
    return combined_data

# Pull current EOL OS query TEMP
def currentEOLQuerytemp(session_id, assetview_url):
    # Initialize the offset and json_string variables
    offset = 0
    pull_size = 150
    json_data = []
    max_retries = 15

    eol_query = (

    )

    eol_query_param = ( 

    )

    # Get the initial response to retrieve the count, using offset 0, limit 1, and sendResponse 0
    count = assetview_query(session_id, offset, 1, 0, assetview_url, eol_query, eol_query_param)

    # Print out the count (for testing)
    print(f"Total number of records [CURRENT TEMP]: {count}")

    # Check if the count is 0, if so, return an empty list
    print("Starting pagination [CURRENT TEMP]...")

    # Call the assetview_query function and increment the offset by either 100 or (if different between offset and count is less than 200) the difference between offset and count
    while offset < count:
        increment = min(pull_size, count - offset)
        retries = 0

        while retries <= max_retries:
            try:
                response = assetview_query(session_id, offset, pull_size, 1, assetview_url, eol_query, eol_query_param)
                # If the request is successful, break the retry loop
                #print(f"Appending data: {json.loads(response.text)}")
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

    # Print the JSON data before returning
    #print("Final JSON data [CURRENT TEMP]:", json_data)
    return json_data

# Pull current EOL OS query
def currentEOLQuery(session_id, assetview_url):
    # Initialize the offset and json_string variables
    offset = 0
    pull_size = 150
    json_data = []
    max_retries = 15

    eol_query = (

    )

    eol_query_param = (

    )

    # Get the initial response to retrieve the count, using offset 0, limit 1, and sendResponse 0
    count = assetview_query(session_id, offset, 1, 0, assetview_url, eol_query, eol_query_param)

    # Print out the count (for testing)
    print(f"Total number of records [CURRENT]: {count}")

    # Check if the count is 0, if so, return an empty list
    if count == 0:
        print("Function aborted because count is 0.")
        return json_data

    print("Starting pagination [CURRENT]...")

    # Call the assetview_query function and increment the offset by either 100 or (if different between offset and count is less than 200) the difference between offset and count
    while offset < count:
        increment = min(pull_size, count - offset)
        retries = 0

        while retries <= max_retries:
            try:
                response = assetview_query(session_id, offset, pull_size, 1, assetview_url, eol_query, eol_query_param)
                # If the request is successful, break the retry loop
                #print(f"Appending data: {json.loads(response.text)}")
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

    # Print the JSON data before returning
    #print("Final JSON data:", json_data)
    return json_data

# Pull future EOL OS query
def futureEOLQuery(session_id, assetview_url):
    # Initialize the offset and json_string variables
    offset = 0
    pull_size = 150
    json_data = []
    max_retries = 15

    os_query = (

    )

    os_query_param = (

    )

    # Get the initial response to retrieve the count, using offset 0, limit 1, and sendResponse 0
    count = assetview_query(session_id, offset, 1, 0, assetview_url, os_query, os_query_param)

    # Print out the count (for testing)
    print(f"Total number of records [FUTURE]: {count}")

    # Check if the count is 0, if so, return an empty list
    if count == 0:
        print("Function aborted because count is 0.")
        return json_data

    print("Starting pagination [FUTURE]...")

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
    # Configure mode; Can be set to "current" or "future"
    query_mode = "current"

    # Establish Qualys session
    try:
        session_id = start_session(username, password, auth_url)
    except Exception as e:
        print(f"An error occurred while starting the session: {str(e)}")
        exit()

    if query_mode == "current":
        # Pull / format current EOL OS data
        try:
            currentEOLData = format(combinedEOLQuery(session_id, assetview_url))
            # Deduplicate the data
            currentEOLData = deduplicate(currentEOLData)
            # Write the data to output #1
            Alteryx.write(currentEOLData, 1)
        except Exception as e:
            print(f"An error occurred during the current EOL QID query: {str(e)}")
            exit()
    elif query_mode == "future":
        # Pull / format future EOL OS data
        try:
            futureEOLData = format(futureEOLQuery(session_id, assetview_url))
            # Deduplicate the data
            futureEOLData = deduplicate(futureEOLData)
            # Write the data to output #2
            Alteryx.write(futureEOLData, 2)
        except Exception as e:
            print(f"An error occurred during the future EOL OS query: {str(e)}")
            exit()
    else:
        print("Invalid query mode specified. Please use 'current' or 'future'.")
        exit()

    # Terminate the session
    try:
        kill_session(session_id, auth_url)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    username = "USERNAME"  # Replaced with placeholder
    password = "PASSWORD"  # Replaced with placeholder
    auth_url = "{AUTH_URL}"  # Replaced with placeholder
    assetview_url = "{ASSETVIEW_URL}"  # Replaced with placeholder
    main(username, password, auth_url, assetview_url)
