import urllib2
import json
import logging

'''
The module provides Python API to retreive stock information from Yahoo! Finance
using Yahoo Query Language.

The module uses Yahoo Query API, and sends REST to retrieve JSON, then converts
the result in a list of dictionary objects, and returns it.


Basic Usage:
   >>> import pyql
   >>> list = ['FFIV', 'MSFT', 'GOOG']
   >>> print pyql.lookup(list)
   >>> list = ['AAPL']
   >>> print pyql.lookup(list)



'''

class Pyql:
	pass

def lookupQuote(symbols):
	yql = "select * from yahoo.finance.quotes where symbol in (" \
					+ '\'' \
					+ '\',\''.join( symbols ) \
					+ '\'' \
					+ ")"

	url = "http://query.yahooapis.com/v1/public/yql?q=" \
			+ urllib2.quote( yql ) \
			+ "&format=json&env=http%3A%2F%2Fdatatables.org%2Falltables.env&callback="
	#logging.warning(url)
	try:
		result = urllib2.urlopen(url)
	except urllib2.HTTPError, e:
		print ("HTTP error: ", e.code)
	except urllib2.URLError, e:
		print ("Network error: ", e.reason)

	data = json.loads( result.read() )
	jsonQuotes = data['query']['results']['quote']

	# To make sure the function returns a list
	pythonQuotes = []
	if type( jsonQuotes ) == type ( dict() ):
		pythonQuotes.append( jsonQuotes )
	else:
		pythonQuotes = jsonQuotes

	return pythonQuotes

def lookupKeyStats(symbols):
	yql = "select * from yahoo.finance.keystats where symbol in (" \
					+ '\'' \
					+ '\',\''.join( symbols ) \
					+ '\'' \
					+ ")"

	url = "http://query.yahooapis.com/v1/public/yql?q=" \
			+ urllib2.quote( yql ) \
			+ "&format=json&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback="
	#logging.warning(url)
	# e.g. with 4 quotes
	# http://query.yahooapis.com/v1/public/yql?q=
	# SELECT%20*%20FROM%20yahoo.finance.quotes%20where%20symbol%20in%20%28%22YHOO%22%2C%22AAPL%22%2C%22GOOG%22%2C%22MSFT%22%29
	# &format=json&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback=cbfunc
	# http://query.yahooapis.com/v1/public/yql?q=
	# SELECT%20*%20FROM%20yahoo.finance.keystats%20where%20symbol%20in%20%28%22YHOO%22%2C%22AAPL%22%2C%22GOOG%22%2C%22MSFT%22%29
	# &format=json&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback=cbfunc
	try:
		result = urllib2.urlopen(url)
	except urllib2.HTTPError, e:
		print ("HTTP error: ", e.code)
	except urllib2.URLError, e:
		print ("Network error: ", e.reason)

	data = json.loads( result.read() )
	jsonQuotes = data['query']['results']['stats']

	# To make sure the function returns a list
	pythonQuotes = []
	if type( jsonQuotes ) == type ( dict() ):
		pythonQuotes.append( jsonQuotes )
	else:
		pythonQuotes = jsonQuotes

	return pythonQuotes

