# `kestra` secret encoder

A commandline too for encodings secrets from JSON files and environment variables for use with `docker`, `kestra` and `dlt`.
It leverages a YAML mapping file to define relationships between JSON file keys, environment variables, and desired `SECRET_` environment variable names in the output `.env` file. 

(see also the [`kestra` documentation](https://kestra.io/docs/how-to-guides/secrets))

This `README` is not yet up-to-date.

## Features

*   **YAML Configuration:** Utilizes a YAML file to define mappings between JSON file keys, environment variables and Kestra secret names, providing a flexible and centralized configuration mechanism.
*   **Multi-File Support:** Reads secrets from multiple JSON files, accommodating complex configurations spread across different files.
*   **Environment Variable Support:** Can read secrets directly from environment variables, useful for injecting credentials or configuration parameters directly into the Kestra environment.
*   **Base64 Encoding:** Encodes all secret values using base64 encoding for secure storage in the `.env` file.
*   **Kestra Compatibility:** Generates a `.env` file with the `SECRET_` prefix as required by Kestra for secret variables.
*   **Error Handling:** Includes comprehensive error handling for scenarios such as file not found, invalid JSON/YAML, and missing keys or environment variables.
*   **Command-Line Interface:** Offers a command-line interface for easy execution and integration into deployment pipelines.

## Installation

```bash
pip install git+https://github.com/kantundpeterpan/kestra_secret_encoder
```

## Usage

```bash
usage: encode_env.py [-h] [-o OUTPUT_FILE] [-p PREFIX] [--secrets_toml SECRETS_TOML] mapping_file {docker,kestra,dlt_dest_bigquery}

Encode secrets from JSON files to an .env file for different destinations using a YAML mapping.

positional arguments:
  mapping_file          Path to the YAML mapping file
  {docker,kestra,dlt_dest_bigquery}
                        Tool credentials are encoded for

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT_FILE
                        Path to the output .env file (default: secrets.toml)
  -p, --prefix PREFIX   Prefix for the environment variables (default: SECRET_)

dlt_dest_bigquery arguments:
  These arguments are required when target_tool is dlt_dest_bigquery

  --secrets_toml SECRETS_TOML
                        Path to the secrets.toml file
```

*   `<mapping_file>`: Path to the YAML mapping file that defines the secret mappings.
*   `-o <output_file>` or `--output <output_file>`: (Optional) Path to the output `.env` file. Defaults to `.env_encoded`.

## Use in `docker-compose.yml`

```yaml
services:
  kestra:
    ...
    env_file: ".env_encode"
    ...
```

## YAML Mapping File Format

The YAML mapping file provides the schema on how secrets are extracted from JSON files and environment variables, and how they are mapped to `SECRET_` variables in the output `.env` file.

The YAML file can contain two primary top-level sections: `files` and `from_env`.

### `files` Section

The `files` section specifies the paths to JSON files to be processed. Keys within this section serve as references for the mapping sections.

```yaml
files:
  my_app_config: /path/to/my_app_config.json
  db_credentials: /path/to/db_credentials.json
```

### Mapping Sections

Each section (except `files` and `from_env`) in the YAML file correlates to a file header defined in the `files` section. The keys in these sections correspond to keys within the respective JSON file, and the values are the desired `SECRET_` environment variable names.

```yaml
my_app_config:
  api_key: API_KEY
  app_name: APP_NAME
  
db_credentials:
  username: DB_USERNAME
  password: DB_PASSWORD
```

### `from_env` Section

The `from_env` section establishes mappings from environment variables to Kestra secret names. Keys in this section represent environment variable names, and values specify the desired `SECRET_` environment variable names.

```yaml
from_env:
  MY_CUSTOM_SECRET: CUSTOM_SECRET
  ANOTHER_SECRET: ANOTHER_SECRET
```

### Example YAML Mapping File

```yaml
files:
  app_config: config/app_config.json
  db: secrets/database.json

app_config:
  api_key: APP_API_KEY
  log_level: LOG_LEVEL

db:
  username: DB_USER
  password: DB_PASSWORD

from_env:
  EXTERNAL_API_KEY: EXTERNAL_API
```

In this example:

*   `app_config.json` will be read, and the values associated with keys `api_key` and `log_level` will be encoded and stored as `SECRET_APP_API_KEY` and `SECRET_LOG_LEVEL` in the `.env` file, respectively.
*   `database.json` will be read, and the values associated with keys `username` and `password` will be encoded and stored as `SECRET_DB_USER` and `SECRET_DB_PASSWORD` in the `.env` file.
*   The value of the environment variable `EXTERNAL_API_KEY` will be encoded and stored as `SECRET_EXTERNAL_API` in the `.env` file.

## Example JSON Files

**config/app_config.json:**

```json
{
  "api_key": "your_api_key_here",
  "log_level": "INFO"
}
```

**secrets/database.json:**

```json
{
  "username": "db_user",
  "password": "db_password"
}
```

## Example Usage

1.  Create the YAML mapping file (e.g., `mapping.yaml`) as described above.
2.  Create the JSON files referenced in the mapping file (e.g., `config/app_config.json` and `secrets/database.json`).
3.  Set any environment variables referenced in the `from_env` section of the mapping file.  For example:

    ```bash
    export EXTERNAL_API_KEY="some_external_api_key"
    ```

4.  Run the script:

    ```bash
    python encode_env.py mapping.yaml -o .env
    ```

This generates a `.env` file containing base64 encoded secrets.

```
SECRET_APP_API_KEY=eW91cl9hcGlfa2V5X2hlcmU=
SECRET_LOG_LEVEL=SU5GTw==
SECRET_DB_USER=ZGJfdXNlcg==
SECRET_DB_PASSWORD=ZGJfcGFzc3dvcmQ=
SECRET_EXTERNAL_API=c29tZV9leHRlcm5hbF9hcGlfa2V5
```

## Error Handling

The script includes error handling for the following:

*   **Mapping file not found:**  If the specified YAML mapping file does not exist.
*   **Invalid YAML:** If the YAML mapping file contains invalid YAML syntax.
*   **File not found:** If any of the JSON files specified in the mapping file do not exist.
*   **Invalid JSON:** If any of the JSON files contain invalid JSON syntax.
*   **Missing key:** If a key specified in the mapping file is not found in the corresponding JSON data.
*   **Missing Environment Variable:** If an environment variable specified in the `from_env` section is not found in the environment.

In case of an error, the script prints an error message to the console and exits. Warnings are shown for non-critical issues like missing environment variables or JSON keys.

## Contributing

Contributions are welcome! Please submit a pull request with your changes.
*   **Invalid JSON:** If any of the JSON files contain invalid JSON syntax.
*   **Missing key:** If a key specified in the mapping file is not found in the corresponding JSON data.
*   **Missing Environment Variable:** If an environment variable specified in the `from_env` section is not found in the environment.

In case of an error, the script prints an error message to the console and exits. Warnings are shown for non-critical issues like missing environment variables or JSON keys.

## Contributing

Contributions are welcome! Please submit a pull request with your changes.
