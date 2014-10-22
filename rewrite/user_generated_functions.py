# add functions below

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

def function_pretending_to_be_a_method(stock):
	"""I'm a method... Not really, i'm actually a fuction."""
	return_string = ""
	for letter in stock.firm_name:
		return_string = return_string + letter + letter
	return return_string

def this_is_a_function(stock):
	"I'm a fuction!"
	return_string = ""
	for letter in stock.firm_name:
		return_string = return_string + letter + " "
	return return_string






















# end of line