import wx
import wxStocks_utilities as utils
import wxStocks_db_functions as db
import numpy, inspect, os
from collections import namedtuple
from wxStocks_classes import Account



def line_number():
	"""Returns the current line number in our program."""
	line_number = inspect.currentframe().f_back.f_lineno
	line_number_string = "Line %d:" % line_number
	return line_number_string
############################################################################################

Tuple_Reference = namedtuple("Four_Tuple_Reference", ["value", "stock"])

def return_ranked_list_from_rank_function(stock_list, rank_function):
	rank_list = []
	copy_list_for_median_adjustment = []
	median_replaced_list = []

	decending = True
	rank_error_as_median = False
	reverse_var = not decending

	first_loop = True

	# first get data from relevant function:
	for stock in stock_list:
		four_tuple = rank_function(Stock = stock)
		# 4-tuple is (relevant_value, Stock, decending, rank_error_as_median)

		print line_number(), four_tuple

		my_tuple = Tuple_Reference(four_tuple[0], four_tuple[1])
		
		print line_number(), my_tuple.stock.symbol, my_tuple.value
		print ""

		rank_list.append(my_tuple)
		copy_list_for_median_adjustment.append(my_tuple)

		if first_loop:
			reverse_var = four_tuple[2]
			#print line_number(), "reverse_var =", reverse_var
			rank_error_as_median = four_tuple[3]
			first_loop = False

	# assign median for error values if desired
	if rank_error_as_median:
		real_values = []
		for relevant_tuple in copy_list_for_median_adjustment:
			if relevant_tuple.value not in [None, "None", "none", "N/A"]:
				real_values.append(relevant_tuple.value)
				#print line_number(), relevant_tuple.stock.symbol, relevant_tuple.value
			else:
				pass
				#print line_number(), relevant_tuple
				#print line_number(), "not adding", relevant_tuple.stock.symbol, ":" , relevant_tuple.value
		median = numpy.median(numpy.array(real_values))

		print line_number(), "Median =", median

		for relevant_tuple in copy_list_for_median_adjustment:
			if relevant_tuple.value in [None, "None", "none", "N/A"]:
				new_tuple = Tuple_Reference(median, relevant_tuple.stock)
				median_replaced_list.append(new_tuple)
			else:
				median_replaced_list.append(relevant_tuple)
		copy_list_for_median_adjustment = median_replaced_list

	# sort
	if rank_error_as_median:
		copy_list_for_median_adjustment.sort(key = lambda x: float(x.value), reverse = reverse_var)

		rank_list_adjustment_list = []

		for median_adjusted_tuple in copy_list_for_median_adjustment:
			for reference_tuple in rank_list:
				if median_adjusted_tuple.stock == reference_tuple.stock:
					rank_list_adjustment_list.append(reference_tuple)

		rank_list = rank_list_adjustment_list		
	else:
		# throw 'None' values on the end
		list_of_relevant_values = []
		list_of_none_values = []
		for relevant_tuple in rank_list:
			if relevant_tuple.value in [None, "none", "N/A"]:
				list_of_none_values.append(relevant_tuple)
			else:
				list_of_relevant_values.append(relevant_tuple)

		rank_list = list_of_relevant_values
		rank_list.sort(key = lambda x: float(x.value), reverse = reverse_var)

		for relevant_tuple in list_of_none_values:
			rank_list.append(relevant_tuple)

	# return sorted stock tuple list
	
	return rank_list

def import_csv_via_user_created_function(wxWindow, user_created_function):
	'''adds import csv data to stocks data via a user created function'''
	dirname = ''
	dialog = wx.FileDialog(wxWindow, "Choose a file", dirname, "", "*.csv", wx.OPEN)
	if dialog.ShowModal() == wx.ID_OK:
		filename = dialog.GetFilename()
		dirname = dialog.GetDirectory()
		
		csv_file = open(os.path.join(dirname, filename), 'rb')
		dict_list_and_attribute_suffix_tuple = user_created_function(csv_file)
		csv_file.close()
	else:
		return None
	dialog.Destroy()
	attribute_suffix = dict_list_and_attribute_suffix_tuple[1]
	success = None
	if len(attribute_suffix) != 3 or attribute_suffix[0] != "_":
		print line_number(), "Error: your attribute suffix is improperly formatted"
		success = "fail"
		return success
	dict_list = dict_list_and_attribute_suffix_tuple[0]
	for this_dict in dict_list:
		if not this_dict:
			continue
		try:
			this_dict['stock']
		except Exception as e:
			print line_number(), e
			print line_number(), "Error: your dictionary does not have the ticker as your_dictionary['stock']"
			if success in ["success", "some"]:
				success = "some"
			else:
				success = "fail"
			continue
		stock = utils.return_stock_by_symbol(this_dict['stock'])
		if not stock:
			if success in ["success", "some"]:
				success = "some"
			else:
				success = "fail"
			continue
		for key, value in this_dict.iteritems():
			if key == "stock":
				continue
			else:
				setattr(stock, key + attribute_suffix, value)
				if success in ["fail", "some"]:
					success = "some"
				else:
					success = "success"

	return success

def import_portfolio_via_user_created_function(wxWindow, portfolio_id, user_created_function):
	dirname = ''
	dialog = wx.FileDialog(wxWindow, "Choose a file", dirname, "", "*.csv", wx.OPEN)
	if dialog.ShowModal() == wx.ID_OK:
		filename = dialog.GetFilename()
		dirname = dialog.GetDirectory()
		
		csv_file = open(os.path.join(dirname, filename), 'rb')

		account_dict = user_created_function(csv_file)

		csv_file.close()
	else:
		return None
	dialog.Destroy()

	if not account_dict:
		print line_number(), "Error: No account dictionary returned from user function."

	cash = account_dict['cash']
	stock_share_tuple_list = account_dict['stock_list']

	account_obj = Account(portfolio_id, cash, stock_share_tuple_list)

	db.save_portfolio_object(account_obj, portfolio_id)

	return account_obj

	

# end of line