import numpy 
import math, time
import config

import sys

import inspect
def line_number():
	"""Returns the current line number in our program."""
	line_number = inspect.currentframe().f_back.f_lineno
	line_number_string = "Line %d:" % line_number
	return line_number_string



####################### Screening functions ###############################################
def return_stocks_with_pe_less_than_10():
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
