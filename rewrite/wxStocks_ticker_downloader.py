import config, urllib2, inspect
import pprint as pp

#new_line = "\n"
#for i in range(1000):
#	print new_line
def download_ticker_symbols():
	headers = {
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
				'Accept-Encoding': 'none',
				'Accept-Language': 'en-US,en;q=0.8',
				'Connection': 'keep-alive',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
				}

	exchanges = config.STOCK_EXCHANGE_LIST
	exchange_data = []

	for exchange in exchanges:
		# Retrieve the webpage as a string
		response = urllib2.Request("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=%s&render=download" % exchange, headers=headers)
		
		try:
			page = urllib2.urlopen(response)
		except urllib2.HTTPError, e:
			print e.fp.read()

		content = page.read()
		content = content.splitlines()

		ticker_data_list = []
		for line in content:
			dummy_list = line.split('"')
			parsed_dummy_list = []
			for datum in dummy_list:
				if datum == ",":
					pass
				elif not datum:
					pass
				else:
					parsed_dummy_list.append(datum)

			ticker_data_list.append(parsed_dummy_list)

		# Remove first unit of data which is:
		# ['Symbol',
		#  'Name',
		#  'LastSale',
		#  'MarketCap',
		#  'ADR TSO',
		#  'IPOyear',
		#  'Sector',
		#  'industry',
		#  'Summary Quote']
		ticker_data_list = ticker_data_list[1:]

		exchange_data = exchange_data + ticker_data_list

		#for ticker_data in ticker_data_list:
		#	print ""
		#	pp.pprint(ticker_data)

	exchange_data.sort(key = lambda x: x[0])

	print line_number(), "Returning ticker download data:", len(exchange_data), "number of items"
	return exchange_data

def line_number():
	"""Returns the current line number in our program."""
	line_number = inspect.currentframe().f_back.f_lineno
	line_number_string = "Line %d:" % line_number
	return line_number_string


#end of line