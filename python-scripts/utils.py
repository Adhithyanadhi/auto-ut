import logging
import json
import constants
import os
import config

def read_file_contents(path):
    if not path:
        logging.error(f"File path cannot be empty {path}", exc_info  =  True)
        raise Exception(f"File path cannot be empty {path}")
    file  =  open(path, "r")
    file_contents  =  file.read()
    file.close()
    return file_contents

def write_to_file(content, path):
    if not path:
        logging.error(f"Write: File path cannot be empty {path}", exc_info = True)
        raise Exception(f"Write: File path cannot be empty {path}")
    f = open(path, "w")
    f.write(content)
    f.close()
    
def set_coverage_file():
    if os.path.isfile(constants.CWD+"/coverage.sh"):
        constants.RUN_COVERAGE_FILE = "coverage.sh"
    elif os.path.isfile(constants.CWD+"/run_coverage.sh"):
        constants.RUN_COVERAGE_FILE = "run_coverage.sh"
    else:
        logging.error(f"coverage.sh file not found", exc_info = True)
        raise Exception(f"coverage.sh file not found")        

def initialize_interface_file_name_map():
    if not os.path.isfile(constants.CWD+"/interface_map.json"):
        config.map_all_interfaces_with_file()
    interface_map_contents = read_file_contents("interface_map.json")
    constants.INTERFACE_FILE_NAME_MAP = json.loads(interface_map_contents)

def initialize_struct_file_name_map():
    if not os.path.isfile(constants.CWD+"/struct_map.json"):
        config.map_all_structs_with_file()
    struct_map_contents = read_file_contents("struct_map.json")
    constants.STRUCT_FILE_NAME_MAP = json.loads(struct_map_contents)
    
def append_to_file(content, path):
    if not path:
        logging.error(f"Append: File path cannot be empty {path}", exc_info = True)
        raise Exception(f"Append: File path cannot be empty {path}")
    if not os.path.isfile(path):
        logging.error(f"Append: File not found {path}", exc_info = True)
        raise Exception(f"Append: File not found {path}")
    f = open(path, "a")
    f.write(content)
    f.close()
