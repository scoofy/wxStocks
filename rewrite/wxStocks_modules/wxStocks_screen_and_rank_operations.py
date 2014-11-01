import wxStocks_utilities as utils
import numpy, inspect
from collections import namedtuple



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

		my_tuple = Tuple_Reference(four_tuple[0], four_tuple[1])
		rank_list.append(my_tuple)
		copy_list_for_median_adjustment.append(my_tuple)

		if first_loop:
			reverse_var = not four_tuple[2]
			rank_error_as_median = four_tuple[3]
			first_loop = False

	# assign median for error values if desired
	if rank_error_as_median:
		real_values = []
		for relevant_tuple in copy_list_for_median_adjustment:
			if relevant_tuple.value not in [None, "none", "N/A"]:
				real_values.append(relevant_tuple.value)
				print line_number(), relevant_tuple.stock.symbol, relevant_tuple.value
			else:
				print line_number(), relevant_tuple
				print line_number(), "not adding", relevant_tuple.stock.symbol, ":" , relevant_tuple.value
		median = numpy.median(numpy.array(real_values))
		for relevant_tuple in copy_list_for_median_adjustment:
			if relevant_tuple.value is None:
				new_tuple = Tuple_Reference(median, relevant_tuple.stock)
				median_replaced_list.append(new_tuple)
		copy_list_for_median_adjustment = median_replaced_list

	# sort
	if rank_error_as_median:
		copy_list_for_median_adjustment.sort(key = lambda x: x.value, reverse = reverse_var)

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
		rank_list.sort(key = lambda x: x.value, reverse = reverse_var)

		for relevant_tuple in list_of_none_values:
			rank_list.append(relevant_tuple)

	# return sorted stock tuple list
	
	return rank_list



	# end of line