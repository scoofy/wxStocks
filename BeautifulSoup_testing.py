import urllib2, time, datetime
from BeautifulSoup import BeautifulSoup

ticker = "GOOG"



class StockFullData(object):
	def __init__(self, symbol):
		self.symbol = symbol
		self.epoch = float(time.time())
		self.created_epoch = float(time.time())
		self.updated = datetime.datetime.now()

def yahoo_annual_cash_flow_scrape(ticker):
	soup = BeautifulSoup(urllib2.urlopen('http://finance.yahoo.com/q/cf?s=%s&annual' % ticker), convertEntities=BeautifulSoup.HTML_ENTITIES)
	table = soup.find("table", { "class" : "yfnc_tabledata1" })

	data_list = []


	for cell in table.findAll("td"):
		text = cell.find(text=True)
		if text:
			text = strip_string_whitespace(text)
			text.replace(u'\xa0', u' ')
			#if text == "Period Ending":
			#	dates = table.findAll("th")
			#	for date in dates:
			#		print date
		if text:
			print text
			data_list.append(str(text))
	#print data_list
	for cell in table.findAll("strong"):
		text = cell.find(text=True)
		if text:
			text = strip_string_whitespace(text)
			text.replace(u'\xa0', u' ')
			#if text == "Period Ending":
			#	dates = table.findAll("th")
			#	for date in dates:
			#		print date
		if text:
			print text
			data_list.append(str(text))

	create_or_update_StockFullData(ticker, data_list, "Cash_Flow")

	cash_flow_layout = 	['''
					0	Period Ending
					1	Period Ending
					2	-
					3	-
					4	-
					5	Operating Activities, Cash Flows Provided By or Used In
					6	Depreciation
					7	-
					8	-
					9	-
					10	Adjustments To Net Income
					11	-
					12	-
					13	-
					14	Changes In Accounts Receivables
					15	-
					16	-
					17	-
					18	Changes In Liabilities
					19	-
					20	-
					21	-
					22	Changes In Inventories
					23	-
					24	-
					25	-
					26	Changes In Other Operating Activities
					27	-
					28	-
					29	-
					30	Investing Activities, Cash Flows Provided By or Used In
					31	Capital Expenditures
					32	-
					33	-
					34	-
					35	Investments
					36	-
					37	-
					38	-
					39	Other Cash flows from Investing Activities
					40	-
					41	-
					42	-
					43	Financing Activities, Cash Flows Provided By or Used In
					44	Dividends Paid
					45	-
					46	-
					47	-
					48	Sale Purchase of Stock
					49	-
					50	-
					51	-
					52	Net Borrowings
					53	-
					54	-
					55	-
					56	Other Cash Flows from Financing Activities
					57	-
					58	-
					59	-
					60	Effect Of Exchange Rate Changes
					61	-
					62	-
					63	-
					64	Net Income
					65	-
					66	-
					67	-
					68	Operating Activities, Cash Flows Provided By or Used In
					69	Total Cash Flow From Operating Activities
					70	-
					71	-
					72	-
					73	Investing Activities, Cash Flows Provided By or Used In
					74	Total Cash Flows From Investing Activities
					75	-
					76	-
					77	-
					78	Financing Activities, Cash Flows Provided By or Used In
					79	Total Cash Flows From Financing Activities
					80	-
					81	-
					82	-
					83	Change In Cash and Cash Equivalents
					84	-
					85	-
					86	-
						''']



def yahoo_annual_income_statement_scrape(ticker):
	soup = BeautifulSoup(urllib2.urlopen('http://finance.yahoo.com/q/is?s=%s&annual' % ticker), convertEntities=BeautifulSoup.HTML_ENTITIES)
	table = soup.find("table", { "class" : "yfnc_tabledata1" })

	data_list = []


	for cell in table.findAll("td"):
		text = cell.find(text=True)
		if text:
			text = strip_string_whitespace(text)
			text.replace(u'\xa0', u' ')
			#if text == "Period Ending":
			#	dates = table.findAll("th")
			#	for date in dates:
			#		print date
		if text:
			print text
			data_list.append(str(text))
	#print data_list
	for cell in table.findAll("strong"):
		text = cell.find(text=True)
		if text:
			text = strip_string_whitespace(text)
			text.replace(u'\xa0', u' ')
			#if text == "Period Ending":
			#	dates = table.findAll("th")
			#	for date in dates:
			#		print date
		if text:
			print text
			data_list.append(str(text))

	create_or_update_StockFullData(ticker, data_list, "Income_Statement")

	income_statment_layout = 	['''
							0	Period Ending
							1	Period Ending
							2	Cost of Revenue
							3	-
							4	-
							5	-
							6	Operating Expenses
							7	Research Development
							8	-
							9	-
							10	-
							11	Selling General and Administrative
							12	-
							13	-
							14	-
							15	Non Recurring
							16	-
							17	-
							18	-
							19	Others
							20	-
							21	-
							22	-
							23	Total Operating Expenses
							24	-
							25	-
							26	-
							27	Income from Continuing Operations
							28	Total Other Income/Expenses Net
							29	-
							30	-
							31	-
							32	Earnings Before Interest And Taxes
							33	-
							34	-
							35	-
							36	Interest Expense
							37	-
							38	-
							39	-
							40	Income Before Tax
							41	-
							42	-
							43	-
							44	Income Tax Expense
							45	-
							46	-
							47	-
							48	Minority Interest
							49	-
							50	-
							51	-
							52	Net Income From Continuing Ops
							53	-
							54	-
							55	-
							56	Non-recurring Events
							57	Discontinued Operations
							58	-
							59	-
							60	-
							61	Extraordinary Items
							62	-
							63	-
							64	-
							65	Effect Of Accounting Changes
							66	-
							67	-
							68	-
							69	Other Items
							70	-
							71	-
							72	-
							73	Preferred Stock And Other Adjustments
							74	-
							75	-
							76	-
							77	Total Revenue
							78	-
							79	-
							80	-
							81	Gross Profit
							82	-
							83	-
							84	-
							85	Operating Income or Loss
							86	-
							87	-
							88	-
							89	Net Income
							90	-
							91	-
							92	-
							93	Net Income Applicable To Common Shares
							94	-
							95	-
							96	-
								''']


def yahoo_annual_balance_sheet_scrape(ticker):
	soup = BeautifulSoup(urllib2.urlopen('http://finance.yahoo.com/q/bs?s=%s&annual' % ticker), convertEntities=BeautifulSoup.HTML_ENTITIES)
	table = soup.find("table", { "class" : "yfnc_tabledata1" })

	data_list = []
	#for row in table.findAll("tr"):
	for cell in table.findAll("td"):#row.findAll("td"):
		text = strip_string_whitespace(cell.findNext(text=True))
		text.replace(u'\xa0', u' ')
		if text:
			print text
			data_list.append(str(text))
	#print data_list
	for cell in table.findAll("strong"):
		text = cell.find(text=True)
		if text:
			text = strip_string_whitespace(text)
			text.replace(u'\xa0', u' ')
			#if text == "Period Ending":
			#	dates = table.findAll("th")
			#	for date in dates:
			#		print date
		if text:
			print text
			data_list.append(str(text))

	create_or_update_StockFullData(ticker, data_list, "Balance_Sheet")

	balance_sheet_layout = 	['''
							0	Period Ending
							1	Period Ending
							2	-
							3	-
							4	-
							5	Assets
							6	Assets
							7	Current Assets
							8	Cash And Cash Equivalents
							9	-
							10	-
							11	-
							12	Short Term Investments
							13	-
							14	-
							15	-
							16	Net Receivables
							17	-
							18	-
							19	-
							20	Inventory
							21	-
							22	-
							23	-
							24	Other Current Assets
							25	-
							26	-
							27	-
							28	Long Term Investments
							29	-
							30	-
							31	-
							32	Property Plant and Equipment
							33	-
							34	-
							35	-
							36	Goodwill
							37	-
							38	-
							39	-
							40	Intangible Assets
							41	-
							42	-
							43	-
							44	Accumulated Amortization
							45	-
							46	-
							47	-
							48	Other Assets
							49	-
							50	-
							51	-
							52	Deferred Long Term Asset Charges
							53	-
							54	-
							55	-
							56	Liabilities
							57	Liabilities
							58	Current Liabilities
							59	Accounts Payable
							60	-
							61	-
							62	-
							63	Short/Current Long Term Debt
							64	-
							65	-
							66	-
							67	Other Current Liabilities
							68	-
							69	-
							70	-
							71	Long Term Debt
							72	-
							73	-
							74	-
							75	Other Liabilities
							76	-
							77	-
							78	-
							79	Deferred Long Term Liability Charges
							80	-
							81	-
							82	-
							83	Minority Interest
							84	-
							85	-
							86	-
							87	Negative Goodwill
							88	-
							89	-
							90	-
							91	Stockholders' Equity
							92	Stockholders' Equity
							93	Misc Stocks Options Warrants
							94	-
							95	-
							96	-
							97	Redeemable Preferred Stock
							98	-
							99	-
							100	-
							101	Preferred Stock
							102	-
							103	-
							104	-
							105	Common Stock
							106	-
							107	-
							108	-
							109	Retained Earnings
							110	-
							111	-
							112	-
							113	Treasury Stock
							114	-
							115	-
							116	-
							117	Capital Surplus
							118	-
							119	-
							120	-
							121	Other Stockholder Equity
							122	-
							123	-
							124	-
							125	Assets
							126	Total Current Assets
							127	-
							128	-
							129	-
							130	Total Assets
							131	-
							132	-
							133	-
							134	Liabilities
							135	Total Current Liabilities
							136	-
							137	-
							138	-
							139	Total Liabilities
							140	-
							141	-
							142	-
							143	Stockholders' Equity
							144	Total Stockholder Equity
							145	-
							146	-
							147	-
							148	Net Tangible Assets
							149	-
							150	-
							151	-
							''']
	

def return_existing_StockFullData(ticker):
	pass

def create_or_update_StockFullData(ticker, data_list, data_type):
	stock = return_existing_StockFullData(ticker)
	if not stock:
		stock = StockFullData(ticker)

	# yahoo balance sheet loop
	cash_flow_data_positions = [1,6,10,14,18,22,26,31,35,39,44,48,52,56,60,64,69,74,79,83]
	income_statement_data_postitions = [2,7,11,15,19,23,28,32,36,40,44,48,52,57,61,65,69,73,77,81,85,89,93]
	balance_sheet_data_positions = [1,8,12,16,20,24,28,32,36,40,44,48,52,59,63,67,71,75,79,83,87,93,97,101,105,109,113,117,121,126,130,135,139,144,148]
	
	data_positions = []
	if data_type == "Cash_Flow":
		data_positions = cash_flow_data_positions
	elif data_type == "Balance_Sheet":
		data_positions = balance_sheet_data_positions
	elif data_type == "Income_Statement":
		data_positions = income_statement_data_postitions
	else:
		print "no data type selected"
		return

	for i in range(len(data_list)):
		if i in data_positions:
			# attribute
			attribute = str(data_list[i])
			attribute = attribute.replace(" ","_")
			attribute = attribute.replace("/","_")
			attribute = attribute.replace("'","")
			if attribute == "Period_Ending":
				attribute = attribute + "_For_" + data_type
			attribute_data_list = []
			for j in range(3):
				data = data_list[i+j+1]
				data = data.replace(",","")
				#try:
				#	data = int(data)
				#except:
				#	# data is not a number
				#	pass
				attribute_data_list.append(data)
			setattr(stock, attribute, attribute_data_list)

	for attribute in dir(stock):
		if not attribute.startswith("_"):
			print ticker+"."+attribute+":" , getattr(stock, attribute)
	return stock


def strip_string_whitespace(some_string):
	stripped_string = " ".join(some_string.split())
	return stripped_string

#stock = yahoo_annual_income_statement_scrape(ticker)
stock = yahoo_annual_cash_flow_scrape(ticker)
#stock = yahoo_annual_balance_sheet_scrape(ticker)







