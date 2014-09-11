import simplecrypt
import config
import inspect, logging
import cPickle as pickle
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
		ticker_list = {"Default": "Default"}
		with open('wxStocks_data/ticker.pk', 'wb') as output:
			pickle.dump(ticker_list, output, pickle.HIGHEST_PROTOCOL)
		ticker_list = open('wxStocks_data/ticker.pk', 'rb')
	GLOBAL_TICKER_DICT = pickle.load(ticker_list)
	ticker_list.close()
	return GLOBAL_TICKER_DICT

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

def load_DATA_ABOUT_PORTFOLIOS():	
	try:
		data_from_portfolios_file = open('wxStocks_data/portfolios.pk', 'rb')
	except Exception, e:
		print line_number(), e
		data_from_portfolios_file = open('wxStocks_data/portfolios.pk', 'wb')
		data_from_portfolios_file = [1,["Primary"]]
		with open('wxStocks_data/portfolios.pk', 'wb') as output:
			pickle.dump(data_from_portfolios_file, output, pickle.HIGHEST_PROTOCOL)
		data_from_portfolios_file = open('wxStocks_data/portfolios.pk', 'rb')
	config.DATA_ABOUT_PORTFOLIOS = pickle.load(data_from_portfolios_file)
	# For config.DATA_ABOUT_PORTFOLIOS structure, see config file
	data_from_portfolios_file.close()
	config.NUMBER_OF_PORTFOLIOS = config.DATA_ABOUT_PORTFOLIOS[0]	
	config.PORTFOLIO_NAMES = []
	for i in range(config.NUMBER_OF_PORTFOLIOS):
		try:
			config.PORTFOLIO_NAMES.append(config.DATA_ABOUT_PORTFOLIOS[1][i])
		except Exception, exception:
			print line_number(), exception
			logging.error('Portfolio names do not match number of portfolios')
	config.PORTFOLIO_OBJECTS_DICT = []
	for i in range(config.NUMBER_OF_PORTFOLIOS):
		try:
			portfolio_account_obj_file = open('wxStocks_data/portfolio_%d_data.pk' % (i+1), 'rb')
			portfolio_obj = pickle.load(portfolio_account_obj_file)
			portfolio_account_obj_file.close()
			config.PORTFOLIO_OBJECTS_LIST.append(portfolio_obj)
		except Exception, e:
			print line_number(), e
	# with open('dummy.pk', 'wb') as output:
	#	pickle.dump(SOME_DATA, output, pickle.HIGHEST_PROTOCOL)
############################################################################################
def line_number():
    """Returns the current line number in our program."""
    line_number = inspect.currentframe().f_back.f_lineno
    line_number_string = "Line %d:" % line_number
    return line_number_string
