from quik_config import find_and_load
import sys

print(f'''sys.argv = {sys.argv}''')

(
    config,
    path_to,
    absolute_path_to,
    project,
    root_path,
    configuration_choices,
    configuration_options,
    as_dict,
    unused_args,
) = find_and_load("main/info.yaml", parse_args=True, default_options=["DEV"], cd_to_filepath=True)

print(f'''config = {config}''')
print(f'''path_to = {path_to}''')
print(f'''absolute_path_to = {absolute_path_to}''')