import locale
### Editable globals that may improve your performance ###
locale.setlocale(locale.LC_ALL, "") # this can be changed to show currency formats differently.
currency_symbol = "$"

STOCK_EXCHANGE_LIST = ["nyse", "nasdaq"] #add "amex", "BATS", "NYSEArca", "NYSEmkt", if desired, non-american exchanges will not function at this point.

DEFAULT_COMMISSION = 10.00

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

ONE_DAY = 86400.

TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE = ONE_DAY * 2 # 48 hours
# This is how long the program will reject rescraping stocks when looking for stocks that were not saved successfully.
TIME_ALLOWED_FOR_BEFORE_YQL_DATA_NO_LONGER_APPEARS_IN_STOCK_LIST = ONE_DAY * 15 # 15 days

PORTFOLIO_PRICE_REFRESH_TIME = ONE_DAY

# adjust these to your own preference

# these will depend on your preferred data sources
DEFAULT_LAST_TRADE_PRICE_ATTRIBUTE_NAME = "LastSale_na"
DEFAULT_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME = "AverageDailyVolume_yf"
DEFAULT_LAST_UPDATE = "last_nasdaq_scrape_update"
DEFAULT_STOCK_EXCHANGE_ATTRIBUTE = "Exchange_na"
DEFAULT_STOCK_WEBSITE_ATTRIBUTE = "Web_address_aa"
#--
SECONDARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME = "LastTradePriceOnly_yf"
SECONDARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME = None
SECONDARY_LAST_UPDATE = "last_yql_basic_scrape_update"
SECONDARY_STOCK_EXCHANGE_ATTRIBUTE = "StockExchange_yf"
SECONDARY_STOCK_WEBSITE_ATTRIBUTE = None
#---
TERTIARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME = None
TERTIARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME = None
TERTIARY_LAST_UPDATE = None
TERTIARY_STOCK_EXCHANGE_ATTRIBUTE = None
TERTIARY_STOCK_WEBSITE_ATTRIBUTE = None
#----
QUATERNARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME = None
QUATERNARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME = None
QUATERNARY_LAST_UPDATE = None
QUATERNARY_STOCK_EXCHANGE_ATTRIBUTE = None
QUATERNARY_STOCK_WEBSITE_ATTRIBUTE = None
#-------------------------------------------------

# There are irrelevant attributes listed in the config file.
# If you want to change them, they are there, and it's a big list.
# It would be a bit messy for this file.
