import os

from super_map import Map, LazyDict
from walk_up import walk_up_until
from dict_recursive_update import recursive_update
import ez_yaml

def find_and_load(file_name, *, default_options=[], go_to_root=True):
    """
    (project):
        (path_to):
            config_file: "./"
        
        # this is your local-machine config choices
        # (should point to a file that is git-ignored)
        # (file will be auto-generated with the correct format)
        (configuration): ./configuration.ignore.yaml
        
        # all possible options that the config file can choose
        (configuration_options):
            (default):
                mode: development
                has_gpu: false
            
            PROD:
                mode: production
                has_gpu: true
            
            TEST:
                mode: testing
            
            GPU:
                has_gpu: true
            
    """
    path = walk_up_until(file_name)
    root_path = FS.dirname(path)
    if go_to_root: os.chdir(root_path)
    # 
    # load the yaml
    # 
    info = ez_yaml.to_object(file_path=path,)
    project = info.get("(project)", {})
    # TODO: add error if missing

    # 
    # load PATHS
    # 
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
        try:
            a_dict.items()
        except Exception as error:
            print(f'''a_dict = {a_dict}''')
        for each_key, each_value in a_dict.items():
            if isinstance(each_value, dict):
                relative_paths[each_key], absolute_paths[each_key] = recursive_convert(each_value)
            else:
                relative_paths[each_key], absolute_paths[each_key] = make_relative_path(str(each_value)), make_absolute_root_path(str(each_value))
        return relative_paths, absolute_paths
    
    path_to, absolute_path_to = recursive_convert(project.get("(path_to)", {}))
    
    
    # 
    # configuration
    # 
    configuration = None
    local_options = None
    local_options_path = project.get("(configuration)", None)
    if local_options_path:
        try:
            configuration = ez_yaml.to_object(file_path=local_options_path)
            local_options = configuration.get("(selected_options)", [])
        except Exception as error:
            pass
    # create the default options file if it doesnt exist, but path does
    if local_options is None:
        if isinstance(local_options_path, str):
            FS.create_folder(FS.dirname(local_options_path))
            ez_yaml.to_file(
                file_path=local_options_path,
                obj={ "(selected_options)": default_options },
            )
        local_options = list(default_options)
        configuration = { "(selected_options)" : local_options }
    configuration_options = project.get("(configuration_options)", {})
    config = configuration_options.get("(default)", {})
    # merge in all the other options
    for each_option in reversed(local_options):
        try:
            config = recursive_update(config, configuration_options[each_option])
        except KeyError as error:
            raise Exception(f"""
            
                Tried to load the "{each_option}" from (project) (configuration_options) inside "{path}"
                This option was from your options list: {local_options}
                But that option doesn't seem to exist in the (configuration_options)
                The available options are: {list(configuration_options.keys())}
                
            """.replace("\n                ", "\n"))
    
    # create a helper for recursive converting to lazy dict (much more useful than a regular dict)
    recursive_lazy_dict = lambda arg: arg if not isinstance(arg, dict) else LazyDict({ key: recursive_lazy_dict(value) for key, value in arg.items() })
    
    return recursive_lazy_dict(dict(
        config=config,
        info=info,
        project=project,
        root_path=root_path,
        path_to=path_to,
        absolute_path_to=absolute_path_to,
        configuration=configuration,
        configuration_options=configuration_options,
    ))

import sys
import os
from os.path import isabs, isfile, isdir, join, dirname, basename, exists, splitext, relpath
from os import remove, getcwd, makedirs, listdir, rename, rmdir, system
from shutil import move
from pathlib import Path
import glob
import shutil

# 
# create a class for generate filesystem management
# 
class FileSys():
    @classmethod
    def write(self, data, to=None):
        # make sure the path exists
        FileSys.create_folder(os.path.dirname(to))
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
            raise Exception('FileSys.copy() needs a new_name= argument:\n    FileSys.copy(from_="location", to="directory", new_name="")\nif you want the name to be the same as before do new_name=None')
        elif new_name is None:
            new_name = os.path.basename(from_)
        
        # get the full path
        to = os.path.join(to, new_name)
        # if theres a file in the target, delete it
        if force and FileSys.exists(to):
            FileSys.delete(to)
        # make sure the containing folder exists
        FileSys.create_folder(os.path.dirname(to))
        if os.path.isdir(from_):
            shutil.copytree(from_, to)
        else:
            return shutil.copy(from_, to)
    
    @classmethod
    def move(self, from_=None, to=None, new_name="", force= True):
        if new_name == "":
            raise Exception('FileSys.move() needs a new_name= argument:\n    FileSys.move(from_="location", to="directory", new_name="")\nif you want the name to be the same as before do new_name=None')
        elif new_name is None:
            new_name = os.path.basename(from_)
        
        # get the full path
        to = os.path.join(to, new_name)
        # make sure the containing folder exists
        FileSys.create_folder(os.path.dirname(to))
        shutil.move(from_, to)
    
    @classmethod
    def exists(self, *args):
        return FileSys.does_exist(*args)
    
    @classmethod
    def does_exist(self, path):
        return os.path.exists(path)
    
    @classmethod
    def is_folder(self, *args):
        return FileSys.is_directory(*args)
        
    @classmethod
    def is_dir(self, *args):
        return FileSys.is_directory(*args)
        
    @classmethod
    def is_directory(self, path):
        return os.path.isdir(path)
    
    @classmethod
    def is_file(self, path):
        return os.path.isfile(path)

    @classmethod
    def list_files(self, path="."):
        return [ x for x in FileSys.ls(path) if FileSys.is_file(x) ]
    
    @classmethod
    def list_folders(self, path="."):
        return [ x for x in FileSys.ls(path) if FileSys.is_folder(x) ]
    
    @classmethod
    def ls(self, filepath="."):
        glob_val = filepath
        if os.path.isdir(filepath):
            glob_val = os.path.join(filepath, "*")
        return glob.glob(glob_val)

    @classmethod
    def touch(self, path):
        FileSys.create_folder(FileSys.dirname(path))
        if not FileSys.exists(path):
            FileSys.write("", to=path)
    
    @classmethod
    def touch_dir(self, path):
        FileSys.create_folder(path)
    
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
            *folders, file_name, file_extension = FileSys.path_pieces("/this/is/a/filepath.txt")
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
    def pwd(self):
        return os.getcwd()

FS = FileSys