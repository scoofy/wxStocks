import numpy 
import math, time
import config

import sys

import pprint as pp

import inspect
from collections import namedtuple

from wxStocks_classes import Stock

goog = Stock("goog")
goog.firm_name = "Google"

functions_to_ignore_list = ["line_number", "functions_names", "namedtuple"]

def line_number():
	"""Returns the current line number in our program."""
	line_number = inspect.currentframe().f_back.f_lineno
	line_number_string = "Line %d:" % line_number
	return line_number_string

Function_Reference = namedtuple("Function_Reference", ["name", "func", "doc"])
def functions_names():
	"""Returns function docs in our module."""
	# First we import the modules we want to inspect
	import user_generated_functions as user_functions
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
	
	for triple in function_triple_list:
		if type(triple) is Function_Reference:
			print ""
			print triple.name
			print triple.doc
			print triple.func
			print inspect.getargspec(triple.func)
			
			print triple.func(stock = goog)

	print ""



####################### Screening functions ###############################################
def return_stocks_with_pe_less_than_10(stock):
	'''PE < 10'''
	screen_results = []
	for ticker in config.GLOBAL_STOCK_DICT:
		stock = config.GLOBAL_STOCK_DICT[ticker]
		try:
			if stock.PERatio_yf:
				if float(stock.PERatio_yf) < 10:
					screen_results.append(stock)
		except Exception as e:
			pass
			#print line_number(),e
	return screen_results
############################################################################################
functions_names()
sys.exit()




















# end of line