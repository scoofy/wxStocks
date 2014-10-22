import inspect
from collections import namedtuple
from wxStocks_classes import Stock

Function_Reference = namedtuple("Function_Reference", ["name", "func", "doc"])

functions_to_ignore_list = ["line_number", "functions_names", "namedtuple"]

def return_function_triple():
	"""Returns function tuple of the form (name, function, doc)."""
	# First we import the modules we want to inspect
	import user_created_tests as user_functions
	import wxStocks_screen_functions as screen_functions

	module_list = []

	user_functions_module_contents = inspect.getmembers(user_functions)
	screen_function_module_contents = inspect.getmembers(screen_functions)
	
	module_list.append(user_functions_module_contents)
	module_list.append(screen_function_module_contents)

	function_triple_list = []

	for module in module_list:
		for function_tuple in module:
			if inspect.isfunction(function_tuple[1]) and function_tuple[0] not in functions_to_ignore_list: 
				triple = Function_Reference(function_tuple[0], function_tuple[1], function_tuple[1].__doc__)
				function_triple_list.append(triple)
	
	return function_triple_list

def return_function_full_names():
	triple_list = return_function_triple()
	full_name_list = [x.name for x in triple_list]
	return full_name_list

def return_function_short_names():
	triple_list = return_function_triple()
	short_name_list = [x.doc for x in triple_list]
	return short_name_list

def return_functions():
	triple_list = return_function_triple()
	function_list = [x.function for x in triple_list]
	return function_list
















# end of line