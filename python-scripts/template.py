from typing import List


# regex to be modified to check dao., utils., service.,


class MOCK_FUNC_DICT:
	def __init__(self, interface_name, mock_func_name, mock_func_inputs, mock_func_outputs):
		self.interface_name: str = interface_name
		self.mock_func_name: str = mock_func_name
		self.mock_func_inputs: List[str] =  mock_func_inputs
		self.mock_func_outputs: List[str] =  mock_func_outputs
		if mock_func_name == "Decode":
			self.mock_run : bool = True
		else:
			self.mock_run : bool = False
	def __repr__(self):
		return str(vars(self))
	def __eq__(self, object) -> bool:
		if self is None and object is None:
			return True
		if self is not None and object is not None:     
			return self.interface_name == object.interface_name and \
			self.mock_func_name == object.mock_func_name and \
			self.mock_func_inputs == object.mock_func_inputs and \
			self.mock_func_outputs == object.mock_func_outputs and \
			self.mock_run == object.mock_run 
		return False

class TEST_CASE_DICT:
	def __init__(self, func_name, test_case_id, inputs, expected_outputs, mock_functions):
		self.func_name: str = func_name
		self.test_case_id: int = test_case_id
		self.inputs: List[str] = inputs
		self.expected_outputs: List[str] = expected_outputs
		self.mock_functions: List[MOCK_FUNC_DICT] = [mock_function for mock_function in mock_functions]
		# self.output_changed : bool = False
	def __repr__(self):
		return str(vars(self))
	def __eq__(val1, val2):
		if val1 is None and val2 is None:
			return True
		if val1 is not None and val2 is not None:
			return val1.func_name == val2.func_name and val1.inputs == val2.inputs and val1.expected_outputs == val2.expected_outputs and val1.mock_functions == val2.mock_functions
		return False

TEST_CASE_TEMPLATE = """
	{
		Case: "%s - %s",
		Inputs: []interface{}{
			%s
		},
		ExpectedOutputs: []interface{}{
			%s
		},
		MockFunctions: []func(ctx tapcontext.TContext){
			%s
		},
	},
"""

MOCK_FUNC_TEMPLATE = """
		func(ctx tapcontext.TContext) {
			tests.%s.
				On(
					"%s",
					%s
				).
				Return(
					%s
				).
				%s
		},
"""

OUTPUT_PARAMETER_TEMPLATE = "out%s"
ASSERT_STATEMENT_TEMPLATE = """
fmt.Println("asserting out%s")
if !assert.Equal(t, test.ExpectedOutputs[%s], out%s){
    panic("Not equal output param - out%s, kindly check")
}"""

AssertTemplate = """
		assert.Equal(t, test.ExpectedOutputs[%s], out%s)
"""

TestServiceInputArgumentTemplate = " test.Inputs[%s].(%s)"



TEST_FUNC_TEMPLATE = """
// %s

func Test%s(t *testing.T) {
	%s
	var ctx = tapcontext.NewTapContext()
	for _, test := range test_cases.%sTestCases {
		fmt.Println("Case - ", test.Case)
		tests.InitializeMockFunctions(test.MockFunctions, ctx)
		%s %s %s.%s(ctx, %s)
		%s
	}
}
"""

class UT_TEST_CASES_DICT:
    def __init__(self, func_name, test_cases):
        self.func_name:str = func_name
        self.test_cases: List[TEST_CASE_DICT] = [test_case for test_case in test_cases]
		

UT_TEST_SERVICE_FILE_TEMPLATE = """
package test_service
import (
%s
)
%s
"""

UT_TEST_CASES_TEMPLATE = """
package test_cases
import (
 %s
)
%s

"""
TEST_CASES_TEMPLATE = """
// %s
var %sTestCases = []TestCase{
	%s
}
"""




RUN_TEMPLATE = """
				Run(func(args mock.Arguments) {
					arg := args.Get(2).(*map[string]interface{})
					(*arg) = make(map[string]interface{})
					(*arg)["status"] = "Ok"
					(*arg)["message"] = "message"
				}).
				Once()
"""

RUN_ONCE_TEMPLATE = "Once()"



