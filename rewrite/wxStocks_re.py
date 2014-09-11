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
import wxStocks_utilities as utils
import wxStocks_testing

# True globals are in config
import config

# Necessary in-module functions
def line_number():
    """Returns the current line number in our program."""
    line_number = inspect.currentframe().f_back.f_lineno
    line_number_string = "Line %d:" % line_number
    return line_number_string


utils.terminal_whitespace()

db.load_all_data()

print line_number(), config.GLOBAL_STOCK_DICT

for i in range(5):
	a = Stock("a")


import gc
def return_list_of_all_stocks_from_active_memory():
	stock_list = []
	for obj in gc.get_objects():
		if type(obj) is Stock:
			stock_list.append(obj)
	#stock_list.sort(key = lambda x: x.symbol)
	return stock_list

all_objs = return_list_of_all_stocks_from_active_memory()
print ""
pp.pprint(all_objs)
print ""
for obj in all_objs:
	utils.print_attributes(obj)
	print ""


print line_number(), config.GLOBAL_STOCK_DICT











