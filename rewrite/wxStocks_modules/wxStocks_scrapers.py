import config, urllib2, inspect, threading, time, logging, sys, ast, datetime
import pprint as pp

from modules.pyql import pyql

import wxStocks_utilities as utils
import wxStocks_db_functions as db

def line_number():
	"""Returns the current line number in our program."""
	line_number = inspect.currentframe().f_back.f_lineno
	line_number_string = "Line %d:" % line_number
	return line_number_string

def download_ticker_symbols(): # from nasdaq.com
	headers = {
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
				'Accept-Encoding': 'none',
				'Accept-Language': 'en-US,en;q=0.8',
				'Connection': 'keep-alive',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
				}

	exchanges = config.STOCK_EXCHANGE_LIST
	exchange_data = []

	for exchange in exchanges:
		# Retrieve the webpage as a string
		response = urllib2.Request("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=%s&render=download" % exchange, headers=headers)
		
		try:
			page = urllib2.urlopen(response)
		except urllib2.HTTPError, e:
			print e.fp.read()

		content = page.read()
		content = content.splitlines()

		ticker_data_list = []
		for line in content:
			dummy_list = line.split('"')
			parsed_dummy_list = []
			for datum in dummy_list:
				if datum == ",":
					pass
				elif not datum:
					pass
				else:
					parsed_dummy_list.append(datum)

			ticker_data_list.append(parsed_dummy_list)

		# Remove first unit of data which is:
		# ['Symbol',
		#  'Name',
		#  'LastSale',
		#  'MarketCap',
		#  'ADR TSO',
		#  'IPOyear',
		#  'Sector',
		#  'industry',
		#  'Summary Quote']
		ticker_data_list = ticker_data_list[1:]

		exchange_data = exchange_data + ticker_data_list

		#for ticker_data in ticker_data_list:
		#	print ""
		#	pp.pprint(ticker_data)

	exchange_data.sort(key = lambda x: x[0])

	print line_number(), "Returning ticker download data:", len(exchange_data), "number of items"
	return exchange_data


def prepareYqlScrape(): # from finance.yahoo.com
	"returns [chunk_list, percent_of_full_scrape_done, number_of_tickers_to_scrape"
	chunk_length = config.SCRAPE_CHUNK_LENGTH # 145 appears to be the longest url string i can query with, but 50 seems more stable
	yql_ticker_list = []

	relevant_tickers = []
	for ticker in config.GLOBAL_STOCK_DICT:
		if config.GLOBAL_STOCK_DICT.get(ticker):
			if config.GLOBAL_STOCK_DICT[ticker].ticker_relevant:
				if "^" in ticker or "/" in ticker:
					#print "this ticker:"
					#print ticker
					#print config.GLOBAL_STOCK_DICT[ticker].yql_ticker
					#print ""
					relevant_tickers.append(config.GLOBAL_STOCK_DICT[ticker].yql_ticker)
				else:
					relevant_tickers.append(ticker)

	# Check if stock has already been recently update (this is important to prevent overscraping yahoo)
	for ticker in relevant_tickers:
		stock = utils.return_stock_by_yql_symbol(ticker) # initially we need only return stocks by ticker, later we will need to use the yql specific symbols
		if stock:
			time_since_update = float(time.time()) - stock.last_yql_basic_scrape_update
			if int(time_since_update) < int(config.TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE):
				print line_number()
				logging.warning("Will not add %s to update list, updated too recently, waste of yql query" % str(stock.symbol))
				continue
		if stock:
			yql_ticker_list.append(stock.yql_ticker)
		else:
			print line_number(), "Something is off with a stock, it's not returning properly"
			yql_ticker_list.append(ticker)
	num_of_tickers = len(yql_ticker_list)
	sleep_time = config.SCRAPE_SLEEP_TIME

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

	# Now set up the last chunk, which will be smaller, and unique.
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
		ticker_chunk = yql_ticker_list[slice_start:slice_end]
		chunk_list.append(ticker_chunk)
		count += 1
		#print line_number(), count
		slice_start += chunk_length
		slice_end += chunk_length

	#print line_number(), "got this far"
	
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
	print line_number(), "Number of tickers to scrape:", number_of_tickers_in_chunk_list
	number_of_tickers_previously_updated = len(relevant_tickers) - number_of_tickers_in_chunk_list
	print line_number(), number_of_tickers_previously_updated
	total_number_of_tickers_done = number_of_tickers_previously_updated
	percent_of_full_scrape_done = round(100 * float(total_number_of_tickers_done) / float(len(relevant_tickers)) )

	print line_number(), str(percent_of_full_scrape_done) + "%%" +" already done" 

	return [chunk_list, percent_of_full_scrape_done, number_of_tickers_in_chunk_list]



def executeYqlScrapePartOne(ticker_chunk_list, position_of_this_chunk):
	sleep_time = config.SCRAPE_SLEEP_TIME
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
			return data
			
def executeYqlScrapePartTwo(ticker_chunk_list, position_of_this_chunk, successful_pyql_data): # This is the big one
	sleep_time = config.SCRAPE_SLEEP_TIME
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
				new_stock = utils.return_stock_by_yql_symbol(value) # must use yql return here for ticker that include a "^" or "/", a format yahoo finance does not use.
				if not new_stock:
					# this should not, ever, happen:
					print line_number()
					logging.error("New Stock should not need to be created here, but we are going to create it anyway, there is a problem with the yql ticker %s" % value)
					new_stock = db.create_new_Stock_if_it_doesnt_exist(value)
				else:
					new_stock.updated = datetime.datetime.now()
					new_stock.epoch = float(time.time())
		for key, value in stock.iteritems():
			# Here we hijack the power of the python object structure
			# This adds the attribute of every possible attribute that can be passed
			if key == "symbol":
				continue # already have this, don't need it again, in fact, the yql symbol is different for many terms
			setattr(new_stock, 
					str(key) + "_yf", 
					value
					)
		print "Success, saving %s: Data 1 (Yahoo Quote)" % new_stock.yql_ticker
	#save
	db.save_GLOBAL_STOCK_DICT()

	for stock2 in data2:
		for key, value in stock2.iteritems():
			if key == "symbol":
				new_stock = utils.return_stock_by_yql_symbol(value)
				if not new_stock:
					# this should not, ever, happen:
					print line_number()
					logging.error("New Stock should not need to be created here, but we are going to create it anyway, there is a problem with the yql ticker %s" % value)
					new_stock = db.create_new_Stock_if_it_doesnt_exist(value)
		for key, value in stock2.iteritems():
			if key == "symbol":
				continue # already have this, don't need it again, in fact, the yql symbol is different for many terms
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
							term = utils.strip_string_whitespace(term)
							key_term = key_str + "_" + term
							key_term = utils.strip_string_whitespace(key_term)
							if "p_52_WeekHigh" in key_term:
								date = key_term[14:]
								setattr(new_stock, 
									"p_52_WeekHigh_Date" + "_yf", 
									date
									)
								key_str = "p_52_WeekHigh"
							elif "p_52_WeekLow" in key_term:
								date = key_term[13:]
								setattr(new_stock, 
									"p_52_WeekLow_Date" + "_yf", 
									date
									)
								key_str = "p_52_WeekLow"
							elif "ForwardPE_fye" in key_term:
								date = key_term[14:]
								setattr(new_stock, 
									"ForwardPE_fiscal_y_end_Date" + "_yf", 
									date
									)
								key_str = "ForwardPE"
							elif "EnterpriseValue_" in key_term:
								date = key_term[16:]
								setattr(new_stock, 
									"EnterpriseValue_Date" + "_yf", 
									date
									)
								key_str = "EnterpriseValue"
							elif "TrailingPE_ttm_" in key_term:
								date = key_term[15:] # will be of form  TrailingPE_ttm__intraday 
								setattr(new_stock, 
									"TrailingPE_ttm_Date" + "_yf", 
									date
									)
								key_str = "TrailingPE_ttm"
							elif "SharesShort_as_of" in key_term:
								date = key_term[18:] # will be of form SharesShort_as_of_Jul_15__2013 
								setattr(new_stock, 
									"SharesShort_as_of_Date" + "_yf", 
									date
									)
								key_str = "SharesShort"
							elif "ShortRatio_as_of" in key_term:
								date = key_term[16:] # will be of form SharesShort_as_of_Jul_15__2013 
								setattr(new_stock, 
									"ShortRatio_as_of_Date" + "_yf", 
									date
									)
								key_str = "ShortRatio"
							elif "ShortPercentageofFloat_as_of" in key_term:
								date = key_term[29:]
								setattr(new_stock, 
									"ShortPercentageofFloat_as_of_Date" + "_yf", 
									date
									)
								key_str = "ShortPercentageofFloat"
							else:
								key_str = str(key + "_" + term)
							content = str(i["content"])
							setattr(new_stock, 
									key_str + "_yf", 
									content
									)
						except Exception, e:
							logging.warning(repr(i))
							logging.warning("complex list method did not work")
							logging.exception(e)
							setattr(new_stock, 
									str(key) + "_yf", 
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
						term = utils.strip_string_whitespace(term)
						key_term = key_str + "_" + term
						key_term = utils.strip_string_whitespace(key_term)
						if "p_52_WeekHigh" in key_term:
							date = key_term[14:]
							setattr(new_stock, 
								"p_52_WeekHigh_Date" + "_yf", 
								date
								)
							key_str = "p_52_WeekHigh"
						elif "p_52_WeekLow" in key_term:
							date = key_term[13:]
							setattr(new_stock, 
								"p_52_WeekLow_Date" + "_yf", 
								date
								)
							key_str = "p_52_WeekLow"
						elif "ForwardPE_fye" in key_term:
							date = key_term[14:]
							setattr(new_stock, 
								"ForwardPE_fiscal_y_end_Date" + "_yf", 
								date
								)
							key_str = "ForwardPE"
						elif "EnterpriseValue_" in key_term:
							date = key_term[16:]
							setattr(new_stock, 
								"EnterpriseValue_Date" + "_yf", 
								date
								)
							key_str = "EnterpriseValue"
						elif "TrailingPE_ttm_" in key_term:
							date = key_term[15:] # will be of form  TrailingPE_ttm__intraday 
							setattr(new_stock, 
								"TrailingPE_ttm_Date" + "_yf", 
								date
								)
							key_str = "TrailingPE_ttm"
						elif "SharesShort_as_of" in key_term:
							date = key_term[18:] # will be of form SharesShort_as_of_Jul_15__2013 
							setattr(new_stock, 
								"SharesShort_as_of_Date" + "_yf", 
								date
								)
							key_str = "SharesShort"
						elif "ShortRatio_as_of" in key_term:
							date = key_term[16:] # will be of form SharesShort_as_of_Jul_15__2013 
							setattr(new_stock, 
								"ShortRatio_as_of_Date" + "_yf", 
								date
								)
							key_str = "ShortRatio"
						elif "ShortPercentageofFloat_as_of" in key_term:
							date = key_term[29:]
							setattr(new_stock, 
								"ShortPercentageofFloat_as_of_Date" + "_yf", 
								date
								)
							key_str = "ShortPercentageofFloat"
						else:
							key_str = str(key + "_" + term)
						content = str(y["content"])
						setattr(new_stock, 
								key_str + "_yf", 
								content
								)
					except Exception, e:
						logging.warning("complex dict method did not work")
						logging.exception(e)
						setattr(new_stock, 
								str(key) + "_yf", 
								x
								)
				else:
					key_str = str(key)
					setattr(new_stock, 
						key_str + "_yf", 
						x
						)
			else:
				key_str = str(key)
				setattr(new_stock, 
						key_str + "_yf", 
						value
						)
		new_stock.last_yql_basic_scrape_update = float(time.time())
		print line_number(), "Success, saving %s: Data 2 (Yahoo Key Statistics)" % new_stock.yql_ticker

	#save again
	db.save_GLOBAL_STOCK_DICT()

	logging.warning("This stock chunk finished successfully.")
	#self.progress_bar.SetValue((float(slice_end)/float(num_of_tickers)) * 100)
	#app.Yield()





#end of line