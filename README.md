# credentials-handler 

This Python script encodes secrets from JSON files or environment variables into an `.env` file or updates a `secrets.toml` file, using a YAML mapping configuration. It supports different target tools such as Docker, Kestra, and `dlt` with BigQuery destination.

## Features

-   **Flexible Mapping:** Uses a YAML file to map JSON file keys or environment variables to environment variable names or `secrets.toml` keys.
-   **Multiple Target Tools:** Supports encoding secrets for Docker, Kestra, and `dlt` BigQuery destination.
-   **Base64 Encoding (Optional):** Encodes values using Base64 encoding (for Kestra).
-   **TOML file update (dlt_dest_bigquery):** Updates an existing `secrets.toml` file with secrets mapped from files or environment variables.
-   **Error Handling:** Provides informative error messages for missing files, invalid YAML/JSON, and missing environment variables.

## Requirements

-   toml (for `dlt_dest_bigquery` target)

## Installation

```bash
pip install 
```

## Usage

```bash
usage: encode_env.py [-h] [-o OUTPUT_FILE] [-p PREFIX] [--secrets_toml SECRETS_TOML] mapping_file {docker,kestra,dlt_dest_bigquery}

Encode secrets from JSON files or environment variables to an .env file or TOML file for different destinations using a YAML mapping.

positional arguments:
  mapping_file          Path to the YAML mapping file. This file defines how to map JSON file contents and environment variables to environment variables or TOML keys.
  {docker,kestra,dlt_dest_bigquery}
                        Tool for which credentials are encoded.

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT_FILE
                        Path to the output .env file (used for Docker and Kestra, default: .env_encoded).
  -p, --prefix PREFIX   Prefix for the environment variables (used for Docker, default: SECRET_).

dlt_dest_bigquery arguments:
  These arguments are required when target_tool is dlt_dest_bigquery

  --secrets_toml SECRETS_TOML
                        Path to the secrets.toml file to be modified
```

### Target Tool Specific Usage

#### Docker

```bash
python encode_env.py mapping.yaml docker -o .env -p DOCKER_SECRET_
```

This command will read the `mapping.yaml` file, encode the secrets, and save them to a `.env` file with the prefix `DOCKER_SECRET_`.

#### Kestra

```bash
python encode_env.py mapping.yaml kestra -o kestra.env
```

This command will read the `mapping.yaml` file, encode the secrets using Base64 encoding, and save them to `kestra.env` with the prefix `SECRET_`.

#### dlt with BigQuery destination

```bash
python encode_env.py mapping.yaml dlt_dest_bigquery --secrets_toml ./secrets.toml
```

This command will read the `mapping.yaml` and `./secrets.toml` file, map and update the secrets into `./secrets.toml` based on the mapping and save the updated file.

### YAML Mapping File Format

The YAML mapping file defines the mapping between JSON file keys or environment variables and environment variable names (for Docker, Kestra) or `secrets.toml` keys (for dlt).

#### Example for Docker/Kestra

```yaml
files:
  my_json_file: path/to/my_json_file.json
  other_json_file: path/to/other_json_file.json

my_json_file:
  api_key: API_KEY
  username: USERNAME

other_json_file:
  password: PASSWORD

from_env:
  MY_ENV_VAR: ENV_VAR_KEY
```

-   **`files`**:  A dictionary mapping file headers to file paths. Each file will be loaded as a JSON object.
-   **`from_env`**: A dictionary mapping environment variable names to environment variable keys (or `secrets.toml` keys).
-   Other sections represent the file headers defined in the `files` section. Under each file header, a dictionary maps JSON keys to environment variable keys (or `secrets.toml` keys).

#### Example for dlt with BigQuery destination

```yaml
files:
  credentials: path/to/google_credentials.json

credentials:
  client_id: destination__bigquery__credentials__client_id
  private_key: destination__bigquery__credentials__private_key

from_env:
  GOOGLE_PROJECT_ID: destination__bigquery__project_id
```

-   **`files`**:  A dictionary mapping file headers to file paths. Each file will be loaded as a JSON object.
-   **`from_env`**: A dictionary mapping environment variable names to `secrets.toml` keys.
-   Other sections represent the file headers defined in the `files` section. Under each file header, a dictionary maps JSON keys to `secrets.toml` keys.  Use double underscore (`__`) to represent nested TOML structures.

**Note:**
-   The `dlt_dest_bigquery` target modifies `secrets.toml` in place, so back up the file before running.
-   The `dlt_dest_bigquery` target does not create an output .env file

### JSON File Format

The JSON files specified in the YAML mapping file should contain key-value pairs that need to be encoded.

Example:

```json
{
  "api_key": "your_api_key",
  "username": "your_username"
}
```

### secrets.toml File Format (for `dlt_dest_bigquery`)

The `secrets.toml` file should be a valid TOML file. The script will update the existing values based on the mapping defined in the YAML file. The script only updates the values. It will not generate the file or create keys, so the keys you wish to update must already exist in the secrets.toml file.

Example:

```toml
[destination.bigquery.credentials]
client_id = "old_client_id"
private_key = "old_private_key"

[destination.bigquery]
project_id = "old_project_id"
```

### Environment Variables

When using the `from_env` section in the YAML file, ensure that the specified environment variables are set before running the script.

## Error Handling

The script provides the following error messages:

-   `Error: Mapping file not found`: If the specified YAML mapping file does not exist.
-   `Error: Invalid YAML in mapping file`: If the YAML mapping file is not a valid YAML file.
-   `Error: Neither 'files' nor 'from_env' section not found in the YAML configuration.`: If neither `files` nor `from_env` is defined in the YAML file
-   `Error: File not found`: If a JSON file specified in the YAML mapping file does not exist.
-   `Error: Invalid JSON in file`: If a JSON file specified in the YAML mapping file is not a valid JSON file.
-   `Warning: Environment variable '{env_var}' not found, skipping.`: If an environment variable specified in the YAML mapping file is not set.
-   `Warning: File header '{section_header}' not found in file data, skipping mappings for this file.`: If the section header is not within the list of files defined within the yaml file
-   `Warning: Key '{json_key}' not found in JSON data for file header '{section_header}', skipping.`: If a json key specified in the YAML mapping file is not set.
-   `Error: secrets.toml file not found`: If the specified secrets.toml file does not exist.
-   `Error: Invalid TOML in secrets.toml file`: If the specified secrets.toml file is not a valid TOML file.
-   `Warning: TOML key '{toml_key}' not found in secrets.toml, skipping.`: If a toml key specified in the YAML mapping file is not found in the secrets.toml file.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

[MIT License](LICENSE)
