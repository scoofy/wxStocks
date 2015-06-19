import os, glob
from wxStocks_modules.wxStocks_classes import CustomAnalysisSpreadsheetCell as Cell

def line_number():
    import inspect
    """Returns the current line number in our program."""
    print 'remove this temporary line number function'
    return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)


'''
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
            function = None
            )

Import your own custom functions from the "functions_for_custom_analysis_go_in_here" folder.
Your import statements should look like this:

def my_custom_spreadsheet():
    from functions_for_custom_analysis_go_in_here import your_file
    data = your_file.your_function()
'''

def test_function_name():
    'test 1 doc string'
    print "\n" * 5, "bong", "\n" * 5

def test_function_2_name():
    'test 2 doc string'
    print "\n" * 5, "bongger2", "\n" * 5

def a_test_function_3_name():
    'test 3 doc string'
    print "\n" * 5, "binger 3", "\n" * 5

def test_function_4_name():
    'test 4 doc string'
    print "\n" * 5, "bingbong4", "\n" * 5

def no_doc_string_and_function_name_is_wayyyy_too_long_long_long_long_long_long_():
    print 'ppppppppoooooooooooooooo'


print "-" * 10
def test2():
    # from functions_for_custom_analysis_go_in_here import your_file
    # test.testing()
    pass

def rms_stock_analysis(stock_list):
    "an RMS analysis"
    #from functions_for_custom_analysis_go_in_here import aaii_formulas as aaii
    all_cells_list = []
    def top_row():
        text = 'BUY CANDIDATES'
        top_row_cell = Cell(row = 0, col=0, text=text)
        all_cells_list.append(top_row_cell)

    def attribute_row():
        row = 1
        column_text_list = [["Score", None],
            ["Action", None],
            ["Ticker", return_ticker],
            ["Price", None],
            ["AvgDly $K Vol", None],
            ["Neff 5Yr H", None],
            ["Neff TTM H", None],
            ["Neff 5 Yr F", None],
            ["Mrgin %%Rnk", None],
            ["ROE %%Rnk", None],
            ["Ticker", None],
            ["Prc2Bk Grwth", None],
            ["Insdr %", None],
            ["NetInst Buy%", None],
            ["Cur Ratio", None],
            ["LTDbt / Eqty %", None],
            ["NeffEv Ebit", None],
            ["NeffCf 3yr H", None],
            ["Name", None],
            ["Score", None],
            ]

        #print line_number(), column_text_list
        cell_list_to_return = []
        for this_tuple in column_text_list:
            #print line_number(), this_tuple
            #print line_number(), column_text_list.index(this_tuple)
            index = column_text_list.index(this_tuple)
            text = this_tuple[0]
            function = this_tuple[1]
            this_cell = Cell(row = 1, col = index, text = text, function = function)
            cell_list_to_return.append(this_cell)
            all_cells_list.append(this_cell)
        return cell_list_to_return

    def return_ticker(stock):
        return stock.ticker

    def create_relevant_stock_data(attribute_cell_list, stock_list = stock_list):
        rows_before_stock_data = 2
        for stock in stock_list:
            for attribute_cell in attribute_cell_list:
                try:
                    text = attribute_cell.function(stock)
                except:
                    text = None
                row = stock_list.index(stock) + rows_before_stock_data
                col = attribute_cell.col
                stock_data_cell = Cell(row = row, col = col, text = text)
                all_cells_list.append(stock_data_cell)





    top_row()
    attribute_cell_list = attribute_row()
    create_relevant_stock_data(attribute_cell_list)
    return all_cells_list































