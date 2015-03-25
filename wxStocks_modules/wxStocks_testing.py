import logging, inspect, numpy, sys
import wxStocks_modules.wxStocks_formulas as formula

def run_test(
	sample_stock, 
	sample_annual_data, 
	sample_analyst_estimates,
	stock_list,
	quit=False
	):
	annual_data_attribute_list = return_dictionary_of_object_attributes_and_values(sample_annual_data)
	analyst_estimates_attribute_list = return_dictionary_of_object_attributes_and_values(sample_analyst_estimates)

	data_lists = [annual_data_attribute_list, analyst_estimates_attribute_list]

	for attribute_list in data_lists:
		if attribute_list:
			for attribute in attribute_list:
				setattr(sample_stock, attribute, attribute_list[attribute])
		else:
			print sample_stock.symbol, "needs to be updated"

	print "\n\n\n\n\n\n"
	print "-" * 3300
	print "Testing area"
	print "\n\n\n\n\n\n"
	print "\n\n\n"
	for equation in formula.stock_only_needed:
		print "\n\n\n"	
		print "trying: %s %s" % (sample_stock.symbol, equation.__name__)
		try:
			print equation(sample_stock)
			continue
		except Exception, exception:
			print ""
			print type(exception), exception, line_number()
			print "function", equation.__name__, ":", "failed for", sample_stock.ticker

	for equation in formula.stock_plus_stock_list_needed:
		print "\n\n\n"	
		print "trying: %s %s" % (sample_stock.symbol, equation.__name__)
		try:
			print equation(sample_stock, stock_list)
			continue
		except Exception, exception:
			print ""
			print type(exception), exception, line_number()
			print "function", equation.__name__, ":", "failed for", sample_stock.ticker

	for equation in formula.annual_data_needed:
		print "\n\n\n"	
		print "trying: %s %s" % (sample_stock.symbol, equation.__name__)
		try:
			print equation(sample_stock, sample_annual_data)
			continue
		except Exception, exception:
			print ""
			print type(exception), exception, line_number()
			print "function", equation.__name__, ":", "failed for", sample_stock.ticker

	print "\n\n\n"

	print_this_dict = return_dictionary_of_object_attributes_and_values(sample_stock)

	#for attribute in print_this_dict:
	#	print "%s:" % attribute, print_this_dict[attribute]

	print "\n\n\n"

	if quit:
		sys.exit()


####################### Utility functions #################################################
def return_dictionary_of_object_attributes_and_values(obj):
	attribute_list = []
	if obj:
		for key in obj.__dict__:
			if key[:1] != "__":
				attribute_list.append(key)

		obj_attribute_value_dict = {}

		for attribute in attribute_list:
			obj_attribute_value_dict[attribute] = getattr(obj, attribute)

		#for attribute in obj_attribute_value_dict:
		#	print attribute, ":", obj_attribute_value_dict[attribute]

		return obj_attribute_value_dict
def line_number():
	"""Returns the current line number in our program."""
	return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)

############################################################################################