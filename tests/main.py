from quik_config import find_and_load

# NOTE: intentionally changes directories to be in the same folder as the config
config, path_to, *_ = find_and_load("main/info.yaml", default_options=["DEV"])
print(f'''config.has_gpu = {config.has_gpu}''')
print(f'''config.constants.pi = {config.constants.pi}''')

# same as above but will not change your directory
config = find_and_load("main/info.yaml", cd_to_filepath=False).config

# get the info object
info = find_and_load("info.yaml", default_options=["DEV"], cd_to_filepath=True)

print(f'''info = {info}''')