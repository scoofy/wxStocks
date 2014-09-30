print "Startup may take a few moments..."

import wxStocks_modules.wxStocks_utilities as utils
utils.start_whitespace()
print "Startup may take a few moments..."


# Requirements that must be installed
import wx, numpy # pycrypto, simplecrypt
from modules.BeautifulSoup import BeautifulSoup

# Standard Libraries
import sys, os, logging, math, inspect, urllib2, json
import pprint as pp
import cPickle as pickle
from wx.lib import sheet

# Internal libraries
from wxStocks_modules.wxStocks_classes import Stock
import wxStocks_modules.wxStocks_db_functions as db
import wxStocks_modules.wxStocks_formulas as formula
import wxStocks_modules.wxStocks_testing
import wxStocks_modules.wxStocks_gui as gui

# True globals are in config
import config

# Encryption
def encryption_possible():
	try:
		import Crypto
		from modules.simplecrypt import encrypt, decrypt
		config.ENCRYPTION_POSSIBLE = True
	except:
		print "Encryption not possible"
		config.ENCRYPTION_POSSIBLE = False
	return config.ENCRYPTION_POSSIBLE

# Necessary in-module functions
def line_number():
    """Returns the current line number in our program."""
    line_number = inspect.currentframe().f_back.f_lineno
    line_number_string = "Line %d:" % line_number
    return line_number_string

# Load data
db.load_all_data()

#for ticker in config.GLOBAL_STOCK_DICT:
#	print dir(config.GLOBAL_STOCK_DICT[ticker])
#sys.exit()





### START ###################################################################
app = None
def main():
	global app
	app = wx.App()
	gui.MainFrame(size=(1020,800), #style = wx.MINIMIZE_BOX | wx.CLOSE_BOX
			  ).Show()
	app.MainLoop()
main()

# end of line