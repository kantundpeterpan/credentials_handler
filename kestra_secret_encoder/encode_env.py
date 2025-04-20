import json
import base64
import argparse
import yaml
import os
import toml

def encode_secrets_docker(mapping_file_path, output_env_file, prefix):
    process_secrets(mapping_file_path, output_env_file, prefix, False)

def encode_secrets_kestra(mapping_file_path, output_env_file):
    process_secrets(mapping_file_path, output_env_file, "SECRET_", True)

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

    def set_nested_value(data, keys, value):
        """Sets a nested value in a dictionary given a list of keys."""
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value

    # Process from_env section
    if 'from_env' in mapping_config:
        for env_var, toml_key in mapping_config['from_env'].items():
            value = os.environ.get(env_var)
            if value is None:
                print(f"Warning: Environment variable '{env_var}' not found, skipping.")
                continue

            keys = toml_key.split('__')  # Split TOML key by '__' for nested structure
            try:
                set_nested_value(secrets_toml_data, keys, value)
            except Exception as e:
                print(f"Error setting value for key '{toml_key}': {e}")
                return

    # Iterate through the YAML mapping and update values in the secrets.toml data
    for section_header, mappings in mapping_config.items():
        if section_header in ['files', 'from_env']:
            continue  # Skip 'files' and 'from_env' sections

        for mapping_key, toml_key in mappings.items():
            keys = toml_key.split('__')  # Split TOML key by '__' for nested structure
            try:
                set_nested_value(secrets_toml_data, keys, mapping_key)
            except Exception as e:
                print(f"Error setting value for key '{toml_key}': {e}")
                return
            
    # Write the updated secrets_toml_data to the output file
    try:
        with open(secrets_toml_path, 'w') as f:
            toml.dump(secrets_toml_data, f)
        print(f"Successfully updated secrets.toml data and saved to {secrets_toml_path}")
    except Exception as e:
        print(f"Error writing to {secrets_toml_path}: {e}")


def process_secrets(mapping_file_path, output_env_file, prefix, mustbase64):
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


def main():
    parser = argparse.ArgumentParser(description="Encode secrets from JSON files to an .env file for different destinations using a YAML mapping.")
    parser.add_argument("mapping_file", help="Path to the YAML mapping file")
    parser.add_argument("target_tool", choices=['docker', 'kestra', 'dlt_dest_bigquery'], help="Tool credentials are encoded for")
    parser.add_argument("-o", "--output", dest="output_file", default="secrets.toml", help="Path to the output .env file (default: secrets.toml)")
    parser.add_argument("-p", "--prefix", dest="prefix", default="SECRET_", help="Prefix for the environment variables (default: SECRET_)")

    # Conditional arguments for dlt_dest_bigquery
    group = parser.add_argument_group('dlt_dest_bigquery arguments', 'These arguments are required when target_tool is dlt_dest_bigquery')
    group.add_argument("--secrets_toml", dest="secrets_toml", help="Path to the secrets.toml file", required=False)


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


if __name__ == "__main__":
    main()