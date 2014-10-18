import wx
import config
import inspect, logging, os, hashlib, getpass
import cPickle as pickle
from modules.pybcrypt import bcrypt

import wxStocks_classes

import traceback, sys

ticker_path = 'wxStocks_modules/wxStocks_data/ticker.pk'
all_stocks_path = 'wxStocks_modules/wxStocks_data/all_stocks_dict.pk'
screen_dict_path = 'wxStocks_modules/wxStocks_data/screen_dict.pk'
named_screen_path = 'wxStocks_modules/wxStocks_data/screen-%s.pk'
screen_name_and_time_created_tuple_list_path = 'wxStocks_modules/wxStocks_data/screen_names_and_times_tuple_list.pk'
secure_file_folder = 'DO_NOT_COPY'
portfolios_path = 'DO_NOT_COPY/portfolios.%s'
portfolio_account_obj_file_path = 'DO_NOT_COPY/portfolio_%d_data.%s'
password_path = 'DO_NOT_COPY/password.txt'

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
def decrypt_if_possible(path):
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
			encrypted_string = encrypted_file.read()
			encrypted_file.close()
			pickled_string = decrypt(config.PASSWORD, encrypted_string)
			data = pickle.loads(pickled_string)
		except Exception as e:
			print line_number(), e
			print line_number(), "Decryption not possible, account file doesn't exist"
			try:
				unencrypted_pickle_file = open(path.replace(".txt",".pk"), 'r')
				data = pickle.load(unencrypted_pickle_file)
				unencrypted_pickle_file.close()
				print line_number(), "Decryption not possible, but unencrypted file exists and will be used instead."
			except Exception as e:
				print e
				error = True
	else:
		try:
			unencrypted_pickle_file = open(path.replace(".txt",".pk"), 'r')
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

def save_DATA_ABOUT_PORTFOLIOS():
	data = config.DATA_ABOUT_PORTFOLIOS
	print line_number(), "config.ENCRYPTION_POSSIBLE", config.ENCRYPTION_POSSIBLE
	if config.ENCRYPTION_POSSIBLE:
		try:
			import Crypto
			from modules.simplecrypt import encrypt, decrypt
		except:
			config.ENCRYPTION_POSSIBLE = False
			print line_number(), "Error: DATA_ABOUT_PORTFOLIOS did not save"
			return
		unencrypted_pickle_string = pickle.dumps(data)
		encrypted_string = encrypt(config.PASSWORD, unencrypted_pickle_string)
		print line_number(), "Saving encrypted DATA_ABOUT_PORTFOLIOS."
		with open(portfolios_path % "txt", 'w') as output:
			output.write(encrypted_string)
	else:
		print line_number(), "Saving unencrypted DATA_ABOUT_PORTFOLIOS."
		with open(portfolios_path % "pk", 'w') as output:
			pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)
def load_DATA_ABOUT_PORTFOLIOS():
	# add encrypt + decryption to this function
	data = None
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
			data = decrypt_if_possible(path = portfolios_path % "txt")
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
	
	# Set config.PORTFOLIO_NAMES
	for i in range(config.NUMBER_OF_PORTFOLIOS):
		try:
			config.PORTFOLIO_NAMES.append(config.DATA_ABOUT_PORTFOLIOS[1][i])
		except Exception, exception:
			print line_number(), exception
			logging.error('Portfolio names do not match number of portfolios')
	print config.PORTFOLIO_NAMES

	# Load portfolio objects
	print line_number(), "--------", config.DATA_ABOUT_PORTFOLIOS[0], "--------"
	load_all_portfolio_objects()

def save_portfolio_object(portfolio_obj, id_number):
	# First, set this object into the portfolio dict, for the first time it's saved:
	config.PORTFOLIO_OBJECTS_DICT[str(id_number)] = portfolio_obj

	encryption_possible = False
	print line_number(), "config.ENCRYPTION_POSSIBLE", config.ENCRYPTION_POSSIBLE
	if config.ENCRYPTION_POSSIBLE:
		try:
			import Crypto
			from modules.simplecrypt import encrypt, decrypt
			encryption_possible = True
		except Exception as e:
			pass
	if encryption_possible:
		path = portfolio_account_obj_file_path % (id_number, "txt")
		unencrypted_pickle_string = pickle.dumps(portfolio_obj)
		encrypted_string = encrypt(config.PASSWORD, unencrypted_pickle_string)
		with open(path, 'w') as output:
			output.write(encrypted_string)
	else:
		path = portfolio_account_obj_file_path % (id_number, "pk")
		with open(path, 'w') as output:
			pickle.dump(portfolio_obj, output, pickle.HIGHEST_PROTOCOL)
def load_portfolio_object(id_number):
	print line_number(), "config.ENCRYPTION_POSSIBLE", config.ENCRYPTION_POSSIBLE
	if config.ENCRYPTION_POSSIBLE:
		path = portfolio_account_obj_file_path % (id_number, "txt")
	else:
		path = portfolio_account_obj_file_path % (id_number, "pk")
	portfolio_obj = decrypt_if_possible(path = path)

	if portfolio_obj:
		config.PORTFOLIO_OBJECTS_DICT[str(id_number)] = portfolio_obj
		print "Portfolio objects dict:", config.PORTFOLIO_OBJECTS_DICT
		return portfolio_obj
	else:
		print line_number(), "Account object failed to load."
		return
def load_all_portfolio_objects(number_of_portfolios = config.DATA_ABOUT_PORTFOLIOS[0]):
	for i in range(number_of_portfolios):
		load_portfolio_object(i+1)
def delete_portfolio_object(id_number):
	"delete account"
	print line_number(), "config.ENCRYPTION_POSSIBLE", config.ENCRYPTION_POSSIBLE
	if config.ENCRYPTION_POSSIBLE:
		path = portfolio_account_obj_file_path % (id_number, "txt")
	else:
		path = portfolio_account_obj_file_path % (id_number, "pk")
	portfolio_obj = decrypt_if_possible(path = path)
	if portfolio_obj:
		try:
			os.remove(path)
		except Exception as e:
			print line_number(), e
			if config.ENCRYPTION_POSSIBLE:
				print "Deleting encrypted file failed, will attempt to delete an unencrypted instance of the file."
				try:
					os.remove(path.replace(".txt", ".pk"))
				except Exception as e:
					print e
					print line_number(), "Error: account object failed to be deleted."
					return
			else:
				print line_number(), "Error: account object failed to be deleted."
				return
		portfolio_obj = None
		print line_number(), "Account object has been deleted."
	else:
		print line_number(), "Error: account object failed to be deleted."
		return

### Password data
def is_saved_password_hash(path = password_path):
	try:
		encrypted_file = open(path, 'r')
		bcrypted_password = encrypted_file.read()
		encrypted_file.close()
		return bcrypted_password
	except IOError:
		return False
def set_password():
	password = getpass.getpass("Set your wxStocks encryption password: ")
	if password:
		check_password = getpass.getpass("\nPlease confirm your password by entering it again: ")
	else:
		check_password =  raw_input('\nFailing to enter a password will make your data insecure.\nPlease confirm no password by leaving the following entry blank.\nIf you want to use a password, type "retry" and press enter to reset your password: ')
		
	if password != check_password:
		print "\nThe passwords you entered did not match.\nPlease try again\n"
		set_password()
	save_password(password)
	return password
def save_password(password, path = password_path):
	print "Generating a secure password hash, this may take a moment..."
	bcrypt_hash = make_pw_hash(password)
	with open(path, 'w') as output:
		output.write(bcrypt_hash)

### Secure data wipe
def delete_all_secure_files(path = secure_file_folder):
	file_list = os.listdir(path)
	for file_name in file_list:
		os.remove(path+"/"+file_name)
############################################################################################

####################### Hashing Functions #######################
####################### SHA256
def make_sha256_hash(pw):
	return hashlib.sha256(pw).hexdigest()

####################### Bcrypt
def make_pw_hash(pw, salt=None):
	if not salt:
		salt = bcrypt.gensalt(8) # this should be 10-12 to be extra secure
	pw_hashed = bcrypt.hashpw(pw, salt)
	return '%s|%s' % (pw_hashed, salt)
def valid_pw(pw, h):
	print "Validating your password, this may take a moment..."
	return h == make_pw_hash(pw, h.split('|')[1])
#########################################################


############################################################################################
def line_number():
	"""Returns the current line number in our program."""
	line_number = inspect.currentframe().f_back.f_lineno
	line_number_string = "Line %d:" % line_number
	return line_number_string

# End of line...