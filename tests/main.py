from quik_config import find_and_load

# NOTE: intentionally changes directories to be in the same folder as the config
config = find_and_load("main/info.yaml").config # will keep going up a directories looking for the file
print(f'''config.has_gpu = {config.has_gpu}''')
print(f'''config.constants.pi = {config.constants.pi}''')

# same as above but will not change your directory
config = find_and_load("main/info.yaml", go_to_root=False).config