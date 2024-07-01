from quik_config import find_and_load, FS

# 
# delete autolog folder
# 
info = find_and_load(
    "tests/info.yaml",
    parse_args=True,
    cd_to_filepath=True,
    path_from_config_to_log_folder="../logs/autolog",
)
print(f'''info.log_folder = {info.log_folder}''')
FS.delete(info.log_folder)


# 
# try with details
# 
config, path_to, *_ = find_and_load(
    "tests/info.yaml",
    parse_args=True,
    cd_to_filepath=True,
    defaults_for_local_data=["DEV"],
    path_from_config_to_log_folder="../logs/autolog",
    config_initial_namer=lambda **_: "hi1_",
    run_namer=lambda run_index, **_: f"run/hi2_{run_index}",
    config_renamer=lambda **_: "hi3",
)

# 
# try without details
# 
config, path_to, *_ = find_and_load(
    "tests/info.yaml",
    parse_args=True,
    cd_to_filepath=True,
    defaults_for_local_data=["DEV"],
    path_from_config_to_log_folder="../logs/autolog",
)
print(f'''config = {config}''')