# Add xls import functions below:
# You can also edit this file (wxStocks_xls_import_functions.py) in your own text editor. 
import config
from wxStocks_modules import wxStocks_utilities as utils
try:
	from modules import xlrd
except:
	pass
########################################### instructions #######################################################
# functions should be of the following form:

#	def your_full_xls_import_function_name(xlrd_workbook, attribute_suffix = "underscore and two letters"): 
#		"""short name""" # <--- this will appear in import dropdowns
#
#		# Add some xlrd processing: 
#		# Note, there are some useful xlrd functions in the xlrd section of the
#		# "wxStocks_modules/wxStocks_utilities.py"
#		# file. You may find helpful, and i would recommend theses functions as the xlrd library is not very clear. 
#		# To access these, simple add "from wxStocks_modules import wxStocks_utilities" to the top of this file or in the functions.
#		
#		data = xlrd.do_stuff(xlrd_workbook)
#		# do stuff to data
#
#		# Always return a list of dictionaries and an properly formatted suffix for your attribute.
#		# Dictionaries should be attribute names, with whatever attribute names you want, except your_dictionary['stock']
#		# "your_dictionary['stock']" must refer to the relevant stock ticker, as a way to fetch that stock from the main database.
#		return (dict_list, attribute_suffix)

################################################################################################################
def process_sample_dot_xls(xlrd_workbook, attribute_suffix = "_xl"):
	'''import sample.xls'''
	import config
	from wxStocks_modules import wxStocks_utilities as utils
	relevant_spreadsheet_list  = utils.return_relevant_spreadsheet_list_from_workbook(xlrd_workbook)

	dict_list = []
	# sample.xls specific

	# only 1 sheet
	if not len(relevant_spreadsheet_list) == 1:
		print ""
		print "Error in process_sample_dot_xls() in wxStocks_xls_import_functions.py"
		print "spreadsheet list > 1 sheet"
		print ""
		return None
	spreadsheet = relevant_spreadsheet_list[0]

	num_columns = spreadsheet.ncols
	num_rows = spreadsheet.nrows

	# important row and column numbers
	attribute_name_row = 2 # 3rd row
	ticker_col = 0 # 1st column

	for row_num in range(num_rows):
		if row_num in [0, 1, 2]:
			continue
		datum = None
		dict_to_add = {}
		for col_num in range(num_columns):
			datum = utils.return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = row_num, column = col_num)
			attribute_name = utils.return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = attribute_name_row, column = col_num)
			if datum:
				print attribute_name, datum
				if col_num == ticker_col:
					dict_to_add = {"stock": datum}
				else:
					if attribute_name:
						dict_to_add[attribute_name] = datum
					else:
						print "Error: wxStocks_xls_import_functions: function: process_sample_dot_xls: Data present with no named attribute."

		if dict_to_add:
			dict_list.append(dict_to_add)

	print dict_list

	return (dict_list, attribute_suffix)

def import_aaii_exported_xls(xlrd_workbook, attribute_suffix = "_aa"):
	'''AAII .xls file'''

	relevant_spreadsheet_list  = utils.return_relevant_spreadsheet_list_from_workbook(xlrd_workbook)

	dict_list = []
	# sample.xls specific

	# only 1 sheet
	if not len(relevant_spreadsheet_list) == 1:
		print ""
		print "Error in process_sample_dot_xls() in wxStocks_xls_import_functions.py"
		print "spreadsheet list > 1 sheet"
		print ""
		return None
	spreadsheet = relevant_spreadsheet_list[0]

	num_columns = spreadsheet.ncols
	num_rows = spreadsheet.nrows

	# important row and column numbers
	attribute_name_row = 0 # 1st row
	ticker_col = 1 # 2nd column

	for row_num in range(num_rows):
		if row_num in [0]: # attribute row
			continue
		dict_to_add = {}
		for col_num in range(num_columns):
			datum = utils.return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = row_num, column = col_num)
			attribute_name = utils.return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = attribute_name_row, column = col_num)
			if not datum:
				datum = "-"
			if col_num == ticker_col:
				dict_to_add = {"stock": str(datum)}
			else:
				if attribute_name:
					dict_to_add[attribute_name] = datum
				else:
					print "Error: wxStocks_xls_import_functions: function: process_sample_dot_xls: Data present with no named attribute."

		if dict_to_add:
			dict_list.append(dict_to_add)

	print dict_list

	return (dict_list, attribute_suffix)





# end of line