import json
import base64
import argparse
import yaml
import os
import toml

def encode_secrets_docker(mapping_file_path, output_env_file, prefix):
    """Encodes secrets for Docker, writing them to an .env file with a given prefix."""
    process_secrets(mapping_file_path, output_env_file, prefix, False)

def encode_secrets_kestra(mapping_file_path, output_env_file):
    """Encodes secrets for Kestra, writing them to an .env file with the prefix 'SECRET_' and base64 encoding."""
    process_secrets(mapping_file_path, output_env_file, "SECRET_", True)

def export_to_env(mapping_file_path, prefix):
    """Prints secrets to stdout, prefixed for Docker."""
    process_secrets_stdout(mapping_file_path, prefix, False)

def encode_secrets_dlt_dest_bigquery(mapping_file_path, secrets_toml_path):
    """
    Encodes secrets for dlt_dest_bigquery by reading a secrets.toml file,
    mapping values from a YAML mapping file, and replacing values in the
    secrets.toml file based on the mapping.
    """
    print(secrets_toml_path)
    try:
        with open(secrets_toml_path, 'r') as f:
            secrets_toml_data = toml.load(f)

    except FileNotFoundError:
        print(f"Error: secrets.toml file not found: {secrets_toml_path}")
        return
    
    except toml.TomlDecodeError as e:
        print(f"Error: Invalid TOML in secrets.toml file: {secrets_toml_path}\n{e}")
        return

    try:
        with open(mapping_file_path, 'r') as f:
            mapping_config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Mapping file not found: {mapping_file_path}")
        return
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in mapping file: {mapping_file_path}\n{e}")
        return

    if 'files' not in mapping_config and 'from_env' not in mapping_config:
        print("Error: Neither 'files' nor 'from_env' section found in the YAML configuration.")
        return

    file_data = {}
    if 'files' in mapping_config:
        for file_header, file_path in mapping_config['files'].items():
            try:
                with open(file_path, 'r') as f:
                    file_data[file_header] = json.load(f)
            except FileNotFoundError:
                print(f"Error: File not found: {file_path}")
                return
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in file: {file_path}")
                return

    def set_nested_value(data, keys, value):
        """Sets a nested value in a dictionary given a list of keys, only if the path exists."""
        current_data = data
        for key in keys[:-1]:
            if isinstance(current_data, dict) and key.lower() in current_data:
                current_data = current_data[key.lower()]
            else:
                return False  # Path does not exist
        if isinstance(current_data, dict) and keys[-1].lower() in current_data:
            current_data[keys[-1].lower()] = value
            return True
        else:
            return False

    # Process from_env section
    if 'from_env' in mapping_config:
        for env_var, toml_key in mapping_config['from_env'].items():
            value = os.environ.get(env_var)
            if value is None:
                print(f"Warning: Environment variable '{env_var}' not found, skipping.")
                continue

            keys = toml_key.split('__')  # Split TOML key by '__' for nested structure
            
            if not set_nested_value(secrets_toml_data, keys, value):
                print(f"Warning: TOML key '{keys}' not found in secrets.toml, skipping.")
                
    # Iterate through the YAML mapping and update values in the secrets.toml data
    for section_header, mappings in mapping_config.items():
        if section_header in ['files', 'from_env']:
            continue  # Skip 'files' and 'from_env' sections

        if section_header not in file_data:
            print(f"Section header '{section_header}' not found, assuming direct mapping.")
            for mapping_key, toml_key in mappings.items():
                print(toml_key)
                keys = toml_key.split('__')  # Split TOML key by '__' for nested structure
                if not set_nested_value(secrets_toml_data, keys, mapping_key):
                    print(f"Warning: TOML key '{toml_key}' not found in secrets.toml, skipping.")
            continue


        data = file_data[section_header]

        for mapping_key, toml_key in mappings.items():
            if mapping_key not in data:
                print(f"Warning: Key '{mapping_key}' not found in JSON data for file header '{section_header}', skipping.")
                continue
            value = data[mapping_key]
            keys = toml_key.split('__')  # Split TOML key by '__' for nested structure
            if not set_nested_value(secrets_toml_data, keys, value):
                print(f"Warning: TOML key '{keys}' not found in secrets.toml, skipping.")

            
    # Write the updated secrets_toml_data to the output file
    try:
        with open(secrets_toml_path, 'w') as f:
            toml.dump(secrets_toml_data, f)
        print(f"Successfully updated secrets.toml data and saved to {secrets_toml_path}")
    except Exception as e:
        print(f"Error writing to {secrets_toml_path}: {e}")


def process_secrets(mapping_file_path, output_env_file, prefix, mustbase64):
    """Processes secrets based on a YAML mapping file, writing them to an .env file."""
    try:
        with open(mapping_file_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Mapping file not found: {mapping_file_path}")
        return
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in mapping file: {mapping_file_path}\n{e}")
        return

    if 'files' not in config and 'from_env' not in config:
        print("Error: Neither 'files' nor 'from_env' section not found in the YAML configuration.")
        return

    if 'files' in config:
        file_data = {}
        for file_header, file_path in config['files'].items():
            try:
                with open(file_path, 'r') as f:
                    file_data[file_header] = json.load(f)
            except FileNotFoundError:
                print(f"Error: File not found: {file_path}")
                return
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in file: {file_path}")
                return

    with open(output_env_file, 'w') as env_file:
        for section_header, mappings in config.items():
            if section_header == 'files':
                continue

            if section_header == 'from_env':
                for env_var, env_key in mappings.items():
                    value = os.environ.get(env_var)
                    if value is None:
                        print(f"Warning: Environment variable '{env_var}' not found, skipping.")
                        continue
                    encoded_value = base64.b64encode(str(value).encode('utf-8')).decode('utf-8') if mustbase64 else value
                    env_file.write(f"{prefix}{env_key}={encoded_value.replace('\n', '\\n')}" + "\n")
                continue

            if section_header not in file_data:
                print(f"Warning: File header '{section_header}' not found in file data, skipping mappings for this file.")
                continue
            
            data = file_data[section_header]

            for json_key, env_key in mappings.items():
                if json_key not in data:
                    print(f"Warning: Key '{json_key}' not found in JSON data for file header '{section_header}', skipping.")
                    continue
                value = data[json_key]
                encoded_value = base64.b64encode(str(value).encode('utf-8')).decode('utf-8') if mustbase64 else value
                env_file.write(f"{prefix}{env_key}={encoded_value}\n")

    print(f"Successfully encoded secrets using mapping from {mapping_file_path} and saved to {output_env_file}")

import logging

def process_secrets_stdout(mapping_file_path, prefix, mustbase64):
    """Processes secrets based on a YAML mapping file, printing to stdout."""
    logging.basicConfig(level=logging.WARNING)

    try:
        with open(mapping_file_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Mapping file not found: {mapping_file_path}")
        return
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in mapping file: {mapping_file_path}\n{e}")
        return

    if 'files' not in config and 'from_env' not in config:
        print("Error: Neither 'files' nor 'from_env' section not found in the YAML configuration.")
        return

    if 'files' in config:
        file_data = {}
        for file_header, file_path in config['files'].items():
            try:
                with open(file_path, 'r') as f:
                    file_data[file_header] = json.load(f)
            except FileNotFoundError:
                print(f"Error: File not found: {file_path}")
                return
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in file: {file_path}")
                return

    for section_header, mappings in config.items():
        if section_header == 'files':
            continue

        if section_header == 'from_env':
            for env_var, env_key in mappings.items():
                value = os.environ.get(env_var)
                if value is None:
                    logging.warning(f"Environment variable '{env_var}' not found, skipping.")
                    continue
                encoded_value = base64.b64encode(str(value).encode('utf-8')).decode('utf-8') if mustbase64 else value
                print(f"{prefix}{env_key}={encoded_value.replace('\n', '\\n')}")
            continue

        if section_header not in file_data:
            logging.warning(f"File header '{section_header}' not found in file data, skipping mappings for this file.")
            continue

        data = file_data[section_header]

        for json_key, env_key in mappings.items():
            if json_key not in data:
                logging.warning(f"Key '{json_key}' not found in JSON data for file header '{section_header}', skipping.")
                continue
            value = data[json_key]
            encoded_value = base64.b64encode(str(value).encode('utf-8')).decode('utf-8') if mustbase64 else value
            print(f"export {prefix}{env_key}='{encoded_value.replace('\n', '\\n')}'")
           

    # print(f"Successfully encoded secrets using mapping from {mapping_file_path} and printed to stdout.")


def main():
    parser = argparse.ArgumentParser(description="Encode secrets from JSON files or environment variables to an .env file or TOML file for different destinations using a YAML mapping.")
    parser.add_argument("mapping_file", help="Path to the YAML mapping file.  This file defines how to map JSON file contents and environment variables to environment variables or TOML keys.")
    parser.add_argument("target_tool", choices=['docker', 'kestra', 'dlt_dest_bigquery', 'export_to_env'], help="Tool for which credentials are encoded.")
    parser.add_argument("-o", "--output", dest="output_file", default=".env_encoded", help="Path to the output .env file (used for Docker and Kestra, default: .env_encoded).")
    parser.add_argument("-p", "--prefix", dest="prefix", default="SECRET_", help="Prefix for the environment variables (used for Docker, default: SECRET_).")

    # Conditional arguments for dlt_dest_bigquery
    group = parser.add_argument_group('dlt_dest_bigquery arguments', 'These arguments are required when target_tool is dlt_dest_bigquery')
    group.add_argument("--secrets_toml", dest="secrets_toml", help="Path to the secrets.toml file to be modified", required=False)


    args = parser.parse_args()

    if args.target_tool == 'docker':
        encode_secrets_docker(args.mapping_file, args.output_file, args.prefix)
    elif args.target_tool == 'kestra':
        encode_secrets_kestra(args.mapping_file, args.output_file)
    elif args.target_tool == 'dlt_dest_bigquery':
        print(args.target_tool)
        # Check if required arguments are provided
        if not (args.secrets_toml):
            parser.error("When target_tool is dlt_dest_bigquery, --secrets_toml is required.")
        encode_secrets_dlt_dest_bigquery(args.mapping_file, args.secrets_toml) #Even though not needed, required by the function interface
    elif args.target_tool == 'export_to_env':
        export_to_env(args.mapping_file, args.prefix)


if __name__ == "__main__":
    main()
