from quik_config import find_and_load

# NOTE: intentionally changes directories to be in the same folder as the config
config, path_to, *_ = find_and_load("main/info.yaml", defaults_for_local_data=["DEV"])
print(f'''config.has_gpu = {config.has_gpu}''')
print(f'''config.constants.pi = {config.constants.pi}''')

# same as above but will not change your directory
config = find_and_load("main/info.yaml", cd_to_filepath=False).config

# get the info object
info = find_and_load("info.yaml", defaults_for_local_data=["DEV"], cd_to_filepath=True)

(
    config,
    path_to,
    absolute_path_to,
    project,
    root_path,
    configuration_choices,
    configuration_options,
    as_dict,
) = find_and_load("info.yaml", defaults_for_local_data=["DEV"])

print(f'''info = {info.config}''')
print(f'''config = {config}''')
print(f'''path_to = {path_to}''')
print(f'''absolute_path_to = {absolute_path_to}''')