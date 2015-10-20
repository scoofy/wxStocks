import logging, inspect, numpy, sys
from wxStocks_modules import wxStocks_utilities as utils
import aaii_utilities as aaii_utils
#from AAII_functions import aaii_utilities as aaii
#
# InstBuyFltP100 - Institutional Buys asd % of Float
# ([Institutions--shares purchased] - [Institutions--shares sold])*.1/[Float]
#
# Invtory2Sales - Ratio of inventory growth to sales growth. Number greater than 1 may indicate increase
# [Inventory Y1]*[Sales Y2]/([Inventory Y2]*[Sales Y1])
#
# Neff 5yrF
# 1/[PE to Div adj EPS Est growth]
#
# Neff 5yrH
# ([Yield]+[EPS Cont-Growth 5yr])/(PE)
#
# Neff LstY
# ([Yield]+[EPS-Growth 1yr])/(PE)
#
# Neff TTMH
# ([Yield]+[EPS Cont-Growth 12m])/(PE)
#
# NeffCf 3yrH - Neff using historical 3yr Cash Flow growth (instead of earnings)
# ([Yield] + [Cash Flow-Growth 3yr])/[Price/CFPS]
#
# NeffCf 5yrH - Neff using historical 5yr Cash Flow growth (instead of earnings)
# ([Yield] + [Cash Flow-Growth 5yr])/[Price/CFPS]
#
# NeffCf TTM - Neff using historical TTM Cash Flow growth (instead of earnings)
# ([Yield] + [Cash Flow-Growth 12m])/[Price/CFPS]
#
# NeffR 5yrH
# [Neff 5yrH]/[NeffCf 5yrH]
#
# NeffR TTM
# [Neff TTMH]/[NeffCf TTM]
#
# Prc2BookGrwth
# ([Price Y1]*[Book value/share Y3])/[Book value/share Y1]
#
# Prc2Rng
# ([Price]-[Price--low 52 weex])/([Price--high 52 week]-[Price--low 52 week])
#
# ROE3YrAvg
# ([Return on equity Y1]+[Return on equity Y2]+[Return on equity Y3])/3
#
# ROEsig2mu - Coefficient of Variation (STD/Avg) for ROE
# (([Return on equity Y1]-[ROE3YrAvg])^2 + ([Return on equity Y2]-[ROEYrAvg])^2 + ([Return on equity Y3]-[ROE3YrAvg])^2)^0.5/(3^0.5*[ROE3YrAvg])
#
#

def aaii_price(Stock):
	try:
		return float(Stock.Price_aa)
	except:
		return None

def aaii_volume(Stock):
	try:
		return float(Stock.Volume__Dollar_Daily_Avg_3m_aa)
	except:
		return None

def neff_3yr_H_x2yield(Stock): # john's formula
	try:
		eps = float(Stock.EPS_Growth_3yr_aa)
	except Exception, exception:
		print line_number(), exception
		print line_number(), "%s is missing required data" % (Stock.symbol)
		print "Stock.EPS_Cont_Growth_3yr_aa"
		return None

	try:
		dividend_yield = float(Stock.Yield_aa)
	except Exception, exception:
		print line_number(), exception
		print line_number(), "%s is missing required data" % (Stock.symbol)
		print "Stock.Yield_aa"
		dividend_yield = 0.

	try:
		pe = float(Stock.PE_aa)
	except Exception, exception:
		print line_number(), exception
		print line_number(), "%s is missing required data" % (Stock.symbol)
		print "Stock.PE_aa"
		return None

	if pe:
		neff = (eps + (dividend_yield * 2.)) / pe
	else:
		neff = None

	return neff

def neff_ratio(Stock, period): # period is either "F" (future) or "H" (historical)
	if period == "F":
		try:
			eps = float(Stock.EPS_Growth_Est_aa)
		except Exception, exception:
			print line_number(), exception
			print line_number(), "%s is missing required data" % (Stock.symbol)
			print "Stock.EPS_Growth_Est_aa"
			return None
	elif period == "H":
		try:
			eps = float(Stock.EPS_Cont_Growth_5yr_aa)
		except Exception, exception:
			print line_number(), exception
			print line_number(), "%s is missing required data" % (Stock.symbol)
			print "Stock.EPS_Cont_Growth_5yr_aa"
			return None
	try:
		dividend_yield = float(Stock.Yield_aa)
	except Exception, exception:
		print line_number(), exception
		print line_number(), "%s is missing required data" % (Stock.symbol)
		print "Stock.Yield_aa"
		dividend_yield = 0.

	try:
		pe = float(Stock.PE_aa)
	except Exception, exception:
		print line_number(), exception
		print line_number(), "%s is missing required data" % (Stock.symbol)
		print "Stock.PE_aa"
		return None

	if pe:
		neff = (eps + dividend_yield) / pe
	else:
		neff = None

	return neff

# Stock Valuation Functions: I use functions, rather than actual methods because they mess up spreadsheets with their superfluous object data

def neff_5_Year_future_estimate(Stock): # done!
	'''
	[Dividend Yield% + 5year Estimate of future %% EPS Growth]/PEttm
	(the last letter "F" in the name stands for "future" estimate, while "H" stands for "historical".)
	'''
	try:
		return 1./float(Stock.PE_to_Div_adj_EPS_Est_growth_aa)
	except:
		return None

	#return neff_ratio(Stock, period = "F")
def neff_TTM_historical(Stock, diluted=False, dividend_multiplier = 3.):
	'''
	[3 x Dividend Yield% + EPS (from continuing operations) historical Growth over TTM]/PEttm
	In this formula you can see that I gave triple weight to dividends.
	I thought that over the short run (TTM) dividends represent stability and "Dividends don't lie".
	-- Robert Schoolfield
	'''
	div_yield = 0.
	try:
		div_yield = float(Stock.Yield_aa)
	except:
		pass

	try:
		dividend_yield = div_yield#/100.
		if not diluted:
			eps_continuing_growth = float(Stock.EPS_Cont_Growth_12m_aa)#/100.
		else:
			eps_continuing_growth = float(Stock.EPS_Dil_Cont_Growth_12m_aa)#/100.
		pe = float(Stock.PE_aa)
	except Exception, exception:
		print line_number(), exception
		print line_number(), "%s is missing required data: .PE_aa, .EPS_Cont_Growth_12m_aa, or .EPS_Dil_Cont_Growth_12m_aa" % (Stock.symbol)
		print ".PE_aa:", Stock.PE_aa
		print ".EPS_Cont_Growth_12m_aa:", Stock.EPS_Cont_Growth_12m_aa
		print ".EPS_Dil_Cont_Growth_12m_aa:", Stock.EPS_Dil_Cont_Growth_12m_aa
		return None
	if pe:
		neff_TTM_historical = ((dividend_multiplier * dividend_yield) + eps_continuing_growth)/pe
	else:
		neff_TTM_historical = None
	return neff_TTM_historical
def neff_5_Year_historical(Stock, period = "H"):
	'''
	[3 x Dividend Yield% + EPS (from continuing operations) historical Growth over TTM]/PEttm
	In this formula you can see that I gave triple weight to dividends.
	I thought that over the short run (TTM) dividends represent stability and "Dividends don't lie".
	-- Robert Schoolfield
	'''
	return neff_ratio(Stock, period = "H")



def marginPercentRank(Stock):
	'''
	Return dictionary of stocks with their percentile rank, unless specific symbol inputed.
	If symbol inputed, return that stock's percentile rank.

	"Percent" Rank of ***Operating*** Margin where Highest Margin = 100%% and Lowest = 0%

	"Percent" Rank = ([Numerical Rank]/[Total Count of Numbers Ranked]) x 100
	If you are ranking 500 different companies, then [Total Count of Numbers Ranked] = 500
	'''
	try:
		return float(Stock.percent_Rank_Operating_margin_12m_aa)
	except Exception, exception:
		print line_number(), exception
		return None
def roePercentRank(Stock):
	'''
	Return dictionary of stocks with their percentile rank, unless specific symbol inputed.
	If symbol inputed, return that stock's percentile rank.

	%% Rank of Return on Equity.
	Bigger is better.
	'''
	try:
		return float(Stock.percent_Rank_Return_on_equity_12m_aa)
	except Exception, exception:
		print line_number(), exception
		return None

def roePercentDev(Stock):
	'''
	# ROE = Net Income / Shareholder's Equity
	# ROEsig2mu - Coefficient of Variation (STD/Avg) for ROE
	# (([Return on equity Y1]-[ROE3YrAvg])^2 + ([Return on equity Y2]-[ROE3YrAvg])^2 + ([Return on equity Y3]-[ROE3YrAvg])^2)^0.5/(3^0.5*[ROE3YrAvg])
	'''
	'''
	(
		([Return on equity Y1]- [ROE3YrAvg])^2
		+([Return on equity Y2]- [ROE3YrAvg])^2
		+([Return on equity Y3]- [ROE3YrAvg])^2
	)^0.5
	/
	(
		3^0.5
		*[ROE3YrAvg]
	)
	'''


	try:
		roe_data = [float(Stock.Return_on_equity_Y1_aa), float(Stock.Return_on_equity_Y2_aa), float(Stock.Return_on_equity_Y3_aa)]

		ROE_y1 = roe_data[0]
		ROE_y2 = roe_data[1]
		ROE_y3 = roe_data[2]

		ROE3YrAvg = (ROE_y1 + ROE_y2 + ROE_y3)/3.
		ROEsig2mu = (((ROE_y1-ROE3YrAvg)**2 + (ROE_y2-ROE3YrAvg)**2 + (ROE_y3-ROE3YrAvg)**2)**0.5)/((3**0.5)*(ROE3YrAvg))

		return ROEsig2mu
	except Exception, exception:
		print line_number(), "roePercentDev has failed due to the following exception:"
		print line_number(), exception
		print line_number(), "the equation will return None"
		return None

def price_to_book_growth(Stock):
	'''
	= Price Growth(over last 3 fiscal years)/Book Value Growth(over last 3 fiscal years)
	= (Price(Y1)/Price(Y3)) / (Book Value(Y1)/Book Value(Y3))
	= (Price(Y1)/Price(Y3)) x (Book Value(Y3)/Book Value(Y1))

	This is a ratio that Warren Buffet likes, so I thought I would throw it in.
	He says it tells him if growth in the Book Value of the company is reflected in the Price growth.
	He likes it around 1.
	'''
	price_year_1 = None # this is the present
	price_year_3 = None # this is the past
	bvps_year_1 = None
	bvps_year_3 = None

	try:
		price_year_1 = float(Stock.Price_Y1_aa)
		price_year_3 = float(Stock.Price_Y3_aa)
		bvps_year_1 = float(Stock.Book_value_to_share_Y1_aa)
		bvps_year_3 = float(Stock.Book_value_to_share_Y3_aa)

		price_growth_to_book_growth = (price_year_1/price_year_3)/(bvps_year_1/bvps_year_3)
		return price_growth_to_book_growth
	except Exception, exception:
		print line_number(), "price_to_book_growth has failed due to the following exception:"
		print line_number(), exception
		print line_number(), "the equation will return None"
		print line_number(), "this equation is incomplete, view notes for more details"
		return None
def price_to_range(Stock):
	'''
	= Price to (52 Week Price Range)
	= ([Current Price] - [52 wk Low Price]) / ([52 wk High Price] - [52 wk Low Price])

	If the current price is close to its 52 wk Low Price, then Prc2Rng is close to zero.
	If the current price is close to its 52 wk High Price, then Prc2Rng is close to one.
	If the current price is half way between its 52 wk High Price and its 52 wk Low Price,
	then Prc2Rng is close to 0.5.

	I like to have it greater than 0.2.
	'''
	# this uses the close in the equation, but should use live price
	#print line_number()
	#logging.warning("this uses the last closing price in the equation, but should use live price")
	current_price = float(Stock.Price_aa)
	the_52_week_low  = float(Stock.Price__low_52_week_aa)
	the_52_week_high = float(Stock.Price__high_52_week_aa)

	price_to_range_var = ((current_price - the_52_week_low)/(the_52_week_high - the_52_week_low))

	return price_to_range_var

def percentage_held_by_insiders(Stock): #done!
	try:
		percentage_held_by_insiders = Stock.Insider_Ownership_percent_aa
		if percentage_held_by_insiders:
			percentage_held_by_insiders = float(percentage_held_by_insiders)
		elif percentage_held_by_insiders == 0 or percentage_held_by_insiders == 0.:
			pass
		else:
			return None
		return percentage_held_by_insiders
	except Exception, exception:
		try:
			print line_number(), exception, "Stock.Insider_Ownership_percent_aa:", Stock.Insider_Ownership_percent_aa
		except:
			print line_number(), exception, "Stock.Insider_Ownership_percent_aa doesn't exist for %s", Stock.ticker
		return None

def net_institution_buy_percent(Stock):
	'''
	# InstBuyFltP100 - Institutional Buys asd % of Float
	# ([Institutions--shares purchased] - [Institutions--shares sold])*.1/[Float]
	'''
	try:
		bought = float(Stock.Institutions__shares_purchased_aa) * .1 # data in thousands
	except:
		bought = 0.
	try:
		sold = float(Stock.Institutions__shares_sold_aa) * .1 # data in thousands
	except:
		sold = 0.
	try:
		share_float = float(Stock.Float_aa) # data in millions
	except:
		print line_number(), "Stocks %s has not Stock.Shares_Average_Q1_aa"
		return None
	try:
		net_insiders_buy = (bought-sold)/share_float
	except Exception, exception:
		print line_number(), exception
		return None

	return net_insiders_buy

def net_institution_buy_percent_with_avg_not_float(Stock):
	'''
	# InstBuyFltP100 - Institutional Buys asd % of Float
	# ([Institutions--shares purchased] - [Institutions--shares sold])*.1/[Float]
	'''
	try:
		bought = float(Stock.Institutions__shares_purchased_aa) * 1000. # data in thousands
	except:
		bought = 0.
	try:
		sold = float(Stock.Institutions__shares_sold_aa) * 1000. # data in thousands
	except:
		sold = 0.
	try:
		avg_shares = float(Stock.Shares_Average_Q1_aa) * 1000000. # data in millions
	except:
		print line_number(), "Stocks %s has not Stock.Shares_Average_Q1_aa"
		return None
	try:
		net_insiders_buy = (bought-sold)/avg_shares
		net_insiders_buy = net_insiders_buy * 100.
	except Exception, exception:
		print line_number(), exception
		return None

	if Stock.ticker == "SLCA":
		print line_number()
		print "\n" * 10
		print "bought:\t", bought
		print "sold:\t", sold
		print "shares:\t", avg_shares
		print "net buy:\t", net_insiders_buy

	return net_insiders_buy

def percentage_held_by_institutions(Stock): #done!
	try:
		percentage_held_by_institutions = float(Stock.Institutional_Ownership_percent_aa)
		return percentage_held_by_institutions
	except Exception, exception:
		print line_number(), exception, ":", Stock.ticker, Stock.Institutional_Ownership_percent_aa
		return None

def current_ratio(Stock): #done! (trivial)
	try:
		current_ratio = float(Stock.Current_ratio_Q1_aa)
		return current_ratio
	except Exception, exception:
		print line_number(), exception
		print "Stock.Current_ratio_Q1_aa = ", Stock.Current_ratio_Q1_aa
		return None
def longTermDebtToEquity(Stock):
	try:
		long_term_debt_to_equity = float(Stock.LT_Debt_to_equity_Q1_aa)
		return long_term_debt_to_equity
	except Exception, exception:
		print line_number(), "longTermDebtToEquity has failed due to the following exception:"
		print line_number(), exception
		print line_number(), "the equation will return None"
		return None

def invtory2sales(Stock):
	'''
	# Invtory2Sales - Ratio of inventory growth to sales growth. Number greater than 1 may indicate increase
	# [Inventory Y1]*[Sales Y2]/([Inventory Y2]*[Sales Y1])
	'''
	try:
		inventory_y1 = float(Stock.Inventory_Y1_aa)
		sales_y2 = float(Stock.Sales_Y2_aa)
		numerator = inventory_y1 * sales_y2
	except:
		numerator = 0.

	try:
		inventory_y2 = float(Stock.Inventory_Y2_aa)
		sales_y1 = float(Stock.Sales_Y1_aa)
		denominator = inventory_y2 * sales_y1
	except:
		# undefined
		return None
	if denominator:
		inventory_to_sales = numerator/denominator
		return inventory_to_sales
	else:
		# undefined
		return None

################################################

def neffEvEBIT(Stock, dividend_multiplier = 2.): #done!
	'''
	Neff ratio replacing Earnings with EBIT and PE with [Enterprise Value/EBIT].
	With a double weight on Dividends.
	(Data reported by database for Enterprise Value and EBIT are not per share, but it doesn't matter because:
	[Enterprise Value/EBIT] = [Enterprise Value per share]/[EBIT per share]
	i.e. # of shares cancels in the ratio.
	Also:
	[EBIT growth %] = [EBIT per share growth %]
	are dimensionless ratios (written as percents).

	EBIT growth %% is calculated as the percent growth in EBIT (over 3 years)
	from the 4th fiscal year (Y5) before the most recent fiscal year (Y1)
	to the first fiscal year (Y2) before the most recent fiscal year(Y1).
	Why I didn't use Y1 I can't remember. The exact name of
	EBIT growth% = (([EBIT Y2]/[EBIT Y5]-1)^(1/3)) x 100
	(The 100 makes it a percentage value.)

	So NeffEv EBIT = (2 x [DivYield%] + [EBIT Growth%])/([Enterprise Value]/[EBIT])
	'''

	try:
		dividend_yield = float(Stock.Yield_aa)/100.
	except:
		dividend_yield = 0.

	try:
		ebit = float(Stock.EBIT_Y1_aa)
		ebit_y2 = float(Stock.EBIT_Y2_aa)
		ebit_y5 = float(Stock.EBIT_Y5_aa)
		ebit_change = ((ebit_y2 / ebit_y5)-1.)
		ebit_change_negative = False
		if ebit_change < 0.:
			ebit_change = abs(ebit_change)
			ebit_change_negative = True
		ebit_growth = ebit_change**(1./3.)
		ebit_growth = ebit_growth * 100.
		if ebit_change_negative:
			ebit_growth = -(ebit_growth)
		enterprise_value = float(Stock.Enterprise_Value_Q1_aa)
		neff_ev_ebit = ((dividend_multiplier * dividend_yield) + ebit_growth)/(enterprise_value/ebit)
		return neff_ev_ebit
	except Exception, exception:
		print line_number(), exception
		return None
def neffCf3Year(Stock, dividend_multiplier = None):
	'''
	(3 year Historical) Neff ratio where Earnings/Share is replaced by CashFlow/Share.

	NeffCf 3yrH - Neff using historical 3yr Cash Flow growth (instead of earnings)
	([Yield] + [Cash Flow-Growth 3yr])/[Price/CFPS]
	'''
	if not dividend_multiplier:
		dividend_multiplier = 1
	# numerator
	try:
		cash_flow_growth = float(Stock.Free_Cash_Flow_Growth_3yr_aa)
	except Exception, exception:
		print line_number(), exception
		print line_number(), "Warning: %s is missing required data" % (Stock.symbol)
		print "Stock.Free_Cash_Flow_Growth_3yr_aa"
		print "It will  be set to 0.00"
		cash_flow_growth = 0.

	try:
		dividend_yield = float(Stock.Yield_aa)
	except:
		dividend_yield = 0.

	# Denominator
	try:
		price_to_fcfps = float(Stock.Price_to_FCFPS_aa)
	except Exception, exception:
		print line_number(), exception
		print line_number(), "Warning: %s is missing required data" % (Stock.symbol)
		print "Stock.Price_to_FCFPS_aa"
		print "It cannot be set to 0, will return none as undefined"
		return None

	neff = ((dividend_yield * dividend_multiplier) + cash_flow_growth)/price_to_fcfps
	return neff

	# honestly not sure if this is correct.

def neffCf5Year(Stock, dividend_multiplier = 2.):
	'''
	(3 year Historical) Neff ratio where Earnings/Share is replaced by CashFlow/Share.

	NeffCf 3yrH - Neff using historical 3yr Cash Flow growth (instead of earnings)
	([Yield] + [Cash Flow-Growth 3yr])/[Price/CFPS]
	'''
	# numerator
	try:
		cash_flow_growth = float(Stock.Free_Cash_Flow_Growth_5yr_aa)
	except Exception, exception:
		print line_number(), exception
		print line_number(), "Warning: %s is missing required data" % (Stock.symbol)
		print "Stock.Free_Cash_Flow_Growth_5yr_aa"
		print "It will  be set to 0.00"
		cash_flow_growth = 0.

	try:
		dividend_yield = float(Stock.Yield_aa)/100.
	except:
		dividend_yield = 0.

	# Denominator
	try:
		price_to_fcfps = float(Stock.Price_to_FCFPS_aa)
	except Exception, exception:
		print line_number(), exception
		print line_number(), "Warning: %s is missing required data" % (Stock.symbol)
		print "Stock.Price_to_FCFPS_aa"
		print "It cannot be set to 0, will return none as undefined"
		return None

	neff = ((dividend_yield * dividend_multiplier) + cash_flow_growth)/price_to_fcfps
	return neff

	# honestly not sure if this is correct.


####################### Utility functions #################################################
def line_number():
	"""Returns the current line number in our program."""
	return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)

############################################################################################




