### Editable globals that may improve your performance ###

STOCK_EXCHANGE_LIST = ["nyse", "nasdaq"] #add "amex" if desired, non-american exchanges will not function at this point.
DEFAULT_STOCK_EXCHANGE_ATTRIBUTE = "StockExchange_yf"

DEFAULT_ENCRYPTION_HARDNESS_LEVEL = 8 # 1-24: i'm under the impression that 8 is the most secure hardness my processer can compute quickly

SCRAPE_CHUNK_LENGTH = 50
# Had errors with yql (yahoo query language) at greater numbers than 50

SCRAPE_SLEEP_TIME = 18
# this is a very important number
# approx 200 calls per hour (yql forums info)
# 3600 seconds in an hour
# 3600 / 200 = 18 seconds pause per query to stay under the 200/hour limit.
# Had ip banned for 24 hour periods scraping yql at a greater rate than this,
# however, their documentation says you can scrape at a faster rate.
# Note that i was banned for periods for scraping at the max rate they officially allow.
ADDITIONAL_DATA_SCRAPE_SLEEP_TIME = 2 
# Less important, because the number of scraping functions you exicute multiplies this by site, 
# but you should adjust this significantly if you get your ip banned.


ABORT_YQL_SCRAPE = False

TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE = float(60*60* 48) # 48 hours
# This is how long the program will reject rescraping stocks when looking for stocks that were not saved successfully.
TIME_ALLOWED_FOR_BEFORE_YQL_DATA_NO_LONGER_APPEARS_IN_STOCK_LIST = float(24*60*60* 15) # 15 days


DEFAULT_ROWS_ON_SALES_PREP_PAGE = 9
DEFAULT_ROWS_ON_TRADE_PREP_PAGE_FOR_TICKERS = 6
# adjust these to your own preference


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

NUMBER_OF_DEAD_TICKERS_THAT_SIGNALS_AN_ERROR = 100
# when downloading tickers, if more than this number of tickers appear to have fallen off the exchange
# it is probably the case that something went wrong, rather than it being a legitimate number.

STOCK_SCRAPE_UPDATE_ATTRIBUTES = ["last_yql_basic_scrape_update",
	
	"last_yahoo_balance_sheet_update",
	"last_yahoo_cash_flow_update",
	"last_yahoo_income_statement_update",

	"last_morningstar_balance_sheet_update",
	"last_morningstar_cash_flow_update",
	"last_morningstar_income_statement_update",

	"last_morningstar_key_ratios_update",


	]

HELD_STOCK_COLOR_HEX = "#FAEFCF"
NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX = "#8A0002"

NUMBER_OF_DEFAULT_PORTFOLIOS = 3

###################################################################################################
################# Do not edit below, all are reset to saved values on startup #####################
###################################################################################################
GLOBAL_STOCK_DICT = {}

GLOBAL_TICKER_LIST = []

ENCRYPTION_POSSIBLE = None
ENCRYPTION_HARDNESS_LEVEL = None

# Portfolio globals
PASSWORD = None

DATA_ABOUT_PORTFOLIOS = [NUMBER_OF_DEFAULT_PORTFOLIOS,[]] 
# Structure of this variable below, 
# see "wxStocks_db_functions.load_DATA_ABOUT_PORTFOLIOS" for more info about loading.

# DATA_ABOUT_PORTFOLIOS = 	[
#								NUMBER_OF_PORTFOLIOS (this will be an integer),
#								[
#									"Portfolio Name" (this will be a string), 
#									etc...
#								]
#							]
DEFAULT_DATA_ABOUT_PORTFOLIOS = [NUMBER_OF_DEFAULT_PORTFOLIOS, []]

# Default name is "Primary"
NUMBER_OF_PORTFOLIOS = 0
PORTFOLIO_NAMES = []

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







