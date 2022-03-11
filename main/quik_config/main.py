import os
from collections import namedtuple

from super_map import Map, LazyDict
from walk_up import walk_up_until
from dict_recursive_update import recursive_update
import ez_yaml
import ruamel.yaml
import regex as re

def find_and_load(file_name, *, parse_args=False, args=None, defaults_for_local_data=[], cd_to_filepath=True):
    """
        Example Python:
            # basic call
            config, path_to, *_ = find_and_load("info.yaml", defaults_for_local_data=["DEV"])
            # full call
            info = find_and_load("info.yaml", defaults_for_local_data=["DEV"], cd_to_filepath=True)
            # parse args from sys.argv (everything after "--")
            info = find_and_load("info.yaml", parse_args=True)
        
        Returns:
            info.config         # the resulting dictionary for all the selected options
            info.path_to            # a dictionary of paths relative to the root_path
            info.absolute_path_to   # same dictionary of paths, but made absolute
            info.unused_args        # all args before a '--' argument
            info.secrets            # (secrets) from the local data file
            info.profile_names      # the dictionary of all possible options
            info.selected_profiles  # the dictionary of the local config-choices files
            info.root_path          # parent folder of the .yaml file
            info.project            # the dictionary to everything inside (project)
            info.local_data         # the local_data file as a dictionary
            info.as_dict            # the dictionary to the whole file (info.yaml)
        
        Example Yaml File:
            (project):
                # paths the code will probably need to use
                (path_to):
                    project_root: "./"
                
                # this is your local-machine config choices
                # (should point to a file that is git-ignored)
                # (this file will be auto-generated with the correct format)
                (local_data): ./local_data.ignore.yaml
                
                # below are options that the config file can choose
                #     when multiple options are selected
                #     their keys/values will be merged recursively
                (profiles):
                    (default):
                        mode: development
                        constants:
                            pi: 3 # pi is 'bout 3 
                    OPTION1:
                        mode: blah blah blah
                    
                    OPTION2:
                        mode: blah2 blah2 blah2
                    
                    OPTION3: !load_yaml_file ./options/opt3.yaml
    """
    
    # 
    # load the yaml
    # 
    if True:
        path = walk_up_until(file_name)
        if path == None:
            raise Exception(f'''\n\nThis is an error while trying to load your local_data file\nI started inside this folder: {os.getcwd()}\nthen I looked for this file: {file_name}\nI checked all the parent folders too and I was unable to find that file.\n\nToDo: Please create that file or possibly run your command from a different directory''')
        root_path = FS.dirname(path)
        if cd_to_filepath: os.chdir(root_path)
        info = ez_yaml.to_object(file_path=path, load_nested_yaml=True)
        project = info.get("(project)", {})
        # TODO: add error if missing

    # 
    # load PATHS
    # 
    if True:
        def make_absolute_root_path(path_string):
            *folders, name, ext = FS.path_pieces(path_string)
            # if there are no folders then it must be a relative path (otherwise it would start with the roo "/" folder)
            if len(folders) == 0:
                folders.append(".")
            # if not absolute, then make it absolute
            if folders[0] != "/":
                if folders[0] == '.' or folders[0] == './':
                    _, *folders = folders
                return FS.absolute_path(FS.join(root_path, path_string))
            return path_string
        def make_relative_path(path_string):
            absolute_path = make_absolute_root_path(path_string)
            return os.path.relpath(absolute_path, root_path)
        
        def recursive_convert(a_dict):
            relative_paths = LazyDict()
            absolute_paths = LazyDict()
            for each_key, each_value in a_dict.items():
                if isinstance(each_value, dict):
                    relative_paths[each_key], absolute_paths[each_key] = recursive_convert(each_value)
                else:
                    relative_paths[each_key], absolute_paths[each_key] = make_relative_path(str(each_value)), make_absolute_root_path(str(each_value))
            return relative_paths, absolute_paths
        
        path_to, absolute_path_to = recursive_convert(project.get("(path_to)", {}))
    
    # 
    # 
    # find selected local_data profiles
    # 
    # 
    if True:
        local_data        = None
        selected_profiles = None
        local_secrets     = {"example": "key29i5805"}
        local_data_path   = project.get("(local_data)", None)
        profile_names     = project.get("(profiles)", {})
        if local_data_path:
            try:
                local_data = ez_yaml.to_object(file_path=local_data_path)
                selected_profiles = local_data.get("(selected_profiles)", [])
                local_secrets     = local_data.get("(secrets)"          , {})
            except Exception as error:
                pass
        # create the default options file if it doesnt exist, but path does
        for each_option in defaults_for_local_data:
            if each_option not in profile_names:
                raise Exception(f"""
                
                    ---------------------------------------------------------------------------------
                    When calling: find_and_load("{path}", defaults_for_local_data= *a list* )
                    `defaults_for_local_data` contained this option: {each_option}
                    
                    However, your info file: {path}
                    only has these options: {list(profile_names.keys())}
                    Inside that file, look for "(project)" -> "(profiles)" -> *option*,
                    
                    LIKELY SOLUTION:
                        Remove {each_option} from the `defaults_for_local_data` in your python file
                    
                    ALTERNATIVE SOLUTIONS:
                        - Fix a misspelling of the option
                        - Add {each_option} to "(profiles)" in {path}
                    ---------------------------------------------------------------------------------
                """.replace("\n                ", "\n"))
        if selected_profiles is None:
            if not isinstance(local_data_path, str):
                selected_profiles = []
                local_secrets = {}
            else:
                FS.create_folder(FS.dirname(local_data_path))
                ez_yaml.to_file(
                    file_path=local_data_path,
                    obj={
                        "(selected_profiles)": defaults_for_local_data,
                        "(secrets)": local_secrets,
                    },
                )
                selected_profiles = list(defaults_for_local_data)
                local_data = { "(selected_profiles)" : selected_profiles }
        config = profile_names.get("(default)", {})
    
    # 
    # merge in all the options data
    # 
    for each_option in reversed(selected_profiles):
        try:
            config = recursive_update(config, profile_names[each_option])
        except KeyError as error:
            raise Exception(f"""
            
                ---------------------------------------------------------------------------------
                Your local config choices in this file: {local_data_path}
                selected these options: {selected_profiles}
                (and there's a problem with this one: {each_option})
                
                Your info file: {path}
                only lists these options available: {list(profile_names.keys())}
                Look for "(project)" -> "(profiles)" -> *option*,to see them
                
                LIKELY SOLUTION:
                    Edit your local config: {local_data_path}
                    And remove "- {each_option}"
                ---------------------------------------------------------------------------------
                
            """.replace("\n                ", "\n"))
            
    # 
    # parse cli arguments
    #
    # TODO:
    #     --profiles=THING,PROD
    #     --help
    if True: 
        if parse_args and args is None:
            import sys
            args = list(sys.argv)
            args.pop(0) # remove the path of the python file
        
        if args is None:
            args = []
        
        # remove up to the first "--" argument
        unused_args = []
        args_copy = list(args)
        while len(args_copy) > 0:
            if args_copy[0] == '--':
                args_copy.pop(0)
                break
            unused_args.append(args_copy.pop(0))
        
        # allow for a little yaml shorthand
        # thing:thing2:value >>> thing: { thing2: value }
        config_args = []
        for each in args_copy:
            match = re.match(r"((?:[a-zA-Z0-9_][a-zA-Z0-9_-]*:)+)([\w\W]*)", each)
            # if shorthand
            if match:
                shorthand_part = match[1]
                value_part = match[2]
                shorthand_parts = shorthand_part.split(":")
                shorthand_parts.pop() # remove the training empty string
                new_begining = ": {".join(shorthand_parts) + ": "
                new_end = "\n"+( "}" * (len(shorthand_parts)-1) )
                config_args.append(new_begining + value_part + new_end)
            else:
                config_args.append(each)
        
        config_data_from_cli = []
        for each_original, each_converted in zip(args_copy, config_args):
            try:
                value = ez_yaml.to_object(string=each_converted)
                if not isinstance(value, dict):
                    raise Exception(f'''the value was not a dictionary''')
                config_data_from_cli.append(value)
            except Exception as error:
                raise Exception(f"""
                
                    ---------------------------------------------------------------------------------
                    When calling: find_and_load("{path}", defaults_for_local_data= *a list* )
                    
                    I was given these arguments: {args_copy}
                    When looking at this argument: {each_original}
                    (which was converted to: '''{each_converted}''' )
                    
                    I tried to parse it as a yaml string, but received an error:
                    
                    __error__
                    {error}
                    __error__
                    
                    
                    LIKELY SOLUTION:
                        Change the argument to be a valid yaml map
                        ex: 'thing: value'
                    ---------------------------------------------------------------------------------
                """.replace("\n                    ", "\n"))
        
        # merge in all the cli data
        for each_dict in config_data_from_cli:
            config = recursive_update(config, each_dict)
    
    
    # convert everything recursively
    recursive_lazy_dict = lambda arg: arg if not isinstance(arg, dict) else LazyDict({ key: recursive_lazy_dict(value) for key, value in arg.items() })
    dict_output = recursive_lazy_dict(dict(
        config=config,
        path_to=path_to,
        absolute_path_to=absolute_path_to,
        unused_args=unused_args,
        secrets=local_secrets,
        profile_names=profile_names,
        selected_profiles=selected_profiles,
        root_path=root_path,
        project=project,
        local_data=local_data,
        as_dict=info,
    ))
    # convert to named tuple for easier argument unpacking
    Info = namedtuple('Info', " ".join(list(dict_output.keys())))
    return Info(**dict_output)

import sys
import os
from os.path import isabs, isfile, isdir, join, dirname, basename, exists, splitext, relpath
from os import remove, getcwd, makedirs, listdir, rename, rmdir, system
from shutil import move
from pathlib import Path
import glob
import shutil

# 
# create a class for generate filesystemtem management
# 
class FileSystem():
    @classmethod
    def write(self, data, to=None):
        # make sure the path exists
        FileSystem.create_folder(os.path.dirname(to))
        with open(to, 'w') as the_file:
            the_file.write(str(data))
    
    @classmethod
    def read(self, filepath):
        try:
            with open(filepath,'r') as f:
                output = f.read()
        except:
            output = None
        return output    
        
    @classmethod
    def delete(self, filepath):
        if isdir(filepath):
            shutil.rmtree(filepath)
        else:
            try:
                os.remove(filepath)
            except:
                pass
    
    @classmethod
    def create_folder(self, path):
        try:
            os.makedirs(path)
        except:
            pass
        
    @classmethod
    def copy(self, from_=None, to=None, new_name="", force= True):
        if new_name == "":
            raise Exception('FileSystem.copy() needs a new_name= argument:\n    FileSystem.copy(from_="location", to="directory", new_name="")\nif you want the name to be the same as before do new_name=None')
        elif new_name is None:
            new_name = os.path.basename(from_)
        
        # get the full path
        to = os.path.join(to, new_name)
        # if theres a file in the target, delete it
        if force and FileSystem.exists(to):
            FileSystem.delete(to)
        # make sure the containing folder exists
        FileSystem.create_folder(os.path.dirname(to))
        if os.path.isdir(from_):
            shutil.copytree(from_, to)
        else:
            return shutil.copy(from_, to)
    
    @classmethod
    def move(self, from_=None, to=None, new_name="", force= True):
        if new_name == "":
            raise Exception('FileSystem.move() needs a new_name= argument:\n    FileSystem.move(from_="location", to="directory", new_name="")\nif you want the name to be the same as before do new_name=None')
        elif new_name is None:
            new_name = os.path.basename(from_)
        
        # get the full path
        to = os.path.join(to, new_name)
        # make sure the containing folder exists
        FileSystem.create_folder(os.path.dirname(to))
        shutil.move(from_, to)
    
    @classmethod
    def exists(self, *args):
        return FileSystem.does_exist(*args)
    
    @classmethod
    def does_exist(self, path):
        return os.path.exists(path)
    
    @classmethod
    def is_folder(self, *args):
        return FileSystem.is_directory(*args)
        
    @classmethod
    def is_dir(self, *args):
        return FileSystem.is_directory(*args)
        
    @classmethod
    def is_directory(self, path):
        return os.path.isdir(path)
    
    @classmethod
    def is_file(self, path):
        return os.path.isfile(path)

    @classmethod
    def list_files(self, path="."):
        return [ x for x in FileSystem.ls(path) if FileSystem.is_file(x) ]
    
    @classmethod
    def list_folders(self, path="."):
        return [ x for x in FileSystem.ls(path) if FileSystem.is_folder(x) ]
    
    @classmethod
    def ls(self, filepath="."):
        glob_val = filepath
        if os.path.isdir(filepath):
            glob_val = os.path.join(filepath, "*")
        return glob.glob(glob_val)

    @classmethod
    def touch(self, path):
        FileSystem.create_folder(FileSystem.dirname(path))
        if not FileSystem.exists(path):
            FileSystem.write("", to=path)
    
    @classmethod
    def touch_dir(self, path):
        FileSystem.create_folder(path)
    
    @classmethod
    def dirname(self, path):
        return os.path.dirname(path)
    
    @classmethod
    def basename(self, path):
        return os.path.basename(path)
    
    @classmethod
    def extname(self, path):
        filename, file_extension = os.path.splitext(path)
        return file_extension
    
    @classmethod
    def path_pieces(self, path):
        """
        example:
            *folders, file_name, file_extension = FileSystem.path_pieces("/this/is/a/filepath.txt")
        """
        folders = []
        while 1:
            path, folder = os.path.split(path)

            if folder != "":
                folders.append(folder)
            else:
                if path != "":
                    folders.append(path)

                break
        folders.reverse()
        *folders, file = folders
        filename, file_extension = os.path.splitext(file)
        return [ *folders, filename, file_extension ]
    
    @classmethod
    def join(self, *paths):
        return os.path.join(*paths)
    
    @classmethod
    def absolute_path(self, path):
        return os.path.abspath(path)
    
    @classmethod
    def make_absolute_path(self, path):
        return os.path.abspath(path)
    
    @classmethod
    def make_relative_path(self, *, to, coming_from):
        return os.path.relpath(to, coming_from)

    @classmethod
    def pwd(self):
        return os.getcwd()

FS = FileSystem