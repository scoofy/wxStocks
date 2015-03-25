import sys, pprint, os, inspect, string, time

def line_number():
	"""Returns the current line number in our program."""
	return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)

try:
	import modules.xlrd as xlrd # AAII is all excel files
except:
	print line_number(), "Error: xlrd is not installed"
	sys.exit()

from wxStocks_modules import wxStocks_utilities as utils
from wxStocks_modules.wxStocks_classes import Stock, Account
from wxStocks_modules import wxStocks_db_functions as db


all_attribute_list = []
all_attribute_dict = {}
duplicate_list = []
duplicate_tuple_list = []
files_that_have_duplicates = []
files_that_are_all_duplicates = []

### xlrd functions
def return_relevant_spreadsheet_list_from_workbook(xlrd_workbook):
	relevant_sheets = []
	for i in range(xlrd_workbook.nsheets):
		sheet = xlrd_workbook.sheet_by_index(i)
		print line_number(), sheet.name
		if sheet.nrows or sheet.ncols:
			print line_number(), "rows x cols:", sheet.nrows, sheet.ncols
			relevant_sheets.append(sheet)
		else:
			print line_number(), "is empty"
	return relevant_sheets
def return_xls_cell_value(xlrd_spreadsheet, row, column):
	return xlrd_spreadsheet.cell_value(rowx=row, colx=column)

def import_aaii_files_from_data_folder():
	""""import aaii .xls files"""
	current_directory = os.path.dirname(os.path.realpath(__file__))
	parent_directory = os.path.split(current_directory)[0]
	grandparent_directory = os.path.split(current_directory)[0]
	great_grandparent_directory = os.path.split(grandparent_directory)[0]
	data_directory = os.path.join(great_grandparent_directory, "AAII_data_import_folder")

	aaii_filenames = [filename for filename in os.listdir(data_directory) if os.path.isfile(os.path.join(data_directory, filename)) and filename != "!.gitignore"]

	expired_data = []
	for filename in aaii_filenames:
		current_time = time.time()
		one_week_in_seconds = 604800
		file_stats = os.stat(data_directory + "/" + filename)
		file_last_modified_epoch = file_stats.st_mtime # last modified
		#print filename, "last modified:", file_stats.st_mtime
		if (current_time - one_week_in_seconds) > file_last_modified_epoch:
			expired_data.append(filename)
	if expired_data:
		print line_number(), "Error: Files\n\t", "\n\t".join(expired_data), "\nare expired data. You must update."
		sys.exit()

	for filename in aaii_filenames:
		print line_number(), "processing file %d of %d" % (aaii_filenames.index(filename), len(aaii_filenames) )
		if "_Key.XLS" in filename:
			continue
		key_dict = process_aaii_xls_key_file(data_directory + "/" + filename[:-4] + "_Key.XLS")
		process_aaii_xls_data_file(data_directory + "/" + filename, key_dict)
	db.save_GLOBAL_STOCK_DICT()
	print line_number(), "AAII import complete."

def process_aaii_xls_key_file(filename):
	xlrd_workbook = xlrd.open_workbook(filename)
	relevant_spreadsheet_list  = return_relevant_spreadsheet_list_from_workbook(xlrd_workbook)

	# only 1 sheet
	if not len(relevant_spreadsheet_list) == 1:
		print line_number(), ""
		print line_number(), "Error in process_sample_dot_xls() in wxStocks_xls_import_functions.py"
		print line_number(), "spreadsheet list > 1 sheet"
		print line_number(), ""
		return None
	spreadsheet = relevant_spreadsheet_list[0]

	num_columns = spreadsheet.ncols
	num_rows = spreadsheet.nrows

	# important row and column numbers
	top_row = 0 # 1st row
	short_name_col = 0 # 1st column
	long_name_col = 1 # 2nd column

	key_dict = {}
	for row_num in range(num_rows):
		short_name, long_name = None, None
		if row_num == top_row:
			continue
		for col_num in range(num_columns):
			datum = return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = row_num, column = col_num)
			if datum:
				if col_num == 0:
					# short_name
					short_name = datum
				elif col_num == 1:
					long_name = datum
			else:
				print line_number(), "Error"
			col_num += 1
		if short_name:
			if long_name:
				key_dict[short_name] = long_name
			else:
				key_dict[short_name] = None
		row_num += 1
	#pprint.pprint(key_dict)

	return key_dict

#count = 0
def process_aaii_xls_data_file(filename, key_dict):
	xlrd_workbook = xlrd.open_workbook(filename)
	relevant_spreadsheet_list  = return_relevant_spreadsheet_list_from_workbook(xlrd_workbook)
	ticker_column_string = u"ticker"

	# only 1 sheet
	if not len(relevant_spreadsheet_list) == 1:
		print line_number(), ""
		print line_number(), "Error in process_sample_dot_xls() in wxStocks_xls_import_functions.py"
		print line_number(), "spreadsheet list > 1 sheet"
		print line_number(), ""
		sys.exit()
	spreadsheet = relevant_spreadsheet_list[0]

	num_columns = spreadsheet.ncols
	num_rows = spreadsheet.nrows

	# important row and column numbers
	top_row = 0 # 1st row

	all_duplicates = True # for testing for files that are all duplicates below
	for row_num in range(num_rows):
		ticker = None
		current_stock = None
		if row_num == top_row:
			for col_num in range(num_columns):
				datum = return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = row_num, column = col_num)
				if datum == ticker_column_string:
					ticker_col = col_num
			continue
		# find ticker only
		for col_num in range(num_columns):
			ticker = return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = row_num, column = ticker_col)
			#print line_number(), ticker
			if ticker:
				current_stock = db.create_new_Stock_if_it_doesnt_exist(ticker)
		for col_num in range(num_columns):
			attribute = return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = top_row, column = col_num)
			#print line_number(), attribute
			#print line_number(), attribute.upper()
			datum = return_xls_cell_value(xlrd_spreadsheet = spreadsheet, row = row_num, column = col_num)
			#print line_number(), datum
			if datum:
				long_attribute_name = key_dict.get(attribute.upper())
				long_attribute_name = remove_inappropriate_characters_from_attribute_name(long_attribute_name)

				global all_attribute_dict
				if long_attribute_name in all_attribute_dict:
					if datum:
						other_datum = all_attribute_dict.get(long_attribute_name) # previously collected data
						if not datum == other_datum:
							print line_number(), "Error: duplicate data key does not have the same value."
							sys.exit()
				setattr(current_stock, long_attribute_name + "_aa", datum)
			#print line_number(), str(ticker) + "." + str(long_attribute_name), "=", str(datum)
			col_num += 1

		row_num += 1
	#pprint.pprint(key_dict)
	#global count
	#count += 1
	#print line_number(), "count =", count


def remove_inappropriate_characters_from_attribute_name(attribute_string):
	if "Inve$tWare" in attribute_string: # weird inve$tware names throwing errors below due to "$".
		attribute_string = attribute_string.replace("Inve$tWare", "InvestWare")

	acceptable_characters = list(string.letters + string.digits + "_")
	unicode_acceptable_characters = []
	for char in acceptable_characters:
		unicode_acceptable_characters.append(unicode(char))
	acceptable_characters = acceptable_characters + unicode_acceptable_characters
	new_attribute_name = ""
	for char in attribute_string:
		if char not in acceptable_characters:
			if char in [" ", "-", ".", ",", "(", ")", u" ", u"-", u".", u",", u"(", u")"]:
				new_char = "_"
			elif char in ["/", u"/"]:
				new_char = "_to_"
			elif char in ["&", u"&"]:
				new_char = "_and_"
			elif char in ["%", u"%"]:
				new_char = "percent"
			else:
				print line_number(), "Error:", char, ":", attribute_string
				sys.exit()
		else:
			new_char = str(char)

		new_attribute_name += new_char
	if new_attribute_name:
		return new_attribute_name

def import_xls_via_user_created_function(wxWindow, user_created_function):
	'''adds import csv data to stocks data via a user created function'''
	try:
		from modules import xlrd
	except:
		print line_number(), line_number(), "Error: cannot import xls file because xlrd module failed to load"
		return
	
	dirname = ''
	dialog = wx.FileDialog(wxWindow, "Choose a file", dirname, "", "*.xls", wx.OPEN)
	if dialog.ShowModal() == wx.ID_OK:
		filename = dialog.GetFilename()
		dirname = dialog.GetDirectory()
		
		#csv_file = open(os.path.join(dirname, filename), 'rb')
		
		xls_workbook = xlrd.open_workbook(dirname + "/" + filename)
		dict_list_and_attribute_suffix_tuple = user_created_function(xls_workbook)
		
	else:
		dialog.Destroy()
		return
	dialog.Destroy()
	
	# process returned tuple
	attribute_suffix = dict_list_and_attribute_suffix_tuple[1]
	success = None
	if len(attribute_suffix) != 3 or attribute_suffix[0] != "_":
		print line_number(), line_number(), "Error: your attribute suffix is improperly formatted"
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
			print line_number(), "Error: your_dictionary['stock'] does not return a recognized ticker symbol."
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

def process_sample_dot_xls(xlrd_workbook, attribute_suffix = "_xl"):
	'''import sample.xls'''
	import config
	relevant_spreadsheet_list  = utils.return_relevant_spreadsheet_list_from_workbook(xlrd_workbook)

	dict_list = []
	# sample.xls specific

	# only 1 sheet
	if not len(relevant_spreadsheet_list) == 1:
		print line_number(), ""
		print line_number(), "Error in process_sample_dot_xls() in wxStocks_xls_import_functions.py"
		print line_number(), "spreadsheet list > 1 sheet"
		print line_number(), ""
		return None
	spreadsheet = relevant_spreadsheet_list[0]

	num_columns = spreadsheet.ncols
	num_rows = spreadsheet.nrows












# end of line