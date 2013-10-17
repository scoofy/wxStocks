import urllib2, time, datetime
from BeautifulSoup import BeautifulSoup

ticker = "GOOG"



class StockFullData(object):
	def __init__(self, symbol):
		self.symbol = symbol
		self.epoch = float(time.time())
		self.created_epoch = float(time.time())
		self.updated = datetime.datetime.now()

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

	stock = StockFullData(ticker)

	# yahoo balance sheet loop
	for i in range(len(data_list)):
		if i in [1, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 59, 63, 67, 71, 75, 79, 83, 87, 93, 97, 101, 105, 109, 113, 117, 121,
				126, 130, 135, 139, 144, 148
				]:
			# attribute
			attribute = str(data_list[i])
			attribute = attribute.replace(" ","_")
			attribute = attribute.replace("/","_")
			attribute = attribute.replace("'","")
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
stock = yahoo_annual_balance_sheet_scrape(ticker)







