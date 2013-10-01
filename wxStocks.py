import wx, sys, os, csv, time, datetime, logging, ast, math, threading, inspect
from pyql import pyql
from wx.lib import sheet
import cPickle as pickle

class Stock(object):
	def __init__(self, symbol):
		self.symbol = symbol
		self.epoch = float(time.time())
		self.created_epoch = float(time.time())
		self.updated = datetime.datetime.now()
class HeldStock(object):
	def __init__(self, symbol, quantity, security_type):
		self.symbol = symbol
		self.quantity = quantity
		self.security_type = security_type
		self.cost_basis = None
class Account(object):
	def __init__(self, id_number, cash, stock_list):
		self.id_number = id_number
		self.availble_cash = cash # there is a ticker "CASH" that already exists, ugh		
		self.stock_list = stock_list
		for stock in self.stock_list:
			setattr(self, stock.symbol, stock)
def line_number():
    """Returns the current line number in our program."""
    line_number = inspect.currentframe().f_back.f_lineno
    line_number_string = "Line %d:" % line_number
    return line_number_string

try:
	ticker_list = open('ticker.pk', 'rb')
except Exception, e:
	print line_number(), e
	ticker_list = open('ticker.pk', 'wb')
	ticker_list = []
	with open('ticker.pk', 'wb') as output:
		pickle.dump(ticker_list, output, pickle.HIGHEST_PROTOCOL)
	ticker_list = open('ticker.pk', 'rb')
GLOBAL_TICKER_LIST = pickle.load(ticker_list)
ticker_list.close()
try:
	stock_list = open('all_stocks.pk', 'rb')
except Exception, e:
	print line_number(), e
	stock_list = open('all_stocks.pk', 'wb')
	stock_list = []
	with open('all_stocks.pk', 'wb') as output:
		pickle.dump(stock_list, output, pickle.HIGHEST_PROTOCOL)
	stock_list = open('all_stocks.pk', 'rb')
GLOBAL_STOCK_LIST = pickle.load(stock_list)
stock_list.close()
SCRAPE_CHUNK_LENGTH = 50
SCRAPE_SLEEP_TIME = 18
TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE = float(60*60* 4) # 4 hours
SCREEN_LIST = []
try:
	data_from_portfolios_file = open('portfolios.pk', 'rb')
except Exception, e:
	print line_number(), lineno(), e
	data_from_portfolios_file = open('portfolios.pk', 'wb')
	data_from_portfolios_file = [1,["Primary"]]
	with open('portfolios.pk', 'wb') as output:
		pickle.dump(data_from_portfolios_file, output, pickle.HIGHEST_PROTOCOL)
	data_from_portfolios_file = open('portfolios.pk', 'rb')
DATA_ABOUT_PORTFOLIOS = pickle.load(data_from_portfolios_file
									# DATA_ABOUT_PORTFOLIOS = 	[
									#								NUMBER_OF_PORTFOLIOS, # this is an integer
									#								[
									#									"Portfolio Name", # string
									#									etc...
									#								]
									#							]
									)
data_from_portfolios_file.close()
NUMBER_OF_PORTFOLIOS = DATA_ABOUT_PORTFOLIOS[0]	
PORTFOLIO_NAMES = []
for i in range(NUMBER_OF_PORTFOLIOS):
	try:
		PORTFOLIO_NAMES.append(DATA_ABOUT_PORTFOLIOS[1][i])
	except Exception, exception:
		print line_number(), exception
		logging.error('Portfolio names do not match number of portfolios')
PORTFOLIO_OBJECTS_LIST = []
for i in range(NUMBER_OF_PORTFOLIOS):
	try:
		portfolio_account_obj_file = open('portfolio_%d_data.pk' % (i+1), 'rb')
		portfolio_obj = pickle.load(portfolio_account_obj_file)
		portfolio_account_obj_file.close()
		PORTFOLIO_OBJECTS_LIST.append(portfolio_obj)
	except Exception, e:
		print line_number(), e
IRRELEVANT_ATTRIBUTES = ["updated",
						"epoch",
						"TradeDate",
						"created_epoch",
						"TrailingPE_ttm_Date",
						"TradeDate",
						"TwoHundreddayMovingAverage",
						"TickerTrend",
						"SharesOwned",
						"SP50052_WeekChange",
						"PricePaid",
						"PercentChangeFromTwoHundreddayMovingAverage",
						"PercentChangeFromFiftydayMovingAverage",
						"PercentChange",
						"PERatioRealtime",
						"OrderBookRealtime",
						"Notes",
						"MostRecentQuarter_mrq",
						"MoreInfo",
						"MarketCapRealtime",
						"LowLimit",
						"LastTradeWithTime",
						"LastTradeTime",
						"LastTradeRealtimeWithTime",
						"LastTradePriceOnly",
						"LastTradeDate",
						"HoldingsValueRealtime",
						"HoldingsValue",
						"HoldingsGainRealtime",
						"HoldingsGainPercentRealtime",
						"HoldingsGainPercent",
						"HoldingsGain",
						"HighLimit",
						"ExDividendDate",
						"DividendPayDate",
						"DaysValueChangeRealtime",
						"DaysValueChange",
						"DaysRangeRealtime",
						"DaysRange",
						"DaysLow",
						"DaysHigh",
						"Commission",
						"Change_PercentChange",
						"ChangeRealtime",
						"ChangePercentRealtime",
						"ChangeFromTwoHundreddayMovingAverage",
						"ChangeFromFiftydayMovingAverage",
						"Change",
						"ChangeinPercent",
						"BidRealtime",
						"Bid",
						"AvgVol_3_month",
						"AvgVol_10_day",
						"AskRealtime",
						"Ask",
						"AnnualizedGain",
						"AfterHoursChangeRealtime",
						"52_WeekLow_Date",
						"52_WeekLow",
						"52_WeekHigh_Date",
						"52_WeekHigh",
						"52_WeekChange",
						"50_DayMovingAverage",
						"200_DayMovingAverage"
						]
# with open('dummy.pk', 'wb') as output:
#	pickle.dump(SOME_DATA, output, pickle.HIGHEST_PROTOCOL)

class GridAllStocks(wx.grid.Grid):
	def __init__(self, *args, **kwargs):
		wx.grid.Grid.__init__(self, *args, **kwargs)
		global GLOBAL_STOCK_LIST
		self.num_rows = len(GLOBAL_STOCK_LIST)
		self.num_columns = 0
		for stock in GLOBAL_STOCK_LIST:
			num_attributes = 0
			for attribute in dir(stock):
				if not attribute.startswith('_'):
					num_attributes += 1
			if self.num_columns < num_attributes:
				self.num_columns = num_attributes
		#print line_number(), "Number of rows: %d" % self.num_rows
		#print line_number(), "Number of columns: %d" % self.num_columns
class StockScreenGrid(wx.grid.Grid):
	def __init__(self, *args, **kwargs):
		wx.grid.Grid.__init__(self, *args, **kwargs)
		
		global SCREEN_LIST
		stock_list = SCREEN_LIST

		self.num_rows = len(stock_list)
		self.num_columns = 0
		for stock in stock_list:
			num_attributes = 0
			for attribute in dir(stock):
				if not attribute.startswith('_'):
					num_attributes += 1
			if self.num_columns < num_attributes:
				self.num_columns = num_attributes
				#print line_number(), num_attributes
		#print line_number(), "Number of rows: %d" % self.num_rows
		#print line_number(), "Number of columns: %d" % self.num_columns
class SalePrepGrid(wx.grid.Grid):
	def __init__(self, *args, **kwargs):
		wx.grid.Grid.__init__(self, *args, **kwargs)

							

class AccountDataGrid(wx.grid.Grid):
	def __init__(self, *args, **kwargs):
		wx.grid.Grid.__init__(self, *args, **kwargs)

class MainFrame(wx.Frame):
	def __init__(self, *args, **kwargs):
		wx.Frame.__init__(self, None, title="wxStocks", *args, **kwargs)

		# Here we create a panel and a notebook on the panel
		main_frame = wx.Panel(self)
		notebook = wx.Notebook(main_frame)

		# create the page windows as children of the notebook
		# add the pages to the notebook with the label to show on the tab
		self.welcome_page = WelcomePage(notebook)
		notebook.AddPage(self.welcome_page, "Welcome")

		self.ticker_list_page = TickerPage(notebook)
		notebook.AddPage(self.ticker_list_page, "Tickers")

		self.scrape_page = ScrapePage(notebook)
		notebook.AddPage(self.scrape_page, "Scrape")

		self.all_stocks_page = AllStocksPage(notebook)
		notebook.AddPage(self.all_stocks_page, "Stocks")

		self.stock_screen_page = ScreenPage(notebook)
		notebook.AddPage(self.stock_screen_page, "Screen")

		self.saved_screen_page = SavedScreenPage(notebook)
		notebook.AddPage(self.saved_screen_page, "Saved Screens")

		self.rank_page = RankPage(notebook)
		notebook.AddPage(self.rank_page, "Rank")

		self.sale_prep_page = SalePrepPage(notebook)
		notebook.AddPage(self.sale_prep_page, "Sale Prep")

		self.trade_page = TradePage(notebook)
		notebook.AddPage(self.trade_page, "Trade")

		self.portfolio_page = PortfolioPage(notebook)
		notebook.AddPage(self.portfolio_page, "Portfolio")

		# finally, put the notebook in a sizer for the panel to manage
		# the layout


		sizer = wx.BoxSizer()
		sizer.Add(notebook, 1, wx.EXPAND)
		main_frame.SetSizer(sizer)

class Tab(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
class WelcomePage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		welcome_page_text = wx.StaticText(self, -1, 
							 "Welcome to wxStocks", 
							 (10,10)
							 )
		instructions_text = '''

	Instructions: 	this program is essentially a work-flow following the tabs above.
	---------------------------------------------------------------------------------------------------------------------------------

	Tickers:		This page is where you load in a .CSV file to create a list of tickers to scrape.
				You can get a properly formatted .CSV from the exchanges you want via a link on this page.

	Scrape:		This page takes the tickers, and then scrapes current stock data using them.

	Stocks:		This page generates a list of all stocks that have been scraped and presents all the data about them.
				Use this page to double check your data to make sure it's accurate and up to date.

	Screen:		This page allows you to screen for stocks that fit your criteria, and save them for later.

	Saved Screens:	This page allows you to recall old screens you've saved.

	Rank:		This page allows you to rank stocks along certain criteria. 

	Sale Prep:	This page allows you to estimate the amount of funds generated from a potential stock sale.

	Trade:		This page (currently not functional) takes the stocks you plan to sell, estimates the amount of money generated, 
				and lets you estimate the volume of stocks to buy to satisfy your diversification requirements.

	Portfolio:	This page allows you to load your portfolios from which you plan on making trades.
				If you have more than one portfolio you plan on working from, you may add more.
	'''

		instructions = wx.StaticText(self, -1, 
									instructions_text, 
									(10,20)
									)


class TickerPage(Tab):
	def __init__(self, parent):
		self.ticker_list_file = None

		wx.Panel.__init__(self, parent)
		text = wx.StaticText(self, -1, 
							 "Welcome to the ticker page. Download correctly formatted .csv files here:", 
							 (10,10)
							 )
		link_button = wx.Button(self, label="nasdaq.com/screening/company-list", pos=(472,5), size=(-1,-1))
		link_button.Bind(wx.EVT_BUTTON, self.linkToTickerCSV, link_button) 

		self.showTickerCSV()

	def linkToTickerCSV(self, e):
		wx.LaunchDefaultBrowser("http://www.nasdaq.com/screening/company-list.aspx")

	def showTickerCSV(self):
		global GLOBAL_TICKER_LIST

		self.displayTickers(GLOBAL_TICKER_LIST)

		add_button = wx.Button(self, label="Add .csv", pos=(10,50), size=(-1,-1))
		add_button.Bind(wx.EVT_BUTTON, self.addCsv, add_button) 

		clear_button = wx.Button(self, label="Delete ticker list", pos=(100,50), size=(-1,-1))
		clear_button.Bind(wx.EVT_BUTTON, self.deleteTickerList, clear_button) 

		self.Show()

	def deleteTickerList(self,e):
		'''delete current ticker list'''
		global GLOBAL_TICKER_LIST
		GLOBAL_TICKER_LIST = []
		# opening the file with w+ mode truncates the file
		with open('ticker.pk', 'wb') as output:
			pickle.dump(GLOBAL_TICKER_LIST, output, pickle.HIGHEST_PROTOCOL)
		self.showTickerCSV()

	def addCsv(self, e):
		'''append a csv to current ticker list'''
		self.dirname = ''
		dialog = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.csv", wx.OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			self.filename = dialog.GetFilename()
			self.dirname = dialog.GetDirectory()
			
			new_ticker_file = open(os.path.join(self.dirname, self.filename), 'rb')
			tickers_to_append = gen_ticker_list(new_ticker_file)
			new_ticker_file.close()

			global GLOBAL_TICKER_LIST
			GLOBAL_TICKER_LIST = GLOBAL_TICKER_LIST + tickers_to_append
			GLOBAL_TICKER_LIST = remove_list_duplicates(GLOBAL_TICKER_LIST)
			GLOBAL_TICKER_LIST.sort()
			with open('ticker.pk', 'wb') as output:
				pickle.dump(GLOBAL_TICKER_LIST, output, pickle.HIGHEST_PROTOCOL)
			self.showTickerCSV()
		dialog.Destroy()

	def displayTickers(self, ticker_list):
		ticker_list.sort()
		ticker_list_massive_str = ""
		for ticker in ticker_list:
			ticker_list_massive_str += ticker
			ticker_list_massive_str += ", "
		height_var = 100
		file_display = wx.TextCtrl(self, -1, 
									ticker_list_massive_str, 
									(10, height_var),
									size = (765, 625),
									style = wx.TE_READONLY | wx.TE_MULTILINE ,
									)
class ScrapePage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		text = wx.StaticText(self, -1, 
							 "Welcome to the scrape page", 
							 (10,10)
							 )
		self.scrape_button = wx.Button(self, label="Scrape YQL", pos=(5,100), size=(-1,-1))
		self.scrape_button.Bind(wx.EVT_BUTTON, self.confirmScrape, self.scrape_button)

		self.abort_scrape_button = wx.Button(self, label="Cancel Scrape", pos=(5,100), size=(-1,-1))
		self.abort_scrape_button.Bind(wx.EVT_BUTTON, self.abortScrape, self.abort_scrape_button)
		self.abort_scrape_button.Hide()
		self.abort_scrape = False

		self.progress_bar = wx.Gauge(self, -1, 100, size=(995, -1), pos = (0, 200))
		self.progress_bar.Hide()
		
		global GLOBAL_TICKER_LIST
		global SCRAPE_SLEEP_TIME
		global SCRAPE_CHUNK_LENGTH
		sleep_time = SCRAPE_SLEEP_TIME

		#if not GLOBAL_TICKER_LIST:
		#	ticker_file = open('ticker.pk', 'rb')
		#	if ticker_file:
		#		GLOBAL_TICKER_LIST = gen_ticker_list(ticker_file)
		#	ticker_file.close()
		ticker_len = len(GLOBAL_TICKER_LIST)
		ticker_len_text = wx.StaticText(self, -1, 
							 "Tickers = %d" % ticker_len, 
							 (10,30)
							 )
		scrape_time_secs = (ticker_len/SCRAPE_CHUNK_LENGTH) * sleep_time * 2
		scrape_time = time_from_epoch(scrape_time_secs)
		scrape_time_text = wx.StaticText(self, -1, 
					 "Time = %s" % scrape_time, 
					 (10,50)
					 )
		self.numScrapedStocks = 0

		#self.Show()
	def confirmScrape(self, event):
		confirm = wx.MessageDialog(None, 
								   "You are about to scrape of Yahoo's YQL database. If you do this too often Yahoo may temporarily block your IP address.", 
								   'Scrape stock data?', 
								   style = wx.YES_NO
								   )
		confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
		yesNoAnswer = confirm.ShowModal()
		#try:
		#	confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
		#except AttributeError:
		#	pass
		confirm.Destroy()

		if yesNoAnswer == wx.ID_YES:
			self.setUpScrape()

	def setUpScrape(self):
		global GLOBAL_TICKER_LIST
		global GLOBAL_STOCK_LIST
		global SCRAPE_CHUNK_LENGTH
		global SCRAPE_SLEEP_TIME
		global TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE
		chunk_length = SCRAPE_CHUNK_LENGTH # 145 appears to be the longest url string i can query with
		ticker_list = []
		for ticker in GLOBAL_TICKER_LIST:
			stock = return_stock_by_symbol(ticker)
			if stock:
				time_since_update = float(time.time()) - stock.epoch
				if int(time_since_update) < int(TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE):
					logging.warning("Will not add %s to update list, updated too recently, waste of yql query" % str(stock.symbol))
					continue
			ticker_list.append(ticker)
		num_of_tickers = len(ticker_list)
		sleep_time = SCRAPE_SLEEP_TIME

		# self.progress_bar.SetValue(0)
		# self.progress_bar.Show()
		# global app
		# app.Yield() # this updates the gui within a script (it must be here, or the progress bar will not show till the function finishes, also below for updates)

		slice_start = 0
		slice_end = chunk_length
		# this is a very important number
		# approx 200 calls per hour (yql forums info)
		# 3600 seconds in an hour
		# 3600 / 200 = 18 seconds pause per query to stay under the 200/hour limit
		if chunk_length < 1:
			logging.error("chunk_length too small, will create infinite loop")
			return
		count = 0
		last_loop = False

		chunk_list = []
		while slice_end < (num_of_tickers + (chunk_length)):
			if slice_end > num_of_tickers:
				slice_end = num_of_tickers
				last_loop = True
			data = None
			data2= None
			logging.info('While loop #%d' % count)
			ticker_chunk = ticker_list[slice_start:slice_end]
			chunk_list.append(ticker_chunk)
			count += 1
			print line_number(), count
			slice_start += chunk_length
			slice_end += chunk_length

		print line_number(), "got this far"
		
		#self.progress_dialog = wx.ProgressDialog('Scrape Progress', 
		#									'The stocks are currently downloading', 
		#									num_of_tickers,
		#									parent=self, 
		#									style=wx.PD_CAN_ABORT|wx.PD_REMAINING_TIME
		#									)


		number_of_tickers_in_chunk_list = 0
		for chunk in chunk_list:
			for ticker in chunk:
				number_of_tickers_in_chunk_list += 1
				print line_number(), number_of_tickers_in_chunk_list
		number_of_tickers_previously_updated = len(GLOBAL_TICKER_LIST) - number_of_tickers_in_chunk_list
		print line_number(), number_of_tickers_previously_updated
		total_number_of_tickers_done = number_of_tickers_previously_updated
		percent_of_full_scrape_done = round(100 * float(total_number_of_tickers_done) / float(len(GLOBAL_TICKER_LIST)) )

		print line_number(), percent_of_full_scrape_done
		
		self.progress_bar.SetValue(percent_of_full_scrape_done)
		self.progress_bar.Show()
		self.scrape_button.Hide()
		self.abort_scrape_button.Show()
		# Process the scrape while updating a progress bar
		timer = threading.Timer(0, self.executeScrapePartOne, [chunk_list, 0])
		timer.start()

			#scrape_thread = threading.Thread(target=self.executeOneScrape, args = (ticker_chunk,))
			#scrape_thread.daemon = True
			#scrape_thread.start()
			#while scrape_thread.isAlive():

			#	# Every two sleep times execute a new scrape
			#	full_scrape_sleep = float(sleep_time * 2)
			#	scrape_thread.join(full_scrape_sleep)
			#	cont, skip = progress_dialog.Update(self.numScrapedStocks)
			#	if not cont:
			#		progress_dialog.Destroy()
			#		return

	def executeScrapePartOne(self, ticker_chunk_list, position_of_this_chunk):
		if self.abort_scrape == True:
			self.abort_scrape = False
			self.progress_bar.Hide()
			print line_number(), "Scrape canceled."
			return
		global GLOBAL_TICKER_LIST
		global GLOBAL_STOCK_LIST
		global SCRAPE_CHUNK_LENGTH
		global SCRAPE_SLEEP_TIME
		global TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE
		sleep_time = SCRAPE_SLEEP_TIME


		ticker_chunk = ticker_chunk_list[position_of_this_chunk]

		if ticker_chunk:
			scrape_1_failed = False
			try:
				data = pyql.lookupQuote(ticker_chunk)
			except:
				logging.warning("Scrape didn't work. Nothing scraped.")
				scrape_1_failed = True
			if scrape_1_failed:
				#time.sleep(sleep_time)
				return
			else:
				logging.warning("Scrape 1 Success: mid-scrape sleep for %d seconds" % sleep_time)

				timer = threading.Timer(sleep_time, self.executeScrapePartTwo, [ticker_chunk_list, position_of_this_chunk, data])
				timer.start()

	def executeScrapePartTwo(self, ticker_chunk_list, position_of_this_chunk, successful_pyql_data):
		if self.abort_scrape == True:
			self.abort_scrape = False
			self.progress_bar.Hide()
			print line_number(), "Scrape canceled."
			return
		global GLOBAL_TICKER_LIST
		global GLOBAL_STOCK_LIST
		global SCRAPE_CHUNK_LENGTH
		global SCRAPE_SLEEP_TIME
		global TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE
		sleep_time = SCRAPE_SLEEP_TIME

		ticker_chunk = ticker_chunk_list[position_of_this_chunk]
		number_of_stocks_in_this_scrape = len(ticker_chunk)

		data = successful_pyql_data

		try:
			data2 = pyql.lookupKeyStats(ticker_chunk)
		except:
			logging.warning("Scrape 2 didn't work. Abort.")
			time.sleep(sleep_time)
			return

		for stock in data:
			new_stock = None
			for key, value in stock.iteritems():
				if key == "symbol":
					new_stock = return_stock_by_symbol(value)
					if not new_stock:
						new_stock = Stock(value)
						GLOBAL_STOCK_LIST.append(new_stock)
					else:
						new_stock.updated = datetime.datetime.now()
						new_stock.epoch = float(time.time())
			for key, value in stock.iteritems():
				# Here we hijack the power of the expando db structure
				# This adds the attribute of every possible attribute that can be passed
				setattr(new_stock, 
						str(key), 
						value
						)
			logging.warning("Success, putting %s: Data 1" % new_stock.symbol)
		#save
		with open('all_stocks.pk', 'wb') as output:
			pickle.dump(GLOBAL_STOCK_LIST, output, pickle.HIGHEST_PROTOCOL)		

		for stock2 in data2:
			for key, value in stock2.iteritems():
				if key == "symbol":
					new_stock = return_stock_by_symbol(value)
					if not new_stock:
						new_stock = Stock(value)
						GLOBAL_STOCK_LIST.append(new_stock)
			for key, value in stock2.iteritems():
				if isinstance(value, (list, dict)):
					#logging.warning(type(value))
					x = repr(value)
					term = None
					content = None
					#logging.warning(x)
					if x[0] == "[":
						y = ast.literal_eval(x)
						#logging.warning(y)
						for i in y:
							try:
								test = i["term"]
								test = i["content"]
							except Exception, e:
								#logging.error(new_stock.symbol)
								#logging.error(y)
								#logging.error("Seems to be [Trailing Annual Dividend Yield, Trailing Annual Dividend Yield%]")									
								continue
							#logging.warning(i)
							try:
								key_str = str(key)
								term = str(i["term"])
								term = term.replace(" ", "_")
								term = term.replace(",", "")
								term = strip_string_whitespace(term)
								key_term = key_str + "_" + term
								key_term = strip_string_whitespace(key_term)
								if "p_52_WeekHigh" in key_term:
									date = key_term[14:]
									setattr(new_stock, 
										"52_WeekHigh_Date", 
										date
										)
									key_str = "52_WeekHigh"
								elif "p_52_WeekLow" in key_term:
									date = key_term[13:]
									setattr(new_stock, 
										"52_WeekLow_Date", 
										date
										)
									key_str = "52_WeekLow"
								elif "ForwardPE_fye" in key_term:
									date = key_term[14:]
									setattr(new_stock, 
										"ForwardPE_fiscal_y_end_Date", 
										date
										)
									key_str = "ForwardPE"
								elif "EnterpriseValue_" in key_term:
									date = key_term[16:]
									setattr(new_stock, 
										"EnterpriseValue_Date", 
										date
										)
									key_str = "EnterpriseValue"
								elif "TrailingPE_ttm_" in key_term:
									date = key_term[15:] # will be of form  TrailingPE_ttm__intraday 
									setattr(new_stock, 
										"TrailingPE_ttm_Date", 
										date
										)
									key_str = "TrailingPE_ttm"
								elif "SharesShort_as_of" in key_term:
									date = key_term[18:] # will be of form SharesShort_as_of_Jul_15__2013 
									setattr(new_stock, 
										"SharesShort_as_of_Date", 
										date
										)
									key_str = "SharesShort"
								elif "ShortRatio_as_of" in key_term:
									date = key_term[16:] # will be of form SharesShort_as_of_Jul_15__2013 
									setattr(new_stock, 
										"ShortRatio_as_of_Date", 
										date
										)
									key_str = "ShortRatio"
								elif "ShortPercentageofFloat_as_of" in key_term:
									date = key_term[29:]
									setattr(new_stock, 
										"ShortPercentageofFloat_as_of_Date", 
										date
										)
									key_str = "ShortPercentageofFloat"
								elif "p_2" in key_term or "p_5" in key_term:
									key_str = key_str[2:]
								else:
									key_str = str(key + "_" + term)
								content = str(i["content"])
								setattr(new_stock, 
										key_str, 
										content
										)
							except Exception, e:
								logging.warning(repr(i))
								logging.warning("complex list method did not work")
								logging.exception(e)
								setattr(new_stock, 
										str(key), 
										x
										)

					elif x[0] == "{":
						y = ast.literal_eval(x)
						try:
							test = y["term"]
							test = y["content"]
						except Exception, e:
							#logging.error(new_stock.symbol)
							#logging.error(y)
							#logging.error("Seems to be [Trailing Annual Dividend Yield, Trailing Annual Dividend Yield%]")									
							continue
						#logging.warning(y)
						try:
							key_str = str(key)
							term = str(y["term"])
							term = term.replace(" ", "_")
							term = term.replace(",", "")
							term = strip_string_whitespace(term)
							key_term = key_str + "_" + term
							key_term = strip_string_whitespace(key_term)
							if "p_52_WeekHigh" in key_term:
								date = key_term[14:]
								setattr(new_stock, 
									"52_WeekHigh_Date", 
									date
									)
								key_str = "52_WeekHigh"
							elif "p_52_WeekLow" in key_term:
								date = key_term[13:]
								setattr(new_stock, 
									"52_WeekLow_Date", 
									date
									)
								key_str = "52_WeekLow"
							elif "ForwardPE_fye" in key_term:
								date = key_term[14:]
								setattr(new_stock, 
									"ForwardPE_fiscal_y_end_Date", 
									date
									)
								key_str = "ForwardPE"
							elif "EnterpriseValue_" in key_term:
								date = key_term[16:]
								setattr(new_stock, 
									"EnterpriseValue_Date", 
									date
									)
								key_str = "EnterpriseValue"
							elif "TrailingPE_ttm_" in key_term:
								date = key_term[15:] # will be of form  TrailingPE_ttm__intraday 
								setattr(new_stock, 
									"TrailingPE_ttm_Date", 
									date
									)
								key_str = "TrailingPE_ttm"
							elif "SharesShort_as_of" in key_term:
								date = key_term[18:] # will be of form SharesShort_as_of_Jul_15__2013 
								setattr(new_stock, 
									"SharesShort_as_of_Date", 
									date
									)
								key_str = "SharesShort"
							elif "ShortRatio_as_of" in key_term:
								date = key_term[16:] # will be of form SharesShort_as_of_Jul_15__2013 
								setattr(new_stock, 
									"ShortRatio_as_of_Date", 
									date
									)
								key_str = "ShortRatio"
							elif "ShortPercentageofFloat_as_of" in key_term:
								date = key_term[29:]
								setattr(new_stock, 
									"ShortPercentageofFloat_as_of_Date", 
									date
									)
								key_str = "ShortPercentageofFloat"
							elif "p_2" in key_term or "p_5" in key_term:
								key_str = key_str[2:]
							else:
								key_str = str(key + "_" + term)
							content = str(y["content"])
							setattr(new_stock, 
									key_str, 
									content
									)
						except Exception, e:
							logging.warning("complex dict method did not work")
							logging.exception(e)
							setattr(new_stock, 
									str(key), 
									x
									)
					else:
						key_str = str(key)
						if "p_2" in key_str or "p_5" in key_str:
							key_str = key_str[2:]
						setattr(new_stock, 
							key_str, 
							x
							)
				else:
					key_str = str(key)
					if "p_2" in key_str or "p_5" in key_str:
						key_str = key_str[2:]
					setattr(new_stock, 
							key_str, 
							value
							)
			logging.warning("Success, putting %s: Data 2" % new_stock.symbol)

		#save again
		with open('all_stocks.pk', 'wb') as output:
			pickle.dump(GLOBAL_STOCK_LIST, output, pickle.HIGHEST_PROTOCOL)		

		logging.warning("This stock chunk finished successfully.")
		#self.progress_bar.SetValue((float(slice_end)/float(num_of_tickers)) * 100)
		#app.Yield()

		logging.warning("Sleeping for %d seconds before the next task" % sleep_time)
		#time.sleep(sleep_time)

		#self.numScrapedStocks += number_of_stocks_in_this_scrape
		#cont, skip = self.progress_dialog.Update(self.numScrapedStocks)
		#if not cont:
		#	self.progress_dialog.Destroy()
		#	return


		number_of_tickers_in_chunk_list = 0
		for chunk in ticker_chunk_list:
			for ticker in chunk:
				number_of_tickers_in_chunk_list += 1
		number_of_tickers_previously_updated = len(GLOBAL_TICKER_LIST) - number_of_tickers_in_chunk_list
		number_of_tickers_done_in_this_scrape = 0
		for i in range(len(ticker_chunk_list)):
			if i > position_of_this_chunk:
				continue
			for ticker in ticker_chunk_list[i]:
				number_of_tickers_done_in_this_scrape += 1
		total_number_of_tickers_done = number_of_tickers_previously_updated + number_of_tickers_done_in_this_scrape
		percent_of_full_scrape_done = round( 100 * float(total_number_of_tickers_done) / float(len(GLOBAL_TICKER_LIST)))

		position_of_this_chunk += 1
		percent_done = round( 100 * float(position_of_this_chunk) / float(len(ticker_chunk_list)) )
		print line_number(), "%d%%" % percent_done, "done this scrape execution."
		print line_number(), "%d%%" % percent_of_full_scrape_done, "done of all tickers."
		self.progress_bar.SetValue(percent_of_full_scrape_done)
		if position_of_this_chunk >= len(ticker_chunk_list):
			# finished
			self.abort_scrape_button.Hide()
			self.scrape_button.Show()
			self.progress_bar.SetValue(100)
			return
		else:
			timer = threading.Timer(sleep_time, self.executeScrapePartOne, [ticker_chunk_list, position_of_this_chunk])
			timer.start()

	def abortScrape(self, event):
		if self.abort_scrape == False:
			self.abort_scrape = True
			self.abort_scrape_button.Hide()
			self.scrape_button.Show()


class AllStocksPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		welcome_page_text = wx.StaticText(self, -1, 
							 "Full Stock List", 
							 (10,10)
							 )

		self.spreadsheet = None

		refresh_button = wx.Button(self, label="refresh", pos=(110,4), size=(-1,-1))
		refresh_button.Bind(wx.EVT_BUTTON, self.spreadSheetFill, refresh_button)

		#self.spreadSheetFill('event')

	def spreadSheetFill(self, event):
		try:
			self.spreadsheet.Destroy()
		except Exception, exception:
			print line_number(), exception

		global GLOBAL_STOCK_LIST
		stock_list = GLOBAL_STOCK_LIST
		self.spreadsheet = GridAllStocks(self, -1, size=(1000,680), pos=(0,50))


		self.spreadsheet.CreateGrid(self.spreadsheet.num_rows, self.spreadsheet.num_columns)
		self.spreadsheet.EnableEditing(False)

		attribute_list = []
		for stock in stock_list:
			for attribute in dir(stock):
				if not attribute.startswith('_'):
					attribute_list.append(str(attribute))
			break
		attribute_list.sort()
		# adjust list order for important terms
		try:
			attribute_list.insert(0, attribute_list.pop(attribute_list.index('symbol')))
		except Exception, e:
			print line_number(), e
		try:
			attribute_list.insert(1, attribute_list.pop(attribute_list.index('Name')))
		except Exception, e:
			print line_number(), e
		#print line_number(), attribute_list

		row_count = 0
		col_count = 0

		for stock in stock_list:
			for attribute in attribute_list:
				#if not attribute.startswith('_'):
				if row_count == 0:
					self.spreadsheet.SetColLabelValue(col_count, str(attribute))
				try:
					self.spreadsheet.SetCellValue(row_count, col_count, str(getattr(stock, attribute)))
				except:
					pass
				col_count += 1
			row_count += 1
			col_count = 0
		self.spreadsheet.AutoSizeColumns()

class ScreenPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		welcome_page_text = wx.StaticText(self, -1, 
							 "Screen Stocks", 
							 (10,10)
							 )
		screen_button = wx.Button(self, label="screen", pos=(110,4), size=(-1,-1))
		screen_button.Bind(wx.EVT_BUTTON, self.screenStocks, screen_button)

		self.drop_down = wx.ComboBox(self, pos=(210, 6), choices=['PE < 10', 'are','default','choices'])

		self.save_screen_button = wx.Button(self, label="save", pos=(900,4), size=(-1,-1))
		self.save_screen_button.Bind(wx.EVT_BUTTON, self.saveScreen, self.save_screen_button)
		self.save_screen_button.Hide()

		#self.my_text = wx.StaticText(self, -1, "default", (600, 10), style=wx.ALIGN_CENTRE)

		self.screen_grid = None

	def saveScreen(self, event):
		global SCREEN_LIST
		current_screen_list = SCREEN_LIST

		try:
			existing_screen_names_file = open('screen_names.pk', 'rb')
		except Exception, exception:
			print line_number(), exception
			existing_screen_names_file = open('screen_names.pk', 'wb')
			empty_list = []
			with open('screen_names.pk', 'wb') as output:
				pickle.dump(empty_list, output, pickle.HIGHEST_PROTOCOL)
			existing_screen_names_file = open('screen_names.pk', 'rb')
		existing_screen_names = pickle.load(existing_screen_names_file)

		save_popup = wx.TextEntryDialog(None,
										  "What would you like to name this group?", 
										  "Save Screen", 
										  "%s screen saved at %s" % (str(time.strftime("%Y-%m-%d")),str(time.strftime("%H:%M:%S")))
										 )
		if save_popup.ShowModal() == wx.ID_OK:
			saved_screen_name = str(save_popup.GetValue())

			if saved_screen_name in existing_screen_names:
				error = wx.MessageDialog(self,
										 'Each saved screen must have a unique name. Please try saving again with a different name.',
										 'Error: Could not save',
										 style = wx.ICON_ERROR
										 )
				error.ShowModal()
				error.Destroy()
				return
			else:
				existing_screen_names.append(saved_screen_name)
				print line_number(), existing_screen_names
				with open('screen_names.pk', 'wb') as output:
					pickle.dump(existing_screen_names, output, pickle.HIGHEST_PROTOCOL)

				with open('screen-%s.pk' % saved_screen_name, 'wb') as output:
					pickle.dump(current_screen_list, output, pickle.HIGHEST_PROTOCOL)

				self.save_screen_button.Hide()

		save_popup.Destroy()



	def screenStocks(self, event):
		global GLOBAL_STOCK_LIST
		stock_list = GLOBAL_STOCK_LIST
		drop_down_value = self.drop_down.GetValue()

		if drop_down_value == 'PE < 10':
			stock_list = screen_pe_less_than_10()

		global SCREEN_LIST
		SCREEN_LIST = stock_list

		try:
			self.screen_grid.Destroy()
		except Exception, e:
			print line_number(), e

		self.screen_grid = StockScreenGrid(self, -1, size=(1000,680), pos=(0,50))
		self.spreadSheetFill(self.screen_grid, stock_list)

		self.save_screen_button.Show()

	def spreadSheetFill(self, spreadsheet, stock_list):
		spreadsheet.CreateGrid(spreadsheet.num_rows, spreadsheet.num_columns)
		spreadsheet.EnableEditing(False)

		attribute_list = []
		for stock in stock_list:
			for attribute in dir(stock):
				if not attribute.startswith('_'):
					attribute_list.append(str(attribute))
			break
		if not attribute_list:
			return
		attribute_list.sort()
		# adjust list order for important terms
		attribute_list.insert(0, attribute_list.pop(attribute_list.index('symbol')))
		attribute_list.insert(1, attribute_list.pop(attribute_list.index('Name')))
		#print line_number(), attribute_list

		row_count = 0
		col_count = 0

		for stock in stock_list:
			for attribute in attribute_list:
				#if not attribute.startswith('_'):
				if row_count == 0:
					spreadsheet.SetColLabelValue(col_count, str(attribute))
				try:
					spreadsheet.SetCellValue(row_count, col_count, str(getattr(stock, attribute)))
				except:
					pass
				col_count += 1
			row_count += 1
			col_count = 0
		spreadsheet.AutoSizeColumns()
class SavedScreenPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		welcome_page_text = wx.StaticText(self, -1, 
							 "Saved screens", 
							 (10,10)
							 )
		refresh_screen_button = wx.Button(self, label="refresh list", pos=(110,5), size=(-1,-1))
		refresh_screen_button.Bind(wx.EVT_BUTTON, self.refreshScreens, refresh_screen_button)

		load_screen_button = wx.Button(self, label="load screen", pos=(200,5), size=(-1,-1))
		load_screen_button.Bind(wx.EVT_BUTTON, self.loadScreen, load_screen_button)

		try:
			existing_screen_names_file = open('screen_names.pk', 'rb')
		except Exception, exception:
			print line_number(), exception
			existing_screen_names_file = open('screen_names.pk', 'wb')
			empty_list = []
			with open('screen_names.pk', 'wb') as output:
				pickle.dump(empty_list, output, pickle.HIGHEST_PROTOCOL)
			existing_screen_names_file = open('screen_names.pk', 'rb')
		existing_screen_names = pickle.load(existing_screen_names_file)
		existing_screen_names_file.close()
		self.drop_down = wx.ComboBox(self, 
									 pos=(305, 6), 
									 choices=existing_screen_names,
									 style = wx.TE_READONLY
									 )

		self.currently_viewed_screen = None
		self.delete_screen_button = wx.Button(self, label="delete", pos=(900,4), size=(-1,-1))
		self.delete_screen_button.Bind(wx.EVT_BUTTON, self.deleteScreen, self.delete_screen_button)
		self.delete_screen_button.Hide()
		
		self.screen_grid = None

	def deleteScreen(self, event):
		confirm = wx.MessageDialog(None, 
								   "You are about to delete this screen.", 
								   'Are you sure?', 
								   wx.YES_NO
								   )
		confirm.SetYesNoLabels(("&Delete"), ("&Cancel"))
		yesNoAnswer = confirm.ShowModal()
		confirm.Destroy()


		print line_number(), self.screen_grid
		if yesNoAnswer != wx.ID_YES:
			return
		try:
			print line_number(), self.currently_viewed_screen
			existing_screen_names_file = open('screen_names.pk', 'rb')
			existing_screen_names = pickle.load(existing_screen_names_file)
			#print line_number(), existing_screen_names
			existing_screen_names.remove(self.currently_viewed_screen)
			with open('screen_names.pk', 'wb') as output:
				pickle.dump(existing_screen_names, output, pickle.HIGHEST_PROTOCOL)
			os.remove('screen-%s.pk' % self.currently_viewed_screen)
			self.screen_grid.Destroy()
		except Exception, exception:
			print line_number(), exception
			error = wx.MessageDialog(self,
									 "Something went wrong. File was not deleted, because this file doesn't seem to exist.",
									 'Error: File Does Not Exist',
									 style = wx.ICON_ERROR
									 )
			error.ShowModal()
			error.Destroy()
			return
		self.refreshScreens('event')

	def refreshScreens(self, event):
		self.drop_down.Hide()
		self.drop_down.Destroy()

		time.sleep(2)

		try:
			existing_screen_names_file = open('screen_names.pk', 'rb')
		except Exception, exception:
			print line_number(), exception
			existing_screen_names_file = open('screen_names.pk', 'wb')
			empty_list = []
			with open('screen_names.pk', 'wb') as output:
				pickle.dump(empty_list, output, pickle.HIGHEST_PROTOCOL)
			existing_screen_names_file = open('screen_names.pk', 'rb')
		existing_screen_names = pickle.load(existing_screen_names_file)

		self.drop_down = wx.ComboBox(self, 
									 pos=(305, 6), 
									 choices=existing_screen_names,
									 style = wx.TE_READONLY
									 )

	def loadScreen(self, event):
		selected_screen_name = self.drop_down.GetValue()
		try:
			saved_screen_file = open('screen-%s.pk' % selected_screen_name, 'rb')
			saved_screen = pickle.load(saved_screen_file)
			saved_screen_file.close()
		except Exception, exception:
			print line_number(), exception
			error = wx.MessageDialog(self,
									 "Something went wrong. This file doesn't seem to exist.",
									 'Error: File Does Not Exist',
									 style = wx.ICON_ERROR
									 )
			error.ShowModal()
			error.Destroy()
			return

		self.currently_viewed_screen = selected_screen_name
		stock_list = saved_screen

		try:
			self.screen_grid.Destroy()
		except Exception, exception:
			print line_number(), exception

		self.spreadSheetFill(stock_list)

	def spreadSheetFill(self, stock_list):
		num_rows = len(stock_list)
		num_columns = 0
		for stock in stock_list:
			num_attributes = 0
			for attribute in dir(stock):
				if not attribute.startswith('_'):
					num_attributes += 1
			if num_columns < num_attributes:
				num_columns = num_attributes
		self.screen_grid = StockScreenGrid(self, -1, size=(980,637), pos=(0,50))

		self.screen_grid.CreateGrid(num_rows, num_columns)
		self.screen_grid.EnableEditing(False)

		attribute_list = []
		for stock in stock_list:
			for attribute in dir(stock):
				if not attribute.startswith('_'):
					attribute_list.append(str(attribute))
			break
		if not attribute_list:
			logging.warning('attribute list empty')
			return
		attribute_list.sort()
		# adjust list order for important terms
		attribute_list.insert(0, attribute_list.pop(attribute_list.index('symbol')))
		attribute_list.insert(1, attribute_list.pop(attribute_list.index('Name')))
		#print line_number(), attribute_list

		row_count = 0
		col_count = 0

		for stock in stock_list:
			for attribute in attribute_list:
				#if not attribute.startswith('_'):
				if row_count == 0:
					self.screen_grid.SetColLabelValue(col_count, str(attribute))
				try:
					self.screen_grid.SetCellValue(row_count, col_count, str(getattr(stock, attribute)))
				except:
					pass
				col_count += 1
			row_count += 1
			col_count = 0
		self.screen_grid.AutoSizeColumns()

		self.delete_screen_button.Show()
class RankPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.full_ticker_list = []
		self.sorted_full_ticker_list = []


		self.lists_in_ticker_list = [] # currently unused

		self.full_attribute_list = []
		global IRRELEVANT_ATTRIBUTES
		self.irrelevant_attributes = IRRELEVANT_ATTRIBUTES

		self.held_ticker_list = []
		self.screen_ticker_list = []


		rank_page_text = wx.StaticText(self, -1, 
							 "Rank", 
							 (10,10)
							 )
		refresh_screen_button = wx.Button(self, label="refresh", pos=(110,5), size=(-1,-1))
		refresh_screen_button.Bind(wx.EVT_BUTTON, self.refreshScreens, refresh_screen_button)

		load_screen_button = wx.Button(self, label="add screen", pos=(200,5), size=(-1,-1))
		load_screen_button.Bind(wx.EVT_BUTTON, self.loadScreen, load_screen_button)

		load_portfolio_button = wx.Button(self, label="add account", pos=(191,30), size=(-1,-1))
		load_portfolio_button.Bind(wx.EVT_BUTTON, self.loadAccount, load_portfolio_button)


		try:
			existing_screen_names_file = open('screen_names.pk', 'rb')
		except Exception, exception:
			print line_number(), exception
			existing_screen_names_file = open('screen_names.pk', 'wb')
			empty_list = []
			with open('screen_names.pk', 'wb') as output:
				pickle.dump(empty_list, output, pickle.HIGHEST_PROTOCOL)
			existing_screen_names_file = open('screen_names.pk', 'rb')
		existing_screen_names = pickle.load(existing_screen_names_file)
		existing_screen_names_file.close()
		self.drop_down = wx.ComboBox(self, 
									 pos=(305, 6), 
									 choices=existing_screen_names,
									 style = wx.TE_READONLY
									 )

		global PORTFOLIO_NAMES
		self.portfolio_name_tuple_list = []
		for i in range(len(PORTFOLIO_NAMES)):
			tuple_to_append = [PORTFOLIO_NAMES[i], (i+1)]
			self.portfolio_name_tuple_list.append(tuple_to_append)
			#print line_number(), self.portfolio_name_tuple_list

		self.accounts_drop_down = wx.ComboBox(self, 
									 pos=(305, 31), 
									 choices=PORTFOLIO_NAMES,
									 style = wx.TE_READONLY
									 )


		self.currently_viewed_screen = None
		self.clear_button = wx.Button(self, label="clear", pos=(900,4), size=(-1,-1))
		self.clear_button.Bind(wx.EVT_BUTTON, self.clearGrid, self.clear_button)
		self.clear_button.Hide()

		self.sort_button = wx.Button(self, label="Sort by:", pos=(420,30), size=(-1,-1))
		self.sort_button.Bind(wx.EVT_BUTTON, self.sortStocks, self.sort_button)
		self.sort_drop_down = wx.ComboBox(self, 
									 pos=(520, 31), 
									 choices=self.full_attribute_list,
									 style = wx.TE_READONLY
									 )
		self.sort_button.Hide()
		self.sort_drop_down.Hide()

		
		self.screen_grid = None

	def clearGrid(self, event):
		confirm = wx.MessageDialog(None, 
								   "You are about to clear this grid.", 
								   'Are you sure?', 
								   wx.YES_NO
								   )
		confirm.SetYesNoLabels(("&Clear"), ("&Cancel"))
		yesNoAnswer = confirm.ShowModal()
		confirm.Destroy()
		if yesNoAnswer != wx.ID_YES:
			return

		self.full_ticker_list = []
		self.sorted_full_ticker_list = []
		self.full_attribute_list = []
		self.held_ticker_list = []
		self.screen_ticker_list = []
		
		self.spreadSheetFill(self.full_ticker_list)


		self.clear_button.Hide()
		self.sort_button.Hide()
		self.sort_drop_down.Hide()

	def refreshScreens(self, event):
		self.drop_down.Hide()
		self.drop_down.Destroy()

		self.accounts_drop_down.Hide()
		self.accounts_drop_down.Destroy()

		time.sleep(2)

		try:
			existing_screen_names_file = open('screen_names.pk', 'rb')
		except Exception, exception:
			print line_number(), exception
			existing_screen_names_file = open('screen_names.pk', 'wb')
			empty_list = []
			with open('screen_names.pk', 'wb') as output:
				pickle.dump(empty_list, output, pickle.HIGHEST_PROTOCOL)
			existing_screen_names_file = open('screen_names.pk', 'rb')
		existing_screen_names = pickle.load(existing_screen_names_file)

		self.drop_down = wx.ComboBox(self, 
									 pos=(305, 6), 
									 choices=existing_screen_names,
									 style = wx.TE_READONLY
									 )

		global PORTFOLIO_NAMES
		self.portfolio_name_tuple_list = []
		for i in range(len(PORTFOLIO_NAMES)):
			tuple_to_append = [PORTFOLIO_NAMES[i], (i+1)]
			self.portfolio_name_tuple_list.append(tuple_to_append)
			print line_number(), self.portfolio_name_tuple_list

		self.accounts_drop_down = wx.ComboBox(self, 
									 pos=(305, 31), 
									 choices=PORTFOLIO_NAMES,
									 style = wx.TE_READONLY
									 )
	def loadScreen(self, event):
		selected_screen_name = self.drop_down.GetValue()
		try:
			saved_screen_file = open('screen-%s.pk' % selected_screen_name, 'rb')
			saved_screen = pickle.load(saved_screen_file)
			saved_screen_file.close()
		except Exception, exception:
			print line_number(), exception
			error = wx.MessageDialog(self,
									 "Something went wrong. This file doesn't seem to exist.",
									 'Error: File Does Not Exist',
									 style = wx.ICON_ERROR
									 )
			error.ShowModal()
			error.Destroy()
			return

		self.currently_viewed_screen = selected_screen_name
		for i in saved_screen:
			if str(i.symbol) not in self.screen_ticker_list:
				self.screen_ticker_list.append(str(i.symbol))
			if str(i.symbol) not in self.full_ticker_list:
				self.full_ticker_list.append(str(i.symbol))

		try:
			self.screen_grid.Destroy()
		except Exception, exception:
			print line_number(), exception

		self.spreadSheetFill(self.full_ticker_list)
	def loadAccount(self, event):
		selected_account_name = self.accounts_drop_down.GetValue()
		tuple_not_found = True
		for this_tuple in self.portfolio_name_tuple_list:
			if selected_account_name == this_tuple[0]:
				tuple_not_found = False
				try:
					saved_account_file = open('portfolio_%d_data.pk' % this_tuple[1], 'rb')
					saved_account = pickle.load(saved_account_file)
					saved_account_file.close()
				except Exception, exception:
					print line_number(), exception
					error = wx.MessageDialog(self,
											 "Something went wrong. This file doesn't seem to exist.",
											 'Error: File Does Not Exist',
											 style = wx.ICON_ERROR
											 )
					error.ShowModal()
					error.Destroy()
					return
		if tuple_not_found:
			error = wx.MessageDialog(self,
									 "Something went wrong. This data doesn't seem to exist.",
									 'Error: Data Does Not Exist',
									 style = wx.ICON_ERROR
									 )
			error.ShowModal()
			error.Destroy()
			return

		for stock in saved_account.stock_list:
			if str(stock.symbol) not in self.held_ticker_list:
				self.held_ticker_list.append(str(stock.symbol))
			if str(stock.symbol) not in self.full_ticker_list:
				self.full_ticker_list.append(str(stock.symbol))

		try:
			self.screen_grid.Destroy()
		except Exception, exception:
			print line_number(), exception

		self.spreadSheetFill(self.full_ticker_list)
	def spreadSheetFill(self, ticker_list):
		global GLOBAL_STOCK_LIST
		stock_list = []
		for ticker in ticker_list:
			stock_absent = True
			for stock in GLOBAL_STOCK_LIST:
				if str(ticker) == str(stock.symbol):
					stock_list.append(stock)
					stock_absent = False
			if stock_absent:
				logging.error('Ticker "%s" does not appear to be in the GLOBAL_STOCK_LIST' % ticker)

		self.full_attribute_list = [] # Reset root attribute list
		attribute_list = []

		num_rows = len(stock_list)
		num_columns = 0
		for stock in stock_list:
			num_attributes = 0
			for attribute in dir(stock):
				if not attribute.startswith('_'):
					if attribute not in self.irrelevant_attributes:
						num_attributes += 1
			if num_columns < num_attributes:
				num_columns = num_attributes
		self.screen_grid = StockScreenGrid(self, -1, size=(980,637), pos=(0,60))

		self.screen_grid.CreateGrid(num_rows, num_columns)
		self.screen_grid.EnableEditing(False)


		for stock in stock_list:
			for attribute in dir(stock):
				if not attribute.startswith('_'):
					if attribute not in self.irrelevant_attributes:
						attribute_list.append(str(attribute))
						if str(attribute) not in self.full_attribute_list:
							self.full_attribute_list.append(str(attribute)) # Reset root attribute list
			break
		#for i in self.full_attribute_list:
		#	print line_number(), i
		if not attribute_list:
			logging.warning('attribute list empty')
			return
		attribute_list.sort()
		# adjust list order for important terms
		attribute_list.insert(0, attribute_list.pop(attribute_list.index('symbol')))
		attribute_list.insert(1, attribute_list.pop(attribute_list.index('Name')))
		#print line_number(), attribute_list

		row_count = 0
		col_count = 0

		for stock in stock_list:
			for attribute in attribute_list:
				#if not attribute.startswith('_'):
				if row_count == 0:
					self.screen_grid.SetColLabelValue(col_count, str(attribute))
				try:
					self.screen_grid.SetCellValue(row_count, col_count, str(getattr(stock, attribute)))
					if str(stock.symbol) in self.held_ticker_list:
						self.screen_grid.SetCellBackgroundColour(row_count, col_count, "#FAEFCF")
				except Exception, exception:
					pass
					#print line_number(), exception
				col_count += 1
			row_count += 1
			col_count = 0
		self.screen_grid.AutoSizeColumns()

		try:
			self.sort_drop_down.Destroy()
			self.sort_drop_down = wx.ComboBox(self, 
											 pos=(520, 31), 
											 choices=self.full_attribute_list,
											 style = wx.TE_READONLY
											 )
		except Exception, exception:
			pass
			#print line_number(), exception
		self.clear_button.Show()
		self.sort_button.Show()
		self.sort_drop_down.Show()
	def sortStocks(self, event):
		sort_field = self.sort_drop_down.GetValue()
		do_not_sort_reversed = ["symbol"]
		if sort_field in do_not_sort_reversed:
			reverse_var = False
		else:
			reverse_var = True

		num_stock_value_list = []
		str_stock_value_list = []
		incompatible_stock_list = []
		self.full_ticker_list = remove_list_duplicates(self.full_ticker_list)
		for ticker in self.full_ticker_list:
			stock = return_stock_by_symbol(ticker)
			if stock:
				try:
					val = getattr(stock, sort_field)
					try:
						float(val)
						num_stock_value_list.append(stock)
					except:
						str_stock_value_list.append(stock)
				except Exception, exception:
					#print line_number(), exception
					incompatible_stock_list.append(stock)

		num_stock_value_list.sort(key = lambda x: float(getattr(x, sort_field)), reverse=reverse_var)
		
		str_stock_value_list.sort(key = lambda x: getattr(x, sort_field))

		incompatible_stock_list.sort(key = lambda x: x.symbol)

		self.sorted_full_ticker_list = []
		for stock in num_stock_value_list:
			self.sorted_full_ticker_list.append(str(stock.symbol))
		for stock in str_stock_value_list:
			self.sorted_full_ticker_list.append(str(stock.symbol))
		for incompatible_stock in incompatible_stock_list:
			self.sorted_full_ticker_list.append(str(incompatible_stock.symbol))
		self.spreadSheetFill(self.sorted_full_ticker_list)
		self.sort_drop_down.SetStringSelection(sort_field)
class SalePrepPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		trade_page_text = wx.StaticText(self, -1, 
							 "Sale Prep", 
							 (10,10)
							 )
		self.ticker_list = []



		global NUMBER_OF_PORTFOLIOS
		global PORTFOLIO_NAMES

		global PORTFOLIO_OBJECTS_LIST
		self.portfolio_obj_list = PORTFOLIO_OBJECTS_LIST
		
		self.checkbox_list = []
		for i in range(NUMBER_OF_PORTFOLIOS):
			horizontal_offset = 0
			if i>=5:
				horizontal_offset = 200
			checkbox_to_add = wx.CheckBox(self, -1, 
										  PORTFOLIO_NAMES[i], 
										  pos=((600+ horizontal_offset), (16*i)), 
										  size=(-1,-1)
										  )
			try:
				throw_error = PORTFOLIO_OBJECTS_LIST[i].stock_list
				checkbox_to_add.SetValue(True)
			except Exception, exception:
				pass#print line_number(), exception
			self.checkbox_list.append(checkbox_to_add)
		
		line = wx.StaticLine(self, -1, pos=(0,83), size=(1000,-1))

		refresh_button = wx.Button(self, label="Clear and Refresh Spreadsheet", pos=(110,5), size=(-1,-1))
		refresh_button.Bind(wx.EVT_BUTTON, self.spreadSheetFill, refresh_button)

		load_new_account_data_button = wx.Button(self, label="Refresh Accounts Data and Spreadsheet", pos=(110,30), size=(-1,-1))
		load_new_account_data_button.Bind(wx.EVT_BUTTON, self.refreshAccountData, load_new_account_data_button)

		self.save_button = wx.Button(self, label="Export to Trade Window", pos=(420,50), size=(-1,-1))
		self.save_button.Bind(wx.EVT_BUTTON, self.exportSaleCandidates, self.save_button)
		self.save_button.Hide()

		self.saved_text = wx.StaticText(self, -1, 
										"Data is now in memory.", 
										(433,55)
										)
		self.saved_text.Hide()

		self.grid = None
		for i in range(len(self.checkbox_list)):
			box = self.checkbox_list[i]
			if box:
				is_checked = box.GetValue()
				#print line_number(), is_checked
				if is_checked:
					self.spreadSheetFill('event')
					break

	def exportSaleCandidates(self, event):
		print line_number(), "Boom goes the dynamite!"
		self.save_button.Hide()
		self.saved_text.Show()
		
	def refreshAccountData(self, event):
		######## Rebuild Checkbox List in case of new accounts
		global PORTFOLIO_OBJECTS_LIST
		self.portfolio_obj_list = PORTFOLIO_OBJECTS_LIST
		for i in self.checkbox_list:
			try:
				i.Destroy()
			except Exception, exception:
				print line_number(), exception
		self.checkbox_list = []
		for i in range(NUMBER_OF_PORTFOLIOS):
			horizontal_offset = 0
			if i>=5:
				horizontal_offset = 200
			checkbox_to_add = wx.CheckBox(self, -1, 
										  PORTFOLIO_NAMES[i], 
										  pos=((600 + horizontal_offset), (16*i)), 
										  size=(-1,-1)
										  )
			try:
				throw_error = PORTFOLIO_OBJECTS_LIST[i].stock_list
				checkbox_to_add.SetValue(True)
			except Exception, exception:
				pass#print line_number(), exception
			self.checkbox_list.append(checkbox_to_add)
		self.spreadSheetFill("event")
	def spreadSheetFill(self, event):
		try:
			self.grid.Destroy()
		except Exception, exception:
			pass
			#print line_number(), exception
		
		relevant_portfolios_list = []
		for i in range(len(self.checkbox_list)):
			box = self.checkbox_list[i]
			is_checked = box.GetValue()
			if is_checked:
				relevant_portfolios_list.append(self.portfolio_obj_list[i])

		num_columns = 17
		default_rows = 9
		num_rows = default_rows
		for account in relevant_portfolios_list:
			try:
				num_rows += 1 # for account name
				num_stocks = len(account.stock_list)
				num_rows += num_stocks
				#print line_number(), num_rows
			except Exception, exception:
				pass#print line_number(), exception

		self.grid = SalePrepGrid(self, -1, size=(1000,650), pos=(0,83))
		self.grid.CreateGrid(num_rows, num_columns)
		self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.updateGrid, self.grid)


		for column_num in range(num_columns):
			for row_num in range(num_rows):
				if not ((row_num >= default_rows and column_num in [1,2]) or (row_num == 3 and column_num == 14)):
					self.grid.SetReadOnly(row_num, column_num, True)
				elif column_num == 14:
					self.grid.SetCellBackgroundColour(row_num, column_num, "#C5DBCA")
				elif column_num == 1:
					self.grid.SetCellBackgroundColour(row_num, column_num, "#CFE8FC")
				elif column_num == 2:
					self.grid.SetCellBackgroundColour(row_num, column_num, "#CFFCEF")

		self.grid.SetCellValue(2, 0, str(time.time()))
		self.grid.SetCellValue(2, 14, "Input carryover loss (if any)")
		self.grid.SetCellValue(3, 14, str(0.00))

		self.grid.SetCellValue(7, 0, "Totals:")
		
		for i in range(num_columns):
			self.grid.SetCellBackgroundColour(6, i, "#333333")
			self.grid.SetCellBackgroundColour(8, i, "#333333")

		self.grid.SetCellValue(5, 1, "# of shares to sell")
		self.grid.SetCellValue(5, 2, "% of shares to sell")
		self.grid.SetCellValue(5, 3, "Ticker")
		self.grid.SetCellValue(5, 4, "Syntax Check")
		self.grid.SetCellValue(5, 5, "Name")
		self.grid.SetCellValue(5, 6, "Sale Check")
		self.grid.SetCellValue(5, 7, "# of shares to sell")
		self.grid.SetCellValue(5, 8, "% of shares to sell")
		self.grid.SetCellValue(5, 9, "Total # of shares")
		self.grid.SetCellValue(5, 10, "Price")
		self.grid.SetCellValue(5, 11, "Sale Value")
		self.grid.SetCellValue(5, 12, "Commission loss ($10/trade)")
		self.grid.SetCellValue(5, 13, "FIFO Capital Gains")
		self.grid.SetCellValue(5, 14, "Adjusted Capital Gains (including carryovers)")
		self.grid.SetCellValue(5, 15, "Market Value")
		self.grid.SetCellValue(5, 16, "Unrealized Capital +/-")

		global PORTFOLIO_NAMES
		portfolio_num = 0

		row_count = default_rows
		col_count = 0
		for account in relevant_portfolios_list:
			try:
				throw_error = account.stock_list
				# intentionally throws an error if account hasn't been imported

				self.grid.SetCellValue(row_count, 0, PORTFOLIO_NAMES[portfolio_num])
				self.grid.SetCellBackgroundColour(row_count, 1, "white")
				self.grid.SetReadOnly(row_count, 1, True)
				self.grid.SetCellBackgroundColour(row_count, 2, "white")
				self.grid.SetReadOnly(row_count, 2, True)
				portfolio_num += 1
				row_count += 1

				for stock in account.stock_list:
					#if row_count == 0:
					#	self.screen_grid.SetColLabelValue(col_count, str(attribute))
					stock_data = return_stock_by_symbol(stock.symbol)

					self.grid.SetCellValue(row_count, 3, stock.symbol)
					try:
						self.grid.SetCellValue(row_count, 5, stock_data.Name)
					except Exception, exception:
						print line_number(), exception
					self.grid.SetCellValue(row_count, 9, stock.quantity)
					try:
						self.grid.SetCellValue(row_count, 10, stock_data.LastTradePriceOnly)
					except Exception, exception:
						print line_number(), exception
					self.grid.SetCellValue(row_count, 15, str(float(stock.quantity.replace(",","")) * float(stock_data.LastTradePriceOnly)))
					row_count += 1
			except Exception, exception:
				print line_number(), exception, "\nAn account appears to not be loaded with a .csv, but this isn't a problem."
		self.grid.AutoSizeColumns()
	def updateGrid(self, event):
		row = event.GetRow()
		column = event.GetCol()
		value = self.grid.GetCellValue(row, column)
		num_shares = self.grid.GetCellValue(row, 9)
		price = self.grid.GetCellValue(row, 10)
		if column == 1:
			try:
				number_of_shares_to_sell = int(value)
			except:
				self.setGridError(row)
			#print line_number(), "# of stocks to sell changed"
			self.grid.SetCellValue(row, 2, "")
			if num_shares >= number_of_shares_to_sell:
				self.grid.SetCellValue(row, 7, str(number_of_shares_to_sell))
				percent_of_total_holdings = round(100 * float(number_of_shares_to_sell)/float(num_shares))
				self.grid.SetCellValue(row, 8, "%d%%" % percent_of_total_holdings)
				if int(num_shares) == int(number_of_shares_to_sell):
					self.grid.SetCellValue(row, 6, "All")
					self.grid.SetCellTextColour(row, 6, "black")
				else:
					self.grid.SetCellValue(row, 6, "Some")
					self.grid.SetCellTextColour(row, 6, "black")
				sale_value = float(number_of_shares_to_sell) * float(price)
				self.grid.SetCellValue(row, 11, "$%.2f" % sale_value)

				percent_to_commission = 100 * 10/sale_value
				self.grid.SetCellValue(row, 12, "%.2f%%" % percent_to_commission)
			else:
				self.setGridError(row)

		if column == 2:
			if "%" in value:
				value = value.strip("%")
				try:
					value = float(value)/100
				except:
					self.setGridError(row)
			else:
				try:
					value = float(value)
				except:
					self.setGridError(row)
			percent_of_holdings_to_sell = value
			self.grid.SetCellValue(row, 1, "")
			if percent_of_holdings_to_sell <= 1:
				self.grid.SetCellValue(row, 8, "%d%%" % round(percent_of_holdings_to_sell * 100))

				number_of_shares_to_sell = int(math.floor( int(num_shares) * percent_of_holdings_to_sell ) )
				self.grid.SetCellValue(row, 7, str(number_of_shares_to_sell))

				if int(num_shares) == int(number_of_shares_to_sell):
					self.grid.SetCellValue(row, 6, "All")
					self.grid.SetCellTextColour(row, 6, "black")
				else:
					self.grid.SetCellValue(row, 6, "Some")
					self.grid.SetCellTextColour(row, 6, "black")
				sale_value = float(number_of_shares_to_sell) * float(price)
				self.grid.SetCellValue(row, 11, "$%.2f" % sale_value)

				percent_to_commission = 100 * 10/sale_value
				self.grid.SetCellValue(row, 12, "%.2f%%" % percent_to_commission)

			else:
				self.setGridError(row)
		self.saved_text.Hide()
		self.save_button.Show()
	def setGridError(self, row):
		self.grid.SetCellValue(row, 6, "Error")
		self.grid.SetCellTextColour(row, 6, "red")

		self.grid.SetCellValue(row, 7, "")
		self.grid.SetCellValue(row, 8, "")
		self.grid.SetCellValue(row, 11, "")
		self.grid.SetCellValue(row, 12, "")


class TradePage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		trade_page_text = wx.StaticText(self, -1, 
							 "Set up trades", 
							 (10,10)
							 )
		self.ticker_list = []

		add_ticker_text_entry = wx.TextCtrl(self, -1, "TICKER", pos=(210,8), size=(53, -1))
		add_ticker_button = wx.Button(self, label="Add Ticker", pos=(110,5), size=(-1,-1))
		add_ticker_button.Bind(wx.EVT_BUTTON, self.addTicker, add_ticker_button)

	def addTicker(self, event):
		pass

class PortfolioPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		####
		portfolio_page_panel = wx.Panel(self, -1, pos=(0,5), size=( wx.EXPAND, wx.EXPAND))

		portfolio_account_notebook = wx.Notebook(portfolio_page_panel)
		
		global DATA_ABOUT_PORTFOLIOS
		portfolios_that_already_exist = DATA_ABOUT_PORTFOLIOS[1]
		global NUMBER_OF_PORTFOLIOS		
		portfolio_names = ["Primary", "Secondary", "Tertiary"]

		if not portfolios_that_already_exist:
			new_portfolio_name_list = []
			for i in range(NUMBER_OF_PORTFOLIOS):
				#print line_number(), i
				portfolio_name = None
				if NUMBER_OF_PORTFOLIOS < 10:
					portfolio_name = "Portfolio %d" % (i+1)
				else:
					portfolio_name = "%dth" % (i+1)
				if i in range(len(portfolio_names)):
					portfolio_name = portfolio_names[i]
				portfolio_account = PortfolioAccountTab(portfolio_account_notebook, (i+1))
				portfolio_account_notebook.AddPage(portfolio_account, portfolio_name)

				new_portfolio_name_list.append(portfolio_name)

				DATA_ABOUT_PORTFOLIOS[1] = new_portfolio_name_list
				
				with open('portfolios.pk', 'wb') as output:
					pickle.dump(DATA_ABOUT_PORTFOLIOS, output, pickle.HIGHEST_PROTOCOL)
		else:
			need_to_save = False
			for i in range(NUMBER_OF_PORTFOLIOS):
				#print line_number(), i
				try:
					portfolio_name = portfolios_that_already_exist[i]
				except Exception, exception:
					print line_number(), exception
					if i < 3:
						number_words = ["Primary", "Secondary", "Tertiary"]
						portfolio_name = number_words[i]
					else:
						portfolio_name = "Portfolio %d" % (i+1)
					portfolios_that_already_exist.append(portfolio_name)
					need_to_save = True

				portfolio_account = PortfolioAccountTab(portfolio_account_notebook, (i+1))
				portfolio_account_notebook.AddPage(portfolio_account, portfolio_name)
			if need_to_save == True:

				DATA_ABOUT_PORTFOLIOS[1] = portfolios_that_already_exist
				
				with open('portfolios.pk', 'wb') as output:
					pickle.dump(DATA_ABOUT_PORTFOLIOS, output, pickle.HIGHEST_PROTOCOL)


		if not portfolios_that_already_exist:
			DATA_ABOUT_PORTFOLIOS[1] = new_portfolio_name_list
			with open('portfolios.pk', 'wb') as output:
				pickle.dump(DATA_ABOUT_PORTFOLIOS, output, pickle.HIGHEST_PROTOCOL)
		
		sizer2 = wx.BoxSizer()
		sizer2.Add(portfolio_account_notebook, 1, wx.EXPAND)
		self.SetSizer(sizer2)		
		####
class PortfolioAccountTab(Tab):
	def __init__(self, parent, tab_number):
		tab_panel = wx.Panel.__init__(self, parent, tab_number)
		
		self.portfolio_id = tab_number
		#print line_number(), self.portfolio_id
		try:
			portfolio_file = open('portfolio_%d.pk' % self.portfolio_id, 'rb')
		except Exception, e:
			print line_number(), e
			portfolio_file = open('portfolio_%d.pk' % self.portfolio_id, 'wb')
			new_portfolio_entry = []
			with open('portfolio_%d.pk' % self.portfolio_id, 'wb') as output:
				pickle.dump(new_portfolio_entry, output, pickle.HIGHEST_PROTOCOL)
			portfolio_file = open('portfolio_%d.pk' % self.portfolio_id, 'rb')
		self.portfolio_data = pickle.load(portfolio_file)
		portfolio_file.close()

		global PORTFOLIO_OBJECTS_LIST
		try:
			self.account_obj = PORTFOLIO_OBJECTS_LIST[(int(self.portfolio_id) - 1)]
		except Exception, e:
			print line_number(), e
			try:
				portfolio_account_obj_file = open('portfolio_%d_data.pk' % self.portfolio_id, 'rb')
				self.account_obj = pickle.load(portfolio_account_obj_file)
				PORTFOLIO_OBJECTS_LIST[(int(self.portfolio_id) - 1)] = self.account_obj
				portfolio_account_obj_file.close()
			except Exception, e:
				print line_number(), e
				self.account_obj = None
			# 	portfolio_account_obj_file = open('portfolio_%d_data.pk' % self.portfolio_id, 'wb')
			# 	portfolio_account_obj = []
			# 	with open('portfolio_%d_data.pk' % self.portfolio_id, 'wb') as output:
			# 		pickle.dump(portfolio_account_obj, output, pickle.HIGHEST_PROTOCOL)
			# 	portfolio_account_obj_file = open('portfolio_%d_data.pk' % self.portfolio_id, 'rb')
			# # Why does this error!!!
			

	

		trade_page_text = wx.StaticText(self, -1, 
							 "Your portfolio", 
							 (5,5)
							 )

		add_button = wx.Button(self, label="Add account (Schwab positions .csv)", pos=(100,0), size=(-1,-1))
		add_button.Bind(wx.EVT_BUTTON, self.addAccountCSV, add_button) 

		clear_button = wx.Button(self, label="Clear this portfolio", pos=(830,0), size=(-1,-1))
		clear_button.Bind(wx.EVT_BUTTON, self.confirmDeleteAccount, clear_button) 

		rename_button = wx.Button(self, label="Rename this portfolio", pos=(355,0), size=(-1,-1))
		rename_button.Bind(wx.EVT_BUTTON, self.changeTabName, rename_button) 

		change_number_of_portfolios_button = wx.Button(self, label="Change number of portfolios", pos=(518,0), size=(-1,-1))
		change_number_of_portfolios_button.Bind(wx.EVT_BUTTON, self.changeNumberOfPortfolios, change_number_of_portfolios_button) 

		print_portfolio_data_button = wx.Button(self, label="p", pos=(730,0), size=(-1,-1))
		print_portfolio_data_button.Bind(wx.EVT_BUTTON, self.printData, print_portfolio_data_button) 

		self.current_account_spreadsheet = AccountDataGrid(self, -1, size=(980,637), pos=(0,50))
		self.spreadSheetFill(self.current_account_spreadsheet, self.portfolio_data)
	def printData(self, event):
		if self.account_obj:
			print line_number(),"cash:", self.account_obj.availble_cash
			for account_attribute in dir(self.account_obj):
				if not account_attribute.startswith("_"):
					print line_number(),account_attribute, ":"
					try:
						for stock_attribute in dir(getattr(self.account_obj, account_attribute)):
							if not stock_attribute.startswith("_"):
								print line_number(),stock_attribute, getattr(getattr(self.account_obj, account_attribute), stock_attribute)
					except Exception, exception:
						print line_number(),exception
	def changeNumberOfPortfolios(self, event):
		global NUMBER_OF_PORTFOLIOS
		num_of_portfolios_popup = wx.NumberEntryDialog(None,
									  "What would you like to call this portfolio?", 
									  "Rename tab",
									  "Caption", 
									  NUMBER_OF_PORTFOLIOS,
									  0,
									  10
									  )
		if num_of_portfolios_popup.ShowModal() != wx.ID_OK:
			return

		new_number_of_portfolios = num_of_portfolios_popup.GetValue()
		num_of_portfolios_popup.Destroy()

		NUMBER_OF_PORTFOLIOS = new_number_of_portfolios
		DATA_ABOUT_PORTFOLIOS[0] = new_number_of_portfolios
		with open('portfolios.pk', 'wb') as output:
			pickle.dump(DATA_ABOUT_PORTFOLIOS, output, pickle.HIGHEST_PROTOCOL)
		confirm = wx.MessageDialog(self,
								 "The number of portfolios has changed. The change will be applied the next time you launch this program.",
								 'Restart Required',
								 style = wx.ICON_EXCLAMATION
								 )
		confirm.ShowModal()
		confirm.Destroy()
	def spreadSheetFill(self, spreadsheet, account_data):
		self.current_account_spreadsheet.Destroy()

		num_rows = len(account_data)
		columns = 0
		for row in account_data:
			num_cells = 0
			for cell in row:
				num_cells += 1
			if num_cells > columns:
				columns = num_cells
		num_columns = columns
		spreadsheet = AccountDataGrid(self, -1, size=(980,637), pos=(0,50))
		spreadsheet.CreateGrid(num_rows, num_columns)
		spreadsheet.EnableEditing(False)

		row_count = 0
		col_count = 0
		for row in account_data:
			for cell in row:
				#if not attribute.startswith('_'):
				if row_count == 0:
					pass
				elif row_count == 1:
					spreadsheet.SetColLabelValue(col_count, str(cell))
				else:
					try:
						spreadsheet.SetCellValue(row_count - 2, col_count, str(cell))
					except:
						pass
				col_count += 1
			row_count += 1
			col_count = 0
		spreadsheet.AutoSizeColumns()
		self.current_account_spreadsheet = spreadsheet
	def addAccountCSV(self, event):
		'''append a csv to current ticker list'''
		self.dirname = ''
		dialog = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.csv", wx.OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			self.filename = dialog.GetFilename()
			self.dirname = dialog.GetDirectory()
			
			new_account_file = open(os.path.join(self.dirname, self.filename), 'rb')
			new_account_file_data = self.importSchwabCSV(new_account_file)
			self.portfolio_data = new_account_file_data
			new_account_file.close()

			with open('portfolio_%d.pk' % self.portfolio_id, 'wb') as output:
				pickle.dump(self.portfolio_data, output, pickle.HIGHEST_PROTOCOL)

			new_account_stock_list = []
			cash = "This should be changed"
			count = 0
			for row in self.portfolio_data:
				print line_number(),count
				if count <= 1:
					count += 1
					continue
				try:
					if row[0] and row[11]:
						if str(row[11]) == "Cash & Money Market":
							cash = row[5]
							print line_number(),'cash'
						elif str(row[11]) == "Equity":
							# format: ticker(0), name(1), quantity(2), price(3), change(4), market value(5), day change$(6), day change%(7), reinvest dividends?(8), capital gain(9), percent of account(10), security type(11)
							# HeldStock.__init__(self, symbol, quantity, security_type)
							stock_to_add = HeldStock(row[0], row[2], row[11])
							new_account_stock_list.append(stock_to_add)
							print line_number(),"stock"
				except Exception, exception:
					print line_number(),exception
					print line_number(),row
				count += 1
			if cash == "This should be changed":
				logging.error('Formatting error in CSV import')
			# Account.__init__(self, cash, stock_list)
			self.account_obj = Account(self.portfolio_id, cash, new_account_stock_list)
			with open('portfolio_%d_data.pk' % self.portfolio_id, 'wb') as output:
				pickle.dump(self.account_obj, output, pickle.HIGHEST_PROTOCOL)
			self.spreadSheetFill(self.current_account_spreadsheet, self.portfolio_data)
			PORTFOLIO_OBJECTS_LIST[(int(self.portfolio_id) - 1)] = self.account_obj
		dialog.Destroy()
	def importSchwabCSV(self, csv_file):
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
	def changeTabName(self, event):
		old_name = self.GetLabel()
		rename_popup = wx.TextEntryDialog(None,
									  "What would you like to call this portfolio?", 
									  "Rename tab", 
									  str(self.GetLabel())
									  )
		rename_popup.ShowModal()
		new_name = str(rename_popup.GetValue())
		rename_popup.Destroy()

		global DATA_ABOUT_PORTFOLIOS
		portfolio_name_list = DATA_ABOUT_PORTFOLIOS[1]
		new_portfolio_names = []
		if new_name != old_name:
			if new_name not in portfolio_name_list:
				for i in portfolio_name_list:
					if i == old_name:
						new_portfolio_names.append(new_name)
					else:
						new_portfolio_names.append(i)
				DATA_ABOUT_PORTFOLIOS[1] = new_portfolio_names
				with open('portfolios.pk', 'wb') as output:
					pickle.dump(DATA_ABOUT_PORTFOLIOS, output, pickle.HIGHEST_PROTOCOL)
				print line_number(),DATA_ABOUT_PORTFOLIOS
				confirm = wx.MessageDialog(self,
										 "This portfolio's name has been changed. The change will be applied the next time you launch this program.",
										 'Restart Required',
										 style = wx.ICON_EXCLAMATION
										 )
				confirm.ShowModal()
				confirm.Destroy()

			else:
				error = wx.MessageDialog(self,
										 'Each portfolio must have a unique name.',
										 'Name Error',
										 style = wx.ICON_ERROR
										 )
				error.ShowModal()
				error.Destroy()
	def confirmDeleteAccount(self, event):
		confirm = wx.MessageDialog(None, 
								   "You are about to delete your current account data. Are you sure you want to delete this data?", 
								   'Delete Portfolio Data?', 
								   wx.YES_NO
								   )
		confirm.SetYesNoLabels(("&Delete"), ("&Cancel"))
		yesNoAnswer = confirm.ShowModal()
		confirm.Destroy()

		if yesNoAnswer == wx.ID_YES:
			self.deleteAccountList()

	def deleteAccountList(self):
		'''delete account'''
		self.portfolio_data = []
		# opening the file with w+ mode truncates the file
		with open('portfolio_%d.pk' % self.portfolio_id, 'wb') as output:
			pickle.dump(self.portfolio_data, output, pickle.HIGHEST_PROTOCOL)
		self.current_account_spreadsheet.Destroy()
		self.current_account_spreadsheet = AccountDataGrid(self, -1, size=(980,637), pos=(0,50))
		self.spreadSheetFill(self.current_account_spreadsheet, self.portfolio_data)
		self.account_obj = None
		PORTFOLIO_OBJECTS_LIST[(int(self.portfolio_id) - 1)] = self.account_obj

####################### Screening functions #######################
def screen_pe_less_than_10():
	global GLOBAL_STOCK_LIST
	screen = []
	for stock in GLOBAL_STOCK_LIST:
		try:
			if stock.PERatio:
				if float(stock.PERatio) < 10:
					screen.append(stock)
		except Exception, e:
			print line_number(),e
	return screen
####################### Pickle functions #######################
def saveStocks(obj, stock_list):
	with open(filename, 'wb') as output:
		pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

#saveobject(company1, r'c:\mypythonobject')
####################### Utility functions #######################
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
def remove_unsafe_chars_from_tags(tag_list):
	escaped_list = []
	for tag in tag_list:
		escaped_string = []
		for char in tag:
			if char in URL_SAFE_CHARS:
				escaped_string.append(char)
			else:
				if char == " ":
					escaped_string.append("_")
		tag = "".join(escaped_string)
		escaped_list.append(tag)
	new_tag_list = escaped_list
	return new_tag_list 
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
		logging.error("something wrong with time_from_epoch function")
		time_str = None
	return time_str	
def return_stock_by_symbol(ticker_symbol):
	global GLOBAL_STOCK_LIST
	for stock in GLOBAL_STOCK_LIST:
		if stock.symbol == ticker_symbol:
			return stock
	#if the function does not return a stock
	return None



app = None
def main():
	global app
	app = wx.App()
	MainFrame(size=(1020,800), #style = wx.MINIMIZE_BOX | wx.CLOSE_BOX
			  ).Show()
	app.MainLoop()
main()