# keep in mind, donot use replace() as it may ruin the output code
# use trim/strip whenever needed
import subprocess
from copy import deepcopy
import template
import utils
import ut_regex
import re
import os
import logging
import sys
import constants
import config
from typing import List

all_mock_functions = {
    "valid": {},
    "invalid": {}
}

def get_all_possible_combinations(initial_arr: List[str], possiblities: List[List[tuple]], combinations: List[List[tuple]], duplicates: List[bool]):
    n: int = len(initial_arr)
    if not duplicates[n-1]:
        for k in range(len(possiblities[n-1])):
            new_arr = deepcopy(initial_arr)
            new_arr[n-1] = possiblities[n-1][k]
            combinations.append(new_arr)
        n -= 1
    else:
        combinations.append(initial_arr)

    for i in range(n-1, -1, -1):
        m: int = len(combinations)
        for j in range(0, m):
            arr = combinations[j]
            for k in range(len(possiblities[i])):
                new_arr = deepcopy(arr)
                new_arr[i] = possiblities[i][k]
                combinations.append(new_arr)
    if len(initial_arr) != n:
        combinations.append(initial_arr)

def fix_import_statements(file_path, content):
    test_service_file_new_import_statements = check_if_new_import_required(file_path, content)
    if len(test_service_file_new_import_statements) > 0:
        import_statements_found = False
        file_contents = utils.read_file_contents(file_path).split('\n')
        for i in range(len(file_contents)):
            line = file_contents[i]
            if "import (" in line:
                import_statements_found = True
                file_contents = file_contents[:i+1] + test_service_file_new_import_statements + file_contents[i+1:]
                file_contents = '\n'.join(file_contents)
                utils.write_to_file(file_contents, file_path)
                break
        if not import_statements_found:
            for i in range(len(file_contents)):
                line = file_contents[i].strip()
                if re.search(ut_regex.PACKAGE, line):
                    file_contents = file_contents[:i+1] + "import (\n" + test_service_file_new_import_statements + "\n" + file_contents[i+1:]
                    file_contents = '\n'.join(file_contents)
                    import_statements_found = True
                    utils.write_to_file(file_contents, file_path)
                    break
        if not import_statements_found:
            logging.error("import statements not found", exc_info = True)
            raise Exception("import statements not found")

def get_next_test_case_id():
    constants.TEST_CASE_ID +=  1
    return constants.TEST_CASE_ID

def get_file_path(interface_name):
    try:
        file_path = constants.INTERFACE_FILE_NAME_MAP.get(interface_name)
        if not file_path:
            logging.error("File not found for interface: %s" % interface_name, exc_info = True)
            raise Exception("File not found for interface: %s" % interface_name)
        return constants.CWD+file_path
    except Exception as e:
        if str(e).startswith("File not found for interface: "):
            config.map_all_interfaces_with_file()
            file_path = constants.INTERFACE_FILE_NAME_MAP.get(interface_name)
            if not file_path:
                logging.error("(tried); File not found for interface: %s" % interface_name, exc_info = True)
                raise Exception("(tried); File not found for interface: %s" % interface_name)
            return file_path
        else:
            raise e

def get_file_path_by_struct(type: str, struct_name: str):
    try:
        file_path = constants.STRUCT_FILE_NAME_MAP[type].get(struct_name)
        if not file_path:
            logging.error(f"Unhandled: struct name not mapped {type}: {struct_name}", exc_info = True)
            raise Exception(f"Unhandled: struct name not mapped {type}: {struct_name}")
        return constants.CWD+file_path
    except Exception as e:
        if str(e).startswith("Unhandled: struct name not mapped"):
            config.map_all_structs_with_file()
            file_path = constants.STRUCT_FILE_NAME_MAP.get(struct_name)
            if not file_path:
                logging.error("(tried); Unhandled: struct name not mapped: %s" % struct_name, exc_info = True)
                raise Exception("(tried); Unhandled: struct name not mapped: %s" % struct_name)
            return file_path
        else:
            raise e


def get_input_output_contents(func_definition):
    if func_definition.count('(') < 1:
        logging.error("invalid data: func definition must have a ( but found: "+func_definition, exc_info = True)
        raise Exception("invalid data: func definition must have a ( but found: "+func_definition)
    if func_definition.count('(') > 2 or func_definition.count(')') > 2:
        logging.error("unhandled: more than 2 ( or )found: "+func_definition, exc_info = True)
        raise Exception("unhandled: more than 2 ( or )found: "+func_definition)
    
    input_contents, output_contents = "", ""
    # output not handled
    if ") (" in func_definition:
        func_definition_contents = func_definition.split(") (")
        if len(func_definition_contents) > 2:
            logging.error("unhandled: ) ( func_definition_contents cannot have len > 2 "+', '.join(func_definition_contents), exc_info = True)
            raise Exception("unhandled: ) ( func_definition_contents cannot have len > 2 "+', '.join(func_definition_contents))
        input_contents, output_contents = func_definition_contents
    else:
        func_definition_contents = func_definition.split(")")
        if len(func_definition_contents) > 2:
            logging.error("unhandled: ) func_definition_contents cannot have len > 2 "+ ', '.join(func_definition_contents), exc_info = True)
            raise Exception("unhandled: ) func_definition_contents cannot have len > 2 "+ ', '.join(func_definition_contents))
        
        input_contents, output_contents = func_definition_contents
    
    output_contents = output_contents.strip()
    input_contents = input_contents.strip().split('(')
    if len(input_contents) > 2:
        logging.error("unhandled: input contents cannot have len > 2 " + input_contents, exc_info = True)
        raise Exception("unhandled: input contents cannot have len > 2 " + input_contents)
    
    if(output_contents[-1]  ==  ')'):
        output_contents = output_contents[:-1]
    return input_contents[1], output_contents

def get_output_parameters(output_contents):
    output_arguments = output_contents.split(',')
    test_service_output_argument_list = []
    
    for output_argument in output_arguments:
        output_argument = output_argument.strip()
        if ' ' in output_argument:
            output_argument = output_argument.split(' ')[-1]
        if(output_argument):
            test_service_output_argument_list.append(output_argument)
            
    return test_service_output_argument_list

def get_input_parameters(input_contents):
    input_arguments_with_variable_name_list = input_contents.split(',')
    variable_type = None
    test_service_input_argument_list = []
    for i in range(len(input_arguments_with_variable_name_list)-1, -1, -1):
        input_argument_with_variable_name = input_arguments_with_variable_name_list[i].strip()
        type_variable_name = input_argument_with_variable_name.split(' ')
        temp = []
        
        for x in type_variable_name:
            if x.strip():
                temp.append(x.strip())
        
        if len(temp) == 1:
            _, variable_type = temp, variable_type
        elif len(temp) == 2:
            _, variable_type = temp
        else:
            logging.error("unhandled: invalid format found (variable_type variable_name) "+ ' '.join(type_variable_name), exc_info = True)
            raise Exception("unhandled: invalid format found (variable_type variable_name) "+ ' '.join(type_variable_name))

        if variable_type == None:
            logging.error("unhandled: invalid format found (variable_type variable_name) "+ ' '.join(type_variable_name), exc_info = True)
            raise Exception("unhandled: invalid format found (variable_type variable_name) "+ ' '.join(type_variable_name))            

        test_service_input_argument_list.append(variable_type)
    test_service_input_argument_list.reverse()
    return test_service_input_argument_list

def generate_test_service(func_name, interface_name, test_service_input_argument_list, test_service_output_argument_list):
    test_service_output_assert_statement_list = []
    test_service_input_arguments = []
    
    for i in range(len(test_service_input_argument_list)):
        if i  ==  0:
            continue
        test_service_input_arguments.append(template.TestServiceInputArgumentTemplate % (i-1, test_service_input_argument_list[i]))
    func_input_parameters  = ', '.join(test_service_input_arguments)

    output_parameter_list = []
    for i in range(len(test_service_output_argument_list)):
        output_parameter_list.append(template.OUTPUT_PARAMETER_TEMPLATE % (i))
        test_service_output_assert_statement_list.append(template.ASSERT_STATEMENT_TEMPLATE % (i, i, i, i))
    func_output_parameters = ', '.join(output_parameter_list)
    assert_statements = join_list('\n', test_service_output_assert_statement_list)
    
    if constants.SERVICE_NAME == "tap-crm-lead-management-backend":
        test_service = template.TEST_FUNC_TEMPLATE %(func_name, func_name, "Init()\n", func_name, func_output_parameters, interface_name, func_name, func_input_parameters, assert_statements)
    else:        
        test_service = template.TEST_FUNC_TEMPLATE %(func_name, func_name, "", func_name, func_output_parameters, interface_name, func_name, func_input_parameters, assert_statements)
    return test_service



def get_func_name_from_func_definition(func_definition):
    return func_definition.split('(')[0].strip()

def get_func_name_interface_name_from_func_call(func_call: str):
    # campaignMemberActivity, err :=  s.demoStationDao.GenericGetCampaignMemberDemoStationActivityMapping(ctx, getData)
    # campaignMemberActivity.x, err :=  s.demoStationDao.GenericGetCampaignMemberDemoStationActivityMapping(ctx, getData)
    # s.demoStationDao.GenericGetCampaignMemberDemoStationActivityMapping(ctx, getData)
    func_call = func_call.strip()
    regex_result = re.compile(ut_regex.MOCK_OBJECT).findall(func_call)
    if len(regex_result) !=  1:
        logging.error(f"unhandled regex for func_call - {func_call}", exc_info = True)
        raise Exception(f"unhandled regex for func_call - {func_call}")
    interface, interface_type, func_name = regex_result[0]        
    interface = interface[0].upper() + interface[1:]+interface_type[:-1]
    
    if interface  ==  "" or func_call  ==  "":
        logging.error(f"unhandled func, interface name extraction {func_call}", exc_info = True)
        raise Exception(f"unhandled func, interface name extraction {func_call}")
    return func_name.strip(), interface.strip()

def get_func_definition(path, interface, func_name):
    file_contents = utils.read_file_contents(path)
    lines = file_contents.split('\n')
    func_name_pattern = func_name+"("
    interface_found = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if not interface_found and "type " + interface + " interface {" in line:
            interface_found = True
        elif interface_found and line  ==  "}":
            logging.error(f"unhandled: interface :{interface} found but func_name_pattern {func_name_pattern} not found in file: {path}", exc_info = True)
            raise Exception(f"unhandled: interface :{interface} found but func_name_pattern {func_name_pattern} not found in file: {path}")
        elif interface_found and  func_name_pattern in line:
            return line
    if interface_found:
        logging.error(f"unhandled: interface found {interface} but func not found {func_name_pattern}", exc_info = True)
        raise Exception(f"unhandled: interface found {interface} but func not found {func_name_pattern}")
    else:
        logging.error(f"unhandled: interface not found {interface} in file {path} for function {func_name_pattern}", exc_info = True)
        raise Exception(f"unhandled: interface not found {interface} in file {path} for function {func_name_pattern}")

def form_default_arguments(args, func_name) -> List[str]:
    default_args_list =  []
    for arg in args:
        if not arg:
            logging.error(f"Arg cannot be empty for func_name {func_name}", exc_info = True)
            raise Exception(f"Arg cannot be empty for func_name {func_name}")

        if func_name  ==  "Decode" and arg  == "interface{}":
            arg = "Decode2ndParameterPtr"
        elif func_name  ==  "Marshal" and arg  ==  "interface{}":
            arg = "uint64(1)"
        elif "*http.Response" in arg:
            arg = "GetHttpReponse(Decode1stParameter)"
        elif"*" in arg:
            arg = "&" + arg[1:] + "{}"
        # elif"*" in arg:
        #     arg = arg[1:].replace('.', '')
        #     arg = arg[0].upper() + arg[1:] + "Ptr"
        elif arg  ==  "tapcontext.TContext":
            arg = "ctx"
        elif "[]models." in arg or "[]resources." in arg:
            arg +=  "{}"
        elif "[]" in arg:
            arg +=  "{}"
        elif "resources.FilterInput" in arg:
            arg = "mock.Anything"
        elif "resources.ServiceResult" in arg:
            arg =  """resources.ServiceResult{
							IsError: true,
							Code:    500,
						}"""
        elif "models." in arg or "resources." in arg or "map[" in arg:
            arg +=  "{}"
        elif arg  ==  "error":
            arg = f'fmt.Errorf("Error in {func_name}")'
        elif arg  ==  "uint64":
            arg = "uint64(1)"
        elif arg  ==  "string":
            arg = '""'
        elif arg  ==  "interface{}":
            arg = "uint64(1)"
        elif arg  ==  "io.ReadCloser":
            arg =  "IoNopCloser(Decode1stParameter)"
        elif arg  ==  "int64":
            arg = "int64(1)"
        elif arg  ==  "int":
            arg = "int(1)"
        elif arg  ==  "bool":
            arg = "true"
        else:
            logging.error(f"unhandled: default arg {arg}, func_name {func_name}", exc_info = True)
            raise Exception(f"unhandled: default arg {arg}, func_name {func_name}")
        default_args_list.append(arg)
    return default_args_list

def get_func_call_statement(mock_func_call_file_path: str, mock_func_call_file_line_number: int, mock_func_name: str):
    mock_func_call_file_contents = utils.read_file_contents(mock_func_call_file_path)
    mock_func_call_lines =  mock_func_call_file_contents.split('\n')

    # mock_func_call_file_line_number: 1 based indexing
    if len(mock_func_call_lines) >=  mock_func_call_file_line_number:
        if mock_func_name in mock_func_call_lines[mock_func_call_file_line_number-1]:
            return mock_func_call_lines[mock_func_call_file_line_number-1]

    for line in mock_func_call_lines:
        line = str(line).strip()
        if line and mock_func_name in line and re.search(ut_regex.OTHER_INTERFACE_FUNC_CALL, line):
            return line


def replace_input_parameters(test_case: template.TEST_CASE_DICT, mock_func: template.MOCK_FUNC_DICT, unexpected_method_call_input_params):
    # assuming func call will not be having more than 10 params
    if len(unexpected_method_call_input_params) > 10:
        logging.error("unexpected_method_call_input_params > 10", exc_info = True)
        raise Exception("unexpected_method_call_input_params > 10")
    if len(mock_func.mock_func_inputs) !=  len(unexpected_method_call_input_params):
        logging.error("mock_func and unexpected_method length are not equal", exc_info = True)
        raise Exception("mock_func and unexpected_method length are not equal")

    for i in range(len(unexpected_method_call_input_params)):
        if unexpected_method_call_input_params[i][3:].startswith("resources.FilterInput{SearchText:"):
            mock_func.mock_func_inputs[i] = "mock.Anything"
        elif unexpected_method_call_input_params[i][3:].strip()  ==  "&datatypes.JSON(nil)":
            mock_func.mock_func_inputs[i] = "datatypesJSONPtr"
        elif mock_func.mock_func_inputs[i] !=  "ctx":
            mock_func.mock_func_inputs[i] = unexpected_method_call_input_params[i][3:]
            if "(*datatypes.JSON)(" in mock_func.mock_func_inputs[i]:
                for datatypesJson in list(set(re.compile(ut_regex.DATATYPES_JSON).findall(mock_func.mock_func_inputs[i]))):
                    mock_func.mock_func_inputs[i] = mock_func.mock_func_inputs[i].replace(datatypesJson, "&datatypesJSON")                
            if "(*uint64)(0x" in mock_func.mock_func_inputs[i]:
                for ptr_with_address in list(set(re.compile(ut_regex.UINT64).findall(mock_func.mock_func_inputs[i]))):
                    mock_func.mock_func_inputs[i] = mock_func.mock_func_inputs[i].replace(ptr_with_address, "Uint64Ptr")
            if "0x" in mock_func.mock_func_inputs[i]:
                for hex in list(set(re.compile(ut_regex.HEX).findall(mock_func.mock_func_inputs[i]))):
                    mock_func.mock_func_inputs[i] = mock_func.mock_func_inputs[i].replace(hex, "uint64("+str(int(hex, 16))+")")
    
    if mock_func.mock_func_name == "Unmarshal":
        unmarshal_2nd_param = mock_func.mock_func_inputs[2][1:]
        if unmarshal_2nd_param.startswith('['):
            unmarshal_2nd_param = unmarshal_2nd_param.split('{')[0].replace('.', '')
            mock_func.mock_func_inputs[2] = unmarshal_2nd_param[0].upper() + unmarshal_2nd_param[1:] + "ArrPtr"
        else:
            unmarshal_2nd_param = unmarshal_2nd_param.split('{')[0].replace('.', '')
            mock_func.mock_func_inputs[2] = unmarshal_2nd_param[0].upper() + unmarshal_2nd_param[1:] + "Ptr"
    elif mock_func.mock_func_name  ==  "Decode":
        decode_2nd_param = mock_func.mock_func_inputs[2]
        decode_param = decode_2nd_param[1:]
        request_found, decode_found = False, False
        # replace post_request output bases on Decode's output struct
        for i in range(len(test_case.mock_functions)-1, -1, -1):
            mock_func = test_case.mock_functions[i]
            if mock_func.mock_func_name in ["PostRequest", "GetRequest", "UpdateRequest", "DeleteRequest", "PatchRequest"]:
                request_found = True
                # GetHttpReponseInterface(resources.FilteredContactsResponse{Data: []map[string]interface{}(nil), TotalCount: uint64(0)}),
                if decode_2nd_param.startswith("&resources.") or decode_2nd_param.startswith("&models."):
                    mock_func.mock_func_outputs[0] = f"GetHttpReponseInterface({decode_param})" 
                elif decode_2nd_param.startswith("&[]resources.") or decode_2nd_param.startswith("&[]models."):
                    mock_func.mock_func_outputs[0] = f"GetHttpReponseInterface({decode_param.replace('(nil)', '{}')})" 
                    
                elif decode_2nd_param.startswith("&map[string]interface") or decode_2nd_param.startswith("&map[string]interface"):
                    mock_func.mock_func_outputs[0] = f"GetHttpReponse({decode_param})" 
                else:
                    logging.error(f"unhandled: unknown decond 2nd param {decode_2nd_param}", exc_info = True)
                    raise Exception(f"unhandled: unknown decond 2nd param {decode_2nd_param}")
            elif mock_func.mock_func_name  ==  "Decode":
                decode_found = True
                # GetHttpReponseInterface(resources.FilteredContactsResponse{Data: []map[string]interface{}(nil), TotalCount: uint64(0)}).Body
                if decode_2nd_param.startswith("&resources.") or decode_2nd_param.startswith("&models."):
                    mock_func.mock_func_inputs[1] = f"GetHttpReponseInterface({decode_param}).Body" 
                    mock_func.mock_func_inputs[2] = f"&{decode_param}" 
                elif decode_2nd_param.startswith("&[]resources.") or decode_2nd_param.startswith("&[]models."):
                    mock_func.mock_func_inputs[1] = f"GetHttpReponseInterface({decode_param.replace('(nil)', '{}')}).Body" 
                    mock_func.mock_func_inputs[2] = f"&{decode_param.replace('(nil)', '{}')}" 
                elif decode_2nd_param.startswith("&map[string]interface") or decode_2nd_param.startswith("&map[string]interface"):
                    mock_func.mock_func_inputs[1] = f"GetHttpReponse({decode_param}).Body" 
                    mock_func.mock_func_inputs[2] = f"&{decode_param}" 
                else:
                    logging.error(f"unhandled: unknown decond 2nd param {decode_2nd_param}", exc_info = True)
                    raise Exception(f"unhandled: unknown decond 2nd param {decode_2nd_param}")
                mock_func.mock_run = False
            if request_found and decode_found:
                break
        if not request_found or not decode_found:
            logging.error(f"unhandled: request_found: {request_found}, decode_found: {decode_found} in test_case {test_case.__dict__}", exc_info = True)
            raise Exception(f"unhandled: request_found: {request_found}, decode_found: {decode_found} in test_case {test_case.__dict__}")
    return mock_func

def form_import_statements(file_content):
    import_statements = []
    if "tests." in file_content:
        import_statements.append(f'"gitlab.com/tekion/development/tap/mas/{constants.SERVICE_NAME}/tests"')
    if "resources." in file_content:
        import_statements.append(f'"gitlab.com/tekion/development/tap/mas/{constants.SERVICE_NAME}/resources"')
    if "models." in file_content:
        import_statements.append(f'"gitlab.com/tekion/development/tap/mas/{constants.SERVICE_NAME}/models"')
    if "io." in file_content:
        import_statements.append('"io"')
        import_statements.append(f'"gitlab.com/tekion/development/tap/mas/{constants.SERVICE_NAME}/models"')
    if "mock." in file_content:
        import_statements.append('"github.com/stretchr/testify/mock"')
    if "fmt." in file_content:
        import_statements.append('"fmt"')
    if "time." in file_content:
        import_statements.append('"time"')
    if "datatypes." in file_content:
        import_statements.append('"gorm.io/datatypes"')
    if "http." in file_content:
        import_statements.append('"net/http"')
    if "tapcontext." in file_content:
        import_statements.append('"gitlab.com/tekion/development/tap/backend/taplibgo/tapcontext"')
    if "testing." in file_content:
        import_statements.append('"testing"')
    if "assert." in file_content:
        import_statements.append('"github.com/stretchr/testify/assert"')
    if "test_cases." in file_content:
        import_statements.append(f'"gitlab.com/tekion/development/tap/mas/{constants.SERVICE_NAME}/tests/test_cases"')
    return import_statements        

def join_list(separator: str, l: List[any]):
    joined_list = separator.join(l)
    if joined_list:
        return joined_list + separator
    return ""

def go_test(path):
    prev = os.getcwd()
    try:
        os.chdir(path)
        go_test_output = os.popen("/usr/local/go/bin/go test").read()
        if "[build failed]" in go_test_output:
            logging.error("Fix test service", exc_info = True)
            raise Exception("Fix test service")
    except Exception as e:
        raise e
    finally:
        os.chdir(prev)

def go_build(path):
    prev = os.getcwd()
    os.chdir(path)
    try:
        proc = subprocess.run(["go build"], shell = True, check = True, stdout = subprocess.PIPE)
        if proc.stdout !=  b'':
            logging.error(f"proc-stdout : {proc.stdout}", exc_info = True)
            raise Exception(f"proc-stdout : {proc.stdout}")
    except Exception as e:
        logging.error(e, exc_info = True)
        logging.error(f"Build failed in {os.getcwd()}", exc_info = True)
        raise Exception(f"Build failed in {os.getcwd()}")
    finally:
        os.chdir(prev)

def form_ut_test_cases(ut_test_case_dict: template.UT_TEST_CASES_DICT, is_only_test_cases: bool):
    ut_test_cases = []
    import_statements = []
    
    for test_case in ut_test_case_dict.test_cases:
        if test_case.test_case_id  ==  0:
            logging.error(f"unhandled: test_case_id is 0 for test_case {test_case}", exc_info = True)
            raise Exception(f"unhandled: test_case_id is 0 for test_case {test_case}")
        mock_functions = []
        for mock_func in test_case.mock_functions:
            new_mock = None
            if mock_func.mock_run  ==  True:
                new_mock =  template.MOCK_FUNC_TEMPLATE % (mock_func.interface_name, mock_func.mock_func_name, join_list(',\n', mock_func.mock_func_inputs), join_list(',\n', mock_func.mock_func_outputs), template.RUN_TEMPLATE)
            else:
                new_mock = template.MOCK_FUNC_TEMPLATE % (mock_func.interface_name, mock_func.mock_func_name, join_list(',\n', mock_func.mock_func_inputs), join_list(',\n', mock_func.mock_func_outputs), template.RUN_ONCE_TEMPLATE)
            mock_functions.append(new_mock)
            
        ut_test_cases.append(template.TEST_CASE_TEMPLATE % (test_case.func_name, test_case.test_case_id, join_list(',\n', test_case.inputs), join_list(',\n', test_case.expected_outputs), join_list('\n', mock_functions)))
    
    test_cases = template.TEST_CASES_TEMPLATE % (ut_test_case_dict.func_name, ut_test_case_dict.func_name, join_list('\n', ut_test_cases))
    if is_only_test_cases:
        return test_cases

    import_statements = form_import_statements(join_list(',\n', ut_test_cases))
    return template.UT_TEST_CASES_TEMPLATE % (join_list('\n', import_statements), test_cases)

def replace_expected_outputs(expected_outputs:List, index:int, actual:str):
    # extract actual from "actual : <actual_content>"
    actual = list(set(re.compile(ut_regex.ACTUAL).findall(actual)))[0]
    actual = actual.strip()
    if "&errors.errorString{s:" in actual:
        actual = 'fmt.Errorf("%s")'%(actual.split("&errors.errorString{s:")[1][1:-2])
    elif "<nil>(<nil>)" in actual:
        actual = "nil"
    elif "(*uint64)(0x" in actual:
        for ptr_with_address in list(set(re.compile(ut_regex.UINT64).findall(actual))):
            actual = actual.replace(ptr_with_address, "Uint64Ptr")
    elif "0x" in actual:
        for hex in list(set(re.compile(ut_regex.HEX).findall(actual))):
            actual = actual.replace(hex, "uint64("+str(int(hex, 16))+")")
    expected_outputs[index] = actual
    return expected_outputs

def output_assertion(test_case: template.TEST_CASE_DICT, failed_test_case: str):
    actual = ""
    output_assert_failed_temp = failed_test_case.split("asserting out")
    output_assert_failed = output_assert_failed_temp[-1]
    output_assert_failed_index = int(list(set(re.compile(ut_regex.NOT_EQUAL_OUTPUT_PARAM).findall(failed_test_case)))[0].strip())
    if output_assert_failed_index >=  len(test_case.expected_outputs):
        logging.error(f"unhandled: invalid output_assert_failed_index {output_assert_failed_index} extracted_from: {output_assert_failed_temp}", exc_info = True)
        raise Exception(f"unhandled: invalid output_assert_failed_index {output_assert_failed_index} extracted_from: {output_assert_failed_temp}")
    output_assert_failed_lines = output_assert_failed.split('\n')
    for i in range(len(output_assert_failed_lines)):
        output_assert_failed_lines[i] = output_assert_failed_lines[i].strip()
        if "Not equal:" in output_assert_failed_lines[i] and "expected:" in (output_assert_failed_lines[i+1]) and "actual  :" in (output_assert_failed_lines[i+2]):
            actual = output_assert_failed_lines[i+2].strip() 
            test_case.expected_outputs = replace_expected_outputs(test_case.expected_outputs, output_assert_failed_index, actual)
            return test_case
    logging.error(f"Unhandled: output_assert_failed {failed_test_case}", exc_info = True)
    raise Exception(f"Unhandled: output_assert_failed {failed_test_case}")

def closet_call_i_have(test_case: template.TEST_CASE_DICT, failed_test_case: str):
    failed_test_case_lines = failed_test_case.split('\n')
    unexpected_method_call_input_params = []
    mock_func_name = ""
    for i in range(len(failed_test_case_lines)):
        if "mock: Unexpected Method Call" in failed_test_case_lines[i]:
            i +=  3
            mock_func_name = get_func_name_from_func_definition(failed_test_case_lines[i])
            i +=  1
            while "The closest call I have is: " not in failed_test_case_lines[i]:
                if failed_test_case_lines[i].strip():
                    unexpected_method_call_input_params.append(failed_test_case_lines[i].strip())
                i +=  1
            break
    # we can have duplicate mock func, hence replacing the latest mock
    for i in range(len(test_case.mock_functions)-1, -1, -1):
        mock_func = test_case.mock_functions[i]
        if(mock_func.mock_func_name  ==  mock_func_name):
            mock_func = replace_input_parameters(test_case=test_case, mock_func = mock_func, unexpected_method_call_input_params= unexpected_method_call_input_params)
            break

        
def called_over_1_times(ut_test_case_dict: template.UT_TEST_CASES_DICT, test_case_q: List[template.TEST_CASE_DICT],test_case: template.TEST_CASE_DICT, failed_test_case: str) -> template.TEST_CASE_DICT:
    failed_test_case_lines = failed_test_case.split('\n')
    unexpected_method_call_input_params = []
    mock_func_name = ""
    new_mock_func: template.MOCK_FUNC_DICT = None
    for i in range(len(failed_test_case_lines)):
        if "mock: The method has been called over 1 times" in failed_test_case_lines[i]:
            i +=  3
            mock_func_name = get_func_name_from_func_definition(failed_test_case_lines[i])
            if mock_func_name  ==  "BeginTransaction":
                new_mock_func = constants.MOCK_BEGIN_TRANSACTION
            elif mock_func_name  ==  "AddTransactorToContext":
                new_mock_func = constants.MOCK_ADD_TRANSACTOR_TO_CONTEXT
            elif mock_func_name  ==  "GetExistingTransactorFromContext":
                new_mock_func = constants.MOCK_GET_EXISTING_TRANSACTOR_FROM_CONTEXT
            else:
                i +=  1
                while not failed_test_case_lines[i].startswith("at: ["):
                    if failed_test_case_lines[i].strip():
                        unexpected_method_call_input_params.append(failed_test_case_lines[i].strip())
                    i +=  1
                break
    
    if new_mock_func is None:
        for i in range(len(test_case.mock_functions)-1, -1, -1):
            mock_func = test_case.mock_functions[i]
            if(mock_func.mock_func_name  ==  mock_func_name):
                new_mock_func = replace_input_parameters(test_case=test_case, mock_func = mock_func, unexpected_method_call_input_params= unexpected_method_call_input_params)
                break

    if new_mock_func == None:
        raise Exception("unhandled mock_func is None")

    test_case_q = mock_other_possible_test_cases(test_case_q = test_case_q, ut_test_case_dict = ut_test_case_dict, test_case = test_case, mock_func=new_mock_func, is_output_used = [])
    test_case.mock_functions.append(new_mock_func)
    return test_case




def get_struct_name_type(file_path: str, struct_name: str):
    file_contents = utils.read_file_contents(path = file_path).replace('\t', '')
    structs = file_contents.split('struct {')
    struct_pattern = "type "+struct_name+" "
    # donot strip struct_pattern 
    for i in range(len(structs)):
        struct_content = structs[i]
        if struct_pattern in struct_content:
            struct_pattern, struct_content = struct_pattern.strip(), struct_content.strip()
            primary_key = structs[i+1].strip().split('\n')[0].strip()
            if len(primary_key.split(' ')) < 2:
                val = int(input(f"Check struct {struct_name} \n 1. modify and re-rerun \n 2. continue without primary key validation.\n") )
                print("continuing...")
                if val == 1:
                    raise Exception(f"Check struct {struct_name}")
                elif val == 2:
                    return ["", "", False]
                
            var_name_type = list(set(re.compile(ut_regex.VARIABLE_TYPE).findall(primary_key)))[0]
            if len(var_name_type) !=  2:
                logging.error(f"Unhandled: couldn't extract var name and type from struct_content - {struct_content}", exc_info = True)
                raise Exception(f"Unhandled: couldn't extract var name and type from struct_content - {struct_content}")
            if not var_name_type[0] or not var_name_type[1]:
                logging.error(f"Unhandled: var_name or type should have a value found var_name : {var_name_type[0]} and var_type: {var_name_type[1]} from struct_content - {struct_content}", exc_info = True)
                raise Exception(f"Unhandled: var_name or type should have a value found var_name : {var_name_type[0]} and var_type: {var_name_type[1]} from struct_content - {struct_content}")
            if var_name_type[1] not in ["uint64", "int", "int64", "float"]:
                return ["", "", False]
            return var_name_type[0], var_name_type[1], True
    logging.error(f"Unhandled: struct pattern didnot match {struct_pattern}", exc_info = True)
    raise Exception(f"Unhandled: struct pattern didnot match {struct_pattern}")

def get_primary_id_and_type(arg: str):
    if "[]" in arg:
        arg = arg[2:]
    if "{}" in arg:
        arg = arg[:-2]
    if "{" in arg:
        arg = arg.split("{")[0]
    struct_details = arg.split('.')
    if len(struct_details) !=  2:
        logging.error(f"Unhandled: struct details {arg}", exc_info = True)
        raise Exception(f"Unhandled: struct details {arg}")
    struct_type, struct_name = struct_details
    
    path = get_file_path_by_struct(type = struct_type, struct_name = struct_name)
    return get_struct_name_type(file_path = path, struct_name = struct_name)

def other_possible_arg(output_param: str):
    if output_param.startswith("fmt.Errorf"):
        return ["nil"], False
    if "errorString" in output_param:
        return ["nil"], False
    if output_param  ==  "txObj":
        return ["nil"], True
    if output_param == "true":
        return ["false"], True
    if output_param == "false":
        return ["true"], True
    if output_param.startswith("GetHttpReponse(") or output_param.startswith("GetHttpReponseInterface("):
        return ["nil"], True
    if output_param.startswith("resources.ServiceResult"):
        return ["resources.ServiceResult{\n\t\t\t\t\t\t\tIsError: false,\n\t\t\t\t\t\t\tCode:    200,\n\t\t\t\t\t\t}"], True
    
    if not (output_param.startswith("models.") or output_param.startswith("resources.") or output_param.startswith("[]models.") or output_param.startswith("[]resources.")):
        return [], True
    primary_key, type_name, found_primay_key = get_primary_id_and_type(output_param)
    default_val = None
    if found_primay_key:
        default_val = form_default_arguments([type_name], "")[0]

    if found_primay_key and ("[]models." in output_param or "[]resources." in output_param):
        return [output_param[:-1]+"\n{},\n}"], True
    # if found_primay_key and ("[]models." in output_param or "[]resources." in output_param):
    #     return [output_param[:-1]+"\n{},\n}",  output_param[:-1]+"\n{\n"+ primary_key + f": {default_val},\n" + "},\n}"], True
    elif found_primay_key and ("models." in output_param or "resources." in output_param):
        return [output_param[:-1]+"\n"+ primary_key + f": {default_val}" + ",\n}"], True
    elif "[]models." in output_param or "[]resources." in output_param:
        return [output_param[:-1]+"\n{},\n}",  output_param[:-1]+"\n{\n},\n}"], True
    elif "models." in output_param or "resources." in output_param:
        return [], True
    logging.error(f"unhandled: {output_param}", exc_info = True)
    raise Exception(f"unhandled: {output_param}")

def check_test_case_already_available(test_case_q: List[template.TEST_CASE_DICT], ut_test_case_dict: template.UT_TEST_CASES_DICT, test_case: template.TEST_CASE_DICT):
    if not test_case:
        return True
    already_available = False
    for tc in test_case_q:
        if tc  ==  test_case:
            already_available = True
            break
    
    if ut_test_case_dict:
        for tc in ut_test_case_dict.test_cases:
            if tc  ==  test_case:
                already_available = True
                break
    return already_available

def add_mock_to_list(new_mock_func: template.MOCK_FUNC_DICT):
    invalid = "invalid"
    if all_mock_functions[invalid].get(new_mock_func.interface_name) is None:
        all_mock_functions[invalid][new_mock_func.interface_name] = {}
    if all_mock_functions[invalid][new_mock_func.interface_name].get(new_mock_func.mock_func_name) is None:
        all_mock_functions[invalid][new_mock_func.interface_name][new_mock_func.mock_func_name] = new_mock_func


def mock_other_possible_test_cases(test_case_q: List[template.TEST_CASE_DICT], ut_test_case_dict: template.UT_TEST_CASES_DICT, test_case: template.TEST_CASE_DICT, mock_func: template.MOCK_FUNC_DICT, is_output_used: List[bool]):
    if len(is_output_used) == 0:
        return test_case_q
    n = len(mock_func.mock_func_outputs)
    other_output_possibilites, duplicates = [[]]*n, [True]*n
    for i in range(n):
        if is_output_used[i]:
            other_output_possibilites[i], duplicates[i] = other_possible_arg(mock_func.mock_func_outputs[i])
        else:
            other_output_possibilites[i] = []
        
    combinations: List[List[str]] = []
    get_all_possible_combinations(mock_func.mock_func_outputs, other_output_possibilites, combinations, duplicates)

    combinations = combinations[1:]
    for possible_output in combinations:
        test_case_copy = None
        test_case_copy = deepcopy(test_case)
        input_params_copy = deepcopy(mock_func.mock_func_inputs)
            
        new_mock_func = template.MOCK_FUNC_DICT(mock_func.interface_name, mock_func.mock_func_name, input_params_copy, possible_output)
        add_mock_to_list(new_mock_func = new_mock_func)
        test_case_copy.mock_functions.append(new_mock_func)
        if test_case_copy is None:
            continue
                        
        if not check_test_case_already_available(test_case_q = test_case_q, ut_test_case_dict = ut_test_case_dict, test_case = test_case_copy):
            test_case_copy.test_case_id = get_next_test_case_id()
            test_case_q.append(test_case_copy)
    
    return test_case_q


def get_output_param_usage(mock_func_call_output_content):
    is_output_used = []
    output_params = mock_func_call_output_content.split(',')
    for output_param in output_params:
        output_param = output_param.strip()
        if output_param == "_":
            is_output_used.append(0)
        else:
            is_output_used.append(1)
    return is_output_used


def mock_unexpected_method_call(test_case_q: List[template.TEST_CASE_DICT], ut_test_case_dict: template.UT_TEST_CASES_DICT, test_case: template.TEST_CASE_DICT, mock_func_name: template.MOCK_FUNC_DICT, failed_test_case: str) -> template.MOCK_FUNC_DICT:
    mock_file_path = list(set(re.compile(ut_regex.MOCK_FILE_PATH_RECOVERED).findall(failed_test_case)))[0][1].strip().split(' ')[1].strip()
    mock_file_path_name, mock_file_path_line_number = mock_file_path.split(':')
    mock_file_path_line_number = int(mock_file_path_line_number.strip())
    mock_func_call_statement = get_func_call_statement(mock_file_path_name, mock_file_path_line_number, mock_func_name)        
    _, called_interface_name = get_func_name_interface_name_from_func_call(func_call=mock_func_call_statement)
    mock_func_call_output_statement = mock_func_call_statement.split(':=')[0].strip()
    mock_func_call_output_content = mock_func_call_output_statement.split('=')[0].strip()
    is_output_used = get_output_param_usage(mock_func_call_output_content)

    called_func_file_path = get_file_path(interface_name = called_interface_name)
    called_func_definition = get_func_definition(called_func_file_path, called_interface_name, mock_func_name)
    input_contents, output_contents = get_input_output_contents(called_func_definition)
    called_func_input_arguments = get_input_parameters(input_contents)
    called_func_output_arguments = get_output_parameters(output_contents)
    mock_func_input_arguments = form_default_arguments(called_func_input_arguments, mock_func_name)
    mock_func_output_arguments = form_default_arguments(called_func_output_arguments, mock_func_name)
    if constants.SERVICE_NAME in ["tap-crm-activity-management-backend", "tap-crm-account-management-backend"] and called_interface_name.endswith("Dao"):
        called_interface_name = called_interface_name[:-3] + "Repo"

    mock_interface = "Mock"+called_interface_name
    new_mock_func = template.MOCK_FUNC_DICT(mock_interface, mock_func_name, mock_func_input_arguments, mock_func_output_arguments)
    add_mock_to_list(new_mock_func = new_mock_func)
    
    test_case_q = mock_other_possible_test_cases(test_case_q = test_case_q, ut_test_case_dict = ut_test_case_dict, test_case = test_case, mock_func=new_mock_func, is_output_used = is_output_used)
    return new_mock_func


def method_cal_was_unexpected(test_case_q: List[template.TEST_CASE_DICT], ut_test_case_dict: template.UT_TEST_CASES_DICT, test_case: template.TEST_CASE_DICT, failed_test_case: str):
    to_mock_func_list = list(set(re.compile(ut_regex.EITHER_DO_MOCK_ON).findall(failed_test_case)))
    if len(to_mock_func_list) !=  1:
        logging.error(f"unhandled: no or more mock found in {failed_test_case}", exc_info = True)
        raise Exception(f"unhandled: no or more mock found in {failed_test_case}")
    new_mock_func: template.MOCK_FUNC_DICT = None
    mock_func_name = to_mock_func_list[0]

    if mock_func_name  ==  "BeginTransaction":
        new_mock_func = constants.MOCK_BEGIN_TRANSACTION
    elif mock_func_name  ==  "AddTransactorToContext":
        new_mock_func = constants.MOCK_ADD_TRANSACTOR_TO_CONTEXT
    elif mock_func_name  ==  "GetExistingTransactorFromContext":
        new_mock_func = constants.MOCK_GET_EXISTING_TRANSACTOR_FROM_CONTEXT
        test_case_q = mock_other_possible_test_cases(test_case_q = test_case_q, ut_test_case_dict = ut_test_case_dict, test_case = test_case, mock_func=new_mock_func, is_output_used = [1])
    else:
        new_mock_func = mock_unexpected_method_call(ut_test_case_dict = ut_test_case_dict, test_case_q = test_case_q, test_case = test_case, failed_test_case = failed_test_case, mock_func_name = mock_func_name)
    test_case.mock_functions.append(new_mock_func)
    return test_case

def run_test_case(func_name):
    return os.popen("/usr/local/go/bin/go test -timeout 30s -run ^Test%s$ gitlab.com/tekion/development/tap/mas/%s/tests/service" % (func_name, constants.SERVICE_NAME)).read()

def write_to_back_up_file(ut_test_case_dict, file_path):
    test_cases = form_ut_test_cases(ut_test_case_dict, False)
    utils.write_to_file(test_cases, file_path)

def auto_generate_test_cases(test_case_q: List[template.TEST_CASE_DICT], func_name) -> template.UT_TEST_CASES_DICT:
    ut_test_case_dict =  template.UT_TEST_CASES_DICT(func_name = func_name, test_cases = [])
    try:
        func_name = ut_test_case_dict.func_name
        while len(test_case_q):
            test_case = test_case_q[0]
            test_case_q = test_case_q[1:]
            
            tries = 0
            while tries < 10:
                test_cases = form_ut_test_cases(template.UT_TEST_CASES_DICT(func_name, [test_case]), False)
                ut_test_cases_file = constants.CWD+"/tests/test_cases/auto_generated_test_cases.go"
                utils.write_to_file(test_cases, ut_test_cases_file)
                go_build("tests/test_cases")
                test_run_output  = run_test_case(func_name = func_name) 

                if "--- FAIL: " not in  test_run_output:
                    if len(ut_test_case_dict.test_cases) and ut_test_case_dict.test_cases[-1]  ==  test_case:
                        logging.error("unhandled: need to handle this, no idea what to do", exc_info = True)
                        raise Exception("unhandled: need to handle this, no idea what to do")
                    ut_test_case_dict.test_cases.append(test_case)
                    break
                else:
                    tries +=  1

                failed_test_case = test_run_output.replace('\t', '').split("Case -")[-1]                
                
                if "asserting out" in failed_test_case:
                    test_case = output_assertion(test_case = test_case, failed_test_case = failed_test_case)

                elif "The closest call I have is: " in failed_test_case:
                    closet_call_i_have(test_case = test_case, failed_test_case = failed_test_case)

                elif "assert: mock: I don't know what to return because the method call was unexpected." in failed_test_case:
                    test_case = method_cal_was_unexpected(test_case_q = test_case_q, ut_test_case_dict = ut_test_case_dict, test_case = test_case, failed_test_case = failed_test_case)

                elif "assert: mock: The method has been called over 1 times." in failed_test_case:
                    test_case = called_over_1_times(ut_test_case_dict = ut_test_case_dict, test_case_q = test_case_q, test_case = test_case, failed_test_case = failed_test_case)

                else:
                    print("testcase: ", failed_test_case)
                    logging.error("unhandled: auto_generate", exc_info = True)
                    # if "panic: interface conversion: interface {} is nil, not" in failed_test_case:
                    raise Exception("unhandled: auto_generate")

            if tries >=  10:
                logging.error("Unhandled: couldn't generate successful test-case in 10 tries", exc_info = True)
                raise Exception("Unhandled: couldn't generate successful test-case in 10 tries")    

        return ut_test_case_dict
    except Exception as e:
        logging.error(e, exc_info = True)
        return ut_test_case_dict

def re_assign_test_case_ids(ut_test_case_dict: template.UT_TEST_CASES_DICT):
    for i in range(len(ut_test_case_dict.test_cases)-1, -1, -1):
        ut_test_case_dict.test_cases[i].test_case_id = i+1
    return ut_test_case_dict

def get_import_statements(file_name):
    file_contents = utils.read_file_contents(file_name).replace('\t', '')
    if "import (" in file_contents:
        import_structure = list(set(re.compile(ut_regex.IMPORT_STRCTURE).findall(file_contents)))
        if len(import_structure) == 0:
            return []
        return list(filter(None, import_structure[0].replace('\t', '').split('\n')))
    return []

def check_if_new_import_required(file_name, content):
    return list(set(form_import_statements(content)) - set(get_import_statements(file_name)))

def check_exisiting_ut() -> int:
    go_test("tests/service")
    
    utils.set_coverage_file()
    
    try:
        old_coverage_contents = os.popen(f"sh {constants.CWD}/{constants.RUN_COVERAGE_FILE}").read()
    except Exception as e:
        logging.info("old_coverage_contents", old_coverage_contents)
        raise Exception("check existing mock functions")
    
    if "[build failed]" in old_coverage_contents:
        logging.error("old coverage contents", old_coverage_contents)
        raise Exception(old_coverage_contents)
    
    if "--FAIL:" in old_coverage_contents:
        logging.error("fix existing UT", exc_info = True)
        raise Exception("fix existing UT")

    old_coverage_contents = old_coverage_contents.split('\n')
    old_coverage_found = False
    for i in range(len(old_coverage_contents)-1, -1, -1):
        line = old_coverage_contents[i]
        if "coverage: " in line:
            old_coverage = float(list(set(re.compile(ut_regex.COVERAGE).findall(line)))[0])
            old_coverage_found = True
            break
    if not old_coverage_found:
        logging.error(f"old coverage  not found", exc_info = True)
        raise Exception(f"old coverage  not found")
    return old_coverage


def main():
    try:
        if len(sys.argv) < 3:
            logging.error(f"not all arguments are given - {' '.join(sys.argv)}")
            raise Exception(f"not all arguments are given - {' '.join(sys.argv)}")
        constants.CWD, file_name = sys.argv[1].split('/service/v1/')
        constants.SERVICE_NAME = constants.CWD.split('/')[-1]
        constants.HOME_DIR = sys.argv[0].split('/python-scripts/auto_generate.py')[0]
        
        logging.basicConfig(filename=constants.HOME_DIR+"/python-scripts/generate_ut.log",
                        filemode='w',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
        os.chdir(constants.CWD)

        if os.path.isfile(constants.CWD+"/tests/test_cases/auto_generated_test_cases.go"):
            os.system("rm tests/test_cases/auto_generated_test_cases.go")
        
        old_coverage = check_exisiting_ut()
        utils.initialize_constants()
        utils.initialize_interface_file_name_map()
        utils.initialize_struct_file_name_map()
        ut_test_cases_file = constants.CWD+f"/tests/test_cases/{file_name.split('.go')[0]}_test_cases.go"
        if not os.path.isfile(ut_test_cases_file):
            logging.info(f"Test cases file not found: {ut_test_cases_file} creating new file")
            utils.create_file(content=template.UT_TEST_CASES_TEMPLATE % ("", ""), path=ut_test_cases_file)

        test_service_file = constants.CWD+f"/tests/service/{file_name.split('.go')[0]}_test.go"
        if not os.path.isfile(test_service_file):
            logging.info(f"Test cases file not found: {test_service_file} creating new file")
            utils.create_file(content=template.UT_TEST_SERVICE_FILE_TEMPLATE % ("", ""), path=test_service_file)

        func_name = sys.argv[3]
        interface_name = sys.argv[2]
        path = constants.CWD+f"/service/v1/{file_name}"


        func_definition = get_func_definition(path, interface_name, func_name)
        input_contents, output_contents = get_input_output_contents(func_definition)
        test_service_input_argument_list = get_input_parameters(input_contents)
        test_service_output_argument_list = get_output_parameters(output_contents)
        test_service = generate_test_service(func_name, interface_name, test_service_input_argument_list, test_service_output_argument_list)
        utils.append_to_file(test_service, test_service_file)
        fix_import_statements(test_service_file, test_service)
        
        # ignore 0th element as ctx is not used in test_case input
        inputs = form_default_arguments(test_service_input_argument_list[1:], func_name)
        outputs = form_default_arguments(test_service_output_argument_list, func_name)    
        test_case = template.TEST_CASE_DICT(func_name, get_next_test_case_id(), inputs, outputs, [])
        test_case_q = [test_case]
        
        for i in range(len(inputs)):
            other_possible_args, _ = other_possible_arg(inputs[i])
            for arg in other_possible_args:
                input_params = deepcopy(inputs)
                test_case_copy = deepcopy(test_case)
                input_params[i] = arg
                test_case_copy.inputs = input_params
                test_case_copy.test_case_id = get_next_test_case_id()
                test_case_q.append(test_case_copy)
        ut_test_case_dict = None

        ut_test_case_dict = auto_generate_test_cases(test_case_q =  test_case_q, func_name = func_name)
        ut_test_case_dict = re_assign_test_case_ids(ut_test_case_dict)
        test_cases = form_ut_test_cases(ut_test_case_dict, True)
        utils.append_to_file(test_cases, ut_test_cases_file)
        fix_import_statements(ut_test_cases_file, test_cases)
        
        if os.path.isfile(constants.CWD+"/tests/test_cases/auto_generated_test_cases.go"):
            os.system("rm tests/test_cases/auto_generated_test_cases.go")

        new_coverage_contents = os.popen(f"sh {constants.CWD}/{constants.RUN_COVERAGE_FILE}").read()
        if "--FAIL:" in new_coverage_contents:
            logging.error("coverage run failed", exc_info = True)
            raise Exception("coverage run failed")
        new_coverage_contents = new_coverage_contents.split('\n')
        new_coverage_found = False
        for line in new_coverage_contents:
            if "coverage: " in line:
                new_coverage = float(list(set(re.compile(ut_regex.COVERAGE).findall(line)))[0])
                new_coverage_found = True
        if not new_coverage_found:
            logging.error(f"new coverage not found", exc_info = True)
            raise Exception(f"new coverage not found")
        
        print(f"Coverage {new_coverage} (+{round(new_coverage-old_coverage, 2)}) {func_name}")
    except Exception as e:
        logging.error(e, exc_info = True)
        logging.error("Exepection occured", exc_info = True)
        print(e)
if __name__  ==  "__main__":
    main()

