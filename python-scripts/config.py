import utils
import ut_regex
import constants
import re
import json
import os
import sys

def map_all_interfaces_with_file():
    folders = ["/service/v1", "/utils", "/db", "/es", "/scripts"]
    interface_file_name_map_json = {}
    
    for folder in folders:
        filenames = next(os.walk(constants.CWD+folder), (None, None, []))[2]
        for file_name in filenames:
            file_path = constants.CWD+folder+"/"+file_name
            file_contents = utils.read_file_contents(file_path).split("\n")
            for line in file_contents:
                line = line.strip()
                if not line:
                    continue
                regex_result = list(set(re.compile(ut_regex.INTERFACE_DECLARATION).findall(line)))
                for interface in regex_result:
                    if len(regex_result) > 0:
                        interface_file_name_map_json[interface] = folder+"/"+file_name
                    
    utils.write_to_file(json.dumps(interface_file_name_map_json), constants.CWD+"/interface_map.json")


def map_all_structs_with_file():
    folders = ["/models", "/resources"]
    struct_file_name_map_json = {}
    
    for folder in folders:
        struct_file_name_map_json[folder[1:]] = {}
        filenames = next(os.walk(constants.CWD+folder), (None, None, []))[2]
        for file_name in filenames:
            file_path = constants.CWD+folder+"/"+file_name
            file_contents = utils.read_file_contents(file_path).split("\n")
            for line in file_contents:
                line = line.strip()
                if not line:
                    continue
                regex_result = list(set(re.compile(ut_regex.STRUCT_DECLARATION).findall(line)))
                for struct in regex_result:
                    if len(regex_result) > 0:
                        struct_file_name_map_json[folder[1:]][struct] = folder+"/"+file_name
                    
    utils.write_to_file(json.dumps(struct_file_name_map_json), constants.CWD+"/struct_map.json")


def main():
    
    if len(sys.argv) > 1:
        sys.argv[1] == "--setup"
        utils.append_to_file(f"\nsource {os.getcwd()}/.autout.sh", f"{os.environ['HOME']}/.zshrc")        
    else:
        map_all_interfaces_with_file()
        map_all_structs_with_file()

if __name__  ==  "__main__":
    main()