import math, numpy
from collections import namedtuple
def line_number():
	"""Returns the current line number in our program."""
	return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)

# Formulas from the CFA Curriculum: Equities
########## Equity Valuation ##########

# Mispricing:
def mispricing(estimated_value, market_price, intrinsic_value):

	# Ve - P = (V - P) + (Ve - V)


	Ve 	= float(estimated_value)
	P 	= float(market_price)
	V 	= float(intrinsic_value)

	estimated_mispricing = (Ve - P)
	actually_mispricing = (V - P)
	error = (Ve - V)
	# not exactly sure what, if anything, should be returned here


########## Return Concepts ##########

# Holding Period Return
def holding_period_return(initial_share_price,
						  share_price_after_holding_period,
						  per_share_dividend_after_holding_period):
	# r 	= rate_of_return
	
	### holding period: t = 0 -> t = h
	
	D_H = float(per_share_dividend_after_holding_period) 	# D = dividend, H = Holding period time unit
	P_H = float(share_price_after_holding_period)			# P = price, H = Holding period time unit
	P_0 = float(initial_share_price)						# P = price, 0 = Time unit value of 0

	# r = ((D_H + P_H)/P_0) - 1
	# r = (D_H/P_0) + (P_H - P_0)/P_0

	dividend_yield = D_H/P_0
	price_appreciation_return = (P_H-P_0)/P_0
	holding_period_return = dividend_yield + price_appreciation_return
	return holding_period_return

# alpha and required return
def expected_alpha(expected_return, required_return):
	expected_alpha = float(expected_return) - float(required_return)
	return expected_alpha

def realized_alpha(actual_holding_period_return, contemporanious_required_return):
	# contemporanious required return is the required return throughout the holding period
	realized_alpha = float(actual_holding_period_return) - float(contemporanious_required_return)
	return realized_alpha

# Internal Rate of Return
def internal_rate_of_return(year_ahead_dividend, estimated_dividend_growth_rate, share_price):
	# IRR = internal_rate_of_return # or required return assuming market efficiency
	D 	= float(year_ahead_dividend)
	P 	= float(share_price) # market_price
	E_Div_Growth = float(estimated_dividend_growth_rate)

	IRR = D/(P + E_Div_Growth)
	return IRR

# Equity Risk Premium
### version 1 (adjusts premium for share's partucular level of systematic risk)
def equity_risk_premium_for_share_ver_1(current_expected_risk_free_rate, beta_i):
	RFR_e 	= float(current_expected_risk_free_rate)
	#beta_i 	= equity_risk_premium
	required_return_on_share_i = RFR_e + float(beta_i)
	RR_i 	= required_return_on_share_i

	return RR_i


### version 2 (does not make beta adjustment to risk premium, but adds discounts and premia required to develope overall risk adjustment)
def equity_risk_premium_for_share_ver_2(current_expected_risk_free_rate, beta_i, other_risk_premia=[], discounts_for_i=[]):
	RFR_e 	= float(current_expected_risk_free_rate)
	#beta_i 	= equity_risk_premium
	other_risk_premia = sum(other_risk_premia)
	RR_i = RFR_e + float(beta_i) + (other_risk_premia / discounts_for_i)
	raise Exception("look this function up")

# Gordon Growth Model for estimating equity risk premium
def equity_risk_premium_via_gordon_growth_model(dividend_yield_on_index_based_on_year_ahead_aggeragate_forcasted_dividends_and_aggregate_market_value,
															consensus_long_term_earnings_growth_rate,
															current_long_term_govt_bond_yield):
	D_1		= float(dividend_yield_on_index_based_on_year_ahead_aggeragate_forcasted_dividends_and_aggregate_market_value)
	E_g 	= float(consensus_long_term_earnings_growth_rate)
	B_y 	= float(current_long_term_govt_bond_yield)

	GGM_ERP = D_1 + E_g - B_y
	
	gordon_growth_model_equity_risk_premium = GGM_ERP
	return gordon_growth_model_equity_risk_premium

# Macroeconomic estimates for equity risk premium 
# Total Return to Equity (Ibbotson & Chen)
def equity_risk_premium_ibbotson_and_chen(expected_inflation,
											real_EPS_expected_growth_rate,
											PE_ratio_expected_growth_rate,
											expected_income_component_including_reinvestment_of_income,
											expected_risk_free_rate):
	I_e 	 = float(expected_inflation) # formula below
	rEPS_r_e = float(real_EPS_expected_growth_rate) # should track real GDP growth rate (adjustments can be made)
	PE_r_e 	 = float(PE_ratio_expected_growth_rate) # baseline should be zero
	Income_e = float(expected_income_component_including_reinvestment_of_income) # use forward looking market yield
	RFR_e 	 = float(expected_risk_free_rate)

	ERP = (((1 + I_e)(1 + rEPS_r_e)(1 + PE_r_e) - 1) + Income_e) - RFR_e

	return ERP
### APPROXIMATE implicit inflation forcast
def implicit_inflation_forcast_approximation():
	Y_20t = float(treasury_bond_20_year_yield)
	Y_20tips = float(treasury_inflation_protected_security_20_year_yield)

	I_e = (1 + Y_20t)/(1 + Y_20tips) - 1 # APPROXIMATE, NOT EQUAL.

	approximate_explected_inflation = I_e
	return approximate_explected_inflation

# CAPM
### for the purpose of required return on equity
def CAPM_via_ERP(expected_risk_free_rate, beta_of_stock_i, equity_risk_premium):
	RFR_e = float(expected_risk_free_rate)
	beta_i = float(beta_of_stock_i)
	ERP = float(equity_risk_premium)

	RR_i = RFR_e + beta_i(ERP)

	required_return_on_share_i = RR_i

### formally, the capm is actually
def CAPM(risk_free_rate, beta_i, expected_return_on_market_portfolio):
	RFR = float(risk_free_rate)
	E_R_m = float(expected_return_on_market_portfolio)

	E_RR_i = RFR + float(beta_i)(E_R_m - RFR)

	expected_required_return_on_share_i = E_RR_i # in equilibrium
	return expected_required_return_on_share_i

# Beta Estimation for a Public Company (Blume 1971)
def adjusted_beta(raw_beta):
	adjusted_beta = (2./3.)*float(raw_beta) + (1./3.)

	forward_looking_beta = adjusted_beta
	return forward_looking_beta

# Beta Estimation for Private or thinly traded Company
def beta_estimate_for_private_or_thinly_traded_company(beta_from_comparable,
														debt_of_comparable,
														equity_of_comparable,
														debt_of_target,
														equity_of_target):
	beta_e = float(beta_from_comparable)
	D = float(debt_of_comparable)
	E = float(equity_of_comparable)
	D_prime = float(debt_of_target)
	E_prime = float(equity_of_target)

	beta_u = (1./(1.+(D/E)))*beta_e # APPROXIMATION
	# beta_u = unlevered_beta
	beta_e_prime = (1.+(D_prime/E_prime))*beta_u # APPROXIMATION
	# * note, this assumes the debt of the firms does not fluctuate,
	# 	otherwise use beta_u = ((1/(1+(D/E)))**-1) * (beta_e + (D/E)*debt_beta)

	estimated_target_beta = beta_e_prime
	return estimated_target_beta


# Multifactor Models

def multifactor_model_basic(risk_free_rate, stock, factor_sensitivity_and_risk_premium_attribute_name_tuple_list):
	# r = RFR + risk_premium_1 + ... + risk_premium_k
	# risk_premium_i = factory_sensitivity_i * factor_risk_premium_i
	RFR = float(risk_free_rate)

	# tuple list should contain the attribute names of each sinsitivity factor, and it's risk premium

	risk_premium_list = []
	for factor_tuple in factor_sensitivity_and_risk_premium_attribute_name_tuple_list:
		factor_sensitivity = float(getattr(stock, factor_tuple[0]))
		factor_risk_premium = float(getattr(stock, factor_tuple[1]))
		risk_premium_for_stock_i = factor_sensitivity * factor_risk_premium
		risk_premium_list.append(risk_premium_for_stock_i)

	sum_of_risk_premiums = 0.
	for risk_premium in risk_premium_list:
		sum_of_risk_premiums += risk_premium

	r = RFR + sum_of_risk_premiums

	estimated_required_return = r
	return estimated_required_return

# Fama-French Model (for data: http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
def fama_french_model(risk_free_rate,
						beta_mkt_sub_i,
						beta_size_sub_i,
						beta_value_sub_i,


						R_mkt_minus_RFR = None,
						small_minus_big = None,
						high_minus_low = None,

						return_on_value_weighted_market_index = None,
						small_cap_return_premium_equal_to_the_average_return_on_small_cap_portfolios = None,
						average_return_on_large_cap_portfolios = None,
						value_return_premium_equal_to_the_average_return_on_high_book_to_market_portfolios = None,
						average_return_on_low_book_to_market_portfolios = None,
						):
	# only one of the groups of keyword arguments is required

	if R_mkt_minus_RFR is None: # return on va
		R_F = float(risk_free_rate)
		R_M = float(return_on_value_weighted_market_index)
		R_mkt_minus_RFR = R_M - R_F # return on market value weighted index in excess of the one month t-bill rate
	else:
		R_mkt_minus_RFR = float(R_mkt_minus_RFR)

	# small-cap return premium
	if small_minus_big is None:
		R_small = float(small_cap_return_premium_equal_to_the_average_return_on_small_cap_portfolios)
		R_big = float(average_return_on_large_cap_portfolios)
	else:
		SMB = float(small_minus_big)
	
	# value return premium
	if high_minus_low is None:
		R_HBM = float(value_return_premium_equal_to_the_average_return_on_high_book_to_market_portfolios)
		R_LBM = float(average_return_on_low_book_to_market_portfolios)
		HML = R_HBM - R_LBM
	else:
		HML = float(high_minus_low) 

	beta_mkt_sub_i = float(beta_mkt_sub_i)
	beta_size_sub_i = float(beta_size_sub_i)
	beta_value_sub_i = float(beta_value_sub_i)

	r_i = R_F + beta_mkt_sub_i(RMRF) + beta_size_sub_i(SMB) + beta_value_sub_i(HML)

	required_return_on_share_i = r_i
	return required_return_on_share_i
# Pastor-Stambaugh Model
def pastor_strambaugh_model(liquidity_premium,
							liquidity,

							risk_free_rate,
							beta_mkt_sub_i,
							beta_size_sub_i,
							beta_value_sub_i,

							R_mkt_minus_RFR = None,
							small_minus_big = None,
							high_minus_low = None,

							return_on_value_weighted_market_index = None,
							small_cap_return_premium_equal_to_the_average_return_on_small_cap_portfolios = None,
							average_return_on_large_cap_portfolios = None,
							value_return_premium_equal_to_the_average_return_on_high_book_to_market_portfolios = None,
							average_return_on_low_book_to_market_portfolios = None,
							):

	Fama_French_Model = fama_french_model(risk_free_rate,
						beta_mkt_sub_i,
						beta_size_sub_i,
						beta_value_sub_i,


						R_mkt_minus_RFR,
						small_minus_big,
						high_minus_low,

						return_on_value_weighted_market_index,
						small_cap_return_premium_equal_to_the_average_return_on_small_cap_portfolios,
						average_return_on_large_cap_portfolios,
						value_return_premium_equal_to_the_average_return_on_high_book_to_market_portfolios,
						average_return_on_low_book_to_market_portfolios,
						)

	FFM = Fama_French_Model
	# liquidity premium
	LIQ = float(liquidity_premium)

	r_i = FFM + float(beta_liquidty_sub_i)*(LIQ)

	required_return_on_share_i = r_i
	return required_return_on_share_i

# Buildup Methods
def buildup_method(risk_free_rate, equity_risk_premium, discount_list):
	RFR = float(risk_free_rate)
	ERP = float(equity_risk_premium)
	discounts_for_i = 0.
	for discount in discount_list:
		discounts_for_i += float(discount)

	r_i = RFR + ERP + discounts_for_i

	required_return_on_share_i = r_i
	return required_return_on_share_i

### Bond Yield Plus Risk Premium
def bond_yield_plus_risk_premium_method(yield_to_market_for_firms_long_term_debt,
										risk_premium_for_equity_specific_concerns,):
	YTM_LTD = float(yield_to_market_for_firms_long_term_debt)
	risk_premium = float(risk_premium_for_equity_specific_concerns) # typically 3%-4%, note: debt risk is already included in YTM

	BYPRP = YTM_LTD + risk_premium

	bond_yield_plus_risk_premium_cost_of_equity = BYPRP
	return bond_yield_plus_risk_premium_cost_of_equity


# Equity Risk Premium: International considerations
def equity_risk_premium_with_international_considerations(equity_risk_premium_for_developed_markets,
															country_specific_premium):
	ERP_M = float(equity_risk_premium_for_developed_markets)
	country_premium = float(country_specific_premium) # typically: emerging market bond yield - developed market bond yield

	ERP = ERP_M + country_premium

	equity_risk_premium = ERP
	return equity_risk_premium

# WACC
def WACC(market_value_of_debt,
		market_value_of_common_equity,
		required_return_on_equity,
		required_return_on_debt,
		marginal_tax_rate):
	MVD = float(market_value_of_debt)
	MVCE = float(market_value_of_common_equity)
	r = float(required_return_on_equity)
	r_d = float(required_return_on_debt) # typically YTM of firm debt based on market values
	tax = float(marginal_tax_rate)

	WACC = ((MVD/(MVD-MVCE)) * r_d * (1. - tax)) + ((MVCE/(MVD-MVCE)) * r)

	weighted_avg_cost_of_capital = WACC
	return weighted_avg_cost_of_capital

# Forcasting (revist this often, it's very difficult)
# Forcasting Balance Sheet & Cash Flow (Modeling)

### ROIC
def return_on_invested_capital(net_operating_profit_less_adjusted_taxes,
								operating_assets,
								operating_liabilities):
	NOPLAT = float(net_operating_profit_less_adjusted_taxes)
	Investment_Capital = float(operating_assets) - float(operating_liabilities)

	ROIC = NOPLAT/Investment_Capital

	return_on_invested_capital = ROIC
	return return_on_invested_capital
### ROCE
def return_on_capital_employed(total_value_of_debt,
								total_value_of_equity,
								operating_profit,):
	Capital_Employed = float(total_value_of_debt) + float(total_value_of_equity)
	ROCE = float(operating_profit)/Capital_Employed

	return_on_capital_employed = ROCE # = ROIC before tax

# Discounted Dividend Models

# Present Value Models

# V_0 = sigma_1_to_n(CF_t/((1 + r)**t))
def present_value__holding_period_return(number_of_payments, 
										payment_list_or_value_if_stable, 
										discount_rate
										):
	
	#         n    CF_t
	# V_0 = sigma -------
	#        t=1  (1+r)^t

	r = float(discount_rate)

	if type(payment_list_or_value_if_stable) is list:
		payment_list = payment_list_or_value_if_stable
		payment_list_len_equal_to_t = payment_list
		if number_of_payments == len(payment_list_len_equal_to_t):
			pass
		else:
			print line_number(), "payment list not formated properly"
			return
	else:
		stable_payment_value = payment_list_or_value_if_stable
		payment_list_len_equal_to_t = []
		for i in range(number_of_payments):
			payment_list_len_equal_to_t.append(stable_payment_value)

	payment_list = payment_list_len_equal_to_t # just a list of payments, may be stable, increasing or decreasing. (even random)

	cash_flow_time_payment_dict = {} # {t: p} e.g. {1: $500, 2: $500, etc.}
	for i in range(number_of_payments):
		cash_flow_time_payment_dict[str(i+1)] = float(payment_list[i]) # must adjust for 0th numbers
	sum_of_discounted_CFs = 0
	for t, CF_t in cash_flow_time_payment_dict.iteritems():
		PV_t = CF_t/((1.+r)**t)
		# present value if this payment = payment / (1+ discount rate) ** periods_till_payment
		sum_of_discounted_CFs += PV_t
	present_value = sum_of_discounted_CFs
	return present_value

# Discount Dividend Value

def dividend_discount_model_for_multiple_holding_periods(number_of_periods, 
														dividend_list_or_stable_value, 
														share_price_at_final_period
														):

	#         n     D_t         P_n
	# V_0 = sigma -------   + -------
	#        t=1  (1+r)^t     (1+r)^n

	P_n = float(share_price_at_final_period)
	n = number_of_periods

	# format dividends
	if type(dividend_list_or_stable_value) is list:
		dividend_list = payment_list_or_value_if_stable
		if len(dividend_list) == number_of_periods:
			pass
		else:
			print line_number(), "dividend list not formated properly"
			return
	else:
		stable_dividend_value = dividend_list_or_stable_value
		dividend_list = []
		for i in range(number_of_periods):
			dividend_list.append(stable_dividend_value)
	
	# dividends
	dividend_payment_dict = {}
	for t in range(n):
		dividend_payment_dict[str(i+1)] = float(dividend_list[t])
	sum_of_discounted_dividends = 0
	for t, D_t in dividend_payment_dict.iteritems():
		PV_D_t = D_t/((1.+r)**t)
		sum_of_discounted_dividends += PV_D_t
	PV_D = sum_of_discounted_dividends

	# sale price
	PV_P_n = P_n/((1.+r)**n)

	V_0 = PV_D + PV_P_n 
	return V_0

# Gordon Growth Model
def gordon_growth_model(discount_rate, 
						growth_rate, 
						current_dividend_amount = None, 
						next_dividend_amount = None):
	
	#       D_0(1+g)   D_1
	# V_0 = -------- = ---
	#         r-g      r-g

	r = float(discount_rate)
	g = float(growth_rate)
	try:
		D_0 = float(current_dividend_amount)
	except:
		pass
	try:
		D_1 = float(next_dividend_amount)
	except:
		pass
	if not r > g:
		print "Error: V_0 infinite"
		return
	
	if (D_1 and D_0) and not (D_1 == D_0 * (1. + g)):
		print "Error: values for dividends do not conform to model"
		return
	elif D_0:
		numerator = D_0 * (1. + g)
	elif D_1:
		numerator = D_1
	else:
		print "Error: need dividend entered"
		return
	
	V_0 = numerator / (r - g)
	return V_0

def gordon_growth_perpetuity(capitalization_rate, dividend_amount):

	#       D
	# V_0 = -
	#       r

	# capitalization rate is discount rate that capitalizes the value of D

	r = float(discount_or_capitalization_rate)
	D = float(dividend_amount)
	V_0 = D/r
	return V_0 # Present value of the perpetuity

# Present Value of Growth Opprotunities (PVGO)

def no_growth_value_per_share(capitalization_rate, earnings_next_period):

	# No-Growth   E_1
	#   Value   = ---
	# Per Share    r

	# assumes PVGO = 0
	# capitalization rate is like a discount rate, but technically capitalizes the earnings

	r = float(capitalization_rate)
	E_1 = float(earnings_next_period)
	no_growth_value_per_share = E_1/r 
	return no_growth_value_per_share

def growth_value_per_share(present_value_of_growth_opprotunities, capitalization_rate, earnings_next_period):
	
	#       E_1
	# V_0 = --- + PVGO
	#        r

	PVGO = float(present_value_of_growth_opprotunities)
	r = float(capitalization_rate)
	E_1 = float(earnings_next_period)
	no_growth_value_per_share = E_1/r 
	V_0 = no_growth_value_per_share + PVGO
	return V_0

def implied_PVGO(share_price, capitalization_rate, earnings_next_period):

	#              E_1
	# PVGO = V_0 - ---
	#               r

	r = float(capitalization_rate)
	E_1 = float(earnings_next_period)
	no_growth_value_per_share = E_1/r 
	P_0 = float(share_price)
	implied_PVGO = P_0 - no_growth_value_per_share
	return implied_PVGO

def implied_leading_PE_from_PVGO(PVGO, capitalization_rate, earnings_next_period):

	# P_0   1   PVGO
	# --- = - + ----
	# E_1   r   E_1

	PVGO = float(PVGO)
	r = float(capitalization_rate)
	E_1 = float(earnings_next_period)
	implied_P_0_to_E_1_ratio = (1/r) + (PVGO/E_1)
	return implied_P_0_to_E_1_ratio

# Gordon Growth model and PE Ratios
def payout_rate(retention_rate = None,
				dividend_payout = None,
				earnings_for_same_year = None
				):

	# retention_rate = b
	# payout_rate = (1-b)
	#                       D_x
	# payout_rate = (1-b) = ---
	#                       E_x

	if retention_rate:
		b = float(retention_rate)
		payout_ratio = (1-b)
		return payout_ratio
	elif dividend_payout and earnings_for_same_year:
		D_x = float(dividend_payout)
		E_x = float(earnings_for_same_year)
		payout_ratio = D_x/E_x
		return payout_ratio
	else:
		print "Error: Missing some necessary inputs"
		return



def justified_leading_PE_via_gordon_growth(equity_risk_premium, 
										 	growth_rate, 
								 			next_dividend_amount = None, 
											predicted_earnings_this_period = None,
											retention_rate = None,
											payout_ratio = None,
											):
	
	# P_0   D_1/E_0   (1-b)
	# --- = ------- = -----
	# E_1     r-g      r-g

	r = float(equity_risk_premium)
	g = float(growth_rate)
	D_1 = None
	E_1 = None
	b = None
	one_minus_b = None

	if next_dividend_amount is not None:
		D_1 = float(next_dividend_amount)

	if predicted_earnings_this_period is not None:
		E_1 = float(predicted_earnings_this_period)
	
	if retention_rate is not None:
		b = float(retention_rate)
	else:
		one_minus_b = float(payout_ratio)

	if D_1 and E_1:
		D_1 = float(D_1)
		E_1 = float(E_1)
		justified_leading_PE = (D_1/E_1)/(r-g)
	elif (b is not None) or (one_minus_b is not None):
		if b is not None:
			b = float(b)
		if one_minus_b is not None:
			one_minus_b = float(one_minus_b)
		else:
			one_minus_b = (1.-b)

		if (b and one_minus_b) and (one_minus_b != (1.-b)):
			print "Error: payout ratio must equal (1 - retention rate)"
			return
		justified_leading_PE = one_minus_b/(r-g)
	else:
		print "Error: not all variables required have been inputted."
		return
	return justified_leading_PE

def justified_trailing_PE_via_gordon_growth(equity_risk_premium, 
										 	growth_rate, 
								 			current_dividend_amount = None, 
											earnings_last_period = None,
											retention_rate = None,
											payout_ratio = None,
											):
	
	# P_0   D_0(1+g)/E_0   (1-b)(1+g)
	# --- = ------------ = ----------
	# E_0       r-g           r-g

	r = float(equity_risk_premium)
	g = float(growth_rate)

	D_0 = None
	if current_dividend_amount is not None:
		D_0 = float(current_dividend_amount)
	E_0 = None
	if earnings_last_period is not None:
		E_0 = float(earnings_last_period)
	b = None
	if retention_rate is not None:
		b = float(retention_rate)
	one_minus_b = None
	if payout_ratio is not None:
		one_minus_b = payout_ratio

	if D_0 and E_0:
		D_0 = float(D_0)
		E_0 = float(E_0)
		justified_trailing_PE = ((D_0*(1.+g))/E_0)/(r-g)
	elif b or one_minus_b:
		if b:
			b = float(b)
		if one_minus_b:
			one_minus_b = float(one_minus_b)
		else:
			one_minus_b = (1.-b)

		if (b and one_minus_b) and (one_minus_b != (1.-b)):
			print "Error: payout ratio must equal (1 - retention rate)"
			return
		justified_trailing_PE = (one_minus_b*(1.+g))/(r-g)
	else:
		print "Error: not all variables required have been inputted."
		return
	return justified_trailing_PE

# Estimating Required Return (technically IRR) using GGM

def IRR_via_gordon_growth(current_share_price,
							dividend_growth_rate,

							current_dividend = None,
							next_period_dividend = None):
	#     D_0(1+g)       D_1
	# r = -------- + g = --- + g
	#       P_0          P_0
	D_0 = float(current_dividend)
	P_0 = float(current_share_price)
	g = float(dividend_growth_rate)
	D_1 = float(next_period_dividend)

	if ((D_1 is None) and (D_0 is None)):
		print line_number(), "error"

	if D_1 is not None:
		IRR = (D_1/P_0) + g
	else:
		IRR = ((D_0(1+g))/P_0)+g

	return IRR


def two_stage_dividend_discount_model(number_of_first_stage_periods,
										required_return_on_equity,
										current_dividend,
										short_term_dividend_growth_rate,
										long_term_dividend_growth_rate,

										current_time_period = 1):
	#         n   D_0(1+g_S)^t   D_0 * (1+g_S)^n * (1+g_L)
	# V_0 = sigma ------------ + -------------------------
	#        t=1    (1+r)^t          (1+r)^n * (r-g_L)
	n = int(number_of_first_stage_periods)
	t = int(current_time_period)
	r = float(required_return_on_equity)
	D_0 = float(current_dividend)
	g_S = float(short_term_dividend_growth_rate)
	g_L = float(long_term_dividend_growth_rate)

	V_s1 = 0.
	while t <= n:
		V_t = ((D_0((1.+g_S)**t)/((1.+r)**t)))
		V_s1 += V_t
		t += 1
	V_n = (((D_0*((1+g_S)**n))*(1+g_L))/(((1.+r)**n)*(r-g_L)))
	V_0 = V_s1 + V_n
	return V_0

def H_model_dividend_discount(half_life_in_years_of_high_growth_period,
								required_return_on_equity,
								current_dividend,
								short_term_dividend_growth_rate,
								long_term_dividend_growth_rate):
	#       D_0(1+g_L)   D_0*H*(g_S-g_L)
	# V_0 = ---------- + ---------------
	#         r-g_L           r-g_L
	H = float(half_life_in_years_of_high_growth_period) # high-growth period = 2H
	r = float(required_return_on_equity)
	D_0 = float(current_dividend)
	g_S = float(short_term_dividend_growth_rate)
	g_L = float(long_term_dividend_growth_rate)

	V_0 = ((D_0(1.+g_L))/(r-g_L))/((D_0*H*(g_S-g_L))/(r-g_L))
	return V_0

def three_stage_dividend_discount_model(number_of_first_stage_periods,
										number_of_second_stage_periods,
										required_return_on_equity,
										current_dividend,
										short_term_growth_rate,
										medium_term_growth_rate,
										long_term_growth_rate,

										current_time_period=1):
	#         n   D_0(1+g_S)^t     m   D_0 * (1+g_S)^n * (1+g_M)^t   D_0 * (1+g_S)^n * (1+g_M)^m * (1+g_L)
	# V_0 = sigma ------------ + sigma --------------------------- + -------------------------------------
	#        t=1    (1+r)^t       t=n            (1+r)^t                       (1+r)^m * (r-g_L)
	t = int(current_time_period)
	r = float(required_return_on_equity)
	n = int(number_of_first_stage_periods)
	m = int(number_of_second_stage_periods)
	D_0 = float(current_dividend)
	g_S = float(short_term_growth_rate)
	g_M = float(medium_term_growth_rate)
	g_L = float(long_term_growth_rate)

	V_s1 = 0.
	while t <= n:
		V_t = ((D_0((1.+g_S)**t))/((1.+r)**t))
		V_s1 += V_t
		t += 1

	V_s2 = 0.
	while (t > n) and (t <= m):
		V_t = (D_0 * ((1.+g_S)**n) * ((1.+g_M)**t)) / ((1.+r)**t)
		V_s2 += V_t
		t += 1
	V_s3 = (D_0 * ((1.+g_S)**n) * ((1.+g_M)**m) * (1.+g_L)) / (((1.+r)**m) * (r-g_L))

	V_0 = V_s1 + V_s2 + V_s3
	return V_0

def three_stage_H_model_dividend_discount(half_life_in_years_of_high_growth_period,
											number_of_first_stage_periods,
											number_of_second_stage_periods,
											required_return_on_equity,
											current_dividend,
											short_term_growth_rate,
											medium_term_growth_rate,
											long_term_growth_rate,

											current_time_period = 1):
	#         n   D_0(1+g_S)^t   D_0 * (1+g_S)^n * H * (g_M-g_L)   D_0 * (1+g_S)^n * (1+g_L)
	# V_0 = sigma ------------ + ------------------------------- + -------------------------
	#        t=1    (1+r)^t             (1+r)^n * (r-g_L)              (1+r)^n * (r-g_L)
	H = float(half_life_in_years_of_high_growth_period) # middle-growth period = 2H
	t = int(current_time_period)
	r = float(required_return_on_equity)
	n = int(number_of_first_stage_periods)
	m = int(number_of_second_stage_periods)
	D_0 = float(current_dividend)
	g_S = float(short_term_growth_rate)
	g_M = float(medium_term_growth_rate)
	g_L = float(long_term_growth_rate)

	V_s1 = 0.
	while t <= n:
		V_t = (D_0 * ((1.+g_S)**t))/((1.+r)**t)
		V_s1 += V_t
		t += 1

	V_s2_and_s3 = ((D_0 * ((1.+g_S)**n) * H * (g_M-g_L))/(((1.+r)**n) * (r-g_L))) + ((D_0 * ((1.+g_S)**n) * (1.+g_L))/(((1.+r)**n) * (r-g_L)))
	V_0 = V_s1 + V_s2_and_s3
	return V_0

# Spreadsheet (General) Modeling

def estimate_long_term_growth_rate(long_term_retention_rate_estimate, 
									long_term_ROE_or_required_return_estimate_or_median_industry_ROE):
	# g_LT = (b in mature phase) * (ROE in mature phase)
	# b (retention rate) estimate -> empirical from industry or current rates
	# ROE -> Use DuPont formula, set ROE = r (require return) in long run, use median industry ROE
	g_LT = float(long_term_retention_rate_estimate) * float(long_term_ROE_or_required_return_estimate_or_median_industry_ROE)
	return g_LT
def implied_IRR_from_dividend_discounting(half_life_in_years_of_high_growth_period,
											current_dividend,
											short_term_dividend_growth_rate,
											long_term_dividend_growth_rate,
											current_price):
	#              D_0
	# implied_r = (---)[(1+g_L) + H(g_S-g_L)] + g_L
	#              P_0
	D_0 = float(current_dividend)
	P_0 = float(current_price)
	g_S = float(short_term_dividend_growth_rate)
	g_L = float(long_term_dividend_growth_rate)
	H  = float(half_life_in_years_of_high_growth_period)

	implied_IRR = (((D_0)/P_0)((1.+g_L) + (H*(g_S-g_L)))) + g_L
	return implied_IRR

def sustainable_growth_rate(retention_rate,
							return_on_equity):
	# g = b * ROE
	b = float(retention_rate)
	ROE = float(return_on_equity)
	sustainable_dividend_growth_rate = b * ROE
	g_LT = sustainable_dividend_growth_rate
	return g_LT

def dupont():
	ROE = NI/sales * sales/total_assets * total_assets/shareholders_equity

def sustainable_growth_rate_via_dupont():
	g = (NI - D)/NI * dupont_ROE

# Free Cash Flow Models

# FCFF

def firm_value_via_FCFF():
	#               inf    FCFF_t
	# Firm Value = sigma ----------
	#               t=1  (1+WACC)^t
	raise Exception("This formula isn't written, use single_stage_FCFF_valuation() instead")

def single_stage_FCFF_valuation(weighted_avg_cost_of_capital,
								FCFF_growth_rate,
								FCFF_this_period = None,
								FCFF_next_period = None):
	# "free cash flow to the firm"
	#
	#                FCFF_1     FCFF_0 * (1+g)
	# Firm Value = ---------- = --------------
	#               WACC - g       WACC - g
	FCFF_1 = float(FCFF_next_period)
	FCFF_0 = float(FCFF_this_period)
	g = float(FCFF_growth_rate)
	WACC = float(weighted_avg_cost_of_capital)

	if FCFF_1 is None:
		FCFF_1 = FCFF_0 * (1.+g)
	V_0 = FCFF_1/(WACC-g)
	return V_0

def equity_value_via_FCFF():
	equity_value = firm_value - market_value_of_debt
	#firm_value = firm_value_via_FCFF()
	raise Exception("Not sure what this formula is for, i'll have to go back and read it.")

def WACC_for_FCFF(market_value_of_debt,
					market_value_of_common_equity,
					cost_of_debt_captial,
					cost_of_equity_capital,
					marginal_tax_rate):
	#             Debt_mv                                     Equity_mv
	# WACC = ------------------- * r_d * (1-tax_rate)  + ------------------- * r
	#        Debt_mv + Equity_mv                         Debt_mv + Equity_mv

	# r_d(1-tax_rate) = after tax cost of debt
	# r = cost of equity
	debt_mv = float(market_value_of_debt)
	equity_mv = float(market_value_of_common_equity)
	tax = float(marginal_tax_rate)
	r_d = float(cost_of_debt_captial)
	r = float(cost_of_equity_capital)

	WACC = ((debt_mv/(debt_mv+equity_mv))*r_d*(1.-tax)) + ((equity_mv/(debt_mv + equity_mv))*r)
	return WACC
def FCFF_from_net_income(net_income_available_to_common_shareholders,
						net_non_cash_charge,
						interest_expense,
						marginal_tax_rate,
						fixed_capital_investment,
						working_capital_investment):
	NI = float(net_income_available_to_common_shareholders)
	NCC = float(net_non_cash_charge) # depreciation, amortization, etc
	Int = float(interest_expense)
	tax_rate = float(marginal_tax_rate)
	FCInv = float(fixed_capital_investment)
	WCInv = float(working_capital_investment)

	FCFF = NI + NCC + Int(1.-tax_rate) - FCInv - WCInv

	return FCFF

def FCFF_from_CF_statement(cash_flow_from_operations,
							interest_expense,
							marginal_tax_rate,
							fixed_capital_investment):
	CFO = float(cash_flow_from_operations)
	Int = float(interest_expense)
	tax_rate = float(marginal_tax_rate)
	FCInv = float(fixed_capital_investment)

	FCFF = CFO + Int(1.-tax_rate) - FCInv

	return FCFF

def noncash_charge(depreciation,
				  amortization,
				  impairment,
				  restructuring_expence,
				  losses,
				  amortization_of_long_term_bond_discounts,
				  deferred_taxes__maybe,
				  restructuring_income,
				  gains,
				  amortization_of_long_term_bond_premiums,):
	items_to_be_added_back = [depreciation,
							  amortization,
							  impairment,
							  restructuring_expence,
							  losses, # e.g. on sale of fixed asset
							  amortization_of_long_term_bond_discounts,
							  deferred_taxes__maybe, # this requires special attention!
							  # generally for forcasting, ignore deferred taxes
							  # however, if firm is growing and they can be deferred indefinitely
							  # adding back may be warrented.
							 ]
	items_to_be_subtracted = [restructuring_income, # e.g. from a reversal
							  gains, # e.g. on sale of fixed asset
							  amortization_of_long_term_bond_premiums,
							 ]
	items_to_be_added_back = [float(x) for x in items_to_be_added_back]
	items_to_be_subtracted = [float(x) for x in items_to_be_subtracted]
	net_noncash_charge = sum(items_to_be_added_back) - sum(items_to_be_subtracted)

	return net_noncash_charge

# FCFE

def FCFE_via_FCFF(free_cash_flow_to_the_firm,
					interest_expense,
					marginal_tax_rate,
					net_borrowing):
	FCFF = float(free_cash_flow_to_the_firm)
	Int = float(interest_expense)
	tax_rate = float(marginal_tax_rate)
	net_borrowing = float(net_borrowing)

	FCFE = FCFF - Int(1.-tax_rate) + net_borrowing

	return FCFE

def FCFE_via_income_statement(net_income_available_to_common_shareholders,
							net_non_cash_charge,
							fixed_capital_investment,
							working_capital_investment,
							net_borrowing):
	NI = float(net_income_available_to_common_shareholders)
	NCC = float(net_non_cash_charge) # depreciation, amortization, etc
	FCInv = float(fixed_capital_investment)
	WCInv = float(working_capital_investment)
	net_borrowing = float(net_borrowing)

	FCFE = NI + NCC - FCInv - WCInv + net_borrowing

	return FCFE

def FCFE_via_cash_flow_statement(cash_flow_from_operations,
								fixed_capital_investment,
								net_borrowing):
	CFO = float(cash_flow_from_operations)
	FCInv = float(fixed_capital_investment)
	net_borrowing = float(net_borrowing)

	FCFE = CFO - FCInv + net_borrowing

	return FCFE

# FCFF & FCFE from EBIT & EBITDA

def FCFF_via_EBIT(earnings_before_interest_and_tax,
				marginal_tax_rate,
				depreciation_expense,
				fixed_capital_investment,
				working_capital_investment):
	# assuming NCC includes only depreciation
	EBIT = float(earnings_before_interest_and_tax)
	tax_rate = float(marginal_tax_rate)
	Dep = float(depreciation_expense)
	FCInv = float(fixed_capital_investment)
	WCInv = float(working_capital_investment)

	FCFF = EBIT(1.-tax_rate) + Dep - FCInv - WCInv

	return FCFF

def FCFE_via_EBIT(earnings_before_interest_and_tax,
					marginal_tax_rate,
					depreciation_expense,
					fixed_capital_investment,
					working_capital_investment,
					net_borrowing,):
	EBIT = float(earnings_before_interest_and_tax)
	tax_rate = float(marginal_tax_rate)
	Dep = float(depreciation_expense)
	FCInv = float(fixed_capital_investment)
	WCInv = float(working_capital_investment)
	net_borrowing = float(net_borrowing)

	FCFF = FCFF_via_EBIT(EBIT, tax_rate, Dep, FCInv, WCInv)

	FCFE = FCFF - Int(1.-tax_rate) + net_borrowing
	return FCFE

def FCFF_via_EBITDA(earnings_before_interest_tax_depreciation_and_amortization,
					marginal_tax_rate,
					depreciation_expense,
					fixed_capital_investment,
					working_capital_investment):
	EBITDA = float(earnings_before_interest_tax_depreciation_and_amortization)
	tax_rate = float(marginal_tax_rate)
	Dep = float(depreciation_expense)
	FCInv = float(fixed_capital_investment)
	WCInv = float(working_capital_investment)

	FCFF = EBITDA(1.-tax_rate) + Dep(tax_rate) - FCInv - WCInv
	return FCFF

def FCFE_via_EBITDA(earnings_before_interest_tax_depreciation_and_amortization,
					marginal_tax_rate,
					depreciation_expense,
					fixed_capital_investment,
					working_capital_investment,
					net_borrowing):
	EBITDA = float(earnings_before_interest_tax_depreciation_and_amortization)
	tax_rate = float(marginal_tax_rate)
	Dep = float(depreciation_expense)
	FCInv = float(fixed_capital_investment)
	WCInv = float(working_capital_investment)
	net_borrowing = float(net_borrowing)
	
	FCFF = FCFF_via_EBITDA(EBITDA, tax_rate, Dep, FCInv, WCInv)

	FCFE = FCFF - Int(1.-tax_rate) + net_borrowing
	return FCFE

# forcasting FCFF and FCFE

def estimated_FCInv(capital_expenditures,
					depreciation_expense,
					sales_current_period,
					sales_previous_period):
	CapEx = float(capital_expenditures)
	Dep = float(depreciation_expense)
	sales_increase = float(sales_current_period) - float(sales_previous_period)
	FCInv_e = (CapEx - Dep)/sales_increase
	return FCInv_e

def estimated_WCInv(working_capital_current_period,
					working_capital_previous_period,
					sales_current_period,
					sales_previous_period):
	wc_increase = float(working_capital_current_period) - float(working_capital_previous_period)
	sales_increase = float(sales_current_period) - float(sales_previous_period)
	WCInv_e = wc_increase/sales_increase
	return WCInv_e

def estimated_FCFE(capital_expenditures,
					depreciation_expense,
					sales_current_period,
					sales_previous_period,
					working_capital_current_period,
					working_capital_previous_period,

					net_income,
					debt_ratio):
	# assumes relationship between FCInv-Dep & WCInv to sales
	# assumes constant debt ratio

	# from: FCFE = NI - (FCInv - Dep) - WCInv + Net Borrowing
	# and: -> Net Borrowing = DR(FCInv-Dep) + DR(WCInv)
	DR = float(debt_ratio)
	NI = float(net_income)
	Dep = float(depreciation_expense)

	FCInv_e = estimated_FCInv(capital_expenditures, depreciation_expense, sales_current_period, sales_previous_period)
	WCInv_e = estimated_WCInv(working_capital_current_period, working_capital_previous_period, sales_current_period, sales_previous_period)

	FCFE_e = NI - (1.-DR)(FCInv_e-Dep) - (1.-DR)(WCInv_e)
	return FCFE_e

def FCFF_two_stage_model(number_of_periods,
						FCFF_estimate_list,
						FCFF_growth_rate,
						WACC,
						current_time_period = 1):
	#              n     FCFF_t            FCFF_n+1
	# Firm_V_0 = sigma ----------  + ---------------------
	#             t=1  (1+WACC)^t    (1+WACC)^n * (WACC-g)
	t = int(current_time_period)
	n = int(number_of_periods)
	WACC = float(WACC)
	FCFF_estimate_list = [float(x) for x in FCFF_estimate_list]
	if len(FCFF_estimate_list) != n:
		raise Exception("The FCFF estimate list needs to be the same length as the number of periods")
	g = float(FCFF_growth_rate)
	FCFF_terminal = float(FCFF_estimate_list[-1] * (1.+g))
	
	V_s1 = 0.
	while t <= n:
		V_t = FCFF_estimate_list[t]/((1.+WACC)**t)
		V_s1 += V_t
		t += 1
	V_terminal = FCFF_terminal/(((1.+WACC)**n)*(WACC-g))
	Firm_V_0 = V_s1 + V_terminal
	return Firm_V_0

def FCFE_two_stage_model(number_of_periods,
						FCFE_estimate_list,
						FCFE_growth_rate,
						required_return,

						current_time_period = 1):
	#                n   FCFE_t        FCFE_n+1
	# Equity_V_0 = sigma -------  + ---------------
	#               t=1  (1+r)^t    (1+r)^n * (r-g)
	t = int(current_time_period)
	n = int(number_of_periods)
	r = float(required_return)
	FCFE_estimate_list = [float(x) for x in FCFE_estimate_list]
	if len(FCFE_estimate_list) != n:
		raise Exception("The FCFF estimate list needs to be the same length as the number of periods")
	g = float(FCFE_growth_rate)
	FCFE_terminal = float(FCFE_estimate_list[-1] * (1.+g))
	
	V_s1 = 0.
	while t <= n:
		V_t = FCFE_estimate_list[t]/((1.+r)**t)
		V_s1 += V_t
		t += 1
	V_terminal = FCFE_terminal/(((1.+r)**n)*(r-g))
	Firm_V_0 = V_s1 + V_terminal
	return Firm_V_0


def value_of_firm(value_of_operating_assets, value_of_nonoperating_assets):
	V = float(value_of_operating_assets) + float(value_of_nonoperating_assets)
	return V


# Market Based Valuation

# P/E

def pe_ratio(current_price, earnings):
	PE = float(price)/float(earnings)
	return PE

def forward_pe_ratio_annual(current_price, next_period_earnings):
	price_0 = float(current_price)
	earnings_1 = float(next_period_earnings)
	PE_f = price_0/earnings_1
	return PE_f
def forward_pe_ratio_quarterly(current_price, 
								EPS_estimate_list_for_next_four_quarters):
	#CFA uses forcasted quarters # terms below: "EPS (expected for) Quarter t+1"
	price_0 = float(current_price)

	EPS_eQ_t1 = float(EPS_estimate_list_for_next_four_quarters[0])
	EPS_eQ_t2 = float(EPS_estimate_list_for_next_four_quarters[1])
	EPS_eQ_t3 = float(EPS_estimate_list_for_next_four_quarters[2])
	EPS_eQ_t4 = float(EPS_estimate_list_for_next_four_quarters[3])
	
	EPS_eY1 = EPS_eQ_t1 + EPS_eQ_t2 + EPS_eQ_t3 + EPS_eQ_t4

	forward_PE = price_0/EPS_eY1
	return forward_PE

def next_12_months_pe(this_years_expected_earnings,
						next_years_expected_earnings,
						number_of_months_since_last_annual_report): 
	# Less used than quarterly. Acheieve by an offset of predicted eps from next two years.
	EPS_eY1 = float(this_years_expected_earnings)
	EPS_eY2 = float(next_years_expected_earnings)
	month_offset_ratio = float(number_of_months_since_last_annual_report)
	
	months_till = 12-months_offset_ratio

	NTM_PE = ((months_till/12)*EPS_eY1) + ((month_offset_ratio/12)*EPS_eY2)
	return NTM_PE

def trailing_pe_ratio(current_price,
						earnings_ttm):
	# or "current pe"
	price_0 = float(current_price)
	PE_ttm = price_0/float(earnings_ttm)
	return PE_ttm

def normalized_pe_ratio():
	# based on historic pe
	# or preferably:
	# based on historic ROE * BVPS
	raise Exception("not exactly a formula")

# common inverse ratios and their originals

def earnings_yield(current_earnings, current_price): # or "inverse price ratio" # commonly used
	price = float(current_price)
	earnings = float(current_earnings)
	earnings_yield = earnings/price
	return earnings_yield

def price_to_book(current_price, book_value_per_share):
	price = float(current_price)
	BVPS = float(book_value_per_share)
	PB = price/BVPS
	return PB

def book_to_market(book_value_per_share, current_price): # commonly used
	price = float(current_price)
	BVPS = float(book_value_per_share)
	book_to_market = BVPS/price
	return book_to_market

def price_to_sales(current_price, current_sales):
	price = float(current_price)
	sales = float(current_sales)
	price_to_sales = price/sales
	return price_to_sales

def sales_to_price(current_sales, current_price): # rarely used
	price = float(current_price)
	sales = float(current_sales)
	sales_to_price = sales/price
	return sales_to_price

def price_to_cashflow(current_price, current_cashflow):
	price = float(current_price)
	cashflow = float(current_cashflow)
	price_to_cf = price/cashflow
	return price_to_cf

def cashflow_yield(current_cashflow, current_price): # commonly used
	price = float(current_price)
	cashflow = float(current_cashflow)
	cf_yield = cashflow/price
	return cf_yield

def dividend_yield(current_dividend, current_price):
	dividend = float(current_dividend)
	price = float(current_price)
	div_yield = dividend/price
	return div_yield

def price_to_dividend(current_price, current_dividend): # rarely used
	price = float(current_price)
	dividend = float(current_dividend)
	price_to_dividend = price/dividend
	return price_to_dividend

def thomson_first_call_pe():
	# two calculations
	# forward pe based on the mean of analysts' current fiscal year (probably has some actual values in caluculation)
	# forward pe based on the mean of analysts' following fiscal year (estimates)
	# p.387
	raise Exception("not finished yet, look this up")

def justified_pe_based_on_equity_valuation():
	V_0 = value_of_equity_determined_by_some_means
	E = earnings
	PE_j = V_0/E
	raise Exception("this should be more properly defined, look it up")

# Peer-company multiples

def PEG_ratio(current_price, some_earnings_measure, some_earnings_growth_measure):
	P = float(current_price)
	E = float(some_earnings_measure)
	g = float(some_earnings_growth_measure)
	PEG = (P/E)/g
	return PEG

# overall market multiples

def fed_model():
	P = market_price
	E = market_earnings
	Y_10 = ten_year_bond_yield

	(E/P) == Y_10

	# if earnings yield > bond yield: stocks are under-valued (or bonds are trading at a unjustified premium).
	# if earnings yield < bond yield: stocks are over-valued (or bonds are trading at a unjustified discount).
	raise Exception("not really usable in current form i don't think")

def yardeni_model(current_earnings_yield_on_market_index,
					current_moodys_investor_service_a_rated_corporate_bond_yield,
					five_year_growth_rate_forcast_for_market_index,
					weight_of_5_year_forcast):
	CEY = float(current_earnings_yield_on_market_index)
	CBY = float(current_moodys_investor_service_a_rated_corporate_bond_yield)
	LTEG = float(five_year_growth_rate_forcast_for_market_index)
	b = float(weight_of_5_year_forcast) # historically 0.10, but now has been reported 0.10, 0.20, 0.25 (p.402)
	# Residual = ??? # literally cannot find what this is supposed to be and other sources don't have it.

	CEY == CBY - b(LTEG) + Residual

	# easier terms:
	EP_mkt = CEY
	Y_CB_rA = CBY
	g_mkt_5y = LTEG
	b = b

	EP_mkt == Y_CB_rA - b(g_mkt_5y)
	raise Exception("Need to review this formula, it doesn't seem to be a function")


# Price to Book

def price_to_book_via_BVPS(current_price, book_value_per_share):
	price = float(current_price)
	BVPS = float(book_value_per_share)
	PB = price/BVPS
	return PB
def price_to_book_via_equity(current_price, shareholders_equity, shares_outstanding):
	price = float(current_price)
	shareholders_equity = float(shareholders_equity)
	number_of_common_shares = float(shares_outstanding)
	PB = price/(shareholders_equity/number_of_common_shares)
	return PB

def price_to_book_via_assets_and_liabilities(current_price, 
											total_assets,
											total_labilities,
											shares_outstanding): 
	price = float(current_price)
	total_assets = float(total_assets)
	total_labilities = float(total_labilities)
	number_of_common_shares = float(shares_outstanding)
	PB = price/((total_assets-total_liabilities)/number_of_common_shares)
	return PB

def book_value_per_share(common_shareholders_equity, common_shares_outstanding):
	BVPS = float(common_shareholders_equity)/float(number_of_common_shares)
	# or 
def book_value_per_share_via_assets_and_liabilities(total_assets, total_liabilities, number_of_common_shares):
	BVPS = (float(total_assets)-float(total_liabilities))/float(number_of_common_shares)
	return BVPS

def common_shareholders_equity(shareholder_equity, total_value_of_equity_claims_that_are_senior_to_common_stock):
	V_sr = float(total_value_of_equity_claims_that_are_senior_to_common_stock)
	common_shareholders_equity = float(shareholders_equity) - V_sr
	return common_shareholders_equity

def justified_price_to_book_via_ROE(ROE, earnings_growth, required_return_on_equity):
	ROE = float(ROE)
	g = float(earnings_growth)
	r = float(required_return_on_equity)
	PB_0 = (ROE-g)/(r-g)
	# PB_0 = P_0/B_0
	return PB_0

def justified_price_to_book_via_residual_earnings(current_book_value, present_value_of_expected_future_residual_earnings):
	residual_earnings_PV = float(present_value_of_expected_future_residual_earnings)
	B_0 = float(current_book_value)
	PB_0 = (residual_earnings_PV/B_0) + 1
	# PB_0 = P_0/B_0
	return PB_0

# price to sales

# def price_to_sales():
#	P = price_per_share
#	S = annual_net_sales_per_share # total sales - customer discounts
#	PS = P/S

def justified_price_to_sales(current_earnings,
							current_sales,
							retention_rate,
							earnings_growth,
							required_return_on_equity):
	E_0 = float(current_earnings)
	S_0 = float(current_sales)
	b = float(retention_rate)
	g = float(earnings_growth)
	r = float(required_return_on_equity)
	PS_0 = (E_0/S_0)(1-b)(1+g) / (r-g)
	#PS_0 = P_0/S_0
	return PS_0
# Dividend yield

def justified_dividend_yield(dividend_growth_rate, required_return_on_equity):
	g = float(dividend_growth_rate)
	r = float(required_return_on_equity)
	DP_0 = (r-g)/(1+g)
	#DP_0 = D_0/P_0
	return DP_0

# enterprise value / ebitda

def enterprise_value(cash, 
					cash_equivalents, 
					short_term_investments,
					market_value_of_common_equity,
					market_value_of_preferred_stock,
					market_value_of_debt):
	nonearning_assets = float(cash) + float(cash_equivalents) + float(short_term_investments)
	V_ce = float(market_value_of_common_equity)
	V_ps = float(market_value_of_preferred_stock)
	V_d = float(market_value_of_debt)

	EV = V_ce + V_ps + V_d - nonearning_assets
	return EV

def enterprise_value_to_EBITDA(EV, EBITDA):
	EV_to_EBITDA = float(EV)/float(EBITDA)
	return EV_to_EBITDA

def enterprise_value_to_FCFF(EV, FCFF):
	EV_to_FCFF = float(EV)/float(FCFF)
	return EV_to_FCFF

def enterprise_value_to_EBITDAR(EV, EBITDAR): # + rent expense (used for airlines)
	EV_to_EBITDAR = float(EV)/float(EBITDAR)
	return EV_to_EBITDAR

# Momentum Valuation Indicatiors

def unexpected_earnings(current_period_actual_earnings, current_period_expected_earnings):
	EPS_t = float(current_period_actual_earnings)
	eEPS_t = float(current_period_expected_earnings)
	unexpected_EPS_t = EPS_t - eEPS_t
	return unexpected_EPS_t

def standardized_unexpected_earnings():
	#SUE_t = EPS_t - E(EPS_t) / sigma[EPS_t - E(EPS_t)]
	#
	# sigma is st dev over some historical time period
	raise Exception("not finished yet, look this up")
# issues in practice 


def harmonic_mean(data_list):
	#           n
	# X_H = ---------
	#         n    1
	#       sigma ---
	#        i=1  X_i
	denominator = None
	for data in data_list:
		if data != 0.:
			denominator += 1/float(data)
		else:
			raise Exception("Error: divide by zero")
			return
	if denominator != 0.:
		X_WH = len(data_list)/denominator
	else:
		raise Exception("Error: divide by zero")
		return
	return X_WH


HarmonicMeanData = namedtuple("HarmonicMeanData", ["name", "weight", "data"])
def weighted_harmonic_mean(HarmonicMeanData_list):
	#            1
	# X_WH = ---------
	#          n   w_i
	#        sigma ---
	#         i=1  X_i

	denominator = None
	for unit in HarmonicMeanData_list:
		if unit.data != 0.:
			denominator += float(unit.weight)/float(unit.data)
		else:
			print "Error: divide by zero"
			return
	if denominator != 0.:
		X_WH = 1/denominator
	else:
		print "Error: divide by zero"
		return
	return X_WH


# Residual Income

def economic_value_added(net_operating_profit_after_taxes,
						cost_of_capital,
						total_capital):
	NOPAT = float(net_operating_profit_after_taxes)
	C_percent = float(cost_of_capital)
	TC = float(total_capital)

	EVA = NOPAT - (C_percent * TC)
	return EVA

def market_value_added(market_value_of_the_company,
						accounting_book_value_of_total_capital):
	MVA = float(market_value_of_the_company) - float(accounting_book_value_of_total_capital)

def residual_income():
	#              inf   RI_t            inf  E_t - r(B_t_minus_1)
	# V_0 = B_0 + sigma ------- = B_0 + sigma --------------
	#              t=1  (1+r)^t          t=1  (1+r)^t

	B_0 = current_per_share_book_value_of_equity
	B_t = expected_per_share_book_value_of_equity_at_time_t
	r = required_return_on_equity # cost of equity
	E_t = expected_EPS_for_period_t
	RI_t = expected_per_share_residual_income # RI_t = E_t - r(B_t_minus_1)
	raise Exception("i'm not exactly sure how to deal with these infinite sigma additions")
def clean_surplus_relation():
	B_t = B_t_minus_1 + E_t - D_t
	raise Exception("not actually a useful equation, since it typically does not hold")
def residual_income_via_ROE():
	#              inf  (ROE_t - r)B_t_minus_1
	# V_0 = B_0 + sigma ----------------------
	#              t=1         (1+r)^t
	raise Exception("not finished yet, infinite summation, not sure how to impliment, look up")
def residual_income_constant_growth(current_book_value,
									ROE,
									ROE_constant_growth_rate,
									required_return_on_equity):
	#             ROE - r
	# V_0 = B_0 + -------(B_0)
	#               r-g
	B_0 = float(current_book_value)
	ROE = float(ROE)
	g = float(ROE_constant_growth_rate)
	r = float(required_return_on_equity)

	V_0 = B_0 + (B_0 * ((ROE-r)/(r-g)))
	return V_0

def tobins_q(market_value_of_debt_and_equity,
				replacement_cost_of_total_assets): # not on exam
	T_q = float(market_value_of_debt_and_equity)/float(replacement_cost_of_total_assets)
	return T_q

def residual_income_multi_stage(number_of_periods_in_stage_1,
								list_of_earnings_in_stage_1,
								list_of_book_values_in_stage_1,
								current_book_value,
								terminal_price,
								terminal_book_value,
								required_return_on_equity,

								current_time_period = 1):
	#               T   (E_t - r(B_t_minus_1))   P_T - B_T
	# V_0 = B_0 + sigma ---------------------- + ---------
	#              t=1         (1+r)^t            (1+r)^T
	B_0 = float(current_book_value)
	r = float(required_return_on_equity)
	T = int(number_of_periods_in_stage_1)

	if not (len(list_of_earnings_in_stage_1) == T) and (len(list_of_book_values_in_stage_1) == T):
		raise Exception("earnings and book values need to be list length of the time periods.")

	V_s1 = 0.
	for t in range(T):
		print t
		if t == 0:
			B_t_minus_1 = B_0
		else:
			B_t_minus_1 = float(list_of_book_values_in_stage_1[t-1])
		V_s1 += (float(list_of_earnings_in_stage_1[t]) - (r * float(B_t_minus_1)))/((1.+r)**t)
		print V_s1, B_t_minus_1, list_of_book_values_in_stage_1[t]
	V_T = (float(terminal_price) - float(terminal_book_value))/((1+r)**T)
	print V_T
	V_0 = B_0 + V_s1 + V_T
	print V_0
	return V_0

def residual_income_multi_stage_via_ROE(number_of_periods_in_stage_1,
										list_of_ROE_in_stage_1,
										list_of_book_values_in_stage_1,
										current_book_value,
										terminal_price,
										terminal_book_value,
										required_return_on_equity,

										current_time_period = 1):
	#               T   (ROE_t - r)B_t_minus_1   P_T - B_T
	# V_0 = B_0 + sigma ---------------------- + ---------
	#              t=1         (1+r)^t            (1+r)^T
	B_0 = float(current_book_value)
	r = float(required_return_on_equity)
	T = int(number_of_periods_in_stage_1)

	if not (len(list_of_ROE_in_stage_1) == T) and (len(list_of_book_values_in_stage_1) == T):
		raise Exception("earnings and book values need to be list length of the time periods.")

	V_s1 = 0.
	for t in range(T):
		print t
		if t == 0:
			B_t_minus_1 = B_0
		else:
			B_t_minus_1 = float(list_of_book_values_in_stage_1[t-1])
		V_s1 += (float(list_of_ROE_in_stage_1[t]) - (r * float(B_t_minus_1)))/((1.+r)**t)
		print V_s1, B_t_minus_1, list_of_book_values_in_stage_1[t]
	V_T = (float(terminal_price) - float(terminal_book_value))/((1+r)**T)
	print V_T
	V_0 = B_0 + V_s1 + V_T
	print V_0
	return V_0

def residual_income_multi_stage_declining(number_of_periods_in_stage_1,
										list_of_earnings_in_stage_1,
										list_of_book_values_in_stage_1,
										current_book_value,
										terminal_earnings,
										required_return_on_equity,
										persistence_factor,

										current_time_period = 1):
	#               T   (E_t - r(B_t_minus_1))     E_T - r(B_T_minus_1)
	# V_0 = B_0 + sigma ---------------------- + -------------------------
	#              t=1         (1+r)^t           (1+r-w) * (1+r)^T_minus_1

	w = int(persistence_factor) # 1 > w > 0 # 1 will not fade, 0 will fade after first period
	B_0 = float(current_book_value)
	r = float(required_return_on_equity)
	T = int(number_of_periods_in_stage_1)


	if not (len(list_of_earnings_in_stage_1) == T) and (len(list_of_book_values_in_stage_1) == T):
		raise Exception("earnings and book values need to be list length of the time periods.")

	V_s1 = 0.
	for t in range(T):
		print t
		if t == 0:
			B_t_minus_1 = B_0
		else:
			B_t_minus_1 = float(list_of_book_values_in_stage_1[t-1])
		V_s1 += (float(list_of_earnings_in_stage_1[t]) - (r * float(B_t_minus_1)))/((1.+r)**t)
		print V_s1, B_t_minus_1, list_of_book_values_in_stage_1[t]
	V_T = (float(terminal_earnings) - (r * float(list_of_book_values_in_stage_1[-1])))/((1+r-w)*((1+r)**(T-1)))
	print V_T
	V_0 = B_0 + V_s1 + V_T
	print V_0
	return V_0

residual_income_multi_stage_declining(10, [float(x+100) for x in range(10)], [float(x+100) for x in range(10)], 100, 500, .06, 5)

## Private Companies

# Capitalized CF Method

def capitalized_CF_method_FCFF(FCFF_next_period, WACC, growth_rate):
	#       FCFF_1
	# V_f = ------
	#       WACC-g
	V_f = float(FCFF_next_period)/(float(WACC) - float(g))
	return V_f

def capitalized_CF_method_FCFE(FCFE_next_period, required_return, growth_rate):
	#     FCFE_1
	# V = ------
	#      r-g
	V = float(FCFE_next_period)/(float(required_return)-float(growth_rate))
	return V

# Lack of control discounts

def discount_for_lack_of_control(control_premium): # not on exam
	DLOC = 1.-(1./(1.-float(control_premium)))
	return DLOC

def discount_for_lack_of_marketability(marketability_premium): # not on exam
	DLOM = 1.-(1./(1.-float(marketability_premium)))
	return DLOM

def return_multiple_discounts(*discounts):
	placeholder_discount = 1.
	for discount in enumerate(discounts):
		placeholder_discount = placeholder_discount * (1.-float(discount))
	total_discount = 1. - placeholder_discount
	return total_discount



















































# Formulas from the CFA Curriculum: Financial Reporting & Analysis
########## Accounting ##########

# financial ratios list

def current_ratio(current_assets, current_liabilities):
	return (float(current_assets)/float(current_liabilities))

def quick_ratio(cash, short_term_marketable_securities, receivables, current_liabilities):
	return ((float(cash) + float(short_term_marketable_securities) + float(receivables))/float(current_liabilities))

def cash_ratio(cash, short_term_marketable_securities, current_liabilities):
	return ((float(cash) + float(short_term_marketable_securities))/float(current_liabilities))

def defensive_interval_ratio(cash, short_term_marketable_securities, receivables, daily_cash_expenditures):
	return ((float(cash) + float(short_term_marketable_securities) + float(receivables))/float(daily_cash_expenditures))

def receivables_turnover_ratio(total_revenue, average_receivables):
	return (float(total_revenue)/float(average_receivables))

def days_of_sales_outstanding(number_of_days_in_period, receivables_turnover_ratio):
	DSO = float(number_of_days_in_period)/float(receivables_turnover_ratio)
	return DSO

def inventory_turnover_ratio(COGS, average_inventory):
	return (float(COGS)/float(average_inventory))

def days_of_inventory_on_hand(number_of_days_in_period, inventory_turnover_ratio):
	DOH = float(number_of_days_in_period)/float(inventory_turnover_ratio)
	return DOH

def payables_turnover_ratio(purchases, average_trade_payables):
	return (float(purchases)/float(average_trade_payables))

def number_of_days_of_payables(number_of_days_in_period, payables_turnover_ratio):
	return float(number_of_days_in_period)/float(payables_turnover_ratio)

def cash_conversion_cycle(days_of_inventory_on_hand, days_of_sales_outstanding, number_of_days_of_payables):
	DOH = float(days_of_inventory_on_hand)
	DSO = float(days_of_sales_outstanding)
	return (DOH + DSO - float(number_of_days_of_payables))

def working_capital_turnover_ratio(total_revenue, average_working_capital):
	return (float(total_revenue)/float(average_working_capital))

def fixed_asset_turnover_ratio(total_revenue, average_net_fixed_assets):
	return (float(total_revenue)/float(average_net_fixed_assets))

def total_asset_turnover_ratio(total_revenue, average_total_assets):
	return (float(total_revenue)/float(average_total_assets))

def gross_profit_margin(gross_profit, total_revenue):
	return (float(gross_profit)/float(total_revenue))

def operating_profit_margin(operating_profit, total_revenue):
	return (float(operating_profit)/float(total_revenue))

def pretax_margin(earnings_before_tax_but_after_interest, total_revenue):
	return (float(earnings_before_tax_but_after_interest)/float(total_revenue))

def net_profit_margin(net_income, total_revenue):
	return float(net_income)/float(total_revenue)

def operating_ROA(operating_income, average_total_assets):
	operating_return_on_assets = float(operating_income)/float(average_total_assets)
	return operating_return_on_assets

def ROA(net_income, average_total_assets):
	return_on_assets = float(net_income)/float(average_total_assets)
	return return_on_assets

def ROE(net_income, average_shareholders_equity):
	return_on_equity = float(net_income)/float(average_shareholders_equity)
	return return_on_equity

def return_on_total_capital(EBIT, shareholders_equity, interest_bearing_debt):
	return float(EBIT)/(float(shareholders_equity)+float(interest_bearing_debt))

def return_on_common_equity(net_income, preferred_dividends, average_common_shareholders_equity):
	return (float(net_income)-float(preferred_dividends))/float(average_common_shareholders_equity)

def tax_burden(net_income, EBT):
	return float(net_income)/float(EBT)

def interest_burden(EBT, EBIT):
	return float(EBT)/float(EBIT)

def EBIT_margin(EBIT, total_revenue):
	return float(EBIT)/float(total_revenue)

def financial_leverage_ratio(average_total_assets, average_shareholders_equity):
	# Also called "equity multiplier"
	return float(average_total_assets)/float(average_shareholders_equity)

def total_debt():
	# Total interest bearing short term and long term debt.
	# Excluding liabilities such as accrued expences and accounts payable.
	raise Exception("not finished yet, look this up")

def debt_to_assets(total_debt, total_assets):
	return float(total_debt)/float(total_assets)

def debt_to_equity(total_debt, total_shareholders_equity):
	return float(total_debt)/float(total_shareholders_equity)

def debt_to_capital(total_debt, total_shareholders_equity):
	return float(total_debt)/(float(total_debt) + float(total_shareholders_equity))

def interest_coverage_ratio(EBIT, interest_payments):
	return float(EBIT)/float(interest_payments)

def fixed_charge_coverage_ratio(EBIT, lease_payments, interest_payments):
	return (float(EBIT) + float(lease_payments))/(float(interest_payments) + float(lease_payments))

def dividend_payout_ratio(common_share_dividends, net_income_attributable_to_common_shares):
	return float(common_share_dividends)/float(net_income_attributable_to_common_shares)

def retention_rate_via_dividends(net_income_attributable_to_common_shares, common_share_dividends):
	return (float(net_income_attributable_to_common_shares) - float(common_share_dividends))/float(net_income_attributable_to_common_shares)

def retention_rate_via_payout_ratio(payout_ratio):
	return 1 - float(payout_ratio)

def sustainable_growth_rate(retention_rate, ROE):
	return float(retention_rate) * float(ROE)

def EPS(net_income, preferred_dividends, weighted_average_number_of_ordinary_shares_outstanding):
	return (float(net_income) - float(preferred_dividends))/float(weighted_average_number_of_ordinary_shares_outstanding)

def BVPS(common_shareholders_equity, total_number_of_common_shares_outstanding):
	return float(common_shareholders_equity)/float(total_number_of_common_shares_outstanding)

def FCFE_via_CFO(CFO, FCInv, net_borrowing):
	# better formulas in equity library
	return float(CFO) - float(FCInv) + float(net_borrowing)

def FCFF_via_CFO(CFO, interest_expense, tax_rate, FCInv):
	# better formulas in equity library
	return float(CFO) + (float(interest_expense) * (1 - float(tax_rate))) - float(FCInv)

def FIFO_inventory_via_LIFO_inventory(LIFO_inventory, LIFO_reserve):
	return float(LIFO_inventory) + float(LIFO_reserve)

def FIFO_COGS_via_LIFO_COGS(LIFO_COGS, LIFO_reserve_0, LIFO_reserve_1):
	LIFO_reserve_delta = float(LIFO_reserve_1) - float(LIFO_reserve_0)
	FIFO_COGS = float(LIFO_COGS) - LIFO_reserve_delta
	return FIFO_COGS

def FIFO_net_income_via_LIFO_net_income(LIFO_net_income, LIFO_reserve_0, LIFO_reserve_1, tax_rate):
	LIFO_reserve_delta = float(LIFO_reserve_1) - float(LIFO_reserve_0)
	taxes_on_LIFO_reserve_delta = LIFO_reserve_delta * float(tax_rate)
	FIFO_net_income = float(LIFO_net_income) + LIFO_reserve_delta - taxes_on_LIFO_reserve_delta
	return FIFO_net_income












































# end of line