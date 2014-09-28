### Editable globals that may improve your performance ###

STOCK_EXCHANGE_LIST = ["nyse", "nasdaq"] #add "amex" if desired, non-american exchanges will not function at this point.

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

ABORT_YQL_SCRAPE = False

TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE = float(60*60* 48) # 48 hours
# This is how long the program will reject rescraping stocks when looking for stocks that were not saved successfully.
TIME_ALLOWED_FOR_BEFORE_YQL_DATA_NO_LONGER_APPEARS_IN_STOCK_LIST = float(24*60*60* 15) # 15 days


DEFAULT_ROWS_ON_SALES_PREP_PAGE = 9
DEFAULT_ROWS_ON_TRADE_PREP_PAGE_FOR_TICKERS = 6
# adjust these to your own preference


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
# these attributes will not show up on most spreadsheets

NUMBER_OF_DEAD_TICKERS_THAT_SIGNALS_AN_ERROR = 100
# when downloading tickers, if more than this number of tickers appear to have fallen off the exchange
# it is probably the case that something went wrong, rather than it being a legitimate number.

### Do not edit below, all are reset to saved values on startup ###
GLOBAL_STOCK_DICT = {}

GLOBAL_TICKER_LIST = []

ENCRYPTION_POSSIBLE = False
DATA_ABOUT_PORTFOLIOS = [] 
# Structure of this variable below, 
# see "wxStocks_db_functions.load_DATA_ABOUT_PORTFOLIOS" for more info about loading.

# DATA_ABOUT_PORTFOLIOS = 	[
#								NUMBER_OF_PORTFOLIOS (this will be an integer),
#								[
#									"Portfolio Name" (this will be a string), 
#									etc...
#								]
#							]

NUMBER_OF_PORTFOLIOS = 3 
# Default loads to 1
PORTFOLIO_NAMES = []
# Default name is "Primary"

PORTFOLIO_OBJECTS_DICT = {}

STOCK_SCREEN_DICT = {}

SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE = [[],[]] # description below
# [[relevant portfolios list], [sale ticker|#shares tuple list]]








