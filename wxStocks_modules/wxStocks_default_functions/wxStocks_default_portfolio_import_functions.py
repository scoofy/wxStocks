# Add portfolio import functions below:
# You can also edit this file (user/user_functions/wxStocks_csv_import_functions.py) in your own text editor.
import csv, xlrd, logging
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
#		# {cash: your_cash_float_variable, stock_list: [ (ticker_symbol, integer_of_shares_held), (etc,etc), ... ] }
#		# "your_dictionary['cash']" must refer to the relevant cash float.
#		# "your_dictionary['stock_list']" must refer to the relevant list of stock, share tuples.
#		# "your_dictionary['cost_basis_dict']" must refer to the relevant list of stock, cost basis tuples.
#		return (dict_list, attribute_suffix)

################################################################################################################
def sample_csv(csv_file):
	"""Sample CSV portfolio import"""
	# file is default format:
	# with open(csv_file) as csv_file:
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
	cost_basis_dict = {}
	count = 0

	ticker_col = None
	ticker_vars = ["ticker", "symbol"]
	quantity_col = None
	quantity_vars = ["quantity"]
	cost_basis_col = None
	cost_basis_vars = ["costbasis", "cost basis", "cost_basis"]
	market_value_col = None
	market_value_vars = ["marketvalue", "market value", "market_value"]
	cash_row = None
	cash_vars = ["Cash", "cost basis", "cost_basis"]
	for row in portfolio_data:
		for col in row:
			# quick parser for keywords
			if ticker_col is None:
				for var in ticker_vars:
					if var in col.lower():
						ticker_col = row.index(col)
			if quantity_col is None:
				for var in quantity_vars:
					if var in col.lower():
						quantity_col = row.index(col)
			if cost_basis_col is None:
				for var in cost_basis_vars:
					if var in col.lower():
						cost_basis_col = row.index(col)
			if market_value_col is None:
				for var in market_value_vars:
					if var in col.lower():
						market_value_col = row.index(col)
			if cash_row is None:
				for var in cash_vars:
					if var in col:
						cash_row = portfolio_data.index(row)
	# Go!
	if ticker_col is not None and quantity_col is not None:
		for row in portfolio_data:
			if cash_row is not None:
				if row == cash_row:
					cash = row[market_value_col]
					formatted_cash = ""
					for char in cash:
						if char == "$" or char == " ":
							pass
						else:
							formatted_cash += char
					cash = float(formatted_cash)
			ticker = None
			possible_ticker = row[ticker_col]
			if possible_ticker == possible_ticker.upper():
				ticker = possible_ticker
			if ticker:
				stock_shares_tuple = (ticker, row[quantity_col])
				new_account_stock_list.append(stock_shares_tuple)
				if cost_basis_col is not None:
					basis = row[cost_basis_col]
					formatted_basis = ""
					for char in basis:
						if char == "$" or char == " ":
							pass
						else:
							formatted_basis += char
					basis = float(formatted_basis)
					cost_basis_dict[ticker] = basis

	if cash == "This should be changed":
		logging.error('Formatting error in CSV import')
	account_dict = {"cash": cash, "stock_list": new_account_stock_list, "cost_basis_dict": cost_basis_dict}

	if not account_dict:
		logging.error("Error: empty account dictionary to return.")
		return

	return account_dict


def sample_xls(xls_file, attribute_suffix = "_my"):
	"""Sample XLS portfolio import"""
	if not xlrd:
		raise Exception("Module XLRD is not installed on your machine, please install it")
		return

	import config
	from wxStocks_modules import wxStocks_utilities as utils

	xlrd_workbook = xlrd.open_workbook(xls_file.name)

	relevant_spreadsheet_list  = utils.return_relevant_spreadsheet_list_from_workbook(xlrd_workbook)

	dict_list = []
	# sample.xls specific

	# only 1 sheet
	if not len(relevant_spreadsheet_list) == 1:
		raise Exception("\nError in default_xls() in wxStocks_portfolio_import_functions.py\nspreadsheet list > 1 sheet\n")
		return None
	spreadsheet = relevant_spreadsheet_list[0]

	num_columns = spreadsheet.ncols
	num_rows = spreadsheet.nrows

	#print line_number(), self.portfolio_data
	new_account_stock_list = []
	cash = "This should be changed"
	cost_basis_dict = {}
	count = 0

	ticker_col = None
	ticker_vars = ["ticker", "symbol"]
	quantity_col = None
	quantity_vars = ["quantity"]
	cost_basis_col = None
	cost_basis_vars = ["costbasis", "cost basis", "cost_basis"]
	market_value_col = None
	market_value_vars = ["marketvalue", "market value", "market_value"]
	cash_row = None
	cash_vars = ["Cash", "cost basis", "cost_basis"]
	for row_num in range(num_rows):
		for col_num in range(num_columns):
			cell_value = utils.return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = row_num, column = col_num)
			cell_value = str(cell_value)
			# quick parser for keywords
			if ticker_col is None:
				for var in ticker_vars:
					if var in cell_value.lower():
						ticker_col = col_num
			if quantity_col is None:
				for var in quantity_vars:
					if var in cell_value.lower():
						quantity_col = col_num
			if cost_basis_col is None:
				for var in cost_basis_vars:
					if var in cell_value.lower():
						cost_basis_col = col_num
			if market_value_col is None:
				for var in market_value_vars:
					if var in cell_value.lower():
						market_value_col = col_num
			if cash_row is None:
				for var in cash_vars:
					if var in cell_value:
						cash_row = row_num
	# Go!
	if ticker_col is not None and quantity_col is not None:
		for row_num in range(num_rows):
			if cash_row is not None:
				if row_num == cash_row:
					cash = utils.return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = row_num, column = market_value_col)
					formatted_cash = ""
					for char in cash:
						if char == "$" or char == " ":
							pass
						else:
							formatted_cash += char
					cash = float(formatted_cash)
			ticker = None
			possible_ticker = utils.return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = row_num, column = ticker_col)
			if possible_ticker == possible_ticker.upper():
				ticker = possible_ticker
			if ticker:
				stock_shares_tuple = (ticker, utils.return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = row_num, column = quantity_col))
				new_account_stock_list.append(stock_shares_tuple)
				if cost_basis_col is not None:
					basis = utils.return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = row_num, column = cost_basis_col)
					formatted_basis = ""
					for char in basis:
						if char == "$" or char == " ":
							pass
						else:
							formatted_basis += char
					basis = float(formatted_basis)
					cost_basis_dict[ticker] = basis

	if cash == "This should be changed":
		logging.error('Formatting error in CSV import')
	account_dict = {"cash": cash, "stock_list": new_account_stock_list, "cost_basis_dict": cost_basis_dict}

	if not account_dict:
		logging.error("Error: empty account dictionary to return.")
		return

	return account_dict
	return (dict_list, attribute_suffix)




# end of line
