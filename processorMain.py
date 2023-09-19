import requests
import csv

def fetch_data_from_url(url):
    """Fetches data from the given URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def sanitize_data(data):
    """Remove or replace problematic characters from data."""
    if isinstance(data, str):
        # Replace newline characters with a space (or remove them altogether)
        data = data.replace('\n', ' ')
        data = data.replace('*', ' ')  # Replace with space
        return data
    return data

def find_key_recursive(data, target_key, depth=0, parent_key=None):
    if isinstance(data, dict):
        if target_key in data:
            # Yield the 'id' key only if we are at the top level (depth=1) and the parent is 'data'
            if target_key == 'id' and depth == 1 and parent_key == 'data':
                yield data[target_key]
            elif target_key != 'id':  # For keys other than 'id', always yield
                yield data[target_key]

        for key, value in data.items():
            yield from find_key_recursive(value, target_key, depth+1, key)

    elif isinstance(data, list):
        for item in data:
            yield from find_key_recursive(item, target_key, depth+1, parent_key)


def save_to_csv(filename, headers, all_data):
    """Saves the extracted data to a CSV file with a custom delimiter."""
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='*')  # Setting custom delimiter here
        csvwriter.writerow(headers)
        for data_row in all_data:
            sanitized_row = [sanitize_data(data) for data in data_row]
            csvwriter.writerow(sanitized_row)

def extract_data_for_csv(data, keys):

    # Helper function to fetch all values for a key
    def get_all_values(data, key):
        return list(find_key_recursive(data, key, depth=0, parent_key=None))
    
    # First, gather all the data for each key
    all_data = {key: get_all_values(data, key) for key in keys}
    
    # Find the max length of data among all keys to determine number of rows
    max_rows = max(len(values) for values in all_data.values())
    
    # Construct the rows
    extracted_rows = []
    for i in range(max_rows):
        row = []
        for key in keys:
            values = all_data[key]
            if i < len(values):
                row.append(values[i])
            else:
                row.append(None)
        
        # Only append the row if 'id' has a valid value
        if row[0]:  # Assuming 'id' is the first key
            extracted_rows.append(row)
    
    return extracted_rows


def main_exec(keys, output_filename):
    """Modified main function to handle multiple keys and output filenames."""
    # Base URL and IDs (assuming these remain constant across all scripts)
    base_url = "https://BASE_URL_OF_SERVICE/v1/services/"
    
    all_extracted_data = []
    
    # Fetch and extract data for each ID
    for id_ in ids:
        full_url = base_url + id_
        print(f"Fetching data from URL: {full_url}")  # Debug statement
        data = fetch_data_from_url(full_url)
        extracted_rows = extract_data_for_csv(data, keys)
        all_extracted_data.extend(extracted_rows)
    
     # Debug statement
    print(f"Saving {len(all_extracted_data)} rows to {output_filename}")

    # Save to CSV
    save_to_csv(output_filename, keys, all_extracted_data)

if __name__ == "__main__":
    process_csvs()
