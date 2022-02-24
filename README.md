# What is this?

A nice way to integrate a generic config file into the rest of your project

# How do I use this?

`pip install quik-config`

Create a config file like `info.yaml` with a structure like this:
```yaml
# NOTE: names in parentheses are special
# all other names are not special
(project):
    # paths the code will probably need to use
    (path_to):
        project_root: "./"
    
    # this is your local-machine config choices
    # (should point to a file that is git-ignored)
    # (this file will be auto-generated with the correct format)
    (configuration): ./configuration.ignore.yaml
    
    # below are options that the config file can choose
    #     when multiple options are selected
    #     their keys/values will be merged recursively
    (configuration_options):
        (default):
            mode: development
            has_gpu: false
            constants:
                pi: 3 # its 'bout 3 
        
        DEV:
            mode: development
        
        PROD:
            mode: production
            has_gpu: true
        
        TEST:
            mode: testing
        
        GPU:
            has_gpu: true
        
```


```python
from quik_config import find_and_load

# NOTE: intentionally changes directories to be in the same folder as the config
config = find_and_load("info.yaml", default_options=["DEV"]).config # will keep going up a directories looking for the file
print(f'''config.has_gpu = {config.has_gpu}''')
print(f'''config.constants.pi = {config.constants.pi}''')

# same as above but will not change your directory
config = find_and_load("info.yaml", default_options=["DEV"], cd_to_filepath=False,).config

# returns more than just config
info = find_and_load("info.yaml", default_options=["DEV"])
info.config         # the resulting dictionary for all the selected options
info.path_to               # a dictionary of paths relative to the root_path
info.absolute_path_to      # same dictionary of paths, but made absolute
info.project               # the dictionary to everything inside (project)
info.root_path             # parent folder of the .yaml file
info.configuration_choices # the dictionary of the local config-choices files
info.configuration_options # the dictionary of all possible options
info.as_dict               # the dictionary to the whole file (info.yaml)

```
