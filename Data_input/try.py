import requests
import json

# Replace 'your_api_key' with the actual API key if required
api_key = 'eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImRmYjZjMjQyMDU0OTRiZTY4OTcwMjUxOWUzNWI1MzVjIiwiaCI6Im11cm11cjEyOCJ9'

# Replace 'your_api_endpoint' with the actual API endpoint
api_endpoint = 'https://api.dataplatform.knmi.nl/open-data/v1/datasets/Actuele10mindataKNMIstations/versions/2/files'

# Set up the headers with the API key (if required)
headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}

# Make the GET request to the KNMI API
response = requests.get(api_endpoint, headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse and display the response JSON
    files  = response.json()
    print(files["files"][0])
    # print("Structure of the response:")
    # print(json.dumps(files, indent=2))
    if files:
        first_file_url = files["files"][0]['filename']
        file_response = requests.get(first_file_url, headers=headers)

        # Check if the request for the specific file was successful
        if file_response.status_code == 200:
            # Parse and display the content of the first file
            file_data = file_response.json()
            print(json.dumps(file_data, indent=2))
        else:
            print(f"Error retrieving file: {file_response.status_code}, {file_response.text}")
    else:
        print("No files available.")
else:
    # Print an error message if the request was not successful
    print(f"Error: {response.status_code}, {response.text}")