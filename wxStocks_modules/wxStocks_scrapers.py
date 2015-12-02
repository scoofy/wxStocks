import config, urllib2, inspect, threading, time, logging, sys, ast, datetime
import pprint as pp


from modules.pyql import pyql
from modules.BeautifulSoup import BeautifulSoup

import wxStocks_utilities as utils
import wxStocks_db_functions as db

def line_number():
    """Returns the current line number in our program."""
    return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)


# something is clearly broken with additional data scrapes
def scrape_all_additional_data_prep(list_of_ticker_symbols): # Everything except basic yql and nasdaq
    function_list = [
        yf_analyst_estimates_scrape,
        ms_key_ratios_scrape,
        yf_annual_balance_sheet_scrape,
        ms_annual_balance_sheet_scrape,
        yf_annual_income_statement_scrape,
        ms_annual_income_statement_scrape,
        yf_annual_cash_flow_scrape,
        ms_annual_cash_flow_scrape,
    ] # best to stagger these to maximize scrape gaps, but i should automate this somehow.

    scrape_all_additional_data_execute(list_of_ticker_symbols, function_list)

def scrape_all_additional_data_execute(list_of_ticker_symbols, list_of_functions):
    ticker_list = list_of_ticker_symbols
    function_list = list_of_functions

    one_day = (60 * 60 * 24)
    yesterdays_epoch = float(time.time()) - one_day

    if ticker_list:
        print line_number(), "updating:", ticker_list
    else:
        return

    number_of_tickers = len(ticker_list)
    number_of_functions = len(function_list)
    scrape_sleep_time = config.ADDITIONAL_DATA_SCRAPE_SLEEP_TIME

    count = 1
    # Here, best to scrape all data for one stock, switching functions to slow posibility of overscraping
    for ticker_position in range(number_of_tickers):
        for function_position in range(number_of_functions):
            count_adjusted_for_sleep_time = (count * scrape_sleep_time) - (scrape_sleep_time - 1)
            timer = threading.Timer(count_adjusted_for_sleep_time, function_list[function_position], [ticker_list[ticker_position]])
            timer.start()
            count += 1

#################### Nasdaq Ticker Symbol Scraper ##############################################
# no longer used
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
            print line_number(), e.fp.read()

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
        #   print ""
        #   pp.pprint(ticker_data)

    exchange_data.sort(key = lambda x: x[0])

    print line_number(), "Returning ticker download data:", len(exchange_data), "number of items"
    return exchange_data
# end no longer used

def nasdaq_full_ticker_list_downloader() : # from nasdaq.com
    ''' returns list of the form [nasdaq_ticker, firm_name, exchange, is_etf_bool]'''

    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,/*;q=0.8'
    }

    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt"


    nasdaq_tickers = return_webpage(url, headers, delay=0)

    big_list = nasdaq_tickers.split("\r\n")

    ticker_meta_list = [x.split("|") for x in big_list]

    ticker_titles = ticker_meta_list[0]
    ticker_data_list = ticker_meta_list[1:]

    ticker_data_list = ticker_data_list[:-2]


    return_list = []
    for data in ticker_data_list:
        try:
            ticker = data[1].replace("$", "^")
        except:
            print line_number(), data
        firm_name = data[2]

        exchange = None
        exchange_letter = data[3]
        if exchange_letter == "Q":
            exchange = "NASDAQ"
        elif exchange_letter == "N":
            exchange = "NYSE"
        elif exchange_letter == "Z":
            exchange = "BATS"
        elif exchange_letter == "P":
            exchange = "NYSE"
        elif exchange_letter == "A":
            exchange = "NYSEmkt"
        else:
            print line_number(), data

        etf_bool = None
        etf_letter = data[5]
        if etf_letter == "N":
            etf_bool = False
        elif etf_letter == "Y":
            etf_bool = True
        elif etf_letter == " ":
            pass
        else:
            #print ticker_titles
            print line_number(), data, ":", data[5]

        cqs_symbol = data[9]
        nasdaq_symbol = data[10]

        data_to_return = [ticker, firm_name, exchange, etf_bool]
        return_list.append(data_to_return)

    return return_list

# suggestion from Soncrates
def nasdaq_stock_csv_url_and_headers_generator(exchanges=config.STOCK_EXCHANGE_LIST) : # from nasdaq.com
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,/*;q=0.8'
    }
    for exchange in exchanges :
        config.CURRENT_EXCHANGE_FOR_NASDAQ_SCRAPE = exchange.upper()
        yield "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=%s&render=download" % exchange, headers
    config.CURRENT_EXCHANGE_FOR_NASDAQ_SCRAPE = None

def return_webpage(url, headers, delay=15) : # I set the delay here at 15
    print line_number(), 'Scraping nasdaq.com'
    if delay:
        print line_number(), "Sleeping for %d seconds to prevent potential blocking of your ip address. You may change this as a keyword argument of this function." % delay
    time.sleep(delay)
    response = urllib2.Request(url, headers=headers)
    page = urllib2.urlopen(response)
    return page.read()

def nasdaq_csv_stock_data_parsing_generator(csv_file):
    rows_list = csv_file.splitlines()
    for row_num in range(len(rows_list)):
        row_data = rows_list[row_num].decode('utf-8').split('",')
        if row_num == 0:
            dict_list = row_data
            if not dict_list:
                print line_number(), "Error: no description row exists for nasdaq data download"
                return
            else:
                if not dict_list[-1]:
                    # here i will remove the empty string at the end of the typical list i get
                    # this is the default list i get:

                    #[u'"Symbol"',
                    # u'"Name"',
                    # u'"LastSale"',
                    # u'"MarketCap"',
                    # u'"IPOyear"',
                    # u'"Sector"',
                    # u'"industry"',
                    # u'"Summary Quote"',
                    # u'']
                    dict_list.pop()
                else:
                    print line_number(), dict_list[-1]
                    sys.exit()
            continue
        dict_to_return = {}
        if not row_data:
            continue
        else:
            for theoretical_csv_column_number in range(len(dict_list)):
                if row_data[theoretical_csv_column_number] not in [None, u""]:
                    #print line_number()
                    #pp.pprint(row_data[theoretical_csv_column_number])
                    dict_to_return[str(dict_list[theoretical_csv_column_number]).replace('"', "").replace(" ","_")] = str(row_data[theoretical_csv_column_number]).replace('"', "")
        if dict_to_return:
            yield dict_to_return
# suggestion from Soncrates
def convert_nasdaq_csv_to_stock_objects():
    for url, headers in nasdaq_stock_csv_url_and_headers_generator():
        if len(config.STOCK_EXCHANGE_LIST) < 5: # it should be
            nasdaq_csv = return_webpage(url, headers, delay=0)
        else: # incase this program grows beyond my wildest dreams
            nasdaq_csv = return_webpage(url, headers)
        for stock_dict in nasdaq_csv_stock_data_parsing_generator(nasdaq_csv):
            # stock_dict:
            # {
            # 'Sector': 'str',
            # 'LastSale': 'float',
            # 'Summary_Quote': 'ignore',
            # 'Name': 'str',
            # 'industry': 'str',
            # 'Symbol': 'str',
            # 'MarketCap': 'str',
            # 'IPOyear': 'n/a or int'
            # }
            # add ".Exchange" below
            if ("$" in stock_dict.get("Symbol")): # this is an "option chain" and we will ignore
                continue
            if ("/CL" in stock_dict.get("Symbol")): # this is a called option or warrant and we will ignore
                continue
            if ("/W" in stock_dict.get("Symbol")): # this is a warrant and we will ignore
                continue
            if " " in stock_dict.get("Symbol"):
                stock_dict["Symbol"] = stock_dict.get("Symbol").replace(" ", "")
            stock = None
            stock = db.create_new_Stock_if_it_doesnt_exist(stock_dict.get("Symbol"))
            stock.firm_name = stock_dict.get("Name")
            for attribute in stock_dict:
                if attribute not in ["Symbol", "Summary_Quote", "LastSale"]:
                    datum = stock_dict.get(attribute)
                    if datum:
                        db.set_Stock_attribute(stock, attribute, datum, "_na")
                elif attribute == "LastSale":
                    try:
                        datum = float(stock_dict.get(attribute))
                        db.set_Stock_attribute(stock, attribute, datum, "_na")
                    except:
                        db.set_Stock_attribute(stock, attribute, None, "_na")
            stock.Exchange_na = config.CURRENT_EXCHANGE_FOR_NASDAQ_SCRAPE
            stock.last_nasdaq_scrape_update = time.time()
#################### Yahoo Finance Scrapers "_yf" ##############################################
def scrape_loop_for_missing_portfolio_stocks(ticker_list = [], update_regardless_of_recent_updates = False):
    if config.SCRAPE_LOOP_QUEUE:
        ticker_list = config.SCRAPE_LOOP_QUEUE + ticker_list
    if not ticker_list:
        return
    if len(ticker_list) > config.SCRAPE_CHUNK_LENGTH:
        ticker_list, overflow = ticker_list[:config.SCRAPE_CHUNK_LENGTH], ticker_list[config.SCRAPE_CHUNK_LENGTH:]
        config.SCRAPE_LOOP_QUEUE = overflow

    if (float(time.time()) - float(config.SCRAPE_SLEEP_TIME) > float(config.SCRAPE_LOOP_STARTED)):
        config.SCRAPE_LOOP_STARTED = float(time.time())
        ticker_chunk_list_triple = prepareYqlScrape(ticker_list, update_regardless_of_recent_updates = update_regardless_of_recent_updates)
        chunk_list = ticker_chunk_list_triple[0]
        for i in range(len(chunk_list)):
            data = executeYqlScrapePartOne(chunk_list, i)
            executeYqlScrapePartTwo(chunk_list, i, data)
    else:
        sleep_time_left = float(time.time()) - config.SCRAPE_LOOP_STARTED
        time.sleep(sleep_time_left)
        scrape_loop_for_missing_portfolio_stocks(ticker_list = ticker_list)


def prepareYqlScrape(ticker_list = [], update_regardless_of_recent_updates = False): # from finance.yahoo.com
    "returns [chunk_list, percent_of_full_scrape_done, number_of_tickers_to_scrape"
    chunk_length = config.SCRAPE_CHUNK_LENGTH # 145 appears to be the longest url string i can query with, but 50 seems more stable
    yql_ticker_list = []

    relevant_tickers = []

    if not ticker_list: # added so you can update limited tickers
        for ticker in config.GLOBAL_STOCK_DICT:
            if config.GLOBAL_STOCK_DICT.get(ticker):
                #if config.GLOBAL_STOCK_DICT[ticker].ticker_relevant:
                #    if "^" in ticker or "/" in ticker:
                #        #print "this ticker:"
                #        #print ticker
                #        #print config.GLOBAL_STOCK_DICT[ticker].yql_ticker
                #        #print ""
                #        relevant_tickers.append(config.GLOBAL_STOCK_DICT[ticker].yql_ticker)
                #    else:
                #        relevant_tickers.append(ticker)
                relevant_tickers.append(ticker)
    else:
        for ticker in ticker_list:
            if config.GLOBAL_STOCK_DICT.get(ticker.upper()):
                if config.GLOBAL_STOCK_DICT[ticker].ticker_relevant:
                    #if "^" in ticker or "/" in ticker:
                    #    #print "this ticker:"
                    #    #print ticker
                    #    #print config.GLOBAL_STOCK_DICT[ticker].yql_ticker
                    #    #print ""
                    #    relevant_tickers.append(config.GLOBAL_STOCK_DICT[ticker].yql_ticker)
                    #else:
                    #    relevant_tickers.append(ticker)
                    relevant_tickers.append(ticker)
    # Check if stock has already been recently update (this is important to prevent overscraping yahoo)
    for ticker in sorted(relevant_tickers):
        stock = utils.return_stock_by_symbol(ticker) # initially we need only return stocks by ticker, later we will need to use the yql specific symbols
        if stock:
            time_since_update = float(time.time()) - stock.last_yql_basic_scrape_update
            if (int(time_since_update) < int(config.TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE)) and not update_regardless_of_recent_updates:
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
        print line_number()
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
        print line_number()
        logging.info('While loop #%d' % count)
        ticker_chunk = yql_ticker_list[slice_start:slice_end]
        chunk_list.append(ticker_chunk)
        count += 1
        #print line_number(), count
        slice_start += chunk_length
        slice_end += chunk_length

    #print line_number(), "got this far"

    #self.progress_dialog = wx.ProgressDialog('Scrape Progress',
    #                                   'The stocks are currently downloading',
    #                                   num_of_tickers,
    #                                   parent=self,
    #                                   style=wx.PD_CAN_ABORT|wx.PD_REMAINING_TIME
    #                                   )


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
    print line_number()
    print ticker_chunk
    if ticker_chunk:
        scrape_1_failed = False
        try:
            data = pyql.lookupQuote(ticker_chunk)
        except:
            print line_number()
            logging.warning("Scrape didn't work. Nothing scraped.")
            scrape_1_failed = True
        if scrape_1_failed:
            #time.sleep(sleep_time)
            return
        else:
            print line_number(), "Scrape 1 Success: mid-scrape sleep for %d seconds" % sleep_time
            return data
def executeYqlScrapePartTwo(ticker_chunk_list, position_of_this_chunk, successful_pyql_data): # This is the big one
    sleep_time = config.SCRAPE_SLEEP_TIME
    ticker_chunk = ticker_chunk_list[position_of_this_chunk]
    number_of_stocks_in_this_scrape = len(ticker_chunk)

    data = successful_pyql_data

    try:
        data2 = pyql.lookupKeyStats(ticker_chunk)
    except:
        print line_number()
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
            db.set_Stock_attribute(new_stock, str(key), value, "_yf")
        print line_number(), "Success, saving %s: Data 1 (Yahoo Quote)" % new_stock.yql_ticker
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
                            date = None
                            date_str = None
                            term = str(i["term"])
                            term = term.replace(" ", "_")
                            term = term.replace(",", "")
                            term = utils.strip_string_whitespace(term)
                            key_term = key_str + "_" + term
                            key_term = utils.strip_string_whitespace(key_term)
                            if "p_52_WeekHigh" in key_term:
                                date = key_term[14:]
                                date_str = "p_52_WeekHigh_Date"
                                key_str = "p_52_WeekHigh"
                            elif "p_52_WeekLow" in key_term:
                                date = key_term[13:]
                                date_str = "p_52_WeekLow_Date"
                                key_str = "p_52_WeekLow"
                            elif "ForwardPE_fye" in key_term:
                                date = key_term[14:]
                                date_str = "ForwardPE_fiscal_y_end_Date"
                                key_str = "ForwardPE"
                            elif "EnterpriseValue_" in key_term:
                                date = key_term[16:]
                                date_str = "EnterpriseValue_Date"
                                key_str = "EnterpriseValue"
                            elif "TrailingPE_ttm_" in key_term:
                                date = key_term[15:] # will be of form  TrailingPE_ttm__intraday
                                date_str = "TrailingPE_ttm_Date"
                                key_str = "TrailingPE_ttm"
                            elif "SharesShort_as_of" in key_term:
                                date = key_term[18:] # will be of form SharesShort_as_of_Jul_15__2013
                                date_str = "SharesShort_as_of_Date"
                                key_str = "SharesShort"
                            elif "ShortRatio_as_of" in key_term:
                                date = key_term[16:] # will be of form SharesShort_as_of_Jul_15__2013
                                date_str = "ShortRatio_as_of_Date"
                                key_str = "ShortRatio"
                            elif "ShortPercentageofFloat_as_of" in key_term:
                                date = key_term[29:]
                                date_str = "ShortPercentageofFloat_as_of_Date"
                                key_str = "ShortPercentageofFloat"
                            else:
                                date = None
                                date_str = None
                                key_str = str(key + "_" + term)
                            content = str(i["content"])
                            db.set_Stock_attribute(new_stock, key_str, content, "_yf")
                            if date_str:
                                db.set_Stock_attribute(new_stock, date_str, date, "_yf")
                        except Exception, e:
                            line_number()
                            logging.warning(repr(i))
                            logging.warning("complex list method did not work")
                            logging.exception(e)
                            db.set_Stock_attribute(new_stock, str(key), x, "_yf")

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
                        date = None
                        date_str = None
                        term = str(y["term"])
                        term = term.replace(" ", "_")
                        term = term.replace(",", "")
                        term = utils.strip_string_whitespace(term)
                        key_term = key_str + "_" + term
                        key_term = utils.strip_string_whitespace(key_term)
                        if "p_52_WeekHigh" in key_term:
                            date = key_term[14:]
                            date_str = "p_52_WeekHigh_Date"
                            key_str = "p_52_WeekHigh"
                        elif "p_52_WeekLow" in key_term:
                            date = key_term[13:]
                            date_str = "p_52_WeekLow_Date"
                            key_str = "p_52_WeekLow"
                        elif "ForwardPE_fye" in key_term:
                            date = key_term[14:]
                            date_str = "ForwardPE_fiscal_y_end_Date"
                            key_str = "ForwardPE"
                        elif "EnterpriseValue_" in key_term:
                            date = key_term[16:]
                            date_str = "EnterpriseValue_Date"
                            key_str = "EnterpriseValue"
                        elif "TrailingPE_ttm_" in key_term:
                            date = key_term[15:] # will be of form  TrailingPE_ttm__intraday
                            date_str = "TrailingPE_ttm_Date"
                            key_str = "TrailingPE_ttm"
                        elif "SharesShort_as_of" in key_term:
                            date = key_term[18:] # will be of form SharesShort_as_of_Jul_15__2013
                            date_str = "SharesShort_as_of_Date"
                            key_str = "SharesShort"
                        elif "ShortRatio_as_of" in key_term:
                            date = key_term[16:] # will be of form SharesShort_as_of_Jul_15__2013
                            date_str = "ShortRatio_as_of_Date"
                            key_str = "ShortRatio"
                        elif "ShortPercentageofFloat_as_of" in key_term:
                            date = key_term[29:]
                            date_str = "ShortPercentageofFloat_as_of_Date"
                            key_str = "ShortPercentageofFloat"
                        else:
                            key_str = str(key + "_" + term)
                        content = str(y["content"])
                        db.set_Stock_attribute(new_stock, key_str, content, "_yf")
                        if date_str:
                            db.set_Stock_attribute(new_stock, date_str, date, "_yf")
                    except Exception, e:
                        print line_number()
                        logging.warning("complex dict method did not work")
                        logging.exception(e)
                        db.set_Stock_attribute(new_stock, str(key), x, "_yf")
                else:
                    key_str = str(key)
                    db.set_Stock_attribute(new_stock, key_str, x, "_yf")

            else:
                key_str = str(key)
                db.set_Stock_attribute(new_stock, key_str, value, "_yf")

        new_stock.last_yql_basic_scrape_update = float(time.time())
        print line_number(), "Success, saving %s: Data 2 (Yahoo Key Statistics)" % new_stock.yql_ticker

    #save again
    db.save_GLOBAL_STOCK_DICT()

    print line_number(), "This stock chunk finished successfully."
    #self.progress_bar.SetValue((float(slice_end)/float(num_of_tickers)) * 100)
    #app.Yield()

def yqlQuickStockQuoteScrape(ticker_list): # len < 50
    if len(ticker_list) > 50:
        print line_number(), "too many tickers to scrape, using this method, please do a full scrape"
        return
    data = None
    try:
        data = pyql.lookupQuote(ticker_list)
    except:
        print line_number()
        logging.warning("Scrape didn't work. Nothing scraped.")

    if data:
        print line_number(), "Scrape Success"
    return data

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
            db.set_Stock_attribute(new_stock, str(key), value, "_yf")
        print line_number(), "Success, saving %s: Data (Yahoo Quote)" % new_stock.yql_ticker
    #save
    db.save_GLOBAL_STOCK_DICT()

# Stock Annual Data Scraping Functions
# ---- unfortunately after scraping many stocks, these scraping functions need to be overhauled
# ---- it seems that the data that is returned is not formatted properly for firms that are < 4 years old
# ---- I'll need to account for this disparity and rewrite the scrape functions with more precision.
## --- Much has been improved, but i still need to do a re-write it for single year data.
def yf_annual_cash_flow_scrape(ticker):
    print line_number(), "Starting: yf_annual_cash_flow_scrape for %s" % ticker
    stock = utils.return_stock_by_symbol(ticker)

    if not stock:
        print line_number(), "Error: stock %s does not exist" % ticker

    most_recent_update = stock.last_cash_flow_update_yf
    last_acceptable_update = float(time.time()) - config.TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE
    if  most_recent_update > last_acceptable_update:
        print line_number(), "YF Cash flow data for %s is up to date." % ticker
        return


    soup = BeautifulSoup(urllib2.urlopen('http://finance.yahoo.com/q/cf?s=%s&annual' % ticker), convertEntities=BeautifulSoup.HTML_ENTITIES)
    factor = 0
    thousands = soup.body.findAll(text= "All numbers in thousands")
    if thousands:
        factor = 1000

    if not factor:
        print line_number(), "Error: no factor... in need of review"

    table = soup.find("table", { "class" : "yfnc_tabledata1" })

    data_list = []

    find_all_data_in_table(table, "td", data_list, factor)
    find_all_data_in_table(table, "strong", data_list, factor)

    create_or_update_yf_StockAnnualData(ticker, data_list, "Cash_Flow")

    cash_flow_layout =  ['''
                    0   Period Ending
                    1   Period Ending
                    2   -
                    3   -
                    4   -
                    5   Operating Activities, Cash Flows Provided By or Used In
                    6   Depreciation
                    7   -
                    8   -
                    9   -
                    10  Adjustments To Net Income
                    11  -
                    12  -
                    13  -
                    14  Changes In Accounts Receivables
                    15  -
                    16  -
                    17  -
                    18  Changes In Liabilities
                    19  -
                    20  -
                    21  -
                    22  Changes In Inventories
                    23  -
                    24  -
                    25  -
                    26  Changes In Other Operating Activities
                    27  -
                    28  -
                    29  -
                    30  Investing Activities, Cash Flows Provided By or Used In
                    31  Capital Expenditures
                    32  -
                    33  -
                    34  -
                    35  Investments
                    36  -
                    37  -
                    38  -
                    39  Other Cash flows from Investing Activities
                    40  -
                    41  -
                    42  -
                    43  Financing Activities, Cash Flows Provided By or Used In
                    44  Dividends Paid
                    45  -
                    46  -
                    47  -
                    48  Sale Purchase of Stock
                    49  -
                    50  -
                    51  -
                    52  Net Borrowings
                    53  -
                    54  -
                    55  -
                    56  Other Cash Flows from Financing Activities
                    57  -
                    58  -
                    59  -
                    60  Effect Of Exchange Rate Changes
                    61  -
                    62  -
                    63  -
                    64  Net Income
                    65  -
                    66  -
                    67  -
                    68  Operating Activities, Cash Flows Provided By or Used In
                    69  Total Cash Flow From Operating Activities
                    70  -
                    71  -
                    72  -
                    73  Investing Activities, Cash Flows Provided By or Used In
                    74  Total Cash Flows From Investing Activities
                    75  -
                    76  -
                    77  -
                    78  Financing Activities, Cash Flows Provided By or Used In
                    79  Total Cash Flows From Financing Activities
                    80  -
                    81  -
                    82  -
                    83  Change In Cash and Cash Equivalents
                    84  -
                    85  -
                    86  -
                        ''']
def yf_annual_income_statement_scrape(ticker):
    print line_number(), "Starting: yf_annual_income_statement_scrape for %s" % ticker
    stock = utils.return_stock_by_symbol(ticker)

    if not stock:
        print line_number(), "Error: stock %s does not exist" % ticker

    most_recent_update = stock.last_income_statement_update_yf
    last_acceptable_update = float(time.time()) - config.TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE
    if  most_recent_update > last_acceptable_update:
        print line_number(), "YF income statement data for %s is up to date." % ticker
        return

    soup = BeautifulSoup(urllib2.urlopen('http://finance.yahoo.com/q/is?s=%s&annual' % ticker), convertEntities=BeautifulSoup.HTML_ENTITIES)
    factor = 0
    thousands = soup.body.findAll(text= "All numbers in thousands")
    if thousands:
        factor = 1000

    table = soup.find("table", { "class" : "yfnc_tabledata1" })

    data_list = []


    find_all_data_in_table(table, "td", data_list, factor)
    find_all_data_in_table(table, "strong", data_list, factor)

    create_or_update_yf_StockAnnualData(ticker, data_list, "Income_Statement")

    income_statment_layout =    ['''
                            0   Period Ending
                            1   Period Ending
                            2   Cost of Revenue
                            3   -
                            4   -
                            5   -
                            6   Operating Expenses
                            7   Research Development
                            8   -
                            9   -
                            10  -
                            11  Selling General and Administrative
                            12  -
                            13  -
                            14  -
                            15  Non Recurring
                            16  -
                            17  -
                            18  -
                            19  Others
                            20  -
                            21  -
                            22  -
                            23  Total Operating Expenses
                            24  -
                            25  -
                            26  -
                            27  Income from Continuing Operations
                            28  Total Other Income/Expenses Net
                            29  -
                            30  -
                            31  -
                            32  Earnings Before Interest And Taxes
                            33  -
                            34  -
                            35  -
                            36  Interest Expense
                            37  -
                            38  -
                            39  -
                            40  Income Before Tax
                            41  -
                            42  -
                            43  -
                            44  Income Tax Expense
                            45  -
                            46  -
                            47  -
                            48  Minority Interest
                            49  -
                            50  -
                            51  -
                            52  Net Income From Continuing Ops
                            53  -
                            54  -
                            55  -
                            56  Non-recurring Events
                            57  Discontinued Operations
                            58  -
                            59  -
                            60  -
                            61  Extraordinary Items
                            62  -
                            63  -
                            64  -
                            65  Effect Of Accounting Changes
                            66  -
                            67  -
                            68  -
                            69  Other Items
                            70  -
                            71  -
                            72  -
                            73  Preferred Stock And Other Adjustments
                            74  -
                            75  -
                            76  -
                            77  Total Revenue
                            78  -
                            79  -
                            80  -
                            81  Gross Profit
                            82  -
                            83  -
                            84  -
                            85  Operating Income or Loss
                            86  -
                            87  -
                            88  -
                            89  Net Income
                            90  -
                            91  -
                            92  -
                            93  Net Income Applicable To Common Shares
                            94  -
                            95  -
                            96  -
                                ''']
def yf_annual_balance_sheet_scrape(ticker):
    print line_number(), "Starting: yf_annual_balance_sheet_scrape for %s" % ticker
    stock = utils.return_stock_by_symbol(ticker)


    if not stock:
        print line_number(), "Error: stock %s does not exist" % ticker

    most_recent_update = stock.last_balance_sheet_update_yf
    last_acceptable_update = float(time.time()) - config.TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE
    if  most_recent_update > last_acceptable_update:
        print line_number(), "YF balance sheet data for %s is up to date." % ticker
        return

    soup = BeautifulSoup(urllib2.urlopen('http://finance.yahoo.com/q/bs?s=%s&annual' % ticker), convertEntities=BeautifulSoup.HTML_ENTITIES)
    factor = 0
    thousands = soup.body.findAll(text= "All numbers in thousands")
    if thousands:
        factor = 1000
    table = soup.find("table", { "class" : "yfnc_tabledata1" })

    data_list = []

    find_all_data_in_table(table, "td", data_list, factor)
    find_all_data_in_table(table, "strong", data_list, factor)

    create_or_update_yf_StockAnnualData(ticker, data_list, "Balance_Sheet")

    balance_sheet_layout =  ['''
                            0   Period Ending
                            1   Period Ending
                            2   Mar 31 2013
                            3   Mar 31 2012
                            4   Mar 31 2011
                            5   Assets
                            6   Current Assets
                            7   Cash And Cash Equivalents
                            8   4059000000
                            9   4047000000
                            10  3767000000
                            11  Short Term Investments
                            12  320000000
                            13  74000000
                            14  32000000
                            15  Net Receivables
                            16  1754000000
                            17  1524000000
                            18  1322000000
                            19  Inventory
                            20  -
                            21  -
                            22  -
                            23  Other Current Assets
                            24  391000000
                            25  300000000
                            26  206000000
                            27  Long Term Investments
                            28  72000000
                            29  2000000
                            30  5000000
                            31  Property Plant and Equipment
                            32  1191000000
                            33  1063000000
                            34  1086000000
                            35  Goodwill
                            36  364000000
                            37  195000000
                            38  185000000
                            39  Intangible Assets
                            40  68000000
                            41  34000000
                            42  11000000
                            43  Accumulated Amortization
                            44  -
                            45  -
                            46  -
                            47  Other Assets
                            48  245000000
                            49  236000000
                            50  326000000
                            51  Deferred Long Term Asset Charges
                            52  94000000
                            53  62000000
                            54  85000000
                            55  Liabilities
                            56  Current Liabilities
                            57  Accounts Payable
                            58  393000000
                            59  310000000
                            60  224000000
                            61  Short/Current Long Term Debt
                            62  -
                            63  9000000
                            64  -
                            65  Other Current Liabilities
                            66  765000000
                            67  618000000
                            68  592000000
                            69  Long Term Debt
                            70  -
                            71  -
                            72  -
                            73  Other Liabilities
                            74  27000000
                            75  22000000
                            76  72000000
                            77  Deferred Long Term Liability Charges
                            78  23000000
                            79  2000000
                            80  -
                            81  Minority Interest
                            82  -
                            83  -
                            84  -
                            85  Negative Goodwill
                            86  -
                            87  -
                            88  -
                            89  Stockholders' Equity
                            90  Misc Stocks Options Warrants
                            91  -
                            92  -
                            93  -
                            94  Redeemable Preferred Stock
                            95  -
                            96  -
                            97  -
                            98  Preferred Stock
                            99  -
                            100 -
                            101 -
                            102 Common Stock
                            103 64000000
                            104 64000000
                            105 64000000
                            106 Retained Earnings
                            107 7666000000
                            108 6509000000
                            109 5294000000
                            110 Treasury Stock
                            111 -
                            112 -
                            113 -
                            114 Capital Surplus
                            115 -
                            116 -
                            117 -
                            118 Other Stockholder Equity
                            119 -399000000
                            120 3000000
                            121 764000000
                            122 Assets
                            123 Total Current Assets
                            124 6505000000
                            125 5945000000
                            126 5312000000
                            127 Total Assets
                            128 8539000000
                            129 7537000000
                            130 7010000000
                            131 Liabilities
                            132 Total Current Liabilities
                            133 1158000000
                            134 937000000
                            135 816000000
                            136 Total Liabilities
                            137 1208000000
                            138 961000000
                            139 888000000
                            140 Stockholders' Equity
                            141 Total Stockholder Equity
                            142 -
                            143 -
                            144 -
                            145 Net Tangible Assets
                            146 -
                            147 -
                            148 -
                            ''']



def find_all_data_in_table(table, str_to_find, data_list_to_append_to, table_factor=1):
    for cell in table.findAll(str_to_find):
        text = cell.find(text=True)
        if text:
            text = utils.strip_string_whitespace(text)
            text = text.replace(u'\xa0', u' ')
            text = str(text)
            text = text.replace(',', "")
            if text:
                if text[0] == "(":
                    text_list = list(text)
                    text_list[0] = "-"
                    text_list[-1] = ""
                    text = "".join(text_list)
            if utils.is_number(text):
                text_float = float(text) * table_factor
                if utils.relevant_float(text_float):
                    text = str(text_float)
                else:
                    text = str(int(text_float))

            #if text == "Period Ending":
            #   dates = table.findAll("th")
            #   for date in dates:
            #       print date
        if text:
            #print text
            data_list_to_append_to.append(str(text))

def create_or_update_yf_StockAnnualData(ticker, data_list, data_type):
    print line_number(), "--------------"
    print line_number(), data_type
    print line_number(), len(data_list)
    #print data_list

    # ?????????????????????????

    stock = utils.return_stock_by_symbol(ticker)
    if not stock:
        print line_number(), "error in create_or_update_yf_StockAnnualData"


    # yahoo balance sheet loop
    default_amount_of_data = 3
    cash_flow_data_positions = [1,6,10,14,18,22,26,31,35,39,44,48,52,56,60,64,69,74,79,83]
    income_statement_data_postitions = [2,7,11,15,19,23,28,32,36,40,44,48,52,57,61,65,69,73,77,81,85,89,93]
    balance_sheet_data_positions = [1,7,11,15,19,23,27,31,35,39,43,47,51,57,61,65,69,73,77,81,85,90,94,98,102,106,110,114,118,123,127,132,136,141,145]
    # unless data list format is irregular
    # What i'm doing here is complicated, if there are only two units of data
    # in each data position i need to adjust the position of the list from which to grab
    # the data. This is actually a fairly simple iteration.
    # If the data is different by 1 unit of data per section
    # the adjustment is to change the position by 1, for each section.
    # This creates a compounding adjustment, increasing by 1 unit each time,
    # made simple by increasing the adjustment variable each pass.
    #print "len(data_list) =", len(data_list), data_list
    if data_type == "Balance_Sheet" and len(data_list) == 117:#96:
        print line_number(), "adjusting for 2 years worth of Balance_Sheet data"
        default_amount_of_data = 2
        adjusted_balance_sheet_data_positions = []
        adjustment_variable = 0
        for i in balance_sheet_data_positions:
            adjusted_balance_sheet_data_positions.append(i - adjustment_variable)
            adjustment_variable += 1
        balance_sheet_data_positions = adjusted_balance_sheet_data_positions
        #print balance_sheet_data_positions
    elif data_type == "Income_Statement" and len(data_list) == 74:#59:
        print line_number(), "adjusting for 2 years worth of Income_Statement data"
        default_amount_of_data = 2
        adjusted_income_statement_data_positions = []
        adjustment_variable = 0
        for i in income_statement_data_postitions:
            adjusted_income_statement_data_positions.append(i - adjustment_variable)
            adjustment_variable += 1
        income_statement_data_postitions = adjusted_income_statement_data_positions
        #print income_statement_data_postitions
    elif data_type == "Cash_Flow" and len(data_list) == 67:
        print line_number(), "adjusting for 2 years worth of Cash_Flow data"
        default_amount_of_data = 2
        adjusted_cash_flow_data_positions = []
        adjustment_variable = 0
        for i in cash_flow_data_positions:
            adjusted_cash_flow_data_positions.append(i - adjustment_variable)
            adjustment_variable += 1
        cash_flow_data_positions = adjusted_cash_flow_data_positions
        #print cash_flow_data_positions

    data_positions = []
    if data_type == "Cash_Flow":
        data_positions = cash_flow_data_positions
        stock.last_cash_flow_update_yf = float(time.time())
    elif data_type == "Balance_Sheet":
        for i in data_list:
            print line_number(), i
        data_positions = balance_sheet_data_positions
        stock.last_balance_sheet_update_yf = float(time.time())
    elif data_type == "Income_Statement":
        data_positions = income_statement_data_postitions
        stock.last_income_statement_update_yf = float(time.time())
    else:
        print line_number(), "no data type selected"
        return

    # First, define period
    if stock:
        for i in range(len(data_list)):
            if i in data_positions:
                attribute = str(data_list[i])
                attribute = attribute.replace(" ","_")
                attribute = attribute.replace("/","_")
                attribute = attribute.replace("'","")
                if attribute == "Period_Ending":
                    for j in range(default_amount_of_data):
                        data = data_list[i+j+1]
                        #print data
                        data = data[-4:]
                        #print data
                        try:
                            # if annual data periods for yahoo finance date doesn't exist, create it.
                            throw_error = stock.annual_data_periods_yf
                        except:
                            stock.annual_data_periods_yf = []
                            for k in range(default_amount_of_data):
                                stock.annual_data_periods_yf.append("")

                        stock.annual_data_periods_yf[j] = data
    ########

    for i in range(len(data_list)):
        if i in data_positions:
            # attribute
            attribute = str(data_list[i])

            #print attribute

            attribute = attribute.replace(" ","_")
            attribute = attribute.replace("/","_")
            attribute = attribute.replace("'","")
            if attribute == "Period_Ending":
                attribute = attribute + "_For_" + data_type
            attribute_data_list = []
            #print "default amount of data =", default_amount_of_data
            for j in range(default_amount_of_data):
                data = data_list[i+j+1]
                data = data.replace(",","")

                #print data

                #try:
                #   data = int(data)
                #except:
                #   # data is not a number
                #   pass
                attribute_data_list.append(data)

            ### "year fail list" ### no longer relevant
            # year_fail_list = ["", "20XX", "20YY"]

            for k in range(default_amount_of_data):
                year_list = ["", "_t1y", "_t2y"]
                year = year_list[k]
                db.set_Stock_attribute(stock, attribute + year, attribute_data_list[k], "_yf")

                ### I abandoned the method of years below,
                ### it seemed stupid in retrospect to put the years on the object.attributes

                # year = ""
                # if k != 0:
                #   year = stock.periods[k]
                #   if not year:
                #       year = year_fail_list[k]
                #   year = "_" + year
                # #setattr(stock, attribute + year, attribute_data_list[k])
                # db.set_Stock_attribute(stock, str(attribute + year, attribute_data_list[k], "_yf")


    for attribute in dir(stock):
        if not attribute.startswith("_"):
            print line_number(), ticker+"."+attribute+":" , getattr(stock, attribute)

    db.save_GLOBAL_STOCK_DICT()

# Stock Analyst Estimates Scraping Functions
def yf_analyst_estimates_scrape(ticker):
    print line_number(), "Starting: yf_analyst_estimates_scrape for %s" % ticker
    stock = utils.return_stock_by_symbol(ticker)

    if not stock:
        return

    soup = BeautifulSoup(urllib2.urlopen('http://finance.yahoo.com/q/ae?s=%s+Analyst+Estimates' % ticker), convertEntities=BeautifulSoup.HTML_ENTITIES)

    data_list = []
    date_list = [None, None, None, None]

    table = soup.findAll("table", { "class" : "yfnc_tableout1" })

    print line_number(), "table:", len(table), "rows"
    if int(len(table)) == 0:
        print line_number(), "there is either no data for %s, or something went wrong, you can check by visiting" % ticker
        print ""
        print line_number(), 'http://finance.yahoo.com/q/ae?s=%s+Analyst+Estimates' % ticker
        print ""
    count = 0
    for i in table:
        rows = i.findChildren('tr')
        print line_number(), "rows:", len(rows), "columns"
        for row in rows:
            cells = row.findChildren(['strong','th','td','br'])
            # print len(cells)
            # if len(cells) > 20:
            #   # this is very probably a duplicate chunk
            #   continue
            #   pass
            # print "cells:", len(cells)

            # cells_copy = []
            # for i in cells:
            #   if str(i) == "<br />":
            #       continue
            #   else:
            #       cells_copy.append(i)
            # cells = cells_copy
            # #for i in cells:
            # # print i, "\n"
            # print len(cells), "\n"

            for cell in cells:
                if len(cell.contents) == 3: #this is specifically to capture the quarter dates
                    date_period = cell.contents[0]
                    date_period = date_period.replace(" ","_")
                    date_period = date_period.replace("/","_")
                    date_period = date_period.replace(".","")
                    date_period = date_period.replace("'","")
                    date_period = str(date_period)

                    date_value = cell.contents[2]
                    date_value = date_value.replace(" ","_")
                    date_value = date_value.replace("/","_")
                    date_value = date_value.replace(".","")
                    date_value = date_value.replace("'","")
                    date_value = str(date_value)

                    #print count, "|", date_period, "|", date_value
                    count += 1
                    data = date_period
                    date_data = date_value

                    date_position = None
                    if date_period == "Current_Qtr":
                        date_position = 0
                    elif date_period == "Next_Qtr":
                        date_position = 1
                    elif date_period == "Current_Year":
                        date_position = 2
                    elif date_period == "Next_Year":
                        date_position = 3

                    if date_position is not None:
                        if date_list[date_position] is None:
                            date_list[date_position] = date_data
                            #print date_list
                        elif date_list[date_position] != date_value:
                            print line_number(), "Error"
                            return


                elif cell.string is not None:
                    value = cell.string
                    #print count, "|", value
                    count += 1
                    data = str(value)

                else:
                    #print cell
                    children = cell.findChildren()
                    for child in children:
                        value = child.string
                        if value is not None:
                            #print count, "|", value
                            count += 1
                            data = str(value)
                        else:
                            pass
                            # print count, "|", child
                            # count += 1
                if data:
                    if data not in ["Current_Qtr", "Next_Qtr", "Current_Year", "Next_Year"]:
                        data_list.append(data)
                    data = None

    standard_analyst_scrape_positions = [1, ]
    heading_positions = [
                            1,  # Earnings Est
                            28, # Revenue Est
                            60, # Earnings History
                            86, # EPS Trends
                            113,# EPS Revisions
                            135 # Growth Est
                        ]
    subheading_positions = [
                            2, 7, 12, 17, 22, # Earnings Est
                            29, 34, 39, 44, 49, 54, # Revenue Est
                            65, 70, 75, 80, # Earnings History
                            87, 92, 97, 102, 107, # EPS Trends
                            114, 119, 124, 129, # EPS Revisions
                            # this is where the special non-date related subheadings start
                            140, 145, 150, 155, 160, 165, 170, 175, # Growth Est
                            ]

    heading = None
    subheading = None
    date_period_list = ["Current_Qtr", "Next_Qtr", "Current_Year", "Next_Year"]
    date_period_list_position = 0

    earnings_history_date_locations = [heading_positions[2]+1, heading_positions[2]+2, heading_positions[2]+3, heading_positions[2]+4]
    earnings_history_dates = ["12_months_ago", "9_months_ago", "6_months_ago", "3_months_ago"]
    earnings_history_date_position = 0

    growth_estimate_reference_locations = [heading_positions[-1]+1, heading_positions[-1]+2, heading_positions[-1]+3, heading_positions[-1]+4]
    growth_estimate_references = ["Stock", "Industry", "Sector", "S&P_500"]
    growth_estimate_reference_position = 0

    headings = ["Earnings Est", "Revenue Est", "EPS Trends", "EPS Revisions", "Earnings History","Growth Est"]
    subheadings = [
                    "Avg. Estimate",
                    "No. of Analysts",
                    "Low Estimate",
                    "High Estimate",
                    "Year Ago EPS",
                    "Avg. Estimate",
                    "No. of Analysts",
                    "Low Estimate",
                    "High Estimate",
                    "Year Ago Sales",
                    "Sales Growth (year/est)",

                    "Sales Growth (year over est)", # needed for edited subheading

                    "EPS Est",
                    "EPS Actual",
                    "Difference",
                    "Surprise %",
                    "Current Estimate",
                    "7 Days Ago",
                    "30 Days Ago",
                    "60 Days Ago",
                    "90 Days Ago",
                    "Up Last 7 Days",
                    "Up Last 30 Days",
                    "Down Last 30 Days",
                    "Down Last 90 Days",
                    "Current Qtr.",
                    "Next Qtr.",
                    "This Year",
                    "Next Year",
                    "Past 5 Years (per annum)",
                    "Next 5 Years (per annum)",
                    "Price/Earnings (avg. for comparison categories)",
                    "PEG Ratio (avg. for comparison categories)",
                    ]

    next_position_is_heading = False
    next_position_is_subheading = False
    data_countdown = 0

    count = 0 # 0th will always be skipped
    for i in data_list:
        do_print = True

        if str(i) in headings and next_position_is_heading == False:
            next_position_is_heading = True

        elif str(i) in headings and next_position_is_heading == True:
            heading = i
            next_position_is_subheading = True
            next_position_is_heading = False

        elif next_position_is_subheading == True:
            subheading = i
            data_countdown = 4
            next_position_is_subheading = False

        elif data_countdown > 0:
            if str(subheading) not in subheadings:
                print line_number(), "%d > %s > %s" % (count, subheading, i)
                subheading = None
                next_position_is_subheading = True
                continue
            if heading in ["Earnings Est", "Revenue Est", "EPS Trends", "EPS Revisions"]:
                if subheading == "Sales Growth (year/est)":
                    subheading = "Sales Growth (year over est)"
                stock_attribute_name = str(heading) + "_" + str(subheading) + "_" + str(date_period_list[date_period_list_position % 4])
                date_period_list_position += 1

            elif heading in ["Earnings History"]:
                if count not in earnings_history_date_locations:
                    stock_attribute_name = str(heading) + "_" + str(subheading) + "_" + str(earnings_history_dates[earnings_history_date_position % 4])
                    earnings_history_date_position += 1

            elif heading in ["Growth Est"]:
                if count not in growth_estimate_reference_locations:
                    stock_attribute_name = str(heading) + "_" + str(subheading) + "_" + str(growth_estimate_references[growth_estimate_reference_position % 4])
                    growth_estimate_reference_position += 1

            stock_attribute_name = stock_attribute_name.replace(" ","_")
            stock_attribute_name = stock_attribute_name.replace("/","_")
            stock_attribute_name = stock_attribute_name.replace(".","")
            stock_attribute_name = stock_attribute_name.replace("'","")
            stock_attribute_name = stock_attribute_name.replace("%","Pct")
            stock_attribute_name = stock_attribute_name.replace("(","")
            stock_attribute_name = stock_attribute_name.replace(")","")

            db.set_Stock_attribute(stock, stock_attribute_name, i, "_yf")

            print line_number(), "%d > %s.%s = %s" % (count, stock.symbol, stock_attribute_name, i)
            do_print = False

            data_countdown -= 1
            if data_countdown == 0 and next_position_is_subheading != True:
                subheading = None
                next_position_is_subheading = True

        if do_print == True:
            print line_number(), count, "|", i
        count += 1
        skip_position = False
    db.save_GLOBAL_STOCK_DICT()

################################################################################################

##################### Morningstar Scrapers "_ms" ###############################################
# Morningstar Annual Data Scrapers
def ms_annual_cash_flow_scrape(ticker):
    print line_number(), "Starting: ms_annual_cash_flow_scrape for %s" % ticker
    stock = utils.return_stock_by_symbol(ticker)

    if not stock:
        print line_number(), "Error: stock %s does not exist" % ticker

    most_recent_update = stock.last_cash_flow_update_ms
    last_acceptable_update = float(time.time()) - config.TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE
    if  most_recent_update > last_acceptable_update:
        print line_number(), "MS Cash flow data for %s is up to date." % ticker
        return

    if stock:
        exchange = getattr(stock, config.DEFAULT_STOCK_EXCHANGE_ATTRIBUTE)
        if exchange == 'NYSE':
            exchange_code = "XNYS"
        elif exchange in ["NasdaqNM", "NASDAQ"]:
            exchange_code = "XNAS"
        else:
            print line_number(), "Unknown Exchange Code for", stock.symbol
            return
    else:
        print line_number(), 'Stock cannot be updated, need exchange symbol'
        return

    morningstar_raw = urllib2.urlopen('http://financials.morningstar.com/ajax/ReportProcess4HtmlAjax.html?&t=%s:%s&region=usa&culture=en-US&cur=USD&reportType=cf&period=12&dataType=A&order=asc&columnYear=5&rounding=3&view=raw&r=963470&callback=jsonp%d&_=%d' % (exchange_code, ticker, int(time.time()), int(time.time()+150)))
    morningstar_json = morningstar_raw.read()
    #print morningstar_json
    morningstar_string = str(morningstar_json)
    # dummy_str = ""
    # start_copy = False
    # for char in morningstar_string:
    #   if start_copy == False and char != "(":
    #       continue
    #   elif start_copy == False and char == "(":
    #       start_copy = True
    #       continue
    #   elif start_copy == True:
    #       dummy_str += char
    # morningstar_string = dummy_str[:-1]
    # try:
    #   morningstar_json = json.loads(morningstar_string)
    # except Exception, exception:
    #   print exception
    #   print morningstar_string
    #   print morningstar_raw.read()
    #   return

    # #print morningstar_json["ADR"], "<-- should say false"
    # morningstar_html = morningstar_json["result"]

    dummy_str = ""
    start_copy = False
    last_char_was_backslash = False
    for char in morningstar_string:
        if char == "<" and not start_copy:
            start_copy = True
            dummy_str += char
        elif start_copy:
            if char == "\\":
                last_char_was_backslash = True
            elif last_char_was_backslash == True:
                if char in ["t","r","n"]:
                    last_char_was_backslash = False
                elif char in ['"', "'", "/"]:
                    dummy_str += char
                    last_char_was_backslash = False
                else:
                    print line_number(), "\\%s" % char
                    last_char_was_backslash = False

            else:
                dummy_str += char
    #print "\n", dummy_str
    morningstar_html = dummy_str
    soup = BeautifulSoup(morningstar_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #print soup.prettify()
    full_data = []

    div_ids = ["tts", "s", "i"] # these are the three unique labels for divs on morningstar
    for div_id in div_ids:
        count = 0
        for i in range(100): # this may need to be larger
            label = soup.find("div", {"id":"label_%s%d" % (div_id, count)})
            if label:
                try:
                    label["style"]
                    if "display:none;" in str(label["style"]):
                        # I'm not comfortable accepting unshown data right now
                        count+=1
                        continue
                except:
                    pass
                name = label.find("div", {"class":"lbl"})
                try:
                    title = name["title"]
                    name = title
                except:
                    title = None
                    name = name.string
            else:
                name = None
                count += 1
                continue
            #if name:
            #   print name.children()
            data = soup.find("div", {"id":"data_%s%d" % (div_id, count)})
            if data:
                data_list = []
                for i in reversed(range(6)):
                    i += 1 # id's are ordinal
                    data_list.append(data.find("div", {"id":"Y_%d" % i})["rawvalue"])

            #if name and data_list:
            #   print name
            #   for i in data_list:
            #       print i
            #   print "\n","\n"

            full_data.append([name,data_list])
            count+=1

    print "total units of data =", len(full_data)
    #for i in full_data:
    #   print i[0]
    #   for j in i[1]:
    #       print j

    success = False

    for datum in full_data:
        attribute = datum[0]
        attribute = attribute.replace(" ","_")
        attribute = attribute.replace("-","_")
        attribute = attribute.replace("/","_")
        attribute = attribute.replace(",","_")
        attribute = attribute.replace("'","")
        attribute = attribute.replace("(Gain)_", "")
        attribute = attribute.replace("(expense)_", "")
        attribute = attribute.replace("(used_for)", "used_for")
        attribute = attribute.replace("__","_")

        data_list = datum[1]
        trailing_x_year_list = ["", "_t1y", "_t2y", "_t3y", "_t4y", "_t5y"]
        for i in range(len(data_list)):
            if data_list[i] == u'\u2014':
                data_list[i] = "-"
            try:
                db.set_Stock_attribute(stock, str(attribute + trailing_x_year_list[i]), int(data_list[i]), "_ms")
                print line_number(), stock.symbol, str(attribute + trailing_x_year_list[i]) + "_ms", int(data_list[i])
                success = True
            except:
                try:
                    db.set_Stock_attribute(stock, str(attribute + trailing_x_year_list[i]), str(data_list[i]), "_ms")
                    print line_number(), stock.symbol, str(attribute + trailing_x_year_list[i]) + "_ms", str(data_list[i])
                    success = True
                except Exception, exception:
                    print line_number(), exception

    if success:
        db.save_GLOBAL_STOCK_DICT()
    print line_number(), "\n", "cash flow done", "\n"
    return success
def ms_annual_income_statement_scrape(ticker):
    print line_number(), "Starting: ms_annual_income_statement_scrape for %s" % ticker
    stock = utils.return_stock_by_symbol(ticker)
    if not stock:
        print line_number(), "Error: stock %s does not exist" % ticker

    most_recent_update = stock.last_income_statement_update_ms
    last_acceptable_update = float(time.time()) - config.TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE
    if  most_recent_update > last_acceptable_update:
        print line_number(), "MS income statement data for %s is up to date." % ticker
        return


    if stock:
        exchange = getattr(stock, config.DEFAULT_STOCK_EXCHANGE_ATTRIBUTE)
        if exchange == 'NYSE':
            exchange_code = "XNYS"
        elif exchange in ["NasdaqNM", "NASDAQ"]:
            exchange_code = "XNAS"
        else:
            print line_number(), "Unknown Exchange Code for", stock.symbol
            print line_number()
            return
    else:
        print line_number(), 'Stock cannot be updated, need exchange symbol'
        return

    morningstar_raw = urllib2.urlopen('http://financials.morningstar.com/ajax/ReportProcess4HtmlAjax.html?&t=%s:%s&region=usa&culture=en-US&cur=USD&reportType=is&period=12&dataType=A&order=asc&columnYear=5&rounding=3&view=raw&r=354589&callback=jsonp%d&_=%d' % (exchange_code, ticker, int(time.time()), int(time.time()+150)))
    #print morningstar_raw
    morningstar_json = morningstar_raw.read()
    #print morningstar_json
    morningstar_string = str(morningstar_json)
    # dummy_str = ""
    # start_copy = False
    # for char in morningstar_string:
    #   if start_copy == False and char != "(":
    #       continue
    #   elif start_copy == False and char == "(":
    #       start_copy = True
    #       continue
    #   elif start_copy == True:
    #       dummy_str += char
    # morningstar_string = dummy_str[:-1]
    # try:
    #   morningstar_json = json.loads(morningstar_string)
    # except Exception, exception:
    #   print exception
    #   print morningstar_string
    #   print morningstar_raw.read()
    #   return

    # #print morningstar_json["ADR"], "<-- should say false"
    # morningstar_html = morningstar_json["result"]

    dummy_str = ""
    start_copy = False
    last_char_was_backslash = False
    for char in morningstar_string:
        if char == "<" and not start_copy:
            start_copy = True
            dummy_str += char
        elif start_copy:
            if char == "\\":
                last_char_was_backslash = True
            elif last_char_was_backslash == True:
                if char in ["t","r","n"]:
                    last_char_was_backslash = False
                elif char in ['"', "'", "/"]:
                    dummy_str += char
                    last_char_was_backslash = False
                else:
                    print "\\%s" % char
                    last_char_was_backslash = False

            else:
                dummy_str += char
    #print "\n", dummy_str
    morningstar_html = dummy_str

    soup = BeautifulSoup(morningstar_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #print soup.prettify()
    full_data = []

    div_ids = ["tts", "s", "i", "g", "gg"] # these are the three unique labels for divs on morningstar
    for div_id in div_ids:
        count = 0
        for i in range(100): # this may need to be larger
            label = soup.find("div", {"id":"label_%s%d" % (div_id, count)})
            if label:
                try:
                    label["style"]
                    if "display:none;" in str(label["style"]):
                        # I'm not comfortable accepting unshown data right now
                        count+=1
                        continue
                except:
                    pass
                name = label.find("div", {"class":"lbl"})
                try:
                    title = name["title"]
                    name = title
                except:
                    title = None
                    name = name.string
                    if not name:
                        name = label.findAll(text=True)

                        #name = name.string
                        #print name, type(name), "\n"
                        name = str(name)
                        dummy_str = ""
                        u_gone = False # there is a "u" that starts every fake unicode thing
                        for i in name:
                            if i not in ["'",'"',"[","]"]:
                                if i == "u" and u_gone == False:
                                    u_gone = True
                                else:
                                    dummy_str += i
                        name = dummy_str
                        #print name, type(name), "\n"
                if name in ["Basic", "Diluted"]: # here there is a quirk, where EPS is in the previous div, and so you need to grab it and add it onto the name
                    if name == "Basic":
                        try:
                            prefix = label.findPreviousSibling('div').find("div", {"class":"lbl"})["title"]
                        except:
                            prefix = label.findPreviousSibling('div').find("div", {"class":"lbl"}).string
                    elif name == "Diluted":
                        try:
                            prefix = label.findPreviousSibling('div').findPreviousSibling('div').find("div", {"class":"lbl"})["title"]
                        except:
                            prefix = label.findPreviousSibling('div').findPreviousSibling('div').find("div", {"class":"lbl"}).string
                    name = prefix + " " + name
                    #print name

            else:
                name = None
                count += 1
                continue
            #if name:
            #   print name.children()
            data = soup.find("div", {"id":"data_%s%d" % (div_id, count)})
            #print "\n", data, "\n"
            if data:
                #print "\n", data, "\n"
                data_list = []
                for i in reversed(range(6)): # 6 data points on this page
                    i += 1 # id's are ordinal
                    found_data = data.find("div", {"id":"Y_%d" % i})["rawvalue"]
                    #print found_data
                    if found_data:
                        data_list.append(found_data)
            else:
                print data

            #if name and data_list:
            #   print name
            #   for i in data_list:
            #       print i
            #   print "\n","\n"
            if name and data_list:
                full_data.append([str(name),data_list])
            else:
                if not name:
                    print label, "\n", name, "\n"
                elif not data_list:
                    print data
            count+=1

    print "total units of data =", len(full_data)
    #for i in full_data:
    #   print i[0]
    #   for j in i[1]:
    #       print j

    success = False

    #for i in full_data:
    #   print i

    for datum in full_data:
        attribute = datum[0]
        attribute = attribute.replace(" ","_")
        attribute = attribute.replace("-","_")
        attribute = attribute.replace("/","_")
        attribute = attribute.replace(",","_")
        attribute = attribute.replace("'","")
        attribute = attribute.replace("(Gain)_", "")
        attribute = attribute.replace("(expense)_", "")
        attribute = attribute.replace("(used_for)", "used_for")
        attribute = attribute.replace("__","_")

        data_list = datum[1]
        trailing_x_year_list = ["_ttm", "_t1y", "_t2y", "_t3y", "_t4y", "_t5y"]
        for i in range(len(data_list)):
            if data_list[i] == u'\u2014':
                data_list[i] = "-"
            elif data_list[i] == "nbsp":
                continue
            try:
                db.set_Stock_attribute(stock, str(attribute + trailing_x_year_list[i]), int(data_list[i]), "_ms")
                print line_number(), stock.symbol + "." + str(attribute + trailing_x_year_list[i] + "_ms"), "=", int(data_list[i])
                success = True
            except:
                try:
                    db.set_Stock_attribute(stock, str(attribute + trailing_x_year_list[i]), str(data_list[i]), "_ms")
                    print line_number(), stock.symbol + "." + str(attribute + trailing_x_year_list[i] + "_ms"), "=", str(data_list[i])
                    success = True
                except Exception, exception:
                    print line_number(), exception

    if success:
        db.save_GLOBAL_STOCK_DICT()
    print line_number(), "\n", "income statement done", "\n"
    return success
def ms_annual_balance_sheet_scrape(ticker):
    print line_number(), "Starting: ms_annual_balance_sheet_scrape for %s" % ticker
    stock = utils.return_stock_by_symbol(ticker)
    if not stock:
        print line_number(), "Error: stock %s does not exist" % ticker

    most_recent_update = stock.last_balance_sheet_update_ms
    last_acceptable_update = float(time.time()) - config.TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE
    if  most_recent_update > last_acceptable_update:
        print line_number(), "MS balance sheet data for %s is up to date." % ticker
        return


    if stock:
        exchange = getattr(stock, config.DEFAULT_STOCK_EXCHANGE_ATTRIBUTE)
        if exchange == 'NYSE':
            exchange_code = "XNYS"
        elif exchange == "NasdaqNM":
            exchange_code = "XNAS"
        else:
            print line_number(), "Unknown Exchange Code for", stock.symbol
            print line_number()
            return
    else:
        print line_number(), 'Stock cannot be updated, need exchange symbol'
        return

    url = 'http://financials.morningstar.com/ajax/ReportProcess4HtmlAjax.html?&t=%s:%s&region=usa&culture=en-US&cur=USD&reportType=bs&period=12&dataType=A&order=asc&columnYear=5&rounding=3&view=raw'% (exchange_code, ticker)#&r=782238&callback=jsonp%d&_=%d' % (exchange_code, ticker, int(time.time()), int(time.time()+150))
    print line_number(), "\n", url, "\n"
    morningstar_raw = urllib2.urlopen(url)

    print line_number(), "morningstar_raw:", morningstar_raw, "\n"

    if not morningstar_raw:
        print line_number(), "failed", line_number()
    #print morningstar_raw
    morningstar_json = morningstar_raw.read()
    #print "morningstar read", morningstar_json
    #print morningstar_json
    morningstar_string = str(morningstar_json)
    #dummy_str = ""
    #start_copy = False
    #for char in morningstar_string:
    #   if start_copy == False and char != "(":
    #       continue
    #   elif start_copy == False and char == "(":
    #       start_copy = True
    #       continue
    #   elif start_copy == True:
    #       dummy_str += char
    #morningstar_string = dummy_str[:-1]


    dummy_str = ""
    start_copy = False
    last_char_was_backslash = False
    for char in morningstar_string:
        if char == "<" and not start_copy:
            start_copy = True
            dummy_str += char
        elif start_copy:
            if char == "\\":
                last_char_was_backslash = True
            elif last_char_was_backslash == True:
                if char in ["t","r","n"]:
                    last_char_was_backslash = False
                elif char in ['"', "'", "/"]:
                    dummy_str += char
                    last_char_was_backslash = False
                else:
                    print line_number(), "\\%s" % char
                    last_char_was_backslash = False

            else:
                dummy_str += char
    #print "\n", dummy_str
    morningstar_html = dummy_str

    # try:
    #   morningstar_json = json.loads(morningstar_string)
    # except Exception, exception:
    #   print exception
    #   print morningstar_string
    #   print morningstar_raw
    #   return

    # #print morningstar_json["ADR"], "<-- should say false"
    # morningstar_html = morningstar_json["result"]
    soup = BeautifulSoup(morningstar_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #print soup.prettify()
    full_data = []

    div_ids = ["tts", "s", "i", "g", "gg"] # these are the three unique labels for divs on morningstar
    for div_id in div_ids:
        count = 0
        for i in range(100): # this may need to be larger
            label = soup.find("div", {"id":"label_%s%d" % (div_id, count)})
            if label:
                try:
                    label["style"]
                    if "display:none;" in str(label["style"]):
                        # I'm not comfortable accepting unshown data right now
                        count+=1
                        continue
                except:
                    pass
                name = label.find("div", {"class":"lbl"})
                try:
                    title = name["title"]
                    name = title
                except:
                    title = None
                    name = name.string
                    if not name:
                        name = label.findAll(text=True)

                        #name = name.string
                        #print name, type(name), "\n"
                        name = str(name)
                        dummy_str = ""
                        u_gone = False # there is a "u" that starts every fake unicode thing
                        for i in name:
                            if i not in ["'",'"',"[","]"]:
                                if i == "u" and u_gone == False:
                                    u_gone = True
                                else:
                                    dummy_str += i
                        name = dummy_str
                        #print name, type(name), "\n"


            else:
                name = None
                count += 1
                continue
            #if name:
            #   print name.children()
            data = soup.find("div", {"id":"data_%s%d" % (div_id, count)})
            #print "\n", data, "\n"
            if data:
                #print "\n", data, "\n"
                data_list = []
                for i in reversed(range(5)):
                    i += 1 # id's are ordinal
                    found_data = data.find("div", {"id":"Y_%d" % i})["rawvalue"]
                    #print found_data
                    if found_data:
                        data_list.append(found_data)
            else:
                print line_number(), data

            #if name and data_list:
            #   print name
            #   for i in data_list:
            #       print i
            #   print "\n","\n"
            if name and data_list:
                full_data.append([str(name),data_list])
            else:
                if not name:
                    print line_number(), label, "\n", name, "\n"
                elif not data_list:
                    print line_number(), data
            count+=1

    print line_number(), "total units of data =", len(full_data)
    #for i in full_data:
    #   print i[0]
    #   for j in i[1]:
    #       print j

    success = False

    #for i in full_data:
    #   print i

    for datum in full_data:
        attribute = datum[0]
        attribute = attribute.replace(" ","_")
        attribute = attribute.replace("-","_")
        attribute = attribute.replace("/","_")
        attribute = attribute.replace(",","_")
        attribute = attribute.replace("'","")
        attribute = attribute.replace("(Gain)_", "")
        attribute = attribute.replace("(expense)_", "")
        attribute = attribute.replace("(used_for)", "used_for")
        attribute = attribute.replace("__","_")

        data_list = datum[1]
        trailing_x_year_list = ["", "_t1y", "_t2y", "_t3y", "_t4y", "_t5y"]
        for i in range(len(data_list)):
            if data_list[i] == u'\u2014':
                data_list[i] = "-"
            try:
                db.set_Stock_attribute(stock, str(attribute + trailing_x_year_list[i]), int(data_list[i]), "_ms")
                print line_number(), stock.symbol + "." + str(attribute + trailing_x_year_list[i] + "_ms"), "=", int(data_list[i])
                success = True
            except:
                try:
                    db.set_Stock_attribute(stock, str(attribute + trailing_x_year_list[i]), str(data_list[i]), "_ms")
                    print line_number(), stock.symbol + "." + str(attribute + trailing_x_year_list[i] + "_ms"), "=", str(data_list[i])
                    success = True
                except Exception, exception:
                    print line_number(), exception

    if success:
        db.save_GLOBAL_STOCK_DICT()
    print line_number(), "\n", "balance sheet done", "\n"
    return success

# Morningstar Key Ratios (Not increadibly reliable for all data (rounding large numbers), consider alternatives if necessary)
def ms_key_ratios_scrape(ticker):
    stock_exchange_var = config.DEFAULT_STOCK_EXCHANGE_ATTRIBUTE

    print line_number(), "Starting: ms_key_ratios_scrape for %s" % ticker
    ticker = ticker.upper()
    print line_number(), "morningstar_key_ratios_scrape:", ticker
    stock = utils.return_stock_by_symbol(ticker)
    if not stock:
        return
    if stock:
        yesterdays_epoch = float(time.time()) - (60 * 60 * 24)
        #if stock.morningstar_key_ratios_scrape > yesterdays_epoch: # if data is more than a day old
        #   print "Cash flow data for %s is up to date." % ticker
        #   return

    exchange = getattr(stock, stock_exchange_var)
    if exchange == 'NYSE':
        exchange_code = "XNYS"
    elif exchange in ["NasdaqNM", "NASDAQ"]:
        exchange_code = "XNAS"
    else:
        print line_number(), "Unknown Exchange Code for", stock.symbol
        print line_number()
        return


    ### First get your scrape ###
    print line_number(), 'http://financials.morningstar.com/financials/getFinancePart.html?&callback=jsonp1408061143067&t=%s:%s&region=usa&culture=en-US&cur=USD&order=asc&_=1408061143210' % (exchange_code, ticker)
    morningstar_raw = urllib2.urlopen('http://financials.morningstar.com/financials/getFinancePart.html?&callback=jsonp1408061143067&t=%s:%s&region=usa&culture=en-US&cur=USD&order=asc&_=1408061143210' % (exchange_code, ticker))
    #morningstar_raw = urllib2.urlopen('http://financials.morningstar.com/ajax/exportKR2CSV.html?&callback=?&t=%s:%s&region=usa&culture=en-US&cur=USD&order=' % (exchange_code, ticker) )#, int(time.time()), int(time.time()+150)))
    morningstar_json = morningstar_raw.read()
    #print morningstar_json
    morningstar_string = str(morningstar_json)

    # dummy_str = ""
    # start_copy = False
    # for char in morningstar_string:
    #   if start_copy == False and char != "(":
    #       continue
    #   elif start_copy == False and char == "(":
    #       start_copy = True
    #       continue
    #   elif start_copy == True:
    #       dummy_str += char
    # morningstar_string = dummy_str[:-1]
    # try:
    #   morningstar_json = json.loads(morningstar_string)
    # except Exception, exception:
    #   print exception
    #   print morningstar_string
    #   print morningstar_raw.read()
    #   return

    # #print morningstar_json["ADR"], "<-- should say false"
    # morningstar_html = morningstar_json["result"]

    ### Now, remove improper chars ###
    dummy_str = ""
    start_copy = False
    last_char_was_backslash = False
    for char in morningstar_string:
        if char == "<" and not start_copy:
            start_copy = True
            dummy_str += char
        elif start_copy:
            if char == "\\":
                last_char_was_backslash = True
            elif last_char_was_backslash == True:
                if char in ["t","r","n"]:
                    last_char_was_backslash = False
                elif char in ['"', "'", "/"]:
                    dummy_str += char
                    last_char_was_backslash = False
                else:
                    #print "\\%s" % char
                    last_char_was_backslash = False

            else:
                dummy_str += char
    #print "\n", dummy_str
    morningstar_html = dummy_str
    #print morningstar_html


    ### convert to soup ###
    soup = BeautifulSoup(morningstar_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #print soup.prettify()

    full_data = []


    ### parse the soup ###

    # Here we set the dates
    # Y10 = ttm
    # Y9 = t1y
    # Y8 = t2y
    # etc.
    data_list = []

    div_id = "i" # these are the three unique labels for divs on morningstar
    count = 0
    for i in range(100): # this may need to be larger
        label = soup.find("th", {"id":"%s%d" % (div_id, count)})
        if label:
            # first find the row names and units
            try:
                label["style"]
                if "display:none;" in str(label["style"]):
                    # I'm not comfortable accepting unshown data right now
                    count+=1
                    continue
            except:
                pass
            name = label.contents[0]
            if len(label) > 1:
                units = label.contents[1]
                units = units.contents[0]
            #print name, units

            label_data = []
            data_sublist = [str(name), str(units), label_data]
            # Now gather the data using the row id and year in the "header" section
            # "Y0" or year 0, appears to be 10 years ago,
            # where as Y10 appears to be the trailing 12 months data
            # it's a bit of some odd data, but it's obviously manageable.
            for years_ago in reversed(range(11)): # this may also be larger
                data = soup.find("td", {"headers": "Y%d i%d" % (years_ago, count)})
                if data:
                    #print data.contents
                    for datum in data.contents:
                        label_data.append(str(datum))
            #print data_sublist
            #print ""
            data_list.append(data_sublist)
        else:
            name = None
            count += 1
            continue
        #if name:
        #   print name.children()
        data = soup.find("div", {"id":"data_%s%d" % (div_id, count)})
        if data:
            data_list = []
            for i in reversed(range(6)):
                i += 1 # id's are ordinal
                data_list.append(data.find("div", {"id":"Y_%d" % i})["rawvalue"])

        full_data.append([name,data_list])
        count+=1



    print line_number(), "total units of data =", len(data_list)

    success = False


    ### convert to data_lists ###
    #########
    data_list = morningstar_recursive_data_list_string_edit(data_list)
    data_list = morningstar_add_zeros_to_usd_millions(data_list)
    #########
    print line_number()
    pp.pprint(data_list)

    # for unit in data_list:
    #   print unit[0]
    #   print unit[1]
    #   print "------"
    #   for subunit in unit[2]:
    #       print subunit
    #   print ""

    ### save data to object ###
    # datum is [name, units, [datalist]]
    count = 1
    for datum in data_list:
        print ""
        print line_number(), count
        print line_number(), datum[0]
        attribute = datum[0]
        print line_number(), datum[1]
        print line_number(), "------"
        count += 1
        data_list = datum[2]
        trailing_x_year_list = ["_ttm", "_t1y", "_t2y", "_t3y", "_t4y", "_t5y", "_t6y", "_t7y", "_t8y", "_t9y", "_t10y"]
        for i in range(len(data_list)):
            if data_list[i] == u'\u2014':
                data_list[i] = "-"
            try:
                # testing only commented out
                db.set_Stock_attribute(stock, str(attribute + trailing_x_year_list[i]), int(data_list[i]), "_ms")
                #
                print line_number(), stock.symbol + "." + str(attribute + trailing_x_year_list[i] + "_ms"), "=", int(data_list[i])
            except:
                try:
                    # testing only commented out
                    db.set_Stock_attribute(stock, str(attribute + trailing_x_year_list[i]), str(data_list[i]), "_ms")
                    #
                    print line_number(), stock.symbol + "." + str(attribute + trailing_x_year_list[i] + "_ms"), "=", str(data_list[i])
                except Exception, exception:
                    print line_number(), exception
    # testing only
    success = False
    #


    ### save object ###
    stock.last_morningstar_key_ratios_update = float(time.time())

    db.save_GLOBAL_STOCK_DICT()

    print line_number(), "\n", "key ratios done", "\n"
    return success

def morningstar_recursive_data_list_string_edit(data_list, recursion_count = 0):
    dummy_list = []
    #if recursion_count == 0:
    #   print "to save:"
    #   pass
    #pp.pprint(data_list)
    #print ""
    for datum in data_list:
        if type(datum) is list:
            recursion_count += 1
            if recursion_count > 10:
                print line_number(), "max recusions achieved,", line_number()
                return
            print line_number(), "Recursion (%d) for: morningstar_recursive_data_list_string_edit" % recursion_count
            datum = morningstar_recursive_data_list_string_edit(datum, recursion_count = recursion_count)
            print line_number(), "End recursion level %d" % recursion_count
            recursion_count -= 1
        elif type(datum) is (str or unicode):
            #print string, "\n"
            try:
                datum = datum.replace(",", "")
                if not datum.isdigit():
                    raise Exception("Not a number")
                datum = datum.replace("\xe2\x80\x94","-")
                print line_number(), "string (number) saved:", datum
            except:
                datum = datum.replace("%", "perc")
                datum = datum.replace(" ","_")
                #datum = datum.replace("-","_")
                datum = datum.replace("/","_")
                datum = datum.replace(",","_")
                datum = datum.replace("'","")
                datum = datum.replace("(Gain)_", "")
                datum = datum.replace("(expense)_", "")
                datum = datum.replace("(used_for)", "used_for")
                datum = datum.replace("__","_")
                datum = datum.replace("\xc2\xa0", "")
                datum = datum.replace("\xe2\x80\x94","-")

                # datum = datum.replace(u"%", u"perc")
                # datum = datum.replace(u" ",u"_")
                # datum = datum.replace(u"-",u"_")
                # datum = datum.replace(u"/",u"_")
                # datum = datum.replace(u",",u"_")
                # datum = datum.replace(u"'",u"")
                # datum = datum.replace(u"(Gain)_", u"")
                # datum = datum.replace(u"(expense)_", u"")
                # datum = datum.replace(u"(used_for)", u"used_for")
                # datum = datum.replace(u"__",u"_")
                print line_number(), "string saved:", datum
        else:
            print line_number(), "Not able to parse:", datum

        dummy_list.append(datum)



    data_list = dummy_list

    #for sublist in data_list:
    #   print sublist

    #if recursion_count == 0:
    #   print "Saved:"
    #   pp.pprint(data_list)
    #   pass
    return data_list
def morningstar_add_zeros_to_usd_millions(data_list):
    dummy_list = []
    for datum in data_list:
        print line_number(), "edits:"
        print line_number(), datum[1]
        if not len(datum) == 3:
            print line_number()
            logging.error("morningstar_add_zeros_to_usd_millions error, not correctly formated list")
        if datum[1] in ["USD Mil", u"USD Mil", "USD_Mil", u"USD_Mil"]:
            dummy_list_2 = []
            for amount_of_dollars in datum[2]:
                print line_number(), amount_of_dollars
                if str(amount_of_dollars).isdigit():
                    print line_number(), "converting %s to %s000" % (amount_of_dollars, amount_of_dollars)
                    amount_of_dollars = amount_of_dollars + "000"
                dummy_list_2.append(amount_of_dollars)
            datum[2] = dummy_list_2
            datum[1] = "USD_from_Mil"
            dummy_list.append(datum)
        elif datum[1] in ["Mil", u"Mil"]:
            dummy_list_2 = []
            for amount in datum[2]:
                if amount.isdigit():
                    amount = amount + "000"
                dummy_list_2.append(amount)
            datum[2] = dummy_list_2
            datum[1] = "was_Mil"
            dummy_list.append(datum)
        else:
            dummy_list.append(datum)
    data_list = dummy_list
    return data_list
################################################################################################




###################### Bloomberg Scrapers "_bb" ################################################
################################################################################################

###################### EDGAR Scrapers "_ed" ####################################################
################################################################################################

################################################################################################
################################################################################################

################################################################################################
################################################################################################



#end of line