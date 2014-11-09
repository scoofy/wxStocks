import inspect
from collections import namedtuple
def line_number():
	"""Returns the current line number in our program."""
	line_number = inspect.currentframe().f_back.f_lineno
	line_number_string = "Line %d:" % line_number
	return line_number_string

Function_Reference = namedtuple("Function_Reference", ["name", "function", "doc"])

functions_to_ignore_list = ["line_number"]

def return_function_triple(type_of_functions): # "screen", "rank", or "csv_import".
	"""returns function 3-tuple of the form (name, function, doc)."""
	# First we import the modules we want to inspect
	if type_of_functions == "screen":
		import wxStocks_screen_functions as function_file
	elif type_of_functions == "rank":
		import wxStocks_rank_functions as function_file
	elif type_of_functions == "csv_import":
		import wxStocks_csv_import_functions as function_file
	else:
		print line_number(), "Error: No function type defined."
		return

	module_list = [] # In case i want to add more modules here. Looks like it'll probably be one file though.
	function_module_contents = inspect.getmembers(function_file)
	module_list.append(function_module_contents)

	function_triple_list = []
	for module in module_list:
		for function_tuple in module:
			if inspect.isfunction(function_tuple[1]) and function_tuple[0] not in functions_to_ignore_list: 
				triple = Function_Reference(function_tuple[0], function_tuple[1], function_tuple[1].__doc__)
				function_triple_list.append(triple)
	
	return function_triple_list


def return_screen_function_triple():
	"""returns screen function 3-tuple of the form (name, function, doc)."""
	function_triple_list = return_function_triple(type_of_functions = "screen")	
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
	function_triple_list = return_function_triple(type_of_functions = "rank")		
	return function_triple_list
def return_rank_function_full_names():
	'''returns rank functions full names'''
	triple_list = return_rank_function_triple()
	full_name_list = [x.name for x in triple_list]
	return full_name_list
def return_rank_function_short_names():
	'''returns rank functions doc strings'''
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
	'''returns list of rank functions'''
	triple_list = return_rank_function_triple()
	function_list = [x.function for x in triple_list]
	return function_list

def return_csv_import_function_triple():
	"""returns import function 3-tuple of the form (name, function, doc string)."""
	function_triple_list = return_function_triple(type_of_functions = "csv_import")	
	return function_triple_list
def return_csv_import_function_full_names():
	'''returns csv import functions full names'''
	triple_list = return_csv_import_function_triple()
	full_name_list = [x.name for x in triple_list]
	return full_name_list
def return_csv_import_function_short_names():
	'''returns csv import functions doc strings'''
	triple_list = return_csv_import_function_triple()
	short_name_list = []
	for triple in triple_list:
		if len(triple.doc) <= 30:
			# This long: '''123456789012345678901234567890'''
			short_name_list.append(triple.doc)
		else:
			short_name_list.append(triple.name)
	return short_name_list
def return_csv_import_functions():
	'''returns list of csv import functions'''
	triple_list = return_csv_import_function_triple()
	function_list = [x.function for x in triple_list]
	return function_list









# end of line