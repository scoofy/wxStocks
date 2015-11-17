import os, glob, config
from wxStocks_modules.wxStocks_classes import SpreadsheetCell as Cell

def line_number():
    import inspect
    """Returns the current line number in our program."""
    #print 'remove this temporary line number function'
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
            function = None,
            )

Import your own custom functions from the "functions_for_custom_analysis_go_in_here" folder.
Your import statements should look like this:

def my_custom_spreadsheet():
    from functions_for_custom_analysis_go_in_here import your_file
    data = your_file.your_function()
'''
# Note, if you are adding a double click event into your analysis spreadsheets (you programming champ), you may run into errors, here is why:
# There is a preset function in wxStocks_modules/wxStocks_gui.py in the CustomAnalysisPage object, in the create_custom_analysis_spread_sheet method
# This preset event function on double click (search for: self.screen_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK)
# takes the text in that cell, and passes it to the add_ticker_to_research_page in wxStocks_modules/wxStocks_utilities.py,
# which passes it to the research page for processing. If the text is a valid ticker it'll add that stock to the research page.
# I'm not sure how to ensure that only valid ticker columns are allowed to be passed for custom spreadsheets, but for now i'll allow any cell to be double clicked.

def rainbow_spreadsheet(stock_list):
    "rainbow sort"

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

    def make_rainbow_row_list(row_list):
        ones_list =     [row for row in row_list if row.ticker_len == 1]
        twos_list =     [row for row in row_list if row.ticker_len == 2]
        threes_list =   [row for row in row_list if row.ticker_len == 3]
        fours_list =    [row for row in row_list if row.ticker_len == 4]
        fives_list =    [row for row in row_list if row.ticker_len == 5]
        sixs_list =     [row for row in row_list if row.ticker_len == 6]
        sevens_list =   [row for row in row_list if row.ticker_len == 7]

        len_list = [ones_list, twos_list, threes_list, fours_list, fives_list, sixs_list, sevens_list]

        largest_len = 0
        for num_list in len_list:
            if len(num_list) > largest_len:
                largest_len = len(num_list)


        rainbow_list = []
        for i in range(largest_len):
            for num_list in len_list:
                try:
                    rainbow_list.append(num_list[i])
                except:
                    pass
        return rainbow_list

    row_list = make_rainbow_row_list(row_list)

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



def jas_stock_analysis(stock_list):
    "a jas analysis"
    from functions_for_custom_analysis_go_in_here import aaii_formulas as aaii
    import numpy
    import pprint as pp
    import locale

    portfolios = config.PORTFOLIO_OBJECTS_DICT.values()

    #background_color = {"green": "#D1FFD1", "red": "#8A0002", "orange": "#FFE0B2"}
    class Attribute(object):
        def __init__(self, name, function, weight, maximum, minimum, display, size_factor, col, align_right):
            self.name = name
            self.function = function
            self.weight = weight
            self.maximum = maximum
            self.minimum = minimum
            self.size_factor = size_factor
            self.display = display
            self.col = col
            self.align_right = align_right
            self.avg = None
            self.std = None

    class Row(object):
        "used to look at a whole row of stock' data at the same time"
        def __init__(self, stock):
            self.stock = stock

    class Function_Globals(object):
        def __init__(self,
                     default_row_buffer_before_stocks = None,
                     all_cells_list = [],
                     row_list = [],
                     attrbute_name_avg_and_std_triple_list = [],
                     avg_row_cell = None,
                     score_avg = None,
                     score_std = None,
                     ):
            self.default_row_buffer_before_stocks = default_row_buffer_before_stocks
            self.all_cells_list = all_cells_list
            self.row_list = row_list
            self.attrbute_name_avg_and_std_triple_list = attrbute_name_avg_and_std_triple_list
            self.avg_row_cell = avg_row_cell
            self.score_avg = score_avg
            self.score_std = score_std
    function_globals = Function_Globals(default_row_buffer_before_stocks = 2)

    def return_Row_obj_else_create(stock):
        correct_row = None
        for row in function_globals.row_list:
            if row.stock is stock:
                correct_row = row
        if not correct_row:
            correct_row = Row(stock)
            function_globals.row_list.append(correct_row)
        return correct_row


    def top_row():
        text = 'BUY CANDIDATES'
        top_row_cell = Cell(row = 0, col=0, text=text)
        function_globals.all_cells_list.append(top_row_cell)
    def gen_attribute_list(row = 1):
        #print line_number(), column_text_list
        cell_list_to_return = []
        for attribute_obj in attribute_list:
            attribute_cell = Cell(row = row, col = attribute_obj.col, text = attribute_obj.name, col_title = attribute_obj.name)
            function_globals.all_cells_list.append(attribute_cell)
    def create_rows_of_stock_data(stock_list = stock_list):
        rows_before_stock_data = 2
        rows_list = []
        for stock in stock_list:
            stock_row = return_Row_obj_else_create(stock)
            for attribute_obj in attribute_list:
                try:
                    data = attribute_obj.function(stock)
                except: # in case it throws an attribute error
                    data = None
                data_cell = Cell(text = data) # this will be thrown out later
                setattr(stock_row, attribute_obj.name, data_cell)

    def create_data_scores():

        for attribute_obj in attribute_list:
            if attribute_obj.size_factor:
                # first iterate over each attribute, to find the mean and standard dev

                unadjusted_attribute_data_list_valid_values_only = []
                adjusted_attribute_data_list = []
                nonetype_attribute_list = []

                # seperate nonconforming data
                for row in function_globals.row_list:
                    data_cell = getattr(row, attribute_obj.name)
                    data = data_cell.text
                    try:
                        data = float(data)
                        data = round(data, 2)
                        unadjusted_attribute_data_list_valid_values_only.append(data)
                    except:
                        nonetype_attribute_list.append(data)

                if not unadjusted_attribute_data_list_valid_values_only:
                    # no reason to look at data, all is None
                    continue
                else:
                    print line_number(), unadjusted_attribute_data_list_valid_values_only

                # unadjusted avg will be rounded to 3 instead of 2 for identification purposes
                unadjusted_avg = round(numpy.mean(unadjusted_attribute_data_list_valid_values_only), 3)
                unadjusted_avg_len = len(unadjusted_attribute_data_list_valid_values_only)
                # set degree of freedom to subtract from N to 0 if only one date unit
                if len(unadjusted_attribute_data_list_valid_values_only) > 1:
                    number_to_minus_degrees_of_freedom = 1
                else:
                    number_to_minus_degrees_of_freedom = 0
                unadjusted_std = numpy.std(unadjusted_attribute_data_list_valid_values_only, ddof=number_to_minus_degrees_of_freedom)

                if not (isinstance(unadjusted_avg, float) and isinstance(unadjusted_avg_len, float) and isinstance(unadjusted_std, float) ):
                    print line_number()
                    print "unadjusted_avg:", unadjusted_avg
                    print "unadjusted_avg_len:", unadjusted_avg_len
                    print "unadjusted_std:", unadjusted_std


                # set nonconforming data to avg of conforming data
                nonetype_to_avg_attribute_list = []
                for nonconforming_data in nonetype_attribute_list:
                    nonetype_to_avg_attribute_list.append(unadjusted_avg)

                # set conforming data and replaced data into the min/max checks
                for row in function_globals.row_list:
                    data_cell = getattr(row, attribute_obj.name)
                    data = data_cell.text
                    try:
                        data = float(data)
                        data = round(data, 2)
                    except:
                        # replace nonconforming data with avg again
                        data = unadjusted_avg
                    if type(data) is float:
                        if attribute_obj.minimum or attribute_obj.maximum:
                            # normalize data
                            if data < attribute_obj.minimum:
                                adjusted_data = attribute_obj.minimum
                                data_cell.text_color = "#B8B8B8"
                            elif data > attribute_obj.maximum:
                                adjusted_data = attribute_obj.maximum
                                data_cell.text_color = "#B8B8B8"
                            else: # irrelevant
                                adjusted_data = data
                            adjusted_attribute_data_list.append(adjusted_data)
                        elif data and attribute_obj.name == "Cur Ratio": # strange variation in rms code
                            if data > 10.:
                                adjusted_data = 1.7
                                data_cell.text_color = "#B8B8B8"
                            elif data > 4.:
                                adjusted_data = 4.
                                data_cell.text_color = "#B8B8B8"
                            else:
                                adjusted_data = data
                            adjusted_attribute_data_list.append(adjusted_data)
                        elif data and attribute_obj.name == "ROE %"+"Dev": # strange variation in rms code
                            if data < 0.:
                                adjusted_data = 1.5
                                data_cell.text_color = "#B8B8B8"
                            else:
                                adjusted_data = data
                            adjusted_attribute_data_list.append(adjusted_data)
                        elif data and attribute_obj.name == "Inv2sales Grwth": # strange variation in rms code
                            adjusted_data = -abs(data-1.)
                            data_cell.text_color = "#B8B8B8"
                            adjusted_attribute_data_list.append(adjusted_data)
                        else:
                            adjusted_attribute_data_list.append(data)

                adjusted_data_avg = numpy.mean(adjusted_attribute_data_list)
                adjusted_data_avg_len = len(adjusted_attribute_data_list)
                 # set degree of freedom to subtract from N to 0 if only one date unit
                if len(adjusted_attribute_data_list) > 1:
                    number_to_minus_degrees_of_freedom = 1
                else:
                    number_to_minus_degrees_of_freedom = 0
                adjusted_data_std = numpy.std(adjusted_attribute_data_list, ddof=number_to_minus_degrees_of_freedom) # 1 degrees of freedom for std

                if not (isinstance(adjusted_data_avg, float) and isinstance(adjusted_data_avg_len, float) and isinstance(adjusted_data_std, float) ):
                    print line_number()
                    print "adjusted_avg:", adjusted_data_avg
                    print "adjusted_avg_len:", adjusted_data_avg_len
                    print "adjusted_std:", adjusted_data_std

                # set attribute average standard deviation for colors later
                attribute_obj.avg = float(round(adjusted_data_avg, 2))
                attribute_obj.std = float(round(adjusted_data_std, 2))
                #print line_number()
                #print "\n"*2
                #print sorted(adjusted_attribute_data_list)
                #print line_number(), attribute_obj.name, "unadjusted avg", unadjusted_avg, "length=", unadjusted_avg_len
                #print line_number(), attribute_obj.name, "unadjusted std", unadjusted_std
                #print line_number(), attribute_obj.name, "adjusted avg", adjusted_data_avg, "length=", adjusted_data_avg_len
                #print line_number(), attribute_obj.name, "adjusted std", adjusted_data_std
                #print "\n"*2

                function_globals.attrbute_name_avg_and_std_triple_list.append([attribute_obj.name, unadjusted_avg, unadjusted_std])

                for row in function_globals.row_list:
                    if attribute_obj.size_factor:
                        #b =  attribute_obj.function(row.stock)
                        try:
                            b = float(attribute_obj.function(row.stock))
                        except:
                            if attribute_obj.avg:
                                b = attribute_obj.avg
                            else:
                                print line_number(), "No avg for", attribute_obj.name, "set avg to 0"
                                b = 0.

                        if not (type(b) is float):
                            print line_number(), "Error: b should always be float"
                            print type(b)
                            print attribute_obj.name
                            print attribute_obj.avg

                        if attribute_obj.minimum or attribute_obj.maximum:
                            # normalize data
                            if b < attribute_obj.minimum:
                                b = attribute_obj.minimum
                            elif b > attribute_obj.maximum:
                                b = attribute_obj.maximum
                        elif b and attribute_obj.name == "Cur Ratio": # strange variation in rms code
                            if b > 10.:
                                b = 1.7
                            elif b > 4.:
                                b = 4.
                        elif b and attribute_obj.name == "ROE %"+"Dev": # strange variation in rms code
                            if b < 0.:
                                b = 1.5
                        elif b and attribute_obj.name == "Inv2sales Grwth": # strange variation in rms code
                            b = -abs(b-1.)
                        b = round(b, 2)
                        try:
                            mu = float(adjusted_data_avg)
                        except:
                            mu = None
                        try:
                            sigma = float(adjusted_data_std)
                        except:
                            sigma = None
                        if type(b) is float and type(mu) is float and sigma:
                            z_score = (b-mu)/sigma
                            z_score = round(z_score, 2)
                        else:
                            z_score = None
                        z_score_cell = Cell(text = z_score)
                        setattr(row, str(attribute_obj.name) + "__z_score", z_score_cell)

        for stock_row in function_globals.row_list:
            score = 0.0
            for attribute_obj in attribute_list:
                weight = attribute_obj.weight
                if weight:
                    try:
                        z_score_data_cell = getattr(stock_row, attribute_obj.name + "__z_score")
                        z_score_data = z_score_data_cell.text
                        if z_score_data is not None:
                            modified_score_value = z_score_data * weight
                            if attribute_obj.size_factor:
                                if attribute_obj.size_factor == "big":
                                    score += modified_score_value
                                elif attribute_obj.size_factor == "small":
                                    score -= modified_score_value
                                else:
                                    print line_number(), "Error: something went wrong here"
                                z_score_data_cell.text = score
                    except Exception, e:
                        print line_number(), e
                        pass
            stock_row.Score.text = score

    def find_score_standard_deviations():
        score_list = []
        for stock_row in function_globals.row_list:
            score = stock_row.Score.text
            if score is not None:
                if score > 1000:
                    score = 1000
                if score < -1000:
                    score = -1000
                score_list.append(score)
        score_avg = numpy.average(score_list)
        # set degree of freedom to subtract from N to 0 if only one date unit
        if len(score_list) > 1:
            number_to_minus_degrees_of_freedom = 1
        else:
            number_to_minus_degrees_of_freedom = 0
        score_std = numpy.std(score_list, ddof=number_to_minus_degrees_of_freedom)

        if not (isinstance(score_avg, float) and isinstance(score_std, float) ):
            print line_number()
            print "score_avg:", score_avg
            print "score_std:", score_std

        function_globals.score_avg = score_avg
        function_globals.score_std = score_std

        for attribute_obj in attribute_list:
            if attribute_obj.name == "Score":
                attribute_obj.avg = score_avg
                attribute_obj.std = score_std


    def sort_row_list_and_convert_into_cells():
        ''' this is a complex function,
            it sorts by row,
            then find each attribute,
            then looks for the attribute object,
            then sees if the value is outside the bounds of a standard deviation,
            then sets object colors
        '''
        extra_rows = 0
        extra_rows += function_globals.default_row_buffer_before_stocks

        score_avg = None
        score_std = None
        # first, get score avg and std
        for attribute_obj in attribute_list:
            if attribute_obj.name == "Score":
                score_avg = attribute_obj.avg
                score_std = attribute_obj.std

        first_iteration = True
        last_sigma_stage = None

        function_globals.row_list.sort(key = lambda x: x.Score.text, reverse=True)
        for stock_row in function_globals.row_list:
            # Now, check if we need a blank row between sigma's
            if   stock_row.Score.text > (score_avg + (score_std * 3)):
                # greater than 3 sigmas
                if first_iteration:
                    first_iteration = False
                    last_sigma_stage = 3

            elif stock_row.Score.text > (score_avg + (score_std * 2)):
                # greater than 2 sigmas
                if first_iteration:
                    first_iteration = False
                    last_sigma_stage = 2
                if last_sigma_stage > 2:
                    last_sigma_stage = 2

                    empty_row_num = function_globals.row_list.index(stock_row) + extra_rows
                    empty_cell = Cell(text = " ", col = 0, row = empty_row_num, row_title = "3 sigma")
                    function_globals.all_cells_list.append(empty_cell)
                    extra_rows += 1

            elif stock_row.Score.text > (score_avg + (score_std * 1)):
                # greater than 1 sigma
                if first_iteration:
                    first_iteration = False
                    last_sigma_stage = 1
                if last_sigma_stage > 1:
                    last_sigma_stage = 1

                    empty_row_num = function_globals.row_list.index(stock_row) + extra_rows
                    empty_cell = Cell(text = " ", col = 0, row = empty_row_num, row_title = "2 sigma")
                    function_globals.all_cells_list.append(empty_cell)
                    extra_rows += 1

            elif stock_row.Score.text > (score_avg + (score_std * 0)):
                # greater than avg
                if first_iteration:
                    first_iteration = False
                    last_sigma_stage = 0
                if last_sigma_stage > 0:
                    last_sigma_stage = 0

                    empty_row_num = function_globals.row_list.index(stock_row) + extra_rows
                    empty_cell = Cell(text = " ", col = 0, row = empty_row_num, row_title = "1 sigma")
                    function_globals.all_cells_list.append(empty_cell)
                    extra_rows += 1

            elif stock_row.Score.text >= (score_avg - (score_std * 1)):
                if first_iteration:
                    first_iteration = False
                    last_sigma_stage = 0
                if last_sigma_stage > -1:
                    last_sigma_stage = -1

                    empty_row_num = function_globals.row_list.index(stock_row) + extra_rows
                    empty_cell = Cell(text = " ", col = 0, row = empty_row_num, row_title = " ")
                    function_globals.all_cells_list.append(empty_cell)
                    extra_rows += 1

                    # this is the average cell
                    empty_row_num = function_globals.row_list.index(stock_row) + extra_rows
                    avg_cell = Cell(text = " ", col = 0, row = empty_row_num, row_title = "Average")
                    function_globals.all_cells_list.append(avg_cell)
                    function_globals.avg_row_cell = avg_cell
                    extra_rows += 1

                    empty_row_num = function_globals.row_list.index(stock_row) + extra_rows
                    empty_cell = Cell(text = " ", col = 0, row = empty_row_num, row_title = " ")
                    function_globals.all_cells_list.append(empty_cell)
                    extra_rows += 1

            elif stock_row.Score.text > (score_avg - (score_std * 2)):
                # greater than 1 sigma
                if first_iteration:
                    first_iteration = False
                    last_sigma_stage = -1
                if last_sigma_stage > -2:
                    last_sigma_stage = -2

                    empty_row_num = function_globals.row_list.index(stock_row) + extra_rows
                    empty_cell = Cell(text = " ", col = 0, row = empty_row_num, row_title = "-1 sigma")
                    function_globals.all_cells_list.append(empty_cell)
                    extra_rows += 1

            elif stock_row.Score.text > (score_avg - (score_std * 3)):
                # greater than 2 sigma
                if first_iteration:
                    first_iteration = False
                    last_sigma_stage = -2
                if last_sigma_stage > -3:
                    last_sigma_stage = -3

                    empty_row_num = function_globals.row_list.index(stock_row) + extra_rows
                    empty_cell = Cell(text = " ", col = 0, row = empty_row_num, row_title = "-2 sigma")
                    function_globals.all_cells_list.append(empty_cell)
                    extra_rows += 1



            row_num = function_globals.row_list.index(stock_row) + extra_rows

            for attribute_obj in attribute_list:
                data_cell = getattr(stock_row, attribute_obj.name)
                if data_cell.text is not None:
                    data = data_cell.text
                    background_color = None
                    if attribute_obj.avg is not None and attribute_obj.std is not None and data is not None:
                        if attribute_obj.size_factor == "big":
                            if data > (attribute_obj.avg + attribute_obj.std):
                                # better than 1 standard deviation -> green!
                                background_color = "#CCFFCC"
                            elif data < (attribute_obj.avg - (attribute_obj.std * 2)):
                                # worse than 2 standard deviations -> red :/
                                background_color = "#F78181"
                            elif data < (attribute_obj.avg - attribute_obj.std):
                                # worse than 1 standard deviation -> orange
                                background_color = "#FFB499"
                        elif attribute_obj.size_factor == "small":
                            if data < (attribute_obj.avg - attribute_obj.std):
                                # better than 1 standard deviation -> green!
                                background_color = "#CCFFCC"
                            elif data > (attribute_obj.avg + (attribute_obj.std * 2)):
                                # worse than 2 standard deviations -> red :/
                                background_color = "#F78181"
                            elif data > (attribute_obj.avg + attribute_obj.std):
                                # worse than 1 standard deviation -> orange
                                background_color = "#FFB499"

                    new_data_cell = Cell(text = data)
                    new_data_cell.row = row_num
                    new_data_cell.col = attribute_obj.col
                    new_data_cell.background_color = background_color
                    new_data_cell.text_color = data_cell.text_color
                    new_data_cell.align_right = attribute_obj.align_right

                    if attribute_obj.display == "2":
                        new_data_cell.text = "%.2f" % data
                    elif attribute_obj.display == "%":
                        try:
                            data = float(data)
                            if data.is_integer():
                                new_data_cell.text = str(int(round(float(data)))) + "%"
                            else:
                                new_data_cell.text = ("%.2f" % data) + "%"
                        except:
                            new_data_cell.text = str(data) + "%"
                    elif attribute_obj.display == "$":
                        try:
                            new_data_cell.text = config.locale.currency(float(data), grouping = True)
                        except Exception as e:
                            print line_number(), e
                            new_data_cell.text = "$" + str(data)
                    elif attribute_obj.display == "rnk":
                        try:
                            if float(data).is_integer():
                                new_data_cell.text = str(int(data))
                            else:
                                new_data_cell.text = str(data)
                        except:
                            new_data_cell.text = str(data)
                    try:
                        new_data_cell.row_title = stock_row.stock.ticker
                    except:
                        pass
                    function_globals.all_cells_list.append(new_data_cell)

    def create_avg_and_std_cells_for_attributes():
        total_rows = 0
        for cell in function_globals.all_cells_list:
            if cell.row > total_rows:
                total_rows = cell.row

        avg_row_at_the_end = total_rows + 2
        std_row = avg_row_at_the_end + 1
        for attribute_obj in attribute_list:
            for triple in function_globals.attrbute_name_avg_and_std_triple_list:
                if attribute_obj.name == triple[0]:

                    if attribute_obj.display == "2":
                        triple[1] = "%.2f" % triple[1]
                        triple[2] = "%.2f" % triple[2]
                    elif attribute_obj.display == "%":
                        try:
                            triple[1] = float(triple[1])
                            if triple[1].is_integer():
                                triple[1] = str(int(round(float(triple[1])))) + "%"
                            else:
                                triple[1] = ("%.2f" % triple[1]) + "%"
                        except:
                            triple[1] = str(triple[1]) + "%"

                        try:
                            triple[2] = float(triple[2])
                            if triple[2].is_integer():
                                triple[2] = str(int(round(float(triple[2])))) + "%"
                            else:
                                triple[2] = ("%.2f" % triple[2]) + "%"
                        except:
                            triple[2] = str(triple[2]) + "%"

                    elif attribute_obj.display == "$":
                        try:
                            triple[1] = config.locale.currency(float(triple[1]), grouping = True)
                        except Exception as e:
                            print line_number(), e
                            triple[1] = "$" + str(triple[1])

                        try:
                            triple[2] = config.locale.currency(float(triple[2]), grouping = True)
                        except Exception as e:
                            print line_number(), e
                            triple[2] = "$" + str(triple[2])

                    elif attribute_obj.display == "rnk":
                        try:
                            if float(triple[1]).is_integer():
                                triple[1] = str(int(triple[1]))
                            else:
                                triple[1] = str(triple[1])
                        except:
                            triple[1] = str(triple[1])

                        try:
                            if float(triple[2]).is_integer():
                                triple[2] = str(int(triple[2]))
                            else:
                                triple[2] = str(round(triple[2], 2))
                        except:
                            triple[2] = str(triple[2])

                    if function_globals.avg_row_cell:
                        attribute_avg_cell = Cell(text = triple[1],row = function_globals.avg_row_cell.row, col = attribute_obj.col, text_color = "red", align_right = True)
                        function_globals.all_cells_list.append(attribute_avg_cell)
                        attribute_avg_cell = Cell(text = triple[1],row = avg_row_at_the_end, col = attribute_obj.col, row_title = "Average", text_color = "red", align_right = True)
                        function_globals.all_cells_list.append(attribute_avg_cell)
                        attribute_std_cell = Cell(text = triple[2],row = std_row, col = attribute_obj.col, row_title = "Standard Dev",text_color = "red", align_right = True)
                        function_globals.all_cells_list.append(attribute_std_cell)

        score_cols_list = []
        score_display = None
        for attribute_obj in attribute_list:
            if attribute_obj.name == "Score":
                score_cols_list.append(attribute_obj.col)
                score_display = attribute_obj.display
        for col in score_cols_list:
            if function_globals.avg_row_cell:
                score_avg_cell = Cell(text = "%.2f" % function_globals.score_avg, row = function_globals.avg_row_cell.row, col = col, text_color = "red", align_right = True)
                score_avg_cell_2 = Cell(text = "%.2f" % function_globals.score_avg, row = avg_row_at_the_end, col = col, text_color = "red", align_right = True)
                score_std_cell = Cell(text = "%.2f" % function_globals.score_std, row = std_row, col = col, text_color = "red", align_right = True)
                function_globals.all_cells_list.append(score_avg_cell)
                function_globals.all_cells_list.append(score_avg_cell_2)
                function_globals.all_cells_list.append(score_std_cell)



    def return_ticker(stock):
        return stock.ticker
    def return_name(stock):
        return stock.firm_name
    def return_volume(stock):
        return stock#.volume
    def return_relevant_portfolios_in_string(stock):
        #print line_number(), "\n"*10, "--------START---------"
        #print "ticker:", stock.ticker
        #print config.PORTFOLIO_OBJECTS_DICT
        #print "portfolio list:", portfolios
        #print "portfolio 1", portfolios[0]
        #print line_number(),"---------END---------" , "\n"*10
        portfolios_that_contain_stock = []
        for portfolio in portfolios:
            print line_number()
            print "str(stock.ticker) in [str(x) for x in portfolio.stock_shares_dict.keys()]"
            print portfolio.name
            print str(stock.ticker) in [str(x) for x in portfolio.stock_shares_dict.keys()]
            if str(stock.ticker) in [str(x) for x in portfolio.stock_shares_dict.keys()]:
                portfolios_that_contain_stock.append(portfolio.name)
        portfolios_that_contain_stock.sort()
        print line_number(), portfolios_that_contain_stock
        if portfolios_that_contain_stock:
            string_to_return = ", ".join(portfolios_that_contain_stock)
            #string_to_return = "BOOOOOOOOM!"
        else:
            string_to_return = ""
        print line_number(), "\n" * 10, "--------START 2---------"
        if string_to_return:
            print line_number()
            print "success, string to return is:", string_to_return
        else:
            print line_number()
            print "STOCK %s IS NOT IN ANY PORTFOLIOS" % str(stock.ticker)
        print line_number(), "---------END 2---------", "\n" * 10
        return string_to_return


    # attr  = Attribute("name",            function,                               weight, max,    min,    display, size,   col, align_right)
    score   = Attribute("Score",           None,                                   None,   None,   None,   "2",     "big",  0,   True)
    action  = Attribute("Action",          return_relevant_portfolios_in_string,   None,   None,   None,   None,    None,   1,   False)
    ticker  = Attribute("Ticker",          return_ticker,                          None,   None,   None,   None,    None,   2,   False)
    price   = Attribute("Price",           aaii.aaii_price,                        None,   None,   None,   "$",     None,   3,   True)
    volume  = Attribute("AvgDly $K Vol",   aaii.aaii_volume,                       None,   None,   None,   "$",     None,   4,   True)
    neff5h  = Attribute("Neff 3YrH +2xYld",aaii.neff_3yr_H_x2yield,                1.0,    10.,    0.,     "2",     "big",  5,   True)
    neffttm = Attribute("Neff TTM H",      aaii.neff_TTM_historical,               1.0,    10.,    0.,     "2",     "big",  6,   True)
    neff5f  = Attribute("Neff 5 Yr F",     aaii.neff_5_Year_future_estimate,       2.0,    10.,    0.,     "2",     "big",  7,   True)
    margin  = Attribute("Mrgin %"+"Rnk",   aaii.marginPercentRank,                 1.0,    None,   None,   "rnk",   "big",  8,   True)
    roe_rank= Attribute("ROE %"+"Rnk",     aaii.roePercentRank,                    2.0,    None,   None,   "rnk",   "big",  9,   True)
    roe_dev = Attribute("ROE %"+"Dev",     aaii.roePercentDev,                     0.1,    None,   None,   "%",     "small",10,  True)
    ticker2 = Attribute("Ticker",          return_ticker,                          None,   None,   None,   None,    None,   11,  False)
    p2b_g   = Attribute("Prc2Bk Grwth",    aaii.price_to_book_growth,              0.1,    2.,     None,   "%",     "big",  12,  True)
    p2r     = Attribute("Prc 2Rng",        aaii.price_to_range,                    0.1,    0.5,    None,   "2",     "big",  13,  True)
    insiders= Attribute("Insdr %",         aaii.percentage_held_by_insiders,       0.1,    20.,    None,   "%",     "big",  14,  True)
    inst    = Attribute("NetInst Buy%",    aaii.net_institution_buy_percent,       0.1,    None,   None,   "%",     "big",  15,  True)
    current = Attribute("Cur Ratio",       aaii.current_ratio,                     0.1,    None,   None,   "%",     "big",  16,  True)
    ltd2e   = Attribute("LTDbt / Eqty %",  aaii.longTermDebtToEquity,              0.1,    None,   None,   "%",     "small",17,  True)
    neffebit= Attribute("Inv2sales Grwth", aaii.invtory2sales,                     0.1,    None,   None,   "2",     "big",  18,  True)
    neff3h  = Attribute("Neff CF3yrH",     aaii.neffCf3Year,                       1.0,    10.,    0.,     "2",     "big",  19,  True)
    name    = Attribute("Name",            return_name,                            None,   None,   None,   None,    None,   20,  False)
    score2  = Attribute("Score",           None,                                   None,   None,   None,   "2",     "big",  21,  True)

    attribute_list = [score, action, ticker, price, volume, neff5h, neffttm,
        neff5f, margin, roe_rank, roe_dev, ticker2, p2b_g, p2r, insiders, inst,
        current, ltd2e, neffebit, neff3h, name, score2]




    top_row()
    gen_attribute_list()
    create_rows_of_stock_data()
    create_data_scores()
    find_score_standard_deviations()
    sort_row_list_and_convert_into_cells()
    create_avg_and_std_cells_for_attributes()

    print "Done sorting spreadsheet"
    return function_globals.all_cells_list































