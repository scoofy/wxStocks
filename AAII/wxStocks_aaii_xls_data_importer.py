import sys, pprint, os, inspect, string, time, logging

try:
	import xlrd
except:
	try:
		import modules.xlrd as xlrd # AAII is all excel files
	except:
		logging.info("Error: xlrd is not installed")
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
		#logging.info(sheet.name)
		if sheet.nrows or sheet.ncols:
			logging.info(("rows x cols:", sheet.nrows, sheet.ncols))
			relevant_sheets.append(sheet)
		else:
			logging.info("is empty")
	return relevant_sheets
def return_xls_cell_value(xlrd_spreadsheet, row, column):
	return xlrd_spreadsheet.cell_value(rowx=row, colx=column)

def import_aaii_files_from_data_folder(path, time_until_data_needs_update = 999604800): # one week 604800
	""""import aaii .xls files"""
	#current_directory = os.path.dirname(os.path.realpath(__file__))
	#parent_directory = os.path.split(current_directory)[0]
	#grandparent_directory = os.path.split(current_directory)[0]
	#great_grandparent_directory = os.path.split(grandparent_directory)[0]
	#data_directory = os.path.join(great_grandparent_directory, "AAII_data_import_folder")
	data_directory = str(path)

	aaii_filenames = [filename for filename in os.listdir(data_directory)
						if os.path.isfile(os.path.join(data_directory, filename))
						and filename not in ["!.gitignore", ".DS_Store"]
						and "_Key.XLS" not in filename
						and ( filename.endswith("xls") or filename.endswith("XLS") )
						]
	logging.info(aaii_filenames)

	expired_data = []
	for filename in aaii_filenames:
		current_time = time.time()
		file_stats = os.stat(data_directory + "/" + filename)
		file_last_modified_epoch = file_stats.st_mtime # last modified
		#logging.info((filename, "last modified:", file_stats.st_mtime))
		if (current_time - time_until_data_needs_update) > file_last_modified_epoch:
			expired_data.append(filename)
	if expired_data:
		logging.info(("Error: Files\n\t", "\n\t".join(expired_data), "\nare expired data. You must update."))
		return

	for index, filename in enumerate(aaii_filenames):
		#logging.info(("\n\nprocessing file %d of %d\n" % (aaii_filenames.index(filename)+1, len(aaii_filenames) )))
		key_dict = process_aaii_xls_key_file(data_directory + "/" + filename[:-4] + "_Key.XLS")
		process_aaii_xls_data_file(data_directory + "/" + filename, key_dict, index, len(aaii_filenames))
		db.savepoint_db()
	db.commit_db()
	db.save_GLOBAL_STOCK_DICT()
	logging.info("AAII import complete.")

def process_aaii_xls_key_file(filename):
	'grabs the long attribute names to map onto stock objects'
	spreadsheet = xlrd.open_workbook(filename, on_demand=0).sheet_by_index(0)
	#xlrd_workbook = xlrd.open_workbook(filename)
	#relevant_spreadsheet_list  = return_relevant_spreadsheet_list_from_workbook(xlrd_workbook)
	#logging.info(relevant_spreadsheet_list)

	# only 1 sheet
	#if not len(relevant_spreadsheet_list) == 1:
	#	logging.info("")
	#	logging.info("Error in process_sample_dot_xls() in wxStocks_xls_import_functions.py")
	#	logging.info("spreadsheet list > 1 sheet")
	#	logging.info("")
	#	return None
	#spreadsheet = relevant_spreadsheet_list[0]

	spreadsheet_list_of_row_data = []
	for i in range(spreadsheet.nrows):
		row_list = spreadsheet.row_values(i)
		spreadsheet_list_of_row_data.append(row_list)

	spreadsheet_list_of_row_data = tuple(spreadsheet_list_of_row_data)
	key_dict = {}
	for row_list in spreadsheet_list_of_row_data[1:]:
		key_dict[row_list[0]] = remove_inappropriate_characters_from_attribute_name(row_list[1])
	#pprint.pprint(key_dict)

	return key_dict

def process_aaii_xls_data_file(filename, key_dict, the_files_index_in_file_list, number_of_files_being_processed):
	logging.info((filename, "Start!"))
	spreadsheet = xlrd.open_workbook(filename, on_demand=0).sheet_by_index(0)
	#xlrd_workbook = xlrd.open_workbook(filename)
	#relevant_spreadsheet_list  = return_relevant_spreadsheet_list_from_workbook(xlrd_workbook)
	ticker_column_string = u"ticker"

	# only 1 sheet
	#if not len(relevant_spreadsheet_list) == 1:
	#	logging.info("Error in process_sample_dot_xls() in wxStocks_xls_import_functions.py")
	#	logging.info("spreadsheet list > 1 sheet")
	#	sys.exit()
	#spreadsheet = relevant_spreadsheet_list[0]

	num_columns = spreadsheet.ncols
	num_rows = spreadsheet.nrows

	# important row and column numbers
	top_row = 0 # 1st row

	spreadsheet_list_of_row_data = []
	for i in range(spreadsheet.nrows):
		row_list = spreadsheet.row_values(i)
		spreadsheet_list_of_row_data.append(row_list)

	ticker_location = spreadsheet_list_of_row_data[0].index(u'ticker')
	#logging.info(spreadsheet_list_of_row_data[0])

	current_time = time.time()

	logging.info(("spreadsheet_list_of_row_data", len(spreadsheet_list_of_row_data[1:])))
	row_data_len = len(spreadsheet_list_of_row_data)
	spreadsheet_list_of_row_data_attributes = tuple(spreadsheet_list_of_row_data[0])
	spreadsheet_list_of_row_data_list = tuple(spreadsheet_list_of_row_data[1:])
	start_time = time.time()
	last_percent = 0
	spent_time = 0
	for row_list in spreadsheet_list_of_row_data_list:
		raw_percent = float(spreadsheet_list_of_row_data_list.index(row_list))/row_data_len
		percent = int(100*raw_percent)
		percent_of_total_files_processed = float(the_files_index_in_file_list)/number_of_files_being_processed
		percent_of_this_file_processed_of_all_files = raw_percent * (1./number_of_files_being_processed)
		percent_of_entire_process = round(100*(percent_of_total_files_processed + percent_of_this_file_processed_of_all_files), 2)
		whole_percent = int(percent)
		if whole_percent > last_percent:
			spent_time = int(time.time() - start_time)
			last_percent = whole_percent
			logging.info((spreadsheet_list_of_row_data_list.index(row_list), "of", row_data_len, "processing.", str(percent) + "%,", " of this file, which took", spent_time, "seconds.", str(percent_of_entire_process) + "%", "of total."))
		ticker = str(row_list[ticker_location])
		#logging.info(ticker)
		current_stock = db.create_new_Stock_if_it_doesnt_exist(ticker)
		for attribute in spreadsheet_list_of_row_data_attributes:
			#logging.info(("stock attribute", spreadsheet_list_of_row_data[0].index(attribute), "of", len(spreadsheet_list_of_row_data[0])))
			# get the shortened attribute name here
			attribute_index = spreadsheet_list_of_row_data_attributes.index(attribute)
			#logging.info(attribute)
			#logging.info(attribute_index)
			if attribute_index == ticker_location:
				continue
			long_attribute_name = key_dict.get(attribute.upper())
			#logging.info(long_attribute_name)
			#long_attribute_name = remove_inappropriate_characters_from_attribute_name(long_attribute_name) # added to keydict creation
			#logging.info(long_attribute_name)
			datum = row_list[attribute_index]
			db.set_Stock_attribute(current_stock, long_attribute_name, datum, "_aa")
		# set last update time
		if not current_stock.firm_name:
			try:
				current_stock.firm_name = current_stock.Company_name_aa
			except:
				pass
		current_stock.last_aaii_update_aa = current_time

def remove_inappropriate_characters_from_attribute_name(attribute_string):
	attribute_string = str(attribute_string)
	if "Inve$tWare" in attribute_string: # weird inve$tware names throwing errors below due to "$".
		attribute_string = attribute_string.replace("Inve$tWare", "InvestWare")
	acceptable_characters = list(string.ascii_letters + string.digits + "_")
	new_attribute_name = ""
	unacceptible_characters = [" ", "-", ".", ",", "(", ")", u" ", u"-", u".", u",", u"(", u")", "/", u"/", "&", u"&", "%", u"%", "#", u"#", ":", u":", "*", u"*"]
	string_fails = [char for char in unacceptible_characters if char in attribute_string]
	if string_fails:
		#logging.info(string_fails)
		for char in attribute_string:
			if char not in acceptable_characters:
				if char in [" ", "-", ".", ",", "(", ")", u" ", u"-", u".", u",", u"(", u")", "#", u"#", ":", u":", "*", u"*"]:
					new_char = "_"
				elif char in ["/", u"/"]:
					new_char = "_to_"
				elif char in ["&", u"&"]:
					new_char = "_and_"
				elif char in ["%", u"%"]:
					new_char = "percent"
				elif char in ["'"]:
					new_char = ""
				else:
					logging.errors(("Error:", char, ":", attribute_string))
					sys.exit()
			else:
				new_char = str(char)

			new_attribute_name += new_char
	if new_attribute_name:
		attribute_string = new_attribute_name

	attribute_string = utils.remove_leading_underscores(attribute_string)
	return attribute_string











# end of line