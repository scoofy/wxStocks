# Add rank functions below:
# You can also edit this file (wxStocks_rank_functions.py) in your own text editor. 

########################################### instructions #######################################################
# functions should be of the following form:

#	def your_full_rank_function_name(Stock, decending=True, rank_error_as_median=True): 
#		# the stock will be provided by the program from a screen, please keep this as "stock, reversed=".
#		# "reversed" is tells the program whether you want your stocks with largest as better or smallest as metter.
#		# default ordering is largest is better 
#
#		"""short name""" # <--- this will appear in rank dropdowns
#
#		# add some functional property:
#		try:
#			relevant_value = Stock.attribute + Stock.other_attribute
#		except:
#			relevant_value = None
#
#		# Always return a 4-tuple of this form:
#		return (relevant_value, Stock, decending, rank_error_as_median)

################################################################################################################

def rank_stocks_by_peg_ratio(Stock, decending=False, rank_error_as_median=False):
	'''PEG ratio'''
	try:
		relevant_value = getattr(Stock, "PEGRatio_5_yr_expected_yf")
	except:
		relevant_value = None

	return (relevant_value, Stock, decending, rank_error_as_median)

def neff_ratio_5y(Stock, decending=True, rank_error_as_median=True): # requires only primary scrape
	'''5y Neff Ratio'''

	# relevant object attributes
	pe_attr = "PERatio_yf"
	peg_attr = "PEGRatio_5_yr_expected_yf"
	dividend_attr = "DividendYield_yf"

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
		peg5 = getattr(Stock, peg_attr)
		dividend_yield = getattr(Stock, dividend_attr)
		pe = getattr(Stock, pe_attr)
		#print "PEG =", peg5
		#print "type =", type(peg5)
		#print "Yield =", dividend_yield
		#print "type =", type(dividend_yield)
		#print "PE =", pe
		#print "type =", type(pe)

	except Exception, exception:
		print exception
		print "%s is missing required data" % Stock.symbol
		
		return (None, Stock, decending, rank_error_as_median)

		

	if peg5 in ["N/A", "none", "None", None]:
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

	#print "Neff 5 year for %s =" % Stock.symbol, neff5
	return (neff5, Stock, decending, rank_error_as_median)


















# end of line