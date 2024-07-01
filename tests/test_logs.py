from quik_config import find_and_load

# NOTE: intentionally changes directories to be in the same folder as the config
config, path_to, *_ = find_and_load(
    "tests/info.yaml",
    parse_args=True,
    cd_to_filepath=True,
    defaults_for_local_data=["DEV"],
    path_from_config_to_log_folder="../logs/autolog",
)
print(f'''config = {config}''')