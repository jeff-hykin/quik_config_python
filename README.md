# What is this?

The most flexible file+cli config for python projects
- stop hardcoding filepaths
- stop wasing time using `argparse`
- stop with messy config differences for different machines

# How do I use this?

`pip install quik-config`

Create a config file like `info.yaml` with a structure like this:
```yaml
# NOTE: names in parentheses are special, all other names are not!
(project):
    
    # a central place for filepaths
    (path_to):
        this_file:       "./info.yaml"
        blah_file:       "./data/results.txt"
        blahblah_folder: "./data/"
    
    # git-ignore this file path! (file will be generated automatically)
    (local_data): ./local_data.ignore.yaml
            # this^ is where you choose which profile(s)
            # and is where to store auth tokens and other secrets
    
    (profiles):
        (default):
            blah: "blah blah blah"
            mode: development # or production. Same thing really
            has_gpu: maybe
            constants:
                pi: 3 # its 'bout 3 
        
        PROFILE1:
            constants:
                pi: 3.1415926536
                e: 2.7182818285
        
        PROD:
            mode: production
            constants:
                pi: 3.1415926536
                problems: true
        
        PROFILE2:
            constants:
                pi: 3.14
                e: 2.72
        
        TEST:
            mode: testing
        
        GPU:
            has_gpu: true
        
```

Then load in your config in python!

```python
from quik_config import find_and_load

info = find_and_load(
    "info.yaml",
    cd_to_filepath=True,
    parse_args=True,
    defaults_for_local_data=["PROFILE1", "PROD"],
)
# (generates the ./local_data.ignore.yaml if you dont have it)
# loads whatever profiles are mentioned in ./local_data.ignore.yaml 

# Use the data!
print(info.config)
# {
#     "mode": "production",     # from PROD
#     "has_gpu": False,         # from (default)
#     "constants": {
#         "pi": 3.1415926536,   # from PROFILE1
#         "e": 2.7182818285,    # from PROFILE1
#         "problems": True,     # from PROD
#     },
# }
print(info.config.mode)
print(info.config["mode"])
print(info.config.constants.problems)
```

## Different Profiles For Different Machines

Lets say you've got an info.yaml like this:
```yaml
(project):
    name: Example Project1
    poorly_maintained: true
    bug_report_url: https://stackoverflow.com/questions/
    
    
    (local_data): ./local_data.ignore.yaml
    (profiles):
        DEV:
            cores: 1
            database_ip: 192.168.10.10
            mode: dev
        LAPTOP:
            cores: 2
        DESKTOP:
            cores: 8
        UNIX:
            line_endings: "\n"
        WINDOWS:
            line_endings: "\r\n"
        PROD:
            database_ip: 183.177.10.83
            mode: prod
            cores: 32
```

On your Macbook you can edit the `./local_data.ignore.yaml` (or your equivlent) to include something like the following:
```yaml
(selected_profiles):
    - LAPTOP # the cores:2 is used (instead of cores:1 from DEV)
    - UNIX   #     because LAPTOP is higher in the list than DEV
    - DEV
```

On your Windows laptop you can edit it and put:
```yaml
(selected_profiles):
    - LAPTOP
    - WINDOWS
    - DEV
```

## Command Line Arguments

If you have `run.py` like this:

```python
from quik_config import find_and_load

info = find_and_load("info.yaml", parse_args=True)

print("config:",      info.config     )
print("unused_args:", info.unused_args)

# 
# call some other function you've got
# 
#from your_code import run
#run(*info.unused_args)
```

### Example 1

Then run this in the command line:

```shell
python ./run.py
```

Lets say these are the default config values:
```
config: {
    "mode": "development",
    "has_gpu": False,
    "constants": {
        "pi": 3
    }
}
unused_args: []
```

### Example 2

Again but with arguments:

```shell
python ./run.py arg1 --  mode:my_custom_mode  constants:tau:6.2831853072
```

It only looks at args after the `--`. So it looks like:

```
config: {
    "mode": "my_custom_mode",
    "has_gpu": False,
    "constants": {
        "pi": 3,
        "tau": 6.2831853072,
    },
}
unused_args: ["arg1"]
```

### Example 3

Again but with really complicated arguments: <br>
(each argument is parsed as yaml!)

```shell
python ./run.py arg1 --  mode:my_custom_mode  'constants: { tau: 6.2831853072, pi: 3.1415926, reserved_letters: [ "C", "K", "i" ] }'
```

prints:

```
config: {
    "mode": "my_custom_mode", 
    "has_gpu": False, 
    "constants": {
        "pi": 3.1415926, 
        "tau": 6.2831853072, 
        "reserved_letters": ["C", "K", "i", ], 
    }, 
}
unused_args: ["arg1"]
```