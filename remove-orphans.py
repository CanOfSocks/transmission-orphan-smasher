import os
import json
from pathlib import Path
import json
import base64

from urllib import request, parse

def get_transmission_session_id(server_address, server_port, username, password):
    # Transmission RPC endpoint URL
    rpc_url = f'http://{server_address}:{server_port}/transmission/rpc'

    # Prepare the headers for authentication
    credentials = f'{username}:{password}'
    credentials_base64 = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    headers = {'Authorization': 'Basic ' + credentials_base64}

    # Send a GET request to the Transmission RPC endpoint to obtain the session ID
    req = request.Request(rpc_url, headers=headers)
    
    try:
        response = request.urlopen(req)
        # Extract the session ID from the response headers
        session_id = response.headers.get('X-Transmission-Session-Id')
        return session_id
    except request.HTTPError as e:
        # If the server returns an error, extract the session ID from the error response
        session_id = e.headers.get('X-Transmission-Session-Id')
        return session_id

def get_transmission_files_info(server_address, server_port, username, password):
    # Transmission RPC endpoint URL
    rpc_url = f'http://{server_address}:{server_port}/transmission/rpc'

    # Get the session ID
    session_id = get_transmission_session_id(server_address, server_port, username, password)

    if not session_id:
        print("Error: Unable to retrieve Transmission session ID.")
        return None

    # Prepare the JSON-RPC request
    payload = {
        'method': 'torrent-get',
        'arguments': {
            'fields': ['id', 'name', 'files']
        }
    }

    # Set up headers for authentication, JSON-RPC, and session ID
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8'),
        'X-Requested-With': 'XMLHttpRequest',
        'X-Transmission-Session-Id': session_id,
    }

    # Encode the JSON payload
    payload_json = json.dumps(payload).encode('utf-8')

    # Send the POST request to the Transmission RPC endpoint
    req = request.Request(rpc_url, data=payload_json, headers=headers, method='POST')
    response = request.urlopen(req)

    if response.status == 200:
        # Parse the JSON response
        response_data = json.loads(response.read().decode('utf-8'))

        # Extract file information from the response
        files_info = []
        for torrent in response_data['arguments']['torrents']:
            for file_info in torrent['files']:
                files_info.append(str(Path(file_info['name'])))

        return files_info
    else:
        print(f"Error: Unable to get Transmission files info. HTTP Status: {response.status}")
        return None

def remove_substrings_from_strings(strings, substrings):
    modified_strings = []
    for original_string in strings:
        for substring in substrings:
            if not substring.endswith(os.sep):
                substring += os.sep
            original_string = original_string.replace(substring, '')
        modified_strings.append(original_string)
    return modified_strings

def get_all_files_in_directory(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(str(Path(file_path)))
    return file_list

def get_orphans(sanatised_files,transmission_files_info):
    orphans = []
    for all_file in sanatised_files:
        if all_file not in transmission_files_info:
            if all_file.endswith(".part"):
                continue
            #os.remove(all_file)
            orphans.append(all_file)
    return orphans

def remove_orphans(all_files, orphans):
    for orphan in orphans:
        for file in reversed(all_files):
            if file.endswith(orphan):
                print("Removing: {0}".format(file))
                os.remove(file)
                all_files.remove(file)
            

# Get all files
directory_path = str(Path('/downloads'))  # Replace with the path to your directory
all_files = get_all_files_in_directory(directory_path)

#for file in all_files:
#    print(file)

list_of_parent_folders = [str(Path("/downloads/tv")),str(Path("/downloads/movies"))]

sanatised_files = remove_substrings_from_strings(all_files, list_of_parent_folders)

# Get transmission files
server_address = 'localhost'
server_port = 9091
username = 'xxxxxx'
password = 'yyyyyy'


transmission_files_info = get_transmission_files_info(server_address, server_port, username, password)
orphans = []
if transmission_files_info is not None:
    orphans = get_orphans(sanatised_files,transmission_files_info)  

if orphans is not None:
    remove_orphans(all_files, orphans)


