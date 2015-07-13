# Add portfolio import functions below:
# You can also edit this file (wxStocks_csv_import_functions.py) in your own text editor.
import csv
########################################### instructions #######################################################
# functions should be of the following form:

#	def your_full_csv_import_function_name(csv_file, attribute_suffix = "underscore and two letters"):
#		"""short name""" # <--- this will appear in import dropdowns
#
#		# add some csv processing:
#		data = csv.reader(csv_file)
#		# do stuff to data
#
#		# Always return a list of dictionaries and an properly formatted suffix for your attribute.
#		# Dictionaries should be of the following protocol. Note: shares should be passed as integer, one should round their fractional shares as they see appropriate.
#		# {cash: your_cash_float_variable, stock_list: [ (ticker_symbol, integer_of_shares_held), (etc,etc), ... ], cost_basis_dict: {ticker_symbol: cost_basis} }
#		# "your_dictionary['cash']" must refer to the relevant cash float.
#		# "your_dictionary['stock_list']" must refer to the relevant list of stock, share tuples.
#		# "your_dictionary['cost_basis_dict']" must refer to the relevant dictionary of stocks, indexing their cost basis.
#		return (dict_list, attribute_suffix)

# okay, new structure:

# cash -> cash
# change

# stock -> one stock
# add, subtract, update attribute

# stock dict -> stock dict
# add, subtract, update attribute
# but what to do with the unmentioned

# stock dict cost basis -> stock dict cost basis
# best example of above... what to do if not all are mentioned


################################################################################################################
def line_number():
    import inspect
    """Returns the current line number in our program."""
    #print 'remove this temporary line number function'
    return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)


def schwab_csv(csv_file):
	"""Schwab Account CSV"""
	# file is schwab format:
	reader = csv.reader(csv_file)
	row_list = []
	for row in reader:
		row_list.append(row)
	washed_row_list = []
	for row in row_list:
		if row:
			washed_row = []
			for cell in row:
				# strip whitespace
				washed_cell = " ".join(cell.split())
				##
				washed_row.append(washed_cell)
			washed_row_list.append(washed_row)
	new_account_file_data = washed_row_list

	portfolio_data = new_account_file_data

	#print line_number(), self.portfolio_data
	new_account_stock_list = []
	cash = "This should be changed"
	count = 0
	for row in portfolio_data:
		#print line_number(),count
		if count <= 1:
			count += 1
			continue
		try:
			if row[0] and row[11]:
				if str(row[11]) == "Cash & Money Market":
					cash = row[5]
					formatted_cash = ""
					for char in cash:
						if char == "$" or char == " ":
							pass
						else:
							formatted_cash += char
					cash = float(formatted_cash)
					#print line_number(),'cash =', cash
				elif str(row[11]) == "Equity":
					# format: ticker(0), name(1), quantity(2), price(3), change(4), market value(5), day change$(6), day change%(7), reinvest dividends?(8), capital gain(9), percent of account(10), security type(11)
					stock_shares_tuple = (row[0], int(row[2]))
					#print line_number(), stock_shares_tuple
					new_account_stock_list.append(stock_shares_tuple)
					#print line_number(),"stock"
		except Exception, exception:
			#print line_number(),exception
			#print line_number(),row
			pass
		count += 1
	if cash == "This should be changed":
		#print line_number(), 'Formatting error in CSV import'
		pass
	account_dict = {"cash": cash, "stock_list": new_account_stock_list}

	if not account_dict:
		#print line_number(), "Error: empty account dictionary to return."
		return

	return account_dict

def schwab_gain_loss_csv(csv_file):
	"""Schwab Gain/Loss CSV"""
	import pprint as pp
	# file is schwab format:
	reader = csv.reader(csv_file)
	row_list = []
	for row in reader:
		row_list.append(row)
	print line_number()
	pp.pprint(row_list)
	washed_row_list = []
	for row in row_list:
		if row:
			washed_row = []
			for cell in row:
				# strip whitespace
				washed_cell = " ".join(cell.split())
				##
				washed_row.append(washed_cell)
			washed_row_list.append(washed_row)
	new_account_file_data = washed_row_list

	portfolio_data = new_account_file_data

	#print line_number(), self.portfolio_data
	new_account_stock_list = []
	new_account_cost_basis_dict = {}
	count = 0
	for row in portfolio_data:
		#print line_number(),count
		if count <= 1:
			count += 1
			continue
		elif str(row[0]) == "Total":
			count += 1
			continue
		try:
			if row[0] and row[2] and row[7]:
				stock_shares_tuple = (row[0], int(row[2]))
				stock_ticker = str(row[0]).upper()
				new_account_cost_basis_dict[stock_ticker] = row[7]
				new_account_stock_list.append(stock_shares_tuple)
				#print line_number(),"stock"
		except Exception, exception:
			#print line_number(),exception
			#print line_number(),row
			pass
		count += 1

	if not new_account_cost_basis_dict:
		#print line_number(), "Error: empty account dictionary to return."
		return {}

	return new_account_cost_basis_dict

# end of line