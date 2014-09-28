import config
import inspect, logging
import cPickle as pickle

import wxStocks_classes

from modules import Crypto

ticker_path = 'wxStocks_modules/wxStocks_data/ticker.pk'
all_stocks_path = 'wxStocks_modules/wxStocks_data/all_stocks_dict.pk'
screen_names_path = 'wxStocks_modules/wxStocks_data/screen_names.pk'
portfolios_path = 'wxStocks_modules/wxStocks_data/portfolios.pk'
portfolio_account_obj_file_path = 'wxStocks_modules/wxStocks_data/portfolio_%d_data.pk'


####################### Data Loading ###############################################
def load_all_data():
	load_GLOBAL_TICKER_LIST()
	load_GLOBAL_STOCK_DICT()
	load_DATA_ABOUT_PORTFOLIOS()

# start up try/except clauses below

# Dont think these are used any more
def load_GLOBAL_TICKER_LIST():
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
def load_GLOBAL_SCREEN_NAMES():
	try:
		existing_screen_names_file = open(screen_names_path, 'rb')
	except Exception, exception:
		print line_number(), exception
		existing_screen_names_file = open(screen_names_path, 'wb')
		empty_list = []
		with open(screen_names_path, 'wb') as output:
			pickle.dump(empty_list, output, pickle.HIGHEST_PROTOCOL)
		existing_screen_names_file = open(screen_names_path, 'rb')
	existing_screen_names = pickle.load(existing_screen_names_file)
	return 

def load_screen_names():
	try:
		existing_screen_names_file = open(screen_names_path, 'rb')
	except Exception, exception:
		print line_number(), exception
		existing_screen_names_file = open(screen_names_path, 'wb')
		empty_list = []
		with open(screen_names_path, 'wb') as output:
			pickle.dump(empty_list, output, pickle.HIGHEST_PROTOCOL)
		existing_screen_names_file = open(screen_names_path, 'rb')
	existing_screen_names = pickle.load(existing_screen_names_file)
	existing_screen_names_file.close()
	return existing_screen_names


###

### Portfolio functions need encryption/decryption
def save_DATA_ABOUT_PORTFOLIOS(password = None):
	data = config.DATA_ABOUT_PORTFOLIOS
	if config.ENCRYPTION_POSSIBLE:
		import Crypto
		from modules.simplecrypt import encrypt, decrypt
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
		import Crypto
		from modules.simplecrypt import encrypt, decrypt
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
