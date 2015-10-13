# Add screen functions below:
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

def return_stocks_with_pe_less_than_10(stock):
	'''PE < 10'''
	try:
		if stock.PERatio_yf:
			if float(stock.PERatio_yf) < 10:
				return True
	except Exception as e:
		pass
		#print line_number(),e
	return False

def forbes_99_tickers(stock):
	'''forbes 99'''
	from wxStocks_modules import wxStocks_utilities as utils
	the_stock = None
	ticker_text = open("forbes_99_tickers.txt", 'rb')
	for line in ticker_text:
		print str(utils.strip_string_whitespace(line))
		if stock.ticker == str(utils.strip_string_whitespace(line)):
			the_stock = stock
	return the_stock is not None

def jas_tickers(stock):
	'''jas tickers'''
	from wxStocks_modules import wxStocks_utilities as utils
	the_stock = None
	ticker_text = open("jas_tickers.txt", 'rb')
	for line in ticker_text:
		print str(utils.strip_string_whitespace(line))
		if stock.ticker == str(utils.strip_string_whitespace(line)):
			the_stock = stock
	return the_stock is not None














# end of line