import time, datetime, inspect, config
import wxStocks_db_functions as db
import wxStocks_utilities as utils
def line_number():
    """Returns the current line number in our program."""
    line_number = inspect.currentframe().f_back.f_lineno
    line_number_string = "Line %d:" % line_number
    return line_number_string

class Stock(object):
	def __new__(self, symbol):
		symbol = utils.strip_string_whitespace(symbol)
		stock_already_exists = config.GLOBAL_STOCK_DICT.get(symbol.upper())
		if stock_already_exists:
			print "stock_already_exists"
			return stock_already_exists
		else:
			self.held_list = []
			# held list should take certain values into account
			# account where stock is held
			# number of shares held in that account
			# redundant information seems silly,
			# could keep the shares in the account obj only.

			self.symbol = symbol.upper()
			self.ticker = symbol.upper()
			self.firm_name = ""

			self.epoch = float(time.time())
			self.created_epoch = float(time.time())
			self.updated = datetime.datetime.now()

			self.ticker_relevant = True
			# this will be false if stock falls off major exchanges

			self.last_yql_basic_scrape_update = 0.0
			
			self.last_yahoo_balance_sheet_update = 0.0
			self.last_yahoo_cash_flow_update = 0.0
			self.last_yahoo_income_statement_update = 0.0
			
			self.last_morningstar_balance_sheet_update = 0.0
			self.last_morningstar_cash_flow_update = 0.0
			self.last_morningstar_income_statement_update = 0.0
			self.last_morningstar_key_ratios_update = 0.0

			self.yql_ticker = self.ticker
			if "^" in self.yql_ticker:
				# nasdaq csv seems to use "MITT^A" vs "MITT^B" to demarcate classes, 
				# where yahoo does by "MITT-PA" and "MITT-PB", etc.
				self.yql_ticker.replace("^", "-P") 


			# save new object to db
			config.GLOBAL_STOCK_DICT[symbol.upper()] = self
			#print type(self)
			#print 'Saving: Stock("%s")' % symbol.upper()
			#db.save_GLOBAL_STOCK_DICT()
			return self

class Account(object): #portfolio
	def __init__(self, id_number, cash = 0, initial_stock_shares_tuple_list = []):
		self.id_number = id_number
		self.availble_cash = cash # there is a ticker "CASH" that already exists, ugh
		self.stock_list = []
		self.stock_shares_dict = {}
		if initial_stock_shares_tuple_list:
			for a_tuple in initial_stock_shares_tuple_list: # ["NAME", int(NumberOfShares)]
				if a_tuple[0] not in self.stock_list:
					self.stock_list.append(stock)
					self.stock_shares_dict["%s" % a_tuple[0]] = a_tuple[1]

	def update_account(self, updated_cash, updated_stock_shares_tuple_list):
		self.availble_cash = updated_cash
		self.stock_list = []
		self.stock_shares_dict = {}
		for a_tuple in updated_stock_shares_tuple_list: # ["NAME", int(NumberOfShares)]
			if a_tuple[0] not in self.stock_list:
				self.stock_list.append(stock)
				self.stock_shares_dict["%s" % a_tuple[0]] = a_tuple[1]


	def add_stock(stock_shares_tuple):
		if stock_shares_tuple[0] not in stock_list:
			self.stock_list.append(stock)
			self.stock_shares_dict["%s" % a_tuple[0]] = a_tuple[1]
		else: # updating only number of shares held
			self.stock_shares_dict["%s" % a_tuple[0]] = a_tuple[1]






