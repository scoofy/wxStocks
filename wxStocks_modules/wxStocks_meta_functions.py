import inspect, sys
from collections import namedtuple
def line_number():
	"""Returns the current line number in our program."""
	return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)


Function_Reference = namedtuple("Function_Reference", ["name", "function", "doc"])

functions_to_ignore_list = ["line_number"]

def return_function_triple(type_of_functions): # "screen", "rank", "csv_import", "xls_import", "portfolio".
	"""returns function 3-tuple of the form (name, function, doc)."""
	# First we import the modules we want to inspect
	if type_of_functions == "screen":
		import wxStocks_screen_functions as function_file
	elif type_of_functions == "rank":
		import wxStocks_rank_functions as function_file
	elif type_of_functions == "csv_import":
		import wxStocks_csv_import_functions as function_file
	elif type_of_functions == "xls_import":
		import wxStocks_xls_import_functions as function_file
	elif type_of_functions == "portfolio":
		import wxStocks_portfolio_import_functions as function_file
	elif type_of_functions == "analysis":
		import wxStocks_custom_analysis_spreadsheet_builder as function_file
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
				if function_tuple[1].__doc__:
					if len(function_tuple[1].__doc__) > 30:
						print "\n" * 5
						print line_number(), "Error: user function doc strings should be less than 30 characters in length"
						print "\n" * 5
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
		short_name_list.append(triple.doc)
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
		short_name_list.append(triple.doc)
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
		short_name_list.append(triple.doc)
	return short_name_list
def return_csv_import_functions():
	'''returns list of csv import functions'''
	triple_list = return_csv_import_function_triple()
	function_list = [x.function for x in triple_list]
	return function_list


def return_xls_import_function_triple():
	"""returns import function 3-tuple of the form (name, function, doc string)."""
	function_triple_list = return_function_triple(type_of_functions = "xls_import")
	return function_triple_list
def return_xls_import_function_full_names():
	'''returns csv import functions full names'''
	triple_list = return_xls_import_function_triple()
	full_name_list = [x.name for x in triple_list]
	return full_name_list
def return_xls_import_function_short_names():
	'''returns csv import functions doc strings'''
	triple_list = return_xls_import_function_triple()
	short_name_list = []
	for triple in triple_list:
		short_name_list.append(triple.doc)
	return short_name_list
def return_xls_import_functions():
	'''returns list of csv import functions'''
	triple_list = return_xls_import_function_triple()
	function_list = [x.function for x in triple_list]
	return function_list


# unfinished (? -- not sure if this is still the case)
def return_portfolio_import_function_triple():
	"""returns import function 3-tuple of the form (name, function, doc string)."""
	function_triple_list = return_function_triple(type_of_functions = "portfolio")
	return function_triple_list
def return_portfolio_import_function_full_names():
	'''returns portfolio import functions full names'''
	triple_list = return_portfolio_import_function_triple()
	full_name_list = [x.name for x in triple_list]
	return full_name_list
def return_portfolio_import_function_short_names():
	'''returns csv import functions doc strings'''
	triple_list = return_portfolio_import_function_triple()
	short_name_list = []
	for triple in triple_list:
		short_name_list.append(triple.doc)
	return short_name_list
def return_portfolio_import_functions():
	'''returns list of csv import functions'''
	triple_list = return_portfolio_import_function_triple()
	function_list = [x.function for x in triple_list]
	return function_list



def return_custom_analysis_function_triple():
	"""returns custom_analysis function 3-tuple of the form (name, function, doc)."""
	function_triple_list = return_function_triple(type_of_functions = "analysis")
	function_triple_list = [function_triple for function_triple in function_triple_list if function_triple.name != "namedtuple"]
	return function_triple_list
def return_custom_analysis_function_full_names():
	'''returns custom_analysis functions full names'''
	triple_list = return_rank_function_triple()
	full_name_list = [x.name for x in triple_list]
	return full_name_list
def return_custom_analysis_function_short_names():
	'''returns custom_analysis functions doc strings'''
	triple_list = return_rank_function_triple()
	short_name_list = []
	for triple in triple_list:
		short_name_list.append(triple.doc)
	return short_name_list
def return_custom_analysis_functions():
	'''returns list of custom_analysis functions'''
	triple_list = return_rank_function_triple()
	function_list = [x.function for x in triple_list]
	return function_list




# end of line