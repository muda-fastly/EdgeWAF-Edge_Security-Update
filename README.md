# Fastly Dictionary Updater

This script allows you to update the `Enabled` item in the `Edge_Security` dictionary for multiple Fastly services. It fetches the active version of each service, locates the `Edge_Security` dictionary, and updates the `Enabled` item's value to a user-specified number (e.g., 0, 100, or any number in between).

## Prerequisites

1. **Python**: Ensure Python 3.7 or higher is installed on your system.
2. **Fastly API Token**: You need a valid Fastly API token with permissions to manage services and dictionaries.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd fastly_dict_updates
   ```

2. **Create a Virtual Environment (optional but recommended)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies: Install the required Python libraries using pip**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set the Fastly API Token: Export your Fastly API token as an environment variable**:

    ```bash
    export FASTLY_API_TOKEN="your_api_token"
    ```

Replace your_api_token with your actual Fastly API token.

5. **Prepare a File with Service IDs:** 
Create a text or CSV file containing the service IDs you want to update. Each service ID should be on a new line

Example (sids.txt):
    ```bash
    5s2bl6FJAgOfLWFQRxROj3
    Txy84LDUxsqNNbZTEvR2c0
    R1RBk93lLrjelX7vnxlnWL
    ```

**Usage**:
Run the script with the following command:
    ```python3 dict_100.py <file> --value <number>```

<file>: Path to the file containing service IDs (e.g., sids.txt).
<number>: The value to set for the Enabled item (e.g., 0, 100, or any number in between).
Example:
```bash
python3 dict_100.py sids.txt --value 100
```
This will update the Enabled item in the Edge_Security dictionary for all services listed in sids.txt to 100.

**Output**
The script will display the results in a tabular format, including:

Service ID
Service Name
Item Key
Item Value
Dictionary ID
Example Output:
```bash
Results:
+----------------------+----------------+-----------+-------------+----------------+
| Service ID           | Service Name   | Item Key  | Item Value  | Dictionary ID  |
+----------------------+----------------+-----------+-------------+----------------+
| 5s2bl6FJAGofLWFQRxROj3 | Example Service 1 | Enabled   | 100         | dict_12345     |
| Txy84LDUxsqnnbZTEvR2c0 | Example Service 2 | Enabled   | 100         | dict_67890     |
| R1RBk93lLrJELx7vnxlnWL | Example Service 3 | Error     | Edge_Security dictionary not found | N/A            |
+----------------------+----------------+-----------+-------------+----------------+
```

**Requirements**
The script requires the following Python libraries:
requests
tabulate
These are listed in the requirements.txt file.

**Troubleshooting**
1. Missing Fastly API Token: Ensure the FASTLY_API_TOKEN environment variable is set:

```export FASTLY_API_TOKEN="your_api_token"```
2. Permission Errors: Ensure your Fastly API token has the necessary permissions to manage services and dictionaries.
3. Python Version: Ensure you are using Python 3.7 or higher:

```python3 --version```