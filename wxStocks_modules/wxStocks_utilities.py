import inspect, logging, time, csv
import config
def line_number():
	"""Returns the current line number in our program."""
	return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)

def print_attributes(obj):
	for attribute in dir(obj):
		if attribute[:2] != "__":
			if type(obj) is Stock:
				print obj.symbol + "." + attribute, "=", getattr(obj, attribute)
			else:
				print attribute, "=", getattr(obj, attribute)
def start_whitespace():
	print """
	\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
	\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
	\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
	"""

####################### Return functions #################################################
def return_stock_by_symbol(ticker_symbol):
	if not type(ticker_symbol) == str:
		ticker_symbol = str(ticker_symbol)
	try:
		return config.GLOBAL_STOCK_DICT["%s" % ticker_symbol.upper()]
	except Exception as e:
		print line_number()
		logging.error("Stock with symbol %s does not appear to exist" % ticker_symbol.upper())
		return None

def return_all_stocks():
	stock_list = list(config.GLOBAL_STOCK_DICT.values())
	stock_list.sort(key = lambda x: x.symbol)
	return stock_list

def return_stock_by_yql_symbol(yql_ticker_symbol):
	for ticker in config.GLOBAL_STOCK_DICT:
		if config.GLOBAL_STOCK_DICT[ticker].yql_ticker == yql_ticker_symbol:
			return config.GLOBAL_STOCK_DICT[ticker]
	# if none match
	print line_number()
	logging.error("Stock with yql symbol %s does not appear to exist" % yql_ticker_symbol)
	return None

def return_all_up_to_date_stocks():
	stocks_up_to_date_list = []

	current_time = float(time.time())
	for ticker in config.GLOBAL_STOCK_DICT:
		print int(config.TIME_ALLOWED_FOR_BEFORE_YQL_DATA_NO_LONGER_APPEARS_IN_STOCK_LIST/(24*60*60))
		stock = config.GLOBAL_STOCK_DICT[ticker]
		time_since_update = current_time - stock.last_yql_basic_scrape_update
		if int(time_since_update) > int(config.TIME_ALLOWED_FOR_BEFORE_YQL_DATA_NO_LONGER_APPEARS_IN_STOCK_LIST):
			print line_number(), "Will not add %s to stock list, data is over %d days old, please rescrape" % (str(stock.symbol), int(config.TIME_ALLOWED_FOR_BEFORE_YQL_DATA_NO_LONGER_APPEARS_IN_STOCK_LIST/(24*60*60)))
			continue
		else:
			stocks_up_to_date_list.append(stock)
	return stocks_up_to_date_list

def return_stocks_with_data_errors():
	stock_list = return_all_stocks()
	error_list = []
	for stock in stock_list:
		try:
			if stock.ErrorIndicationreturnedforsymbolchangedinvalid_yf:
				if stock.ErrorIndicationreturnedforsymbolchangedinvalid_yf != "None":
					error_list.append(stock)
				else:
					continue
		except:
			continue
	return error_list

def return_cost_basis_per_share(account_obj, ticker):
	'''Return the cost basis per share of a stock in an account, if it exists, else return none'''
	ticker = ticker.upper()

	shares_of_relevant_stock = account_obj.stock_shares_dict.get(ticker)
	if not shares_of_relevant_stock:
		return None

	cost_basis_of_relevant_stock = account_obj.cost_basis_dict.get(ticker)
	if not cost_basis_of_relevant_stock:
		return None

	return cost_basis_of_relevant_stock

def return_account_by_id(id_number):
	try:
		portfolio_obj = config.PORTFOLIO_OBJECTS_DICT[str(id_number)]
		if portfolio_obj:
			return portfolio_obj
		else:
			return None
	except Exception as e:
		print line_number()
		logging.error("Portfolio object with id: %s does not appear to exist" % str(id_number))
		return None	

####################### Stock utility functions #################################################
def stock_value_is_negative(stock_obj, attribute_str):
	try:
		getattr(stock_obj, attribute_str)
	except:
		return False
	#print line_number(), "Is %s.%s:" % (stock_obj.symbol, attribute_str), str(getattr(stock_obj, attribute_str)), "negative?"
	#print str(getattr(stock_obj, attribute_str)).startswith("(") or str(getattr(stock_obj, attribute_str)).startswith("-")
	#print ""
	return str(getattr(stock_obj, attribute_str)).startswith("(") or str(getattr(stock_obj, attribute_str)).startswith("-")
####################### Stock utility functions #################################################

### I don't think this is used any more
def importSchwabCSV(csv_file):
	reader = csv.reader(csv_file)
	row_list = []
	for row in reader:
		row_list.append(row)
	washed_row_list = []
	for row in row_list:
		if row:
			washed_row = []
			for cell in row:
				washed_cell = strip_string_whitespace(cell)
				washed_row.append(washed_cell)
			washed_row_list.append(washed_row)
	return washed_row_list
### End don't think this is used any more

### xlrd
def return_relevant_spreadsheet_list_from_workbook(xlrd_workbook):
	relevant_sheets = []
	for i in range(xlrd_workbook.nsheets):
		sheet = xlrd_workbook.sheet_by_index(i)
		print sheet.name
		if sheet.nrows or sheet.ncols:
			print "rows x cols:", sheet.nrows, sheet.ncols
			relevant_sheets.append(sheet)
		else:
			print "is empty"
		print ""
	return relevant_sheets

def return_xls_cell_value(xlrd_spreadsheet, row, column):
	return xlrd_spreadsheet.cell_value(rowx=row, colx=column)

####################### General utility functions #################################################
def gen_ticker_list(csv_file):
	reader = csv.reader(csv_file)
	reader_list = []
	for row in reader:
		reader_list.append(row)
	ticker_list = []
	for row in reader_list:
		if row:
			if row[0] != "Symbol":
				ticker_list.append(row[0])
	ticker_list = strip_list_whitespace(ticker_list)
	ticker_list.sort()
	return ticker_list
def return_list_of_lists(csv_file):
	full_data = []
	reader = csv.reader(csv_file)
	for row in reader:
		full_data.append(list(row))
	#print line_number(),full_data
	return full_data
def openCSV_return_list_of_lists():
	csv_file = filedialog.askopenfile()
	print line_number(),'opening', csv_file
	try:
		ticker_list = return_list_of_lists(csv_file)
		return ticker_list
	except:
		error_label = Label(main_tab, text='You must import a csv file.')
		error_label.pack()
		return
def remove_list_duplicates(some_list):
	if type(some_list) != "list":
		some_list = list(some_list)
	the_set = set(some_list)
	new_list = list(the_set)
	return new_list
def strip_list_whitespace(some_list):
	tag_list = some_list
	#logging.warning(tag_list)
	new_list = []
	for tag in tag_list:
		tag = " ".join(tag.split())
		new_list.append(tag)
	tag_list = new_list
	new_list = []
	for tag in tag_list:
		if tag:
			new_list.append(tag)
	return new_list
def strip_string_whitespace(some_string):
	stripped_string = " ".join(some_string.split())
	return stripped_string
def time_since_creation(item_epoch_var):
	raw_secs = round(time.time())-round(item_epoch_var)
	#logging.warning(raw_secs)
	raw_secs = int(raw_secs)
	time_str = None
	if raw_secs < 60:
		seconds = raw_secs
		if seconds > 1:
			time_str = "%d seconds" % seconds
		else:
			time_str = "%d second" % seconds
	elif (raw_secs >= 60) and (raw_secs < (60 * 60)):
		minutes = (raw_secs/60)
		if minutes > 1:
			time_str = "%d minutes" % minutes
		else:
			time_str = "%d minute" % minutes
	elif (raw_secs >= (60*60) and (raw_secs < (60 * 60 * 24))):
		minutes = (raw_secs/60)
		hours = (minutes/60)
		if hours > 1:
			time_str = "%d hours" % hours
		else:
			time_str = "%d hour" % hours
	elif (raw_secs >= (60*60*24) and (raw_secs < (60*60*24*30))):
		minutes = (raw_secs/60)
		hours = (minutes/60)
		days = (hours/24)
		if days > 1:
			time_str = "%d days" % days
		else:
			time_str = "%d day" % days
	elif (raw_secs >=(60*60*24*30)) and (raw_secs < (60*60*24*365)):		
		minutes = (raw_secs/60)
		hours = (minutes/60)
		days = (hours/24)
		months = (days/30)
		if months > 1:
			time_str = "%d months" % months
		else:
			time_str = "%d month" % months
	elif raw_secs >= (60*60*24*365):
		minutes = (raw_secs/60)
		hours = (minutes/60)
		days = (hours/24)
		years = (days/365)
		if years > 1:
			time_str = "%d years" % years
		else:
			time_str = "%d year" % years
	else:
		logging.error("something wrong with time_since_creation function")
		time_str = None
	return time_str		
def check_url(url_str):
	link_var = url_str
	deadLinkFound = check_url_instance(link_var)
	if deadLinkFound:
		link_var = "http://" + link_var
		deadLinkFound = check_url_instance(link_var)
		if deadLinkFound:
			link_var = "http://www." + link_var
			deadLinkFound = check_url_instance(link_var)
			if deadLinkFound:
				link_var = None
	return link_var
def check_url_instance(url_str):
	link_var = url_str
	logging.warning(link_var)
	deadLinkFound = True
	try:
		f = urlfetch.fetch(url=link_var, deadline=30)
		if f.status_code == 200:
			#logging.warning(f.content)
			pass
		deadLinkFound = False
	except Exception as e:
		logging.warning('that failed')
		logging.warning(e)
	logging.warning(deadLinkFound)
	return deadLinkFound
def time_from_epoch(item_epoch_var):
	raw_secs = round(item_epoch_var)
	#logging.warning(raw_secs)
	raw_secs = int(raw_secs)
	time_str = None
	if raw_secs < 60:
		seconds = raw_secs
		if seconds > 1:
			time_str = "%d seconds" % seconds
		else:
			time_str = "%d second" % seconds
	elif (raw_secs >= 60) and (raw_secs < (60 * 60)):
		minutes = (raw_secs/60)
		if minutes > 1:
			time_str = "%d minutes" % minutes
		else:
			time_str = "%d minute" % minutes
	elif (raw_secs >= (60*60) and (raw_secs < (60 * 60 * 24))):
		minutes = (raw_secs/60)
		hours = (minutes/60)
		if hours > 1:
			time_str = "about %d hours" % hours
		else:
			time_str = "about %d hour" % hours
	elif (raw_secs >= (60*60*24) and (raw_secs < (60*60*24*30))):
		minutes = (raw_secs/60)
		hours = (minutes/60)
		days = (hours/24)
		if days > 1:
			time_str = "%d days" % days
		else:
			time_str = "%d day" % days
	elif (raw_secs >=(60*60*24*30)) and (raw_secs < (60*60*24*365)):		
		minutes = (raw_secs/60)
		hours = (minutes/60)
		days = (hours/24)
		months = (days/30)
		if months > 1:
			time_str = "%d months" % months
		else:
			time_str = "%d month" % months
	elif raw_secs >= (60*60*24*365):
		minutes = (raw_secs/60)
		hours = (minutes/60)
		days = (hours/24)
		years = (days/365)
		if years > 1:
			time_str = "%d years" % years
		else:
			time_str = "%d year" % years
	else:
		logging.error("something wrong with time_from_epoch function")
		time_str = None
	return time_str	

def is_number(some_string):
	try:
		float(some_string)
		return True
	except Exception, exception:
		# print exception
		return False
def relevant_float(some_float):
	return (some_float - int(some_float)) != 0
def contains_digits(some_string):
    for character in list(some_string):
        if character.isdigit():
            return True
            break
    return False
def first_character_is_digit(some_string):
	return some_string[0].isdigit()

def return_list_of_all_stocks_from_active_memory():
	stock_list = []
	for obj in gc.get_objects():
		if type(obj) is Stock:
			stock_list.append(obj)
	stock_list.sort(key = lambda x: x.symbol)
	return stock_list
def return_stock_from_active_memory(ticker):
	ticker = ticker.upper()
	for obj in gc.get_objects():
		if type(obj) is Stock:
			if obj.symbol == ticker:
				return obj


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
############################################################################################

