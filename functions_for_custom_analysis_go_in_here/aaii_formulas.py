import logging, inspect, numpy, sys
from wxStocks_modules import wxStocks_utilities as utils
import aaii_utilities as aaii_utils
#from AAII_functions import aaii_utilities as aaii

def neff_ratio_5y(Stock): # requires only primary scrape
	# Neff is total return/PE. Source: http://www.forbes.com/2010/06/01/tupperware-cvs-astrazeneca-intelligent-investing-neff-value.html
	# Total return is defined as: EPS growth rate + dividend yield
	# Now YQL provides his data:
	##	PEG 5 year = PE/EPS Growth 5 Year
	##	Yield = Dividend Yield
	##	PE = PE
	####
	## Therefore
	# Neff 5 year = (1 / PEG 5 year) + (Yield / PE)
	# thus:
	try:
		peg5 = Stock.PE_to_EPS_Est_growth_5_years_aa
		dividend_yield = Stock.Yield_aa
		pe = Stock.PE_aa

	except Exception, exception:
		print exception
		print line_number(), "%s is missing required data" % (Stock.symbol)
		return None

	if peg5 is None or str(peg5) == "N/A":
		peg5 = None
	else:
		peg5 = float(peg5)

	if dividend_yield == "None" or dividend_yield is None:
		dividend_yield = 0.
	else:
		dividend_yield = float(dividend_yield)/100.

	if pe is None:
		pass
	else:
		pe = float(pe)/100.

	if peg5 and pe:
		neff5 = (1. / peg5) + (dividend_yield / pe)
	else:
		neff5 = None

	#print "Neff 5 year =", neff5
	return neff5

# Stock Valuation Functions: I use functions, rather than actual methods because they mess up spreadsheets with their superfluous object data

def neff_5_Year_future_estimate(Stock): # done!
	'''
	[Dividend Yield% + 5year Estimate of future %% EPS Growth]/PEttm
	(the last letter "F" in the name stands for "future" estimate, while "H" stands for "historical".)
	'''
	return neff_ratio_5y(Stock)
def neff_TTM_historical(Stock, diluted=False):
	'''
	[3 x Dividend Yield% + EPS (from continuing operations) historical Growth over TTM]/PEttm
	In this formula you can see that I gave triple weight to dividends.
	I thought that over the short run (TTM) dividends represent stability and "Dividends don't lie".
	-- Robert Schoolfield
	'''
	dividend_multiplier = 3.

	try:
		dividend_yield = float(Stock.Yield_aa)/100.
		if not diluted:
			eps_continuing_growth = float(Stock.EPS_Cont_Growth_12m_aa)/100.
		else:
			eps_continuing_growth = float(Stock.EPS_Dil_Cont_Growth_12m_aa)/100.
		pe = float(Stock.PE_aa)
	except Exception, exception:
		print exception
		print line_number(), "%s is missing required data: .Yield_aa, .EPS_Cont_Growth_12m_aa, or .EPS_Dil_Cont_Growth_12m_aa" % (Stock.symbol)
		return None
	if pe:
		neff_TTM_historical = ((dividend_multiplier * dividend_yield) + eps_continuing_growth)/pe
	else:
		neff_TTM_historical = None
	return neff_TTM_historical




def marginPercentRank(Stock):
	'''
	Return dictionary of stocks with their percentile rank, unless specific symbol inputed.
	If symbol inputed, return that stock's percentile rank.

	"Percent" Rank of Net Margin where Highest Margin = 100%% and Lowest = 0%

	"Percent" Rank = ([Numerical Rank]/[Total Count of Numbers Ranked]) x 100
	If you are ranking 500 different companies, then [Total Count of Numbers Ranked] = 500
	'''
	try:
		return float(Stock.percent_Rank_Net_margin_12m_aa)
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
	Coefficient of Variation for (ROE(Y1), ROE(Y2), ROE(Y3))

	= [Standard Deviation of (ROE(Y1), ROE(Y2), ROE(Y3))]/[Average of (ROE(Y1), ROE(Y2), ROE(Y3))]
	This determines how "smooth" the graph is of ROE for the three different years.
	Less than one is "smooth" while greater than one is "not smooth".
	It also determines if the average ROE over the three years is significantly greater than zero.
	'''
	# ROE = Net Income / Shareholder's Equity
	try:
		roe_data = [float(Stock.Return_on_equity_Y1_aa), float(Stock.Return_on_equity_Y2_aa), float(Stock.Return_on_equity_Y3_aa)]

		roe_mean = numpy.mean(roe_data)
		roe_standard_deviation = numpy.std(roe_data)

		roe_percent_deviation = float(roe_standard_deviation) / float(roe_mean)
		return roe_percent_deviation
	except Exception, exception:
		print "roePercentDev has failed due to the following exception:"
		print exception
		print "the equation will return None"
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
		print "price_to_book_growth has failed due to the following exception:"
		print exception
		print "the equation will return None"
		print "this equation is incomplete, view notes for more details"
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
	print line_number()
	logging.warning("this uses the last closing price in the equation, but should use live price")
	current_price = float(Stock.Price_aa)
	the_52_week_low  = float(Stock.Price__low_52_week_aa)
	the_52_week_high = float(Stock.Price__high_52_week_aa)

	price_to_range_var = ((current_price - the_52_week_low)/(the_52_week_high - the_52_week_low))

	return price_to_range_var

def percentage_held_by_insiders(Stock): #done!
	try:
		percentage_held_by_insiders = float(Stock.Insider_Ownership_percent_aa)
		return percentage_held_by_insiders
	except Exception, exception:
		print line_number(), exception
		return None
def percentage_held_by_institutions(Stock): #done!
	try:
		percentage_held_by_institutions = float(Stock.Institutional_Ownership_percent_aa)
		return percentage_held_by_institutions
	except Exception, exception:
		print line_number(), exception
		return None

def current_ratio(Stock): #done! (trivial)
	try:
		current_ratio = float(Stock.Current_ratio_Y1_aa)
		return current_ratio
	except Exception, exception:
		print line_number(), exception
		return None
def longTermDebtToEquity(Stock):
	try:
		long_term_debt_to_equity = float(Stock.LT_Debt_to_equity_Y1_aa)
		return long_term_debt_to_equity
	except Exception, exception:
		print "longTermDebtToEquity has failed due to the following exception:"
		print exception
		print "the equation will return None"
		return None

def neffEvEBIT(Stock): #done!
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
		dividend_multiplier = 2.
		dividend_yield = float(Stock.Yield_aa)
		ebit = float(Stock.EBIT_12m_aa)
		ebit_y2 = float(Stock.EBIT_Y2_aa)
		ebit_y5 = float(Stock.EBIT_Y5_aa)
		ebit_growth = (((ebit_y2 / ebit_y5)-1.)**(1./3.)) * 100.
		enterprise_value = float(Stock.Enterprise_Value_Y1_aa)
		neff_ev_ebit = ((dividend_multiplier * dividend_yield) + ebit_growth)/(enterprise_value/ebit)
		return neff_ev_ebit
	except Exception, exception:
		print line_number(), exception
		return None
def neffCf3Year(Stock): # incomplete: not sure if e/s should be eps growth... very confusing
	'''
	(3 year Historical) Neff ratio where Earnings/Share is replaced by CashFlow/Share.
	'''
	try:
		price = float(Stock.Price_aa)
		cash_flow_per_share = float(Stock.Cash_flow_to_share_12m_aa)
		price_to_cash_flow = price/cash_flow_per_share
		dividend_yield = float(Stock.Yield_aa)
		cashflow_growth_3_years = float(Stock.Cash_Flow_Growth_3yr_aa) # i think this is right because they have Y0 estimates
		cf_to_growth_3_year = price_to_cash_flow / cashflow_growth_3_years
		return cf_to_growth_3_year
	except Exception, exception:
		print exception
		return None

	# honestly not sure if this is correct.

####################### Utility functions #################################################
def line_number():
	"""Returns the current line number in our program."""
	return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)

############################################################################################




