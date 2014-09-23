import wxStocks_utilities as utils
utils.start_whitespace()

# Requirements
import wx, numpy
from BeautifulSoup import BeautifulSoup

# Standard Libraries
import sys, os, csv, time, datetime, logging, ast, math, threading, inspect, urllib2, json
import pprint as pp
import cPickle as pickle
from pyql import pyql
from wx.lib import sheet

# Internal libraries
from wxStocks_classes import Stock
import wxStocks_db_functions as db
import wxStocks_formulas as formula
import wxStocks_testing
import wxStocks_gui as gui

# True globals are in config
import config

# Necessary in-module functions
def line_number():
    """Returns the current line number in our program."""
    line_number = inspect.currentframe().f_back.f_lineno
    line_number_string = "Line %d:" % line_number
    return line_number_string

# Load data
db.load_all_data()

for stock in config.GLOBAL_STOCK_DICT:
	print stock
	print type(stock)






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