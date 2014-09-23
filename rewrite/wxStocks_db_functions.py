import config
import inspect, logging
import cPickle as pickle
import wxStocks_classes

####################### Data Loading ###############################################
def load_all_data():
	load_GLOBAL_TICKER_LIST()
	load_GLOBAL_STOCK_DICT()
	load_DATA_ABOUT_PORTFOLIOS()

# start up try/except clauses below
def load_GLOBAL_TICKER_LIST():
	try:
		ticker_list = open('wxStocks_data/ticker.pk', 'rb')
	except Exception, e:
		print line_number(), e
		ticker_list = open('wxStocks_data/ticker.pk', 'wb')
		ticker_list = []
		with open('wxStocks_data/ticker.pk', 'wb') as output:
			pickle.dump(ticker_list, output, pickle.HIGHEST_PROTOCOL)
		ticker_list = open('wxStocks_data/ticker.pk', 'rb')
	config.GLOBAL_TICKER_LIST = pickle.load(ticker_list)
	ticker_list.close()
	return config.GLOBAL_TICKER_LIST
def save_GLOBAL_TICKER_LIST():
	with open('wxStocks_data/ticker.pk', 'wb') as output:
		pickle.dump(config.GLOBAL_TICKER_LIST, output, pickle.HIGHEST_PROTOCOL)
def delete_GLOBAL_TICKER_LIST():
	config.GLOBAL_TICKER_LIST = []
	with open('wxStocks_data/ticker.pk', 'wb') as output:
		pickle.dump(config.GLOBAL_TICKER_LIST, output, pickle.HIGHEST_PROTOCOL)

def load_GLOBAL_STOCK_DICT():
	try:
		pickled_file = open('wxStocks_data/all_stocks_dict.pk', 'rb')
		stock_dict = pickle.load(pickled_file)
		config.GLOBAL_STOCK_DICT = stock_dict
		stock_dict = dict(stock_dict)

	except Exception, e:
		print line_number(), e
		stock_dict = config.GLOBAL_STOCK_DICT
		with open('wxStocks_data/all_stocks_dict.pk', 'wb') as output:
			pickle.dump(stock_dict, output, pickle.HIGHEST_PROTOCOL)		
	return
def save_GLOBAL_STOCK_DICT():
	print "Saving GLOBAL_STOCK_DICT"
	stock_dict = config.GLOBAL_STOCK_DICT
	with open('wxStocks_data/all_stocks_dict.pk', 'wb') as output:
		pickle.dump(stock_dict, output, pickle.HIGHEST_PROTOCOL)

def save_DATA_ABOUT_PORTFOLIOS():
	with open('wxStocks_data/portfolios.pk', 'wb') as output:
		pickle.dump(config.DATA_ABOUT_PORTFOLIOS, output, pickle.HIGHEST_PROTOCOL)

def load_DATA_ABOUT_PORTFOLIOS():	
	# add encrypt + decryption to this function
	try:
		pickled_data_from_portfolios_file = open('wxStocks_data/portfolios.pk', 'rb')
	except Exception, e:
		print line_number(), e
		default_data_about_portfolios_list = [0,[]]
		with open('wxStocks_data/portfolios.pk', 'wb') as output:
			pickle.dump(default_data_about_portfolios_list, output, pickle.HIGHEST_PROTOCOL)
		pickled_data_from_portfolios_file = open('wxStocks_data/portfolios.pk', 'rb')

		


	config.DATA_ABOUT_PORTFOLIOS = pickle.load(pickled_data_from_portfolios_file)
	# For config.DATA_ABOUT_PORTFOLIOS structure, see config file
	pickled_data_from_portfolios_file.close()
	config.NUMBER_OF_PORTFOLIOS = config.DATA_ABOUT_PORTFOLIOS[0]
	print config.NUMBER_OF_PORTFOLIOS
	config.PORTFOLIO_NAMES = []
	for i in range(config.NUMBER_OF_PORTFOLIOS):
		try:
			config.PORTFOLIO_NAMES.append(config.DATA_ABOUT_PORTFOLIOS[1][i])
		except Exception, exception:
			print line_number(), exception
			logging.error('Portfolio names do not match number of portfolios')
	for i in range(config.NUMBER_OF_PORTFOLIOS):
		try:
			portfolio_account_obj_file = open('wxStocks_data/portfolio_%d_data.pk' % (i+1), 'rb')
			portfolio_obj = pickle.load(portfolio_account_obj_file)
			portfolio_account_obj_file.close()
			config.PORTFOLIO_OBJECTS_DICT["%s" % str(portfolio_obj.id_number)] = portfolio_obj
			print config.PORTFOLIO_OBJECTS_DICT
		except Exception, e:
			print line_number(), e
	# with open('dummy.pk', 'wb') as output:
	#	pickle.dump(SOME_DATA, output, pickle.HIGHEST_PROTOCOL)

def load_account_object(id_number):
	pickled_account =  open('wxStocks_data/portfolio_%s.pk' % str(id_number), 'rb')
	account = pickle.load(pickled_account)
	return account

############################################################################################

def load_screen_names():
	try:
		existing_screen_names_file = open('wxStocks_data/screen_names.pk', 'rb')
	except Exception, exception:
		print line_number(), exception
		existing_screen_names_file = open('wxStocks_data/screen_names.pk', 'wb')
		empty_list = []
		with open('wxStocks_data/screen_names.pk', 'wb') as output:
			pickle.dump(empty_list, output, pickle.HIGHEST_PROTOCOL)
		existing_screen_names_file = open('wxStocks_data/screen_names.pk', 'rb')
	existing_screen_names = pickle.load(existing_screen_names_file)
	existing_screen_names_file.close()
	return existing_screen_names

############################################################################################
def line_number():
	"""Returns the current line number in our program."""
	line_number = inspect.currentframe().f_back.f_lineno
	line_number_string = "Line %d:" % line_number
	return line_number_string
