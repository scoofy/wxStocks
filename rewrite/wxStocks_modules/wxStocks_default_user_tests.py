# Add test functions below:
# You can also edit this file (wxStocks_screen_functions.py) in your own text editor. 

########################################### instructions #######################################################
# functions should be of the following form:

#	def your_full_test_name(stock): # <--- the stock will be provided by the program, please keep this as "stock".
#		"""short name""" # <--- this will appear in screen dropdowns
#
#		# maybe some conditional:
#
#		if stock.attribute >, <, or == some_value:
#			result_bool = True
#		else:
#			result_bool = False
#
#		# or a simpler version like:
#
#		result_bool = stock.attribute > some_test
#		
#		# Just make sure the return value is a boolean so you can...
#
#		return result_bool

#	def my_example_function_returns_true_for_stocks_with_PEs_greater_than_ten(stock):
#		"""PE > 10"""
#		if stock.PERatio_yf > 10:
#			result_bool = True
#		else:
#			result_bool = False
#		return result_bool

################################################################################################################

def ticker_less_than_three_letters(stock):
	"""Ticker < 3 letters"""
	if len(stock.ticker) < 3:
		return True
	else:
		return False

def firm_name_contains_the_letters_LLC(stock):
	"LLC in name"
	llc_in_name = False
	if "LLC" in stock.firm_name:
		llc_in_name = True
	if "llc" in stock.firm_name:
		llc_in_name = True
	return llc_in_name






















# end of line