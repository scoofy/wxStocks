import config
import inspect, logging
import cPickle as pickle

import wxStocks_classes

import traceback, sys

ticker_path = 'wxStocks_modules/wxStocks_data/ticker.pk'
all_stocks_path = 'wxStocks_modules/wxStocks_data/all_stocks_dict.pk'
screen_dict_path = 'wxStocks_modules/wxStocks_data/screen_dict.pk'
named_screen_path = 'wxStocks_modules/wxStocks_data/screen-%s.pk'
screen_name_and_time_created_tuple_list_path = 'wxStocks_modules/wxStocks_data/screen_names_and_times_tuple_list.pk'
portfolios_path = 'wxStocks_modules/wxStocks_data/portfolios.pk'
portfolio_account_obj_file_path = 'wxStocks_modules/wxStocks_data/portfolio_%d_data.pk'


####################### Data Loading ###############################################
def load_all_data():
	load_GLOBAL_TICKER_LIST()
	load_GLOBAL_STOCK_DICT()
	load_DATA_ABOUT_PORTFOLIOS()
	load_GLOBAL_STOCK_SCREEN_DICT()
	load_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST()
# start up try/except clauses below

# Dont think these are used any more
def load_GLOBAL_TICKER_LIST():
	print "Loading GLOBAL_TICKER_LIST"
	try:
		ticker_list = open(ticker_path, 'rb')
	except Exception, e:
		print line_number(), e
		ticker_list = open(ticker_path, 'wb')
		ticker_list = []
		with open(ticker_path, 'wb') as output:
			pickle.dump(ticker_list, output, pickle.HIGHEST_PROTOCOL)
		ticker_list = open(ticker_path, 'rb')
	config.GLOBAL_TICKER_LIST = pickle.load(ticker_list)
	ticker_list.close()
	return config.GLOBAL_TICKER_LIST
def save_GLOBAL_TICKER_LIST():
	with open(ticker_path, 'wb') as output:
		pickle.dump(config.GLOBAL_TICKER_LIST, output, pickle.HIGHEST_PROTOCOL)
def delete_GLOBAL_TICKER_LIST():
	config.GLOBAL_TICKER_LIST = []
	with open(ticker_path, 'wb') as output:
		pickle.dump(config.GLOBAL_TICKER_LIST, output, pickle.HIGHEST_PROTOCOL)
###

### Global Stock dict functions
def create_new_Stock_if_it_doesnt_exist(ticker):
	ticker = ticker.upper()
	stock = config.GLOBAL_STOCK_DICT.get(ticker)
	if stock:
		print "%s already exists." % ticker
		return stock
	else:
		return wxStocks_classes.Stock(ticker)
def load_GLOBAL_STOCK_DICT():
	print "Loading GLOBAL_STOCK_DICT"
	try:
		pickled_file = open(all_stocks_path, 'rb')
		stock_dict = pickle.load(pickled_file)
		config.GLOBAL_STOCK_DICT = stock_dict

	except Exception, e:
		print "If this is your first time opening wxStocks, please ignore the following exception, otherwise, your previously saved data may have been deleted."
		print line_number(), e
		stock_dict = config.GLOBAL_STOCK_DICT
		with open(all_stocks_path, 'wb') as output:
			pickle.dump(stock_dict, output, pickle.HIGHEST_PROTOCOL)		
	return
def save_GLOBAL_STOCK_DICT():
	print "Saving GLOBAL_STOCK_DICT"
	stock_dict = config.GLOBAL_STOCK_DICT
	with open(all_stocks_path, 'wb') as output:
		pickle.dump(stock_dict, output, pickle.HIGHEST_PROTOCOL)

### Stock screen loading information
def load_GLOBAL_STOCK_SCREEN_DICT():
	print "Loading GLOBAL_STOCK_SCREEN_DICT"
	try:
		existing_screen_names_file = open(screen_dict_path, 'rb')
	except Exception, exception:
		print line_number(), exception
		existing_screen_names_file = open(screen_dict_path, 'wb')
		empty_dict = {}
		with open(screen_dict_path, 'wb') as output:
			pickle.dump(empty_dict, output, pickle.HIGHEST_PROTOCOL)
		existing_screen_names_file = open(screen_dict_path, 'rb')
	existing_screen_names = pickle.load(existing_screen_names_file)
	existing_screen_names_file.close()
	config.GLOBAL_STOCK_SCREEN_DICT = existing_screen_names
def save_GLOBAL_STOCK_STREEN_DICT():
	print "Saving GLOBAL_STOCK_STREEN_DICT"
	existing_screens = config.GLOBAL_STOCK_SCREEN_DICT
	with open(screen_dict_path, 'wb') as output:
		pickle.dump(existing_screens, output, pickle.HIGHEST_PROTOCOL)
def save_named_screen(screen_name, stock_list):
	print "Saving screen named: %s" % screen_name
	with open(named_screen_path % screen_name, 'wb') as output:
		pickle.dump(stock_list, output, pickle.HIGHEST_PROTOCOL)

def load_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST():
	print "Loading SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST"
	try:
		existing_tuple_list_file = open(screen_name_and_time_created_tuple_list_path, 'rb')
	except Exception, exception:
		print line_number(), exception
		existing_tuple_list_file = open(screen_name_and_time_created_tuple_list_path, 'wb')
		empty_list = []
		with open(screen_name_and_time_created_tuple_list_path, 'wb') as output:
			pickle.dump(empty_list, output, pickle.HIGHEST_PROTOCOL)
		existing_tuple_list_file = open(screen_name_and_time_created_tuple_list_path, 'rb')
	existing_tuple_list = pickle.load(existing_tuple_list_file)
	existing_tuple_list_file.close()
	config.SCREEN_NAME_AND_TIME_CREATE_TUPLE_LIST = existing_tuple_list
def save_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST():
	print "Saving SCREEN_NAME_AND_TIME_CREATE_TUPLE_LIST"
	tuple_list = config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST
	with open(screen_name_and_time_created_tuple_list_path, 'wb') as output:
		pickle.dump(tuple_list, output, pickle.HIGHEST_PROTOCOL)
###

### Portfolio functions need encryption/decryption
def save_DATA_ABOUT_PORTFOLIOS(password = None):
	data = config.DATA_ABOUT_PORTFOLIOS
	if config.ENCRYPTION_POSSIBLE:
		try:
			import Crypto
			from modules.simplecrypt import encrypt, decrypt
		except:
			config.ENCRYPTION_POSSIBLE = False
			print line_number(), "Error: DATA_ABOUT_PORTFOLIOS did not save"
			return
		unencrypted_pickle_string = pickle.dumps(data)
		encrypted_string = encrypt(password, unencrypted_pickle_string)
		with open(portfolios_path, 'w') as output:
			output.write(encrypted_string)
	else:
		unencrypted_pickle_string = pickle.dumps(data)
		with open(portfolios_path, 'w') as output:
			output.write(unencrypted_pickle_string)
def decrypt_if_possible(path, password=None):
	error = False
	if config.ENCRYPTION_POSSIBLE:
		try:
			import Crypto
			from modules.simplecrypt import encrypt, decrypt
		except:
			config.ENCRYPTION_POSSIBLE = False
			print line_number(), "Error: DATA_ABOUT_PORTFOLIOS did not load"
			return None
		encrypted_file = open(path, 'r')
		encrypted_string = encrypted_file.read()
		ercrypted_file.close()
		pickled_string = decrypt(password, encrypted_string)
		data = pickle.loads(pickled_string)
	else:
		try:
			unencrypted_pickle_file = open(path, 'r')
			pickle_string = unencrypted_pickle_file.read()
			unencrypted_pickle_file.close()
			data = pickle.loads(pickle_string)
		except Exception as e:
			print e
			error = True
	if not error:
		return data
	else:
		if config.ENCRYPTION_POSSIBLE:
			print line_number(), "Error loading encrypted file"
			print line_number(), path
		else:
			print line_number(), "Error loading unencrypted file"
			print line_number(), path
		return None
def load_DATA_ABOUT_PORTFOLIOS(password = None):	
	# add encrypt + decryption to this function
	try:
		DATA_ABOUT_PORTFOLIOS_file_exists = open(portfolios_path, 'r')
	except Exception, e:
		print line_number(), "DATA_ABOUT_PORTFOLIOS does not exist."
		return "DATA_ABOUT_PORTFOLIOS does not exist."

	data = decrypt_if_possible(path = portfolios_path, password = password)
	if data:
		config.DATA_ABOUT_PORTFOLIOS = data
	else:
		return

	# For config.DATA_ABOUT_PORTFOLIOS structure, see config file
	config.NUMBER_OF_PORTFOLIOS = config.DATA_ABOUT_PORTFOLIOS[0]
	#print line_number(), config.NUMBER_OF_PORTFOLIOS
	config.PORTFOLIO_NAMES = []
	for i in range(config.NUMBER_OF_PORTFOLIOS):
		try:
			config.PORTFOLIO_NAMES.append(config.DATA_ABOUT_PORTFOLIOS[1][i])
		except Exception, exception:
			print line_number(), exception
			logging.error('Portfolio names do not match number of portfolios')
	for i in range(config.NUMBER_OF_PORTFOLIOS):
		try:
			data = decrypt_if_possible(path = portfolio_account_obj_file_path % (i+1), password = password)
			if data:
				portfolio_obj = data
				config.PORTFOLIO_OBJECTS_DICT["%s" % str(portfolio_obj.id_number)] = portfolio_obj
				print config.PORTFOLIO_OBJECTS_DICT
		except Exception, e:
			print line_number(), e
def load_account_object(id_number, password = None):
	data = decrypt_if_possible(path = portfolio_account_obj_file_path % id_number, password = password)
	if data:
		portfolio_obj = data
		return account
	else:
		print line_number(), "Account object failed to load."
		return None




############################################################################################

############################################################################################
def line_number():
	"""Returns the current line number in our program."""
	line_number = inspect.currentframe().f_back.f_lineno
	line_number_string = "Line %d:" % line_number
	return line_number_string
