import os, glob
from wxStocks_modules.wxStocks_classes import CustomAnalysisSpreadsheetCell as Cell

'''
You must return a list of Cell objects for these functions to work properly.

Here, you must use the class "Cell" to refer to a cell you want processed.
This allows the program to process your data in to function wxPython code.
The class Cell has the following default keyword arguments:

my_cell = Cell(
            row = None,
            col = None,
            text = None,
            background_color = None,
            text_color = None,
            font_size = None,
            bold = False,
            function = None,
            row_title = None,
            col_title = None
            )

Import your own custom functions from the "functions_for_custom_analysis_go_in_here" folder.
Your import statements should look like this:

def my_custom_spreadsheet():
    from functions_for_custom_analysis_go_in_here import your_file
    data = your_file.your_function()
'''

def sample_spreadsheet(stock_list):
    "sample ticker sort"

    cell_list = [] # Cell object imported above

    class Row(object):
        "this will help in sorting cells"
        def __init__(self, stock):
            self.stock = stock

    if not stock_list: # no empty list drama
        return

    row_list = []
    for stock in stock_list:
        the_row_of_this_stock = stock_list.index(stock)
        this_row = Row(stock = stock)
        # standard stock attributes
        this_row.ticker = stock.ticker
        this_row.ticker_len = len(stock.ticker)
        this_row.firm_name = stock.firm_name
        row_list.append(this_row)

    def sort_my_rows(row_list):
        'sorts rows by ticker length'
        row_list.sort(key = lambda row: row.ticker_len)

    sort_my_rows(row_list)

    # set colors!
    for row in row_list:
        if row.ticker_len == 1:
            row.row_color = "#FFCCFF"
        elif row.ticker_len == 2:
            row.row_color = "#FFCCCC"
        elif row.ticker_len == 3:
            row.row_color = "#FFFFCC"
        elif row.ticker_len == 4:
            row.row_color = "#CCFFCC"
        elif row.ticker_len == 5:
            row.row_color = "#CCFFFF"
        elif row.ticker_len == 6:
            row.row_color = "#CCCCFF"
        elif row.ticker_len == 7:
            row.row_color = "#CC99FF"
        elif row.ticker_len > 7:
            row.row_color = "#FFFFFF"

    for row in row_list:
        ticker_cell = Cell(text = row.ticker, row = row_list.index(row), col = 0, col_title = "ticker", background_color = row.row_color)
        firm_name_cell = Cell(text = row.firm_name, row = row_list.index(row), col = 1, col_title = "name", background_color = row.row_color)
        ticker_len_cell = Cell(text = row.ticker_len, row = row_list.index(row), col = 2, col_title = "ticker length", background_color = row.row_color)
        cell_list.append(ticker_cell)
        cell_list.append(firm_name_cell)
        cell_list.append(ticker_len_cell)


    one_longer_than_row_list = len(row_list)
    end_cell = Cell(text = "", row = one_longer_than_row_list, col = 0, row_title = "end")
    cell_list.append(end_cell)
    return cell_list
















