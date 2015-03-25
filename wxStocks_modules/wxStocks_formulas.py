import logging, inspect, numpy

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
		peg5 = Stock.PEGRatio_5_yr_expected
		dividend_yield = Stock.DividendYield
		pe = Stock.PERatio
		#print "PEG =", peg5
		#print "type =", type(peg5)
		#print "Yield =", dividend_yield
		#print "type =", type(dividend_yield)
		#print "PE =", pe
		#print "type =", type(pe)

	except Exception, exception:
		print exception
		print line_number(), "%s is missing required data" % Stock.symbol
		return None

	if peg5 is None or str(peg5) == "N/A":
		peg5 = None
	else:
		peg5 = float(peg5)

	if dividend_yield == "None" or dividend_yield is None:
		dividend_yield = 0.00
	else:
		dividend_yield = float(dividend_yield)

	if pe is None:
		pass
	else:
		pe = float(pe)


	#print "PEG =", peg5
	#print "type =", type(peg5)
	#print "Yield =", dividend_yield 
	#print "type =", type(dividend_yield)
	#print "PE =", pe
	#print "type =", type(pe)

	if peg5 and pe:
		neff5 = (1 / peg5) + (dividend_yield / pe)
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
def neff_TTM_historical(Stock, annual_data, diluted=False): # Maybe done... double check the math (complicate formula)
	'''
	[3 x Dividend Yield% + EPS (from continuing operations) historical Growth over TTM]/PEttm 
	In this formula you can see that I gave triple weight to dividends.  
	I thought that over the short run (TTM) dividends represent stability and "Dividends don't lie".
	-- Robert Schoolfield
	'''
	if not annual_data:
		print "You must update annual data for %s" % Stock.symbol
		return None
	try:
		dividend_yield = float(Stock.DividendYield)/100
	except Exception, exception:
		print exception
		dividend_yield = 0

	# Get Eps from continuing operations (Income from continuing - Preferred Dividends)/Weight avg common shares
	# Step 1: Income from continuing operations
	try:
		income_from_continuing_operations = annual_data.Net_income_from_continuing_operations_ttm
	except Exception, exception:
		print exception
		try:
			income_from_continuing_operations = annual_data.Net_income_from_continuing_ops_ttm
		except Exception, exception:
			print exception
			income_from_continuing_operations = None

	# Step 2: Calculate EPS from continuing operations t1y

	try:
		income_from_continuing_operations_t1y = annual_data.Net_income_from_continuing_operations_t1y
	except Exception, exception:
		print exception
		try:
			income_from_continuing_operations_t1y = annual_data.Net_income_from_continuing_ops_t1y
		except Exception, exception:
			print exception
			income_from_continuing_operations_t1y = None

	# Step 3: Preferred Dividends
	try:
		preferred_dividend = annual_data.Preferred_dividend_ttm
		preferred_dividend = float(preferred_dividend)
	except Exception, exception:
		#print exception
		preferred_dividend = 0.00

	# Step 4: Preferred Dividends t1y
	try:
		preferred_dividend_t1y = annual_data.Preferred_dividend_t1y
		preferred_dividend_t1y = float(preferred_dividend_t1y)
	except Exception, exception:
		#print exception
		preferred_dividend_t1y = 0.00

	# Step 5: Weighted average common shares
	if not diluted:
		weighted_avg_common_shares_ttm = annual_data.Weighted_average_shares_outstanding_Basic_ttm
	else:
		weighted_avg_common_shares_ttm = annual_data.Weighted_average_shares_outstanding_Diluted_ttm

	# Step 6: Weighted average common shares t1y
	if not diluted:
		weighted_avg_common_shares_t1y = annual_data.Weighted_average_shares_outstanding_Basic_t1y
	else:
		weighted_avg_common_shares_t1y = annual_data.Weighted_average_shares_outstanding_Diluted_t1y


	# Step 7: Calculate EPS from continuing operations ttm

	eps_from_contiuning_operations = (income_from_continuing_operations - preferred_dividend)/weighted_avg_common_shares_ttm

	# Step 8: Calculate EPS from continuing operations t1y

	eps_from_contiuning_operations_t1y = (income_from_continuing_operations_t1y - preferred_dividend_t1y)/weighted_avg_common_shares_t1y

	# Step 9: Calculate EPS from continuing operations growth from t1y to ttm:

	eps_from_continuing_growth = ( (eps_from_contiuning_operations - eps_from_contiuning_operations_t1y)/ eps_from_contiuning_operations_t1y ) # note: NOT x 100 (want the decimal)

	numerator = (3 * dividend_yield) + eps_from_continuing_growth

	pe_ttm = Stock.TrailingPE_ttm
	pe_ttm = float(pe_ttm)

	neff_TTM_historical_result = numerator/pe_ttm

	return neff_TTM_historical_result

def marginPercentRank(Stock, stock_list): #mostly done, but need to add how to deal with error cases
	'''
	"Percent" Rank of Net Margin where Highest Margin = 100%% and Lowest = 0%

	"Percent" Rank = ([Numerical Rank]/[Total Count of Numbers Ranked]) x 100
	If you are ranking 500 different companies, then [Total Count of Numbers Ranked] = 500
	'''
	num_of_stocks = len(stock_list)
	sort_list = []
	error_count = 0
	for this_stock in stock_list:
		try:
			margin = this_stock.ProfitMargin_ttm
			symbol = this_stock.symbol
			if margin[-1] == "%":
				margin = margin[:-1]
				margin = float(margin)
				sort_list.append([margin, symbol])
			else:
				if error_count < 5:
					print line_number(), "Format of profit margin unknown"
				error_count+=1

		except Exception, exception:
			# There needs to be a case here for stocks that fail... ideally there should be none though
			if error_count < 5:
				print line_number(), exception, "Stock appears to have no ProfitMargin_ttm attribute."
			error_count+=1

	if len(sort_list) > 1:
		sort_list.sort(key = lambda x: x[0], reverse=False) # Highest ranking ends last, i.e. closer to 100%

	if len(stock_list) != len(sort_list):
		print "Error: Some Stocks not included in margin rank function"
		return

	position = None
	count = 1 # Need to use ordinal numbering
	for some_tuple in sort_list:
		if Stock.symbol == some_tuple[1]:
			position = count

	if not position:
		print "Error: Something went wrong in margin rank function, no position for", Stock.symbol
		return

	position = float(position)
	rank = (position/num_of_stocks) * 100
	return rank

def roePercentRank(Stock, stock_list): #done!
	'''
	%% Rank of Return on Equity.
	Bigger is better.
	'''
	total_number_of_stocks_in_list = len(stock_list)
	ticker_roe_tuple_list = [] # this is because i need to convert roe strings into floats
	no_roe_list = [] # this will tell me below, if the stock should be counted as tied for 1st percentile
	for i in stock_list:
		try:
			i.ReturnonEquity_ttm
			if i.ReturnonEquity_ttm[-1] == "%":
				roe_float = float(i.ReturnonEquity_ttm[:-1])
				ticker_roe_tuple_list.append((i.symbol, roe_float))
			else:
				ticker_roe_tuple_list.append((i.symbol, None)) # this should automatically sort to the back of the list
				no_roe_list.append(i.symbol)

		except Exception, exception:
			#print exception
			ticker_roe_tuple_list.append((i.symbol, None)) # this should automatically sort to the back of the list
			no_roe_list.append(i.symbol)
	ticker_roe_tuple_list.sort(key = lambda x: x[1])

	#print ticker_roe_tuple_list
	position = None
	for i in ticker_roe_tuple_list:
		#checking the ticker against the desired stock to find percentile
		if Stock.symbol == i[0]:
			position = ticker_roe_tuple_list.index(i)
			position += 1 # This is necessary to prevent dividing by zero cases, also for the calculation
	# check and see if Stock was actually in the stock list
	if position is not None: 
		percentile = float(position)/float(total_number_of_stocks_in_list)
		if Stock.symbol in no_roe_list:
			percentile = 0.00 # tied for lowest possible percentile
		print "total number of stocks =", total_number_of_stocks_in_list
		print "%s's position =" % Stock.symbol, position
		print "percentile =", percentile
		return percentile
	else:
		logging.error("roePercentRank: Stock was not in stock_list")
		return None
def roePercentDev(Stock, annual_data): #done!
	'''
	Coefficient of Variation for (ROE(Y1), ROE(Y2), ROE(Y3)) 

	= [Standard Deviation of (ROE(Y1), ROE(Y2), ROE(Y3))]/[Average of (ROE(Y1), ROE(Y2), ROE(Y3))]  
	This determines how "smooth" the graph is of ROE for the three different years.  
	Less than one is "smooth" while greater than one is "not smooth".
	It also determines if the average ROE over the three years is significantly greater than zero. 
	'''
	# ROE = Net Income / Shareholder's Equity
	if not annual_data:
		print "Error: there is no annual data for %s" % Stock.symbol
		return

	try:
		net_income_Y1 = float(annual_data.Net_income)
		shareholder_equity_Y1 = float(annual_data.Stockholders_equity)
		roe_Y1 = net_income_Y1 / shareholder_equity_Y1

		net_income_Y2 = float(annual_data.Net_income_t1y)
		shareholder_equity_Y2 = float(annual_data.Stockholders_equity_t1y)
		roe_Y2 = net_income_Y1 / shareholder_equity_Y2

		net_income_Y3 = float(annual_data.Net_income_t2y)
		shareholder_equity_Y3 = float(annual_data.Stockholders_equity_t2y)
		roe_Y3 = net_income_Y3 / shareholder_equity_Y3

		roe_data = [roe_Y1, roe_Y2, roe_Y3]

		roe_mean = numpy.mean(roe_data)
		roe_standard_deviation = numpy.std(roe_data)

		roe_percent_deviation = roe_standard_deviation / roe_mean
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
	price_year_3 = None # this is the present
	price_year_1 = None # this is the past
	book_value_year_3 = None
	book_value_year_1 = None

	try:
		# Book Value = Total Assets - Intangibles - Liabilities
		# or
		# Book Value = Total Shareholders Equity - Preferred Equity
		total_stockholder_equity_year_3 = Stock.Stockholders_equity
		total_stockholder_equity_year_1 = Stock.Stockholders_equity_t2y

		# Additional Paid in Capital is capital surplus
		try:
			capital_surplus_year_3 = Stock.Additional_paid_in_capital
			capital_surplus_year_1 = Stock.Additional_paid_in_capital_t2y
		except:
			capital_surplus_year_3 = Stock.Capital_Surplus
			capital_surplus_year_1 = Stock.Capital_Surplus_t2y

		# Treasury Stock
		try:
			treasury_stock_year_3 = Stock.Treasury_stock
			treasury_stock_year_1 = Stock.Treasury_stock_t2y
		except:
			treasury_stock_year_3 = 0
			treasury_stock_year_1 = 0


	except Exception, exception:
		print "price_to_book_growth has failed due to the following exception:"
		print exception
	print "the equation will return None"
	print "this equation is incomplete, view notes for more details"
	return None

	# So, here is the issue, we need price/book growth
	# morningstar has book value trailing 5 years, but not price to book
	# morningstar also has price trailing 5 years in a decent format, but they'll both have to be scraped
	# should be able to combine the two and easily finish this formula
	


def kGrowth(Stock): # incomplete, no definition yet
	print "kGrowth is incomplete ---- no definition for formula yet"
	print "this function will return None"
	return None
def price_to_range(Stock): #done!
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
	logging.warning("this uses the close in the equation, but should use live price")
	current_price = float(Stock.PreviousClose)
	the_52_week_low  = float(Stock.p_52_WeekLow)
	the_52_week_high = float(Stock.p_52_WeekHigh)

	price_to_range_var = ((current_price - the_52_week_low)/(the_52_week_high - the_52_week_low))

	return price_to_range_var

def percentage_held_by_insiders(Stock): #done!
	try:
		if Stock.PercentageHeldbyInsiders:
			if "%" in Stock.PercentageHeldbyInsiders:
				#print Stock.PercentageHeldbyInsiders
				percentage_held_by_insiders = Stock.PercentageHeldbyInsiders[:-1]
				#print percentage_held_by_insiders
				percentage_held_by_insiders = float(percentage_held_by_insiders)
			else:
				percentage_held_by_insiders = float(Stock.PercentageHeldbyInsiders)
			return percentage_held_by_insiders
	except Exception, exception:
		print line_number(), exception
		return None
def percentage_held_by_institutions(Stock): # this may not be necessary
	try:
		if Stock.PercentageHeldbyInstitutions:
			if "%" in Stock.PercentageHeldbyInstitutions:
				print Stock.PercentageHeldbyInstitutions
				percentage_held_by_institutions = Stock.PercentageHeldbyInstitutions[:-1]
				print percentage_held_by_institutions
				percentage_held_by_institutions = float(percentage_held_by_institutions)
			else:
				percentage_held_by_institutions = float(Stock.PercentageHeldbyInstitutions)
			return percentage_held_by_institutions
	except Exception, exception:
		print line_number(), exception
		return None
def current_ratio(Stock): #done! (trivial)
	try:
		if Stock.CurrentRatio_mrq:
			current_ratio = float(Stock.CurrentRatio_mrq)
			return current_ratio
	except Exception, exception:
		print line_number(), exception
		return None
def longTermDebtToEquity(Stock, annual_data):
	try:
		if not annual_data:
			print Stock.symbol, "has no annual data. The longTermDebtToEquity function should be updated here to download annual data in a pinch if it is not here."
		long_term_debt = annual_data.Long_term_debt
		equity = annual_data.Stockholders_equity
		if long_term_debt == "-":
			long_term_debt = 0.00
		else:
			long_term_debt = float(long_term_debt)
		if equity == "-":
			print 'Cannot divide by zero'
			return "None"
		else:
			equity = float(equity)
		return float(long_term_debt/equity)
	except Exception, exception:
		print "longTermDebtToEquity has failed due to the following exception:"
		print exception
		print "the equation will return None"
		return None

def neffEvEBIT(Stock): #incomplete
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



	print "neffEvEBIT is incomplete ---- has not been written yet"
	print "this function will return None"
	return None
def neffCf3Year(Stock): #incomplete: not sure if e/s should be eps growth... very confusing
	'''
	(3 year Historical) Neff ratio where Earnings/Share is replaced by CashFlow/Share.
	'''
	# Neff is total return/PE. Source: http://www.forbes.com/2010/06/01/tupperware-cvs-astrazeneca-intelligent-investing-neff-value.html
	# Total return is defined as: EPS growth rate + dividend yield
	# Now YQL provides his data:
	##	PEG 5 year = PE/EPS Growth 5 Year

	# So our ratio needs to be CF/Share / eps growth 3year

	# Cash Flow Per Share = ("Operating" Cash Flow - Preferred Dividends) / Shares Outstanding
	# either:
	#### operating_cash_flow = float(Stock.OperatingCashFlow_ttm)
	# or 
	operating_cash_flow = float(Stock.Cash_Flows_From_Operating_Activities)
	# preferred stock dividends doesn't exist for many stocks:
	try:
		preferred_dividends = float(Stock.Preferred_dividend_ttm)
	except Exception, exception:
		print "if you have an exception here, it probably means that the stock doesn't pay preferred dividends, but it still should be noted."
		print exception
		preferred_dividends = 0.0
		print "preferred dividends have been set to zero"
	shares_outstanding = float(Stock.SharesOutstanding)

	# So CF/Share:
	cash_flow_per_share = (operating_cash_flow - preferred_dividends)/shares_outstanding

	### do we need the cf/share growth rate???

	##	Yield = Dividend Yield
	##	PE = PE
	####
	## Therefore
	# Neff 5 year = (1 / PEG 5 year) + (Yield / PE)
	# thus:
	print "This formula is incomplete and will return None"
	return None

stock_only_needed = [
	neff_5_Year_future_estimate, 
	price_to_book_growth, 
	kGrowth, 
	price_to_range, 
	percentage_held_by_insiders, 
	percentage_held_by_institutions,
	current_ratio,
	neffEvEBIT,
	neffCf3Year
	]
stock_plus_stock_list_needed = [
	marginPercentRank, 
	roePercentRank 
	]
annual_data_needed = [
	neff_TTM_historical, 
	roePercentDev,
	longTermDebtToEquity
	]
formula_list = stock_only_needed + stock_plus_stock_list_needed + annual_data_needed

####################### Utility functions #################################################
def line_number():
	"""Returns the current line number in our program."""
	return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)

############################################################################################