import os
import requests
from tabulate import tabulate  # Import tabulate for pretty table formatting

def get_active_version(service_id, headers):
    """Fetch the active version for a given service ID."""
    url = f"https://api.fastly.com/service/{service_id}/version"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch versions for service {service_id}: HTTP {response.status_code}: {response.text}")

    versions = response.json()
    for version in versions:
        if version.get("active"):
            return version["number"]

    raise ValueError(f"No active version found for service {service_id}")

def get_service_name(service_id, headers):
    """Fetch the name of the service."""
    url = f"https://api.fastly.com/service/{service_id}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch service name for {service_id}: HTTP {response.status_code}: {response.text}")

    return response.json().get("name", "Unknown")

def update_enabled_item(service_id, dictionary_id, item_key, new_value, headers):
    """Update the item_value of a specific item in a dictionary."""
    url = f"https://api.fastly.com/service/{service_id}/dictionary/{dictionary_id}/item/{item_key}"
    payload = {"item_value": new_value}
    response = requests.put(url, headers=headers, data=payload)

    if response.status_code != 200:
        raise ValueError(f"Failed to update item '{item_key}' in dictionary '{dictionary_id}': HTTP {response.status_code}: {response.text}")

    return response.json()

def list_dictionaries_and_update(service_ids, new_value):
    """List dictionaries for the given service IDs and update the 'Enabled' item in 'Edge_Security'."""
    api_token = os.getenv("FASTLY_API_TOKEN")  # Ensure your Fastly API token is set in the environment
    if not api_token:
        raise ValueError("FASTLY_API_TOKEN environment variable is not set.")

    headers = {
        "Fastly-Key": api_token,
        "Accept": "application/json",
    }

    results = {}
    for service_id in service_ids:
        try:
            # Fetch the service name
            service_name = get_service_name(service_id, headers)

            # Fetch the active version for the service
            version_id = get_active_version(service_id, headers)

            # Make a GET request to fetch dictionaries for the active version
            url = f"https://api.fastly.com/service/{service_id}/version/{version_id}/dictionary"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                results[service_id] = {"error": f"HTTP {response.status_code}: {response.text}", "service_name": service_name}
                continue

            # Parse the dictionaries and find 'Edge_Security'
            dictionaries = response.json()
            edge_security_dict = next((d for d in dictionaries if d["name"] == "Edge_Security"), None)

            if not edge_security_dict:
                results[service_id] = {"error": "Edge_Security dictionary not found", "service_name": service_name}
                continue

            # Fetch items in the 'Edge_Security' dictionary
            dictionary_id = edge_security_dict["id"]
            url = f"https://api.fastly.com/service/{service_id}/dictionary/{dictionary_id}/items"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                results[service_id] = {"error": f"Failed to fetch items for dictionary '{dictionary_id}': HTTP {response.status_code}: {response.text}", "service_name": service_name}
                continue

            # Find the 'Enabled' item and update its value
            items = response.json()
            enabled_item = next((item for item in items if item["item_key"] == "Enabled"), None)

            if not enabled_item:
                results[service_id] = {"error": "'Enabled' item not found in 'Edge_Security' dictionary", "service_name": service_name}
                continue

            # Update the 'Enabled' item value
            updated_item = update_enabled_item(service_id, dictionary_id, "Enabled", str(new_value), headers)
            results[service_id] = {"updated_item": updated_item, "service_name": service_name}

        except requests.RequestException as e:
            results[service_id] = {"error": str(e), "service_name": "Unknown"}
        except ValueError as e:
            results[service_id] = {"error": str(e), "service_name": "Unknown"}

    return results

def load_service_ids(file_path):
    """Load service IDs from a single-column text file or CSV."""
    service_ids = []
    if file_path.endswith(".csv"):
        import csv
        with open(file_path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row or row[0].lower() == "service_id":
                    continue
                service_ids.append(row[0].strip())
    else:
        with open(file_path) as f:
            for line in f:
                service_id = line.strip()
                if service_id:
                    service_ids.append(service_id)
    return service_ids

def print_results_as_table(results):
    """Print the results in a tabular format."""
    table = []
    for service_id, result in results.items():
        service_name = result.get("service_name", "Unknown")
        if "error" in result:
            table.append([service_id, service_name, "Error", result["error"], "N/A"])
        else:
            updated_item = result["updated_item"]
            table.append([
                service_id,
                service_name,
                updated_item.get("item_key", "N/A"),
                updated_item.get("item_value", "N/A"),
                updated_item.get("dictionary_id", "N/A"),
            ])

    # Define column headers
    headers = ["Service ID", "Service Name", "Item Key", "Item Value", "Dictionary ID"]
    print(tabulate(table, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Update 'Enabled' item in 'Edge_Security' dictionary for multiple Fastly services")
    parser.add_argument("file", help="Path to text or CSV file with service IDs (one per line or column)")
    parser.add_argument("--value", type=int, required=True, help="Value to set for the 'Enabled' item (e.g., 0, 100, or any number in between)")
    args = parser.parse_args()

    # Load service IDs from the file
    svc_ids = load_service_ids(args.file)

    # List dictionaries and update the 'Enabled' item
    results = list_dictionaries_and_update(svc_ids, args.value)

    # Print the results as a table
    print("Results:")
    print_results_as_table(results)