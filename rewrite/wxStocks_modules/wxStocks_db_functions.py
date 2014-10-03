import wx
import config
import inspect, logging, os, hashlib
import cPickle as pickle
from modules.pybcrypt import bcrypt

import wxStocks_classes

import traceback, sys

ticker_path = 'wxStocks_modules/wxStocks_data/ticker.pk'
all_stocks_path = 'wxStocks_modules/wxStocks_data/all_stocks_dict.pk'
screen_dict_path = 'wxStocks_modules/wxStocks_data/screen_dict.pk'
named_screen_path = 'wxStocks_modules/wxStocks_data/screen-%s.pk'
screen_name_and_time_created_tuple_list_path = 'wxStocks_modules/wxStocks_data/screen_names_and_times_tuple_list.pk'
portfolios_path = 'DO_NOT_COPY/portfolios.%s'
portfolio_account_obj_file_path = 'DO_NOT_COPY/portfolio_%d_data.%s'

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
def load_named_screen(screen_name):
	print "Loading Screen: %s" % screen_name
	try:
		screen_file = open(named_screen_path % screen_name.replace(' ','_'), 'rb')
		screen = pickle.load(screen_file)
		screen_file.close()
	except Exception as e:
		print line_number(), e
		print "Screen: %s failed to load." % screen_name
	return screen
def save_named_screen(screen_name, stock_list):
	print "Saving screen named: %s" % screen_name
	with open(named_screen_path % screen_name.replace(' ','_'), 'wb') as output:
		pickle.dump(stock_list, output, pickle.HIGHEST_PROTOCOL)
def delete_named_screen(screen_name):
	print "Deleting named screen: %s" % screen_name

	print line_number(), config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST
	config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST = [x for x in config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST if x[0] != screen_name]
	print line_number(), config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST
	save_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST()
	os.remove(named_screen_path % screen_name.replace(' ', '_'))

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
	config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST = existing_tuple_list
def save_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST():
	print "Saving SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST"
	tuple_list = config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST
	with open(screen_name_and_time_created_tuple_list_path, 'wb') as output:
		pickle.dump(tuple_list, output, pickle.HIGHEST_PROTOCOL)
###

### Portfolio functions need encryption/decryption
def save_DATA_ABOUT_PORTFOLIOS(password=""):
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
		print line_number(), "Saving encrypted DATA_ABOUT_PORTFOLIOS."
		with open(portfolios_path % "txt", 'w') as output:
			output.write(encrypted_string)
	else:
		print line_number(), "Saving unencrypted DATA_ABOUT_PORTFOLIOS."
		with open(portfolios_path % "pk", 'w') as output:
			pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)
def decrypt_if_possible(path, password=""):
	error = False
	print line_number(), "config.ENCRYPTION_POSSIBLE", config.ENCRYPTION_POSSIBLE
	if config.ENCRYPTION_POSSIBLE:
		try:
			import Crypto
			from modules.simplecrypt import encrypt, decrypt
		except:
			config.ENCRYPTION_POSSIBLE = False
			print line_number(), "Error: DATA_ABOUT_PORTFOLIOS did not load"
			return
		try:
			encrypted_file = open(path, 'r')
		except Exception as e:
			print line_number(), e
			print line_number(), "Decryption not possible, account file doesn't exist"
			error = True
		encrypted_string = encrypted_file.read()
		ercrypted_file.close()
		pickled_string = decrypt(password, encrypted_string)
		data = pickle.loads(pickled_string)
	else:
		try:
			unencrypted_pickle_file = open(path, 'r')
			data = pickle.load(unencrypted_pickle_file)
			unencrypted_pickle_file.close()
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


def load_DATA_ABOUT_PORTFOLIOS(password=""):
	# add encrypt + decryption to this function
	password = ""
	data = None
	print line_number(), "fix default password"

	print line_number(), "config.ENCRYPTION_POSSIBLE", config.ENCRYPTION_POSSIBLE
	if not config.ENCRYPTION_POSSIBLE:
		print line_number(), "Loading unencrypted DATA_ABOUT_PORTFOLIOS..."
		try:
			DATA_ABOUT_PORTFOLIOS_file_exists = open(portfolios_path % "pk", 'r')
			data = pickle.load(DATA_ABOUT_PORTFOLIOS_file_exists)
			DATA_ABOUT_PORTFOLIOS_file_exists.close()
			config.DATA_ABOUT_PORTFOLIOS = data
		except Exception, e:
			print line_number(), "DATA_ABOUT_PORTFOLIOS does not exist."
			return config.DEFAULT_DATA_ABOUT_PORTFOLIOS
	else:
		print line_number(), "Loading unencrypted DATA_ABOUT_PORTFOLIOS..."
		try:
			data = decrypt_if_possible(path = portfolios_path % "txt", password = password)
		except:
			pass
	if data:
		print line_number(), data
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
def save_portfolio_object(portfolio_data, id_number, password=hashlib.sha256("").hexdigest()):
	encryption_possible = False
	if config.ENCRYPTION_POSSIBLE:
		try:
			import Crypto
			from modules.simplecrypt import encrypt, decrypt
			encryption_possible = True
			config.ENCRYPTION_POSSIBLE = True
		except Exception as e:
			pass
	if encryption_possible:
		path = portfolio_account_obj_file_path % (id_number, "txt")
		unencrypted_pickle_string = pickle.dumps(portfolio_data)
		encrypted_string = encrypt(password, unencrypted_pickle_string)
		with open(path, 'w') as output:
			output.write(encrypted_string, output)
	else:
		path = portfolio_account_obj_file_path % (id_number, "pk")
		with open(path, 'w') as output:
			pickle.dump(portfolio_data, output, pickle.HIGHEST_PROTOCOL)


def load_portfolio_object(id_number, password=hashlib.sha256("").hexdigest()):
	if config.ENCRYPTION_POSSIBLE:
		path = portfolio_account_obj_file_path % (id_number, "txt")
	else:
		path = portfolio_account_obj_file_path % (id_number, "pk")
	portfolio_object = decrypt_if_possible(path = path, password = password)

	if portfolio_object:
		return portfolio_object
	else:
		print line_number(), "Account object failed to load."
		return




############################################################################################

####################### Hashing Functions #######################
def make_sha256_hash(pw):
	return hashlib.sha256(pw).hexdigest()

####################### Bcrypt
def make_pw_hash(pw, salt=None):
	if not salt:
		salt = bcrypt.gensalt(4) # this should be 10-12
	pw_hashed = bcrypt.hashpw(pw, salt)
	return '%s|%s' % (pw_hashed, salt)
def valid_pw(pw, h):
	return h == make_pw_hash(pw, h.split('|')[1])
#########################################################


############################################################################################
def line_number():
	"""Returns the current line number in our program."""
	line_number = inspect.currentframe().f_back.f_lineno
	line_number_string = "Line %d:" % line_number
	return line_number_string

# End of line...