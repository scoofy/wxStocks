import inspect
from collections import namedtuple

Function_Reference = namedtuple("Function_Reference", ["name", "function", "doc"])

functions_to_ignore_list = ["line_number"]

def return_screen_function_triple():
	"""returns screen function 3-tuple of the form (name, function, doc)."""
	# First we import the modules we want to inspect
	import wxStocks_screen_functions as screen_functions

	module_list = [] # In case i want to add more modules here. Looks like it'll probably be one file though.
	screen_function_module_contents = inspect.getmembers(screen_functions)
	module_list.append(screen_function_module_contents)

	function_triple_list = []
	for module in module_list:
		for function_tuple in module:
			if inspect.isfunction(function_tuple[1]) and function_tuple[0] not in functions_to_ignore_list: 
				triple = Function_Reference(function_tuple[0], function_tuple[1], function_tuple[1].__doc__)
				function_triple_list.append(triple)
	
	return function_triple_list
def return_screen_function_full_names():
	'''returns screen functions full names'''
	triple_list = return_screen_function_triple()
	full_name_list = [x.name for x in triple_list]
	return full_name_list
def return_screen_function_short_names():
	'''returns screen functions doc strings'''
	triple_list = return_screen_function_triple()
	short_name_list = []
	for triple in triple_list:
		if len(triple.doc) <= 30:
			# This long: '''123456789012345678901234567890'''
			short_name_list.append(triple.doc)
		else:
			short_name_list.append(triple.name)
	return short_name_list
def return_screen_functions():
	'''returns list of screen functions'''
	triple_list = return_screen_function_triple()
	function_list = [x.function for x in triple_list]
	return function_list

def return_rank_function_triple():
	"""returns rank function 3-tuple of the form (name, function, doc)."""
	# First we import the modules we want to inspect
	import wxStocks_rank_functions as rank_functions

	module_list = [] # In case i want to add more modules here. Looks like it'll probably be one file though.
	screen_function_module_contents = inspect.getmembers(rank_functions)
	module_list.append(screen_function_module_contents)

	function_triple_list = []
	for module in module_list:
		for function_tuple in module:
			if inspect.isfunction(function_tuple[1]) and function_tuple[0] not in functions_to_ignore_list: 
				triple = Function_Reference(function_tuple[0], function_tuple[1], function_tuple[1].__doc__)
				function_triple_list.append(triple)
	
	return function_triple_list
def return_rank_function_full_names():
	'''returns screen functions full names'''
	triple_list = return_rank_function_triple()
	full_name_list = [x.name for x in triple_list]
	return full_name_list
def return_rank_function_short_names():
	'''returns screen functions doc strings'''
	triple_list = return_rank_function_triple()
	short_name_list = []
	for triple in triple_list:
		if len(triple.doc) <= 30:
			# This long: '''123456789012345678901234567890'''
			short_name_list.append(triple.doc)
		else:
			short_name_list.append(triple.name)
	return short_name_list
def return_rank_functions():
	'''returns list of screen functions'''
	triple_list = return_rank_function_triple()
	function_list = [x.function for x in triple_list]
	return function_list












# end of line