import locale, sys, threading, urllib2, platform
from user_data import user_data
### Editable globals all come from user_data.py in the user_data folder ###

DISPLAY_SIZE = None # will be detected

currency_symbol = user_data.currency_symbol

STOCK_EXCHANGE_LIST = user_data.STOCK_EXCHANGE_LIST
DEFAULT_COMMISSION = user_data.DEFAULT_COMMISSION
DEFAULT_ENCRYPTION_HARDNESS_LEVEL = user_data.DEFAULT_ENCRYPTION_HARDNESS_LEVEL
SCRAPE_CHUNK_LENGTH = user_data.SCRAPE_CHUNK_LENGTH

SCRAPE_SLEEP_TIME = user_data.SCRAPE_SLEEP_TIME
ADDITIONAL_DATA_SCRAPE_SLEEP_TIME = user_data.ADDITIONAL_DATA_SCRAPE_SLEEP_TIME

TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE = user_data.TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE
TIME_ALLOWED_FOR_BEFORE_YQL_DATA_NO_LONGER_APPEARS_IN_STOCK_LIST = user_data.TIME_ALLOWED_FOR_BEFORE_YQL_DATA_NO_LONGER_APPEARS_IN_STOCK_LIST

PORTFOLIO_PRICE_REFRESH_TIME = user_data.PORTFOLIO_PRICE_REFRESH_TIME

DEFAULT_ROWS_ON_SALE_PREP_PAGE = 9
DEFAULT_ROWS_ON_TRADE_PREP_PAGE_FOR_TICKERS = 6
# adjust these to your own preference

# these will depend on your preferred data sources
DEFAULT_LAST_TRADE_PRICE_ATTRIBUTE_NAME = user_data.DEFAULT_LAST_TRADE_PRICE_ATTRIBUTE_NAME
DEFAULT_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME = user_data.DEFAULT_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME
DEFAULT_LAST_UPDATE = user_data.DEFAULT_LAST_UPDATE
DEFAULT_STOCK_EXCHANGE_ATTRIBUTE = user_data.DEFAULT_STOCK_EXCHANGE_ATTRIBUTE
DEFAULT_STOCK_WEBSITE_ATTRIBUTE = user_data.DEFAULT_STOCK_WEBSITE_ATTRIBUTE
#--
SECONDARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME = user_data.SECONDARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME
SECONDARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME = user_data.SECONDARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME
SECONDARY_LAST_UPDATE = user_data.SECONDARY_LAST_UPDATE
SECONDARY_STOCK_EXCHANGE_ATTRIBUTE = user_data.SECONDARY_STOCK_EXCHANGE_ATTRIBUTE
SECONDARY_STOCK_WEBSITE_ATTRIBUTE = user_data.SECONDARY_STOCK_WEBSITE_ATTRIBUTE
#---
TERTIARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME = user_data.TERTIARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME
TERTIARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME = user_data.TERTIARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME
TERTIARY_LAST_UPDATE = user_data.TERTIARY_LAST_UPDATE
TERTIARY_STOCK_EXCHANGE_ATTRIBUTE = user_data.TERTIARY_STOCK_EXCHANGE_ATTRIBUTE
TERTIARY_STOCK_WEBSITE_ATTRIBUTE = user_data.TERTIARY_STOCK_WEBSITE_ATTRIBUTE
#----
QUATERNARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME = user_data.QUATERNARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME
QUATERNARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME = user_data.QUATERNARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME
QUATERNARY_LAST_UPDATE = user_data.QUATERNARY_LAST_UPDATE
QUATERNARY_STOCK_EXCHANGE_ATTRIBUTE = user_data.QUATERNARY_STOCK_EXCHANGE_ATTRIBUTE
QUATERNARY_STOCK_WEBSITE_ATTRIBUTE = user_data.QUATERNARY_STOCK_WEBSITE_ATTRIBUTE
#-------------------------------------------------

OS_TYPE = platform.system() # Detect OS
OS_TYPE_INDEX = None
try:
	supported_os_types = ["Darwin", "Linux", "Windows"]
	OS_TYPE_INDEX = supported_os_types.index(OS_TYPE)
except Exception as e:
	print e
	print "This program has not be properly formatted for your OS. Edit the config file if needed."
	sys.exit()

IRRELEVANT_ATTRIBUTES = ["updated",
	"epoch",
	"created_epoch",
	"TrailingPE_ttm_Date_yf",
	"TradeDate_yf",
	"TwoHundreddayMovingAverage_yf",
	"TickerTrend_yf",
	"SharesOwned_yf",
	"SP50052_WeekChange_yf",
	"PricePaid_yf",
	"PercentChangeFromTwoHundreddayMovingAverage_yf",
	"PercentChangeFromFiftydayMovingAverage_yf",
	"PercentChange_yf",
	"PERatioRealtime_yf",
	"OrderBookRealtime_yf",
	"Notes_yf",
	"MostRecentQuarter_mrq_yf",
	"MoreInfo_yf",
	"MarketCapRealtime_yf",
	"LowLimit_yf",
	"LastTradeWithTime_yf",
	"LastTradeTime_yf",
	"LastTradeRealtimeWithTime_yf",
	"LastTradePriceOnly_yf",
	"LastTradeDate_yf",
	"HoldingsValueRealtime_yf",
	"HoldingsValue_yf",
	"HoldingsGainRealtime_yf",
	"HoldingsGainPercentRealtime_yf",
	"HoldingsGainPercent_yf",
	"HoldingsGain_yf",
	"HighLimit_yf",
	"ExDividendDate_yf",
	"DividendPayDate_yf",
	"DaysValueChangeRealtime_yf",
	"DaysValueChange_yf",
	"DaysRangeRealtime_yf",
	"DaysRange_yf",
	"DaysLow_yf",
	"DaysHigh_yf",
	"Commission_yf",
	"Change_PercentChange_yf",
	"ChangeRealtime_yf",
	"ChangePercentRealtime_yf",
	"ChangeFromTwoHundreddayMovingAverage_yf",
	"ChangeFromFiftydayMovingAverage_yf",
	"Change_yf",
	"ChangeinPercent_yf",
	"BidRealtime_yf",
	"Bid_yf",
	"AvgVol_3_month_yf",
	"AvgVol_10_day_yf",
	"AskRealtime_yf",
	"Ask_yf",
	"AnnualizedGain_yf",
	"AfterHoursChangeRealtime_yf",
	"p_52_WeekLow_Date_yf",
	"p_52_WeekLow_yf",
	"p_52_WeekHigh_Date_yf",
	"p_52_WeekHigh_yf",
	"p_52_WeekChange_yf",
	"p_50_DayMovingAverage_yf",
	"p_200_DayMovingAverage_yf"
	]
# these attributes will not show up on most spreadsheets
CLASS_ATTRIBUTES = ["testing_reset_fields",
	"nasdaq_symbol",
	"aaii_symbol",
	"yahoo_symbol",
	"morningstar_symbol",
	"yql_ticker",
	"epoch",
	"created_epoch",
	"updated",
	"ticker_relevant",
	"last_yql_basic_scrape_update",
	"last_balance_sheet_update_yf",
	"last_balance_sheet_update_ms",
	"last_cash_flow_update_yf",
	"last_cash_flow_update_ms",
	"last_income_statement_update_yf",
	"last_income_statement_update_ms",
	"last_key_ratios_update_ms",
	"last_aaii_update_aa",
	"held_list"
	]

NUMBER_OF_DEAD_TICKERS_THAT_SIGNALS_AN_ERROR = 100
# when downloading tickers, if more than this number of tickers appear to have fallen off the exchange
# it is probably the case that something went wrong, rather than it being a legitimate number.


STOCK_SCRAPE_UPDATE_ATTRIBUTES = ["last_yql_basic_scrape_update",

	"last_balance_sheet_update_yf",
	"last_cash_flow_update_yf",
	"last_income_statement_update_yf",

	"last_balance_sheet_update_ms",
	"last_cash_flow_update_ms",
	"last_income_statement_update_ms",

	"last_key_ratios_update_ms",


	]

HELD_STOCK_COLOR_HEX = "#FAEFCF"
NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX = "#8A0002"

NUMBER_OF_DEFAULT_PORTFOLIOS = 3

RANK_PAGE_ATTRIBUTES_THAT_DO_NOT_SORT_REVERSED = ["symbol", "firm_name"]

# Format below should match format here, otherwise errors! You may add fields, but ["button_text", "url", "width"] must exist.
# [string, string with relevant swap above, int]
# IMPORTANT: width is optional, and it's probably better no leave it off, but you can include it if you want to adjust button size
# IMPORTANT: if you want to edit a url, say for a redirect modification or something, then you can write a lambda function, but you must leave the width param in there even if blank.
RESEARCH_PAGE_DICT_LIST = [
	dict(button_text = "Annual Reports",
		 url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%(ticker)s&type=10-k&dateb=&owner=exclude&count=10",),
	dict(button_text = "Quartely Reports",
		 url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%(ticker)s&type=10-q&dateb=&owner=exclude&count=10"),
	#dict(button_text = "Yahoo Finance", url = "http://finance.yahoo.com/q?s=%(ticker)s"),
	dict(button_text = "Wolfram Alpha",  url = "https://www.wolframalpha.com/input/?i=%(firm_name)s+analyst+ratings&lk=5"),
	#dict(button_text = "Google Finance", url = "https://www.google.com/finance?q=%(ticker)s"),
	dict(button_text = "Morningstar",    url = "http://financials.morningstar.com/ratios/r.html?t=%(ticker)s&region=usa&culture=en-US"),
	#dict(button_text = "Bloomberg",      url = "http://www.bloomberg.com/quote/%(ticker)s:US"),
	dict(button_text = "Bloomberg News", url = "http://www.bloomberg.com/search?query=%(ticker)s&sort=time:desc&category=Articles"),
	dict(button_text = "Motley Fool",
		 url = "http://www.fool.com/quote/%(ticker)s",
		 width = -1,
		 lambda_function = lambda x: urllib2.urlopen(x).geturl() + "/analyst-opinion",),
	dict(button_text = "finviz", url = "http://www.finviz.com/quote.ashx?t=%(ticker)s",),
	dict(button_text = "Nasdaq Gurus", url = "http://www.nasdaq.com/symbol/%(ticker)s/guru-analysis")
	]

GENERAL_RESEARCH_PAGE_DICT_LIST = [
	dict(button_text = "FRED",
		 url = "https://research.stlouisfed.org/fred2/categories",),

	]

###################################################################################################
################# Do not edit below, all are reset to saved values on startup #####################
###################################################################################################
ABORT_YQL_SCRAPE = False

DASH = "--"
GLOBAL_PAGES_DICT = {}

# unique ids
MAIN_FRAME_UNIQUE_ID 		= "M"
# top level tabs
#
WELCOME_PAGE_UNIQUE_ID 			= "w"
GET_DATA_PAGE_UNIQUE_ID 		= "g"
#
# ## second level tabs
TICKER_PAGE_UNIQUE_ID				= "g_ti"
YQL_SCRAPE_PAGE_UNIQUE_ID			= "g_yq"
SPREADSHEET_IMPORT_PAGE_UNIQUE_ID	= "g_sp"
# ## ### third level tabs
XLS_IMPORT_PAGE_UNIQUE_ID 				= "g_sp_xls"
CSV_IMPORT_PAGE_UNIQUE_ID 				= "g_sp_csv"
# ## ###
# ##
#
PORTFOLIO_PAGE_UNIQUE_ID 		= "p"
VIEW_DATA_PAGE_UNIQUE_ID 		= "v"
#
# ##
ALL_STOCKS_PAGE_UNIQUE_ID 			= "v_al"
STOCK_DATA_PAGE_UNIQUE_ID 			= "v_st"
# ##
#
ANALYSE_PAGE_UNIQUE_ID 			= "a"
#
# ##
SCREEN_PAGE_UNIQUE_ID 				= "a_sc"
SAVED_SCREEN_PAGE_UNIQUE_ID 		= "a_sa"
RANK_PAGE_UNIQUE_ID 				= "a_ra"
CUSTOM_ANALYSE_META_PAGE_UNIQUE_ID= "a_pe"
# ##
#
RESEARCH_PAGE_UNIQUE_ID			= "r"
SALE_PREP_PAGE_UNIQUE_ID 		= "s"
TRADE_PAGE_UNIQUE_ID 			= "t"
USER_FUNCTIONS_PAGE_UNIQUE_ID 	= "u"
#
# ##
USER_CREATED_TESTS_UNIQUE_ID 			 = "u_cr"
USER_RANKING_FUNCTIONS_UNIQUE_ID 		 = "u_ra"
USER_CSV_IMPORT_FUNCTIONS_UNIQUE_ID 	 = "u_cs"
USER_XLS_IMPORT_FUNCTIONS_UNIQUE_ID 	 = "u_xl"
USER_PORTFOLIO_IMPORT_FUNCTIONS_UNIQUE_ID= "u_po"
USER_CUSTOM_ANALYSIS_FUNCTIONS_UNIQUE_ID = "u_cu"
# ##
#
GLOBAL_UNIQUE_ID_LIST = [
	WELCOME_PAGE_UNIQUE_ID,
	GET_DATA_PAGE_UNIQUE_ID,
	TICKER_PAGE_UNIQUE_ID,
	YQL_SCRAPE_PAGE_UNIQUE_ID,
	SPREADSHEET_IMPORT_PAGE_UNIQUE_ID,
	XLS_IMPORT_PAGE_UNIQUE_ID,
	CSV_IMPORT_PAGE_UNIQUE_ID,
	PORTFOLIO_PAGE_UNIQUE_ID,
	VIEW_DATA_PAGE_UNIQUE_ID,
	ALL_STOCKS_PAGE_UNIQUE_ID,
	STOCK_DATA_PAGE_UNIQUE_ID,
	ANALYSE_PAGE_UNIQUE_ID,
	SCREEN_PAGE_UNIQUE_ID,
	SAVED_SCREEN_PAGE_UNIQUE_ID,
	RANK_PAGE_UNIQUE_ID,
	CUSTOM_ANALYSE_META_PAGE_UNIQUE_ID,
	RESEARCH_PAGE_UNIQUE_ID,
	SALE_PREP_PAGE_UNIQUE_ID,
	TRADE_PAGE_UNIQUE_ID,
	USER_FUNCTIONS_PAGE_UNIQUE_ID,
	USER_CREATED_TESTS_UNIQUE_ID,
	USER_RANKING_FUNCTIONS_UNIQUE_ID,
	USER_CSV_IMPORT_FUNCTIONS_UNIQUE_ID,
	USER_XLS_IMPORT_FUNCTIONS_UNIQUE_ID,
	USER_PORTFOLIO_IMPORT_FUNCTIONS_UNIQUE_ID,
	USER_CUSTOM_ANALYSIS_FUNCTIONS_UNIQUE_ID,
	]
if len(GLOBAL_UNIQUE_ID_LIST) != len(set(GLOBAL_UNIQUE_ID_LIST)):
	# one of the ids is not unique
	print "Error: GLOBAL_UNIQUE_ID_LIST has duplicates"
	dummy_list = []
	duplicates = []
	for u_id in GLOBAL_UNIQUE_ID_LIST:
		if u_id not in dummy_list:
			dummy_list.append(u_id)
		else:
			duplicates.append(u_id)
	print duplicates
	sys.exit()

GLOBAL_TABS_DICT = {}

GLOBAL_STOCK_DICT = {}

GLOBAL_TICKER_LIST = []

GLOBAL_ATTRIBUTE_SET = set([])

ENCRYPTION_POSSIBLE = None
ENCRYPTION_HARDNESS_LEVEL = None

# Portfolio globals
PASSWORD = None


# Default name is "Primary"
NUMBER_OF_PORTFOLIOS = 0
PORTFOLIO_OBJECTS_DICT = {}
###

# Screen globals
GLOBAL_STOCK_SCREEN_DICT = {}
SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST = []
CURRENT_SCREEN_LIST = []
CURRENT_SAVED_SCREEN_LIST = []
RANK_PAGE_ALL_RELEVANT_STOCKS = []
###

SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE = [[],[]] # description below
# [[relevant portfolios list], [sale ticker|#shares tuple list]]

TICKER_AND_ATTRIBUTE_TO_UPDATE_TUPLE_LIST = []

HELD_STOCK_TICKER_LIST = []

CURRENT_EXCHANGE_FOR_NASDAQ_SCRAPE = None

SCRAPE_LOOP_STARTED = 0.0
SCRAPE_LOOP_QUEUE = [] # for "scrape_loop_for_missing_portfolio_stocks()" in scrapers

TIMER_THREAD_ON = False
def TIMER_PRINT():
	if TIMER_THREAD_ON:
		sys.stdout.write('.')
		sys.stdout.flush()
		threading.Thread(target = TIMER_THREAD).run()
def TIMER_THREAD():
	dot = threading.Timer(1., TIMER_PRINT)
	dot.start()




