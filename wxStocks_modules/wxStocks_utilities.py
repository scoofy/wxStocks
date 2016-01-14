import inspect, logging, time, csv
import config
def line_number():
    """Returns the current line number in our program."""
    return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)

def print_attributes(obj):
    for attribute in dir(obj):
        if attribute[:2] != "__":
            if type(obj) is Stock:
                print obj.symbol + "." + attribute, "=", getattr(obj, attribute)
            else:
                print attribute, "=", getattr(obj, attribute)
def start_whitespace():
    print """
    \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
    \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
    \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
    """

####################### Return functions #################################################
def return_stock_by_symbol(ticker_symbol):
    if not type(ticker_symbol) == str:
        ticker_symbol = str(ticker_symbol)
    try:
        return config.GLOBAL_STOCK_DICT["%s" % ticker_symbol.upper()]
    except Exception as e:
        print line_number()
        try:
            ticker_symbol = ticker_symbol.upper()
        except:
            pass
        print line_number()
        print "Stock with symbol %s does not appear to exist" % ticker_symbol
        return None

def return_all_stocks():
    import re
    stock_list = list(config.GLOBAL_STOCK_DICT.values())
    stock_list.sort(key = lambda x: x.symbol)
    return stock_list

def return_stock_by_yql_symbol(yql_ticker_symbol):
    for ticker in config.GLOBAL_STOCK_DICT:
        if config.GLOBAL_STOCK_DICT[ticker].yql_ticker == yql_ticker_symbol:
            return config.GLOBAL_STOCK_DICT[ticker]
    # if none match
    print line_number()
    logging.error("Stock with yql symbol %s does not appear to exist" % yql_ticker_symbol)
    return None

def return_all_up_to_date_stocks():
    stocks_up_to_date_list = []

    current_time = float(time.time())
    for ticker in config.GLOBAL_STOCK_DICT:
        print int(config.TIME_ALLOWED_FOR_BEFORE_YQL_DATA_NO_LONGER_APPEARS_IN_STOCK_LIST/(24*60*60))
        stock = config.GLOBAL_STOCK_DICT[ticker]
        time_since_update = current_time - stock.last_yql_basic_scrape_update
        if int(time_since_update) > int(config.TIME_ALLOWED_FOR_BEFORE_YQL_DATA_NO_LONGER_APPEARS_IN_STOCK_LIST):
            print line_number(), "Will not add %s to stock list, data is over %d days old, please rescrape" % (str(stock.symbol), int(config.TIME_ALLOWED_FOR_BEFORE_YQL_DATA_NO_LONGER_APPEARS_IN_STOCK_LIST/(24*60*60)))
            continue
        else:
            stocks_up_to_date_list.append(stock)
    return stocks_up_to_date_list

def return_stocks_with_data_errors():
    stock_list = return_all_stocks()
    error_list = []
    for stock in stock_list:
        try:
            if stock.ErrorIndicationreturnedforsymbolchangedinvalid_yf:
                if stock.ErrorIndicationreturnedforsymbolchangedinvalid_yf != "None":
                    error_list.append(stock)
                else:
                    continue
        except:
            continue
    return error_list

def return_cost_basis_per_share(account_obj, ticker):
    '''Return the cost basis per share of a stock in an account, if it exists, else return none'''
    ticker = ticker.upper()
    shares_of_relevant_stock = account_obj.stock_shares_dict.get(ticker)
    if not shares_of_relevant_stock:
        return None
    cost_basis_of_relevant_stock = account_obj.cost_basis_dict.get(ticker)
    if not cost_basis_of_relevant_stock:
        return None
    try:
        cost_basis_per_share = float(cost_basis_of_relevant_stock) / shares_of_relevant_stock
    except:
        return None
    return cost_basis_per_share

def return_account_by_id(id_number):
    try:
        portfolio_obj = config.PORTFOLIO_OBJECTS_DICT[str(id_number)]
        if portfolio_obj:
            return portfolio_obj
        else:
            return None
    except Exception as e:
        print line_number()
        logging.error("Portfolio object with id: %s does not appear to exist" % str(id_number))
        return None

def return_last_close_and_last_update_tuple(stock_obj):
    try:
        last_close = float(getattr(stock_obj, config.DEFAULT_LAST_TRADE_PRICE_ATTRIBUTE_NAME))
        last_update_for_last_close = getattr(stock_obj, config.DEFAULT_LAST_UPDATE)
    except:
        try:
            last_close = float(getattr(stock_obj, config.SECONDARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME))
            last_update_for_last_close = getattr(stock_obj, config.SECONDARY_LAST_UPDATE)
        except:
            try:
                last_close = float(getattr(stock_obj, config.TERTIARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME))
                last_update_for_last_close = getattr(stock_obj, config.TERTIARY_LAST_UPDATE)
            except:
                try:
                    last_close = float(getattr(stock_obj, config.QUATERNARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME))
                    last_update_for_last_close = getattr(stock_obj, config.QUATERNARY_LAST_UPDATE)
                except:
                    last_close = None
                    last_update_for_last_close = None
    return [last_close, last_update_for_last_close]

def money_text_to_float(string_with_non_float_chars):
    output_float_text = ""
    for char in string_with_non_float_chars:
        if char.isdigit() or char in [".", u"."]:
            output_float_text = output_float_text + char
    if output_float_text:
        output_float = float(output_float_text)
        return output_float

def return_last_price_if_possible(stock):
    try:
        last_price = getattr(stock, config.DEFAULT_LAST_TRADE_PRICE_ATTRIBUTE_NAME)
    except:
        last_price = None
    if not last_price:
        try:
            last_price = getattr(stock, config.SECONDARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME)
        except:
            last_price = None
        if not last_price:
            try:
                last_price = getattr(stock, config.TERTIARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME)
            except:
                last_price = None
            if not last_price:
                try:
                    last_price = getattr(stock, config.QUATERNARY_LAST_TRADE_PRICE_ATTRIBUTE_NAME)
                except:
                    last_price = None
    return last_price

def return_daily_volume_if_possible(stock):
    try:
        volume = getattr(stock, config.DEFAULT_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME)
    except:
        volume = None
    if not volume:
        try:
            volume = getattr(stock, config.SECONDARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME)
        except:
            volume = None
        if not volume:
            try:
                volume = getattr(stock, config.TERTIARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME)
            except:
                volume = None
            if not volume:
                try:
                    volume = getattr(stock, config.QUATERNARY_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME)
                except:
                    volume = None
    return volume

def return_stocks_exchange_if_possible(stock):
    try:
        exchange = getattr(stock, config.DEFAULT_STOCK_EXCHANGE_ATTRIBUTE)
        if "nyse" in exchange.lower():
            exchange = "NYSE"
        elif "nasdaq" in exchange.lower():
            exchange = "NASDAQ"
    except:
        try:
            exchange = getattr(stock, config.SECONDARY_STOCK_EXCHANGE_ATTRIBUTE)
            if "nyse" in exchange.lower():
                exchange = "NYSE"
            elif "nasdaq" in exchange.lower():
                exchange = "NASDAQ"
        except:
            try:
                exchange = getattr(stock, config.TERTIARY_STOCK_EXCHANGE_ATTRIBUTE)
                if "nyse" in exchange.lower():
                    exchange = "NYSE"
                elif "nasdaq" in exchange.lower():
                    exchange = "NASDAQ"
            except:
                try:
                    exchange = getattr(stock, config.QUATERNARY_STOCK_EXCHANGE_ATTRIBUTE)
                    if "nyse" in exchange.lower():
                        exchange = "NYSE"
                    elif "nasdaq" in exchange.lower():
                        exchange = "NASDAQ"
                except:
                    exchange = None
    return exchange

def return_stocks_website_if_possible(stock):
    try:
        website = str(getattr(stock, config.DEFAULT_STOCK_WEBSITE_ATTRIBUTE))
    except:
        try:
            website = str(getattr(stock, config.SECONDARY_STOCK_WEBSITE_ATTRIBUTE))
        except:
            try:
                website = str(getattr(stock, config.TERTIARY_STOCK_WEBSITE_ATTRIBUTE))
            except:
                try:
                    website = str(getattr(stock, config.QUATERNARY_STOCK_WEBSITE_ATTRIBUTE))
                except:
                    website = None
    return website
####################### Stock utility functions #################################################
def stock_value_is_negative(stock_obj, attribute_str):
    try:
        getattr(stock_obj, attribute_str)
    except:
        return False
    #print line_number(), "Is %s.%s:" % (stock_obj.symbol, attribute_str), str(getattr(stock_obj, attribute_str)), "negative?"
    #print str(getattr(stock_obj, attribute_str)).startswith("(") or str(getattr(stock_obj, attribute_str)).startswith("-")
    #print ""
    return str(getattr(stock_obj, attribute_str)).startswith("(") or str(getattr(stock_obj, attribute_str)).startswith("-")
####################### Stock utility functions #################################################



### I don't think this is used any more
def importSchwabCSV(csv_file):
    reader = csv.reader(csv_file)
    row_list = []
    for row in reader:
        row_list.append(row)
    washed_row_list = []
    for row in row_list:
        if row:
            washed_row = []
            for cell in row:
                washed_cell = strip_string_whitespace(cell)
                washed_row.append(washed_cell)
            washed_row_list.append(washed_row)
    return washed_row_list
### End don't think this is used any more

### xlrd
def return_relevant_spreadsheet_list_from_workbook(xlrd_workbook):
    relevant_sheets = []
    for i in range(xlrd_workbook.nsheets):
        sheet = xlrd_workbook.sheet_by_index(i)
        print sheet.name
        if sheet.nrows or sheet.ncols:
            print "rows x cols:", sheet.nrows, sheet.ncols
            relevant_sheets.append(sheet)
        else:
            print "is empty"
        print ""
    return relevant_sheets

def return_xls_cell_value(xlrd_spreadsheet, row, column):
    return xlrd_spreadsheet.cell_value(rowx=row, colx=column)

####################### General utility functions #################################################
def gen_ticker_list(csv_file):
    reader = csv.reader(csv_file)
    reader_list = []
    for row in reader:
        reader_list.append(row)
    ticker_list = []
    for row in reader_list:
        if row:
            if row[0] != "Symbol":
                ticker_list.append(row[0])
    ticker_list = strip_list_whitespace(ticker_list)
    ticker_list.sort()
    return ticker_list
def return_list_of_lists(csv_file):
    full_data = []
    reader = csv.reader(csv_file)
    for row in reader:
        full_data.append(list(row))
    #print line_number(),full_data
    return full_data
def openCSV_return_list_of_lists():
    csv_file = filedialog.askopenfile()
    print line_number(),'opening', csv_file
    try:
        ticker_list = return_list_of_lists(csv_file)
        return ticker_list
    except:
        error_label = Label(main_tab, text='You must import a csv file.')
        error_label.pack()
        return
def remove_list_duplicates(some_list):
    if type(some_list) != "list":
        some_list = list(some_list)
    the_set = set(some_list)
    new_list = list(the_set)
    return new_list
def strip_list_whitespace(some_list):
    tag_list = some_list
    #logging.warning(tag_list)
    new_list = []
    for tag in tag_list:
        tag = " ".join(tag.split())
        new_list.append(tag)
    tag_list = new_list
    new_list = []
    for tag in tag_list:
        if tag:
            new_list.append(tag)
    return new_list
def strip_string_whitespace(some_string):
    stripped_string = " ".join(some_string.split())
    return stripped_string
def remove_leading_underscores(some_string):
    if some_string[0] in ["_", u"_"]:
        some_string = some_string[1:]
        remove_leading_underscores(some_string)
    return some_string
def time_since_creation(item_epoch_var):
    raw_secs = round(time.time())-round(item_epoch_var)
    #logging.warning(raw_secs)
    raw_secs = int(raw_secs)
    time_str = None
    if raw_secs < 60:
        seconds = raw_secs
        if seconds > 1:
            time_str = "%d seconds" % seconds
        else:
            time_str = "%d second" % seconds
    elif (raw_secs >= 60) and (raw_secs < (60 * 60)):
        minutes = (raw_secs/60)
        if minutes > 1:
            time_str = "%d minutes" % minutes
        else:
            time_str = "%d minute" % minutes
    elif (raw_secs >= (60*60) and (raw_secs < (60 * 60 * 24))):
        minutes = (raw_secs/60)
        hours = (minutes/60)
        if hours > 1:
            time_str = "%d hours" % hours
        else:
            time_str = "%d hour" % hours
    elif (raw_secs >= (60*60*24) and (raw_secs < (60*60*24*30))):
        minutes = (raw_secs/60)
        hours = (minutes/60)
        days = (hours/24)
        if days > 1:
            time_str = "%d days" % days
        else:
            time_str = "%d day" % days
    elif (raw_secs >=(60*60*24*30)) and (raw_secs < (60*60*24*365)):
        minutes = (raw_secs/60)
        hours = (minutes/60)
        days = (hours/24)
        months = (days/30)
        if months > 1:
            time_str = "%d months" % months
        else:
            time_str = "%d month" % months
    elif raw_secs >= (60*60*24*365):
        minutes = (raw_secs/60)
        hours = (minutes/60)
        days = (hours/24)
        years = (days/365)
        if years > 1:
            time_str = "%d years" % years
        else:
            time_str = "%d year" % years
    else:
        logging.error("something wrong with time_since_creation function")
        time_str = None
    return time_str
def check_url(url_str):
    link_var = url_str
    deadLinkFound = check_url_instance(link_var)
    if deadLinkFound:
        link_var = "http://" + link_var
        deadLinkFound = check_url_instance(link_var)
        if deadLinkFound:
            link_var = "http://www." + link_var
            deadLinkFound = check_url_instance(link_var)
            if deadLinkFound:
                link_var = None
    return link_var
def check_url_instance(url_str):
    link_var = url_str
    logging.warning(link_var)
    deadLinkFound = True
    try:
        f = urlfetch.fetch(url=link_var, deadline=30)
        if f.status_code == 200:
            #logging.warning(f.content)
            pass
        deadLinkFound = False
    except Exception as e:
        logging.warning('that failed')
        logging.warning(e)
    logging.warning(deadLinkFound)
    return deadLinkFound
def time_from_epoch(item_epoch_var):
    raw_secs = round(item_epoch_var)
    #logging.warning(raw_secs)
    raw_secs = int(raw_secs)
    time_str = None
    if raw_secs < 60:
        seconds = raw_secs
        if seconds > 1:
            time_str = "%d seconds" % seconds
        else:
            time_str = "%d second" % seconds
    elif (raw_secs >= 60) and (raw_secs < (60 * 60)):
        minutes = (raw_secs/60)
        if minutes > 1:
            time_str = "%d minutes" % minutes
        else:
            time_str = "%d minute" % minutes
    elif (raw_secs >= (60*60) and (raw_secs < (60 * 60 * 24))):
        minutes = (raw_secs/60)
        hours = (minutes/60)
        if hours > 1:
            time_str = "about %d hours" % hours
        else:
            time_str = "about %d hour" % hours
    elif (raw_secs >= (60*60*24) and (raw_secs < (60*60*24*30))):
        minutes = (raw_secs/60)
        hours = (minutes/60)
        days = (hours/24)
        if days > 1:
            time_str = "%d days" % days
        else:
            time_str = "%d day" % days
    elif (raw_secs >=(60*60*24*30)) and (raw_secs < (60*60*24*365)):
        minutes = (raw_secs/60)
        hours = (minutes/60)
        days = (hours/24)
        months = (days/30)
        if months > 1:
            time_str = "%d months" % months
        else:
            time_str = "%d month" % months
    elif raw_secs >= (60*60*24*365):
        minutes = (raw_secs/60)
        hours = (minutes/60)
        days = (hours/24)
        years = (days/365)
        if years > 1:
            time_str = "%d years" % years
        else:
            time_str = "%d year" % years
    else:
        logging.error("something wrong with time_from_epoch function")
        time_str = None
    return time_str

def is_number(some_string):
    try:
        float(some_string)
        return True
    except Exception, exception:
        # print exception
        return False
def relevant_float(some_float):
    return (some_float - int(some_float)) != 0
def contains_digits(some_string):
    for character in list(some_string):
        if character.isdigit():
            return True
            break
    return False
def first_character_is_digit(some_string):
    return some_string[0].isdigit()

def return_dictionary_of_object_attributes_and_values(obj):
    attribute_list = []
    if obj:
        for key in obj.__dict__:
            if key[:1] != "__":
                attribute_list.append(key)

        obj_attribute_value_dict = {}

        for attribute in attribute_list:
            obj_attribute_value_dict[attribute] = getattr(obj, attribute)

        #for attribute in obj_attribute_value_dict:
        #   print attribute, ":", obj_attribute_value_dict[attribute]

        return obj_attribute_value_dict

####################### utility functions involving pages #######################################
def add_ticker_to_research_page(ticker):
    research_page_ref = config.GLOBAL_PAGES_DICT.get(config.RESEARCH_PAGE_UNIQUE_ID)
    research_page = research_page_ref.obj
    research_page.addStock("event", ticker = ticker)

def update_all_dynamic_grids():
    refresh_all_portfolio_spreadsheets()
    refresh_all_stocks_page_spreadsheet()
    refresh_one_stock_data_page_spreadsheet()
    refresh_sale_prep_page_spreadsheet()
    refresh_trade_page_spreadsheet()

def refresh_all_portfolio_spreadsheets():
    # refresh portfolios
    portfolio_main_tab_ref = config.GLOBAL_PAGES_DICT.get(config.PORTFOLIO_PAGE_UNIQUE_ID)
    portfolio_main_tab_index = portfolio_main_tab_ref.index
    possible_number_of_portfolios = len(config.GLOBAL_PAGES_DICT) - len(config.GLOBAL_UNIQUE_ID_LIST)
    print line_number()
    for i in range(possible_number_of_portfolios):
        portfolio_account_ref_str = str(portfolio_main_tab_index) + "." + str(i + 1)
        print portfolio_account_ref_str
        portfolio_account_ref = config.GLOBAL_PAGES_DICT.get(portfolio_account_ref_str)
        if portfolio_account_ref:
            if portfolio_account_ref.obj.portfolio_obj:
                portfolio_grid_update_function = portfolio_account_ref.obj.spreadSheetFill(portfolio_account_ref.obj.portfolio_obj)
                print line_number(), portfolio_account_ref.name, "has loaded a new spreadsheet"

def refresh_all_stocks_page_spreadsheet():
    # refresh all stock grid if it exists
    all_stocks_page_ref = config.GLOBAL_PAGES_DICT.get(config.ALL_STOCKS_PAGE_UNIQUE_ID)
    if all_stocks_page_ref:
        if not all_stocks_page_ref.obj.first_spread_sheet_load:
            all_stocks_page_ref.obj.spreadSheetFillAllStocks('event')
            print line_number(), all_stocks_page_ref.name, "has loaded a new spreadsheet"
        else:
            print line_number(), "all_stocks_page_ref.obj has no loaded spreadsheet"

def refresh_one_stock_data_page_spreadsheet():
    # refresh one stock grid if it exists
    one_stocks_data_page_ref = config.GLOBAL_PAGES_DICT.get(config.STOCK_DATA_PAGE_UNIQUE_ID)
    if one_stocks_data_page_ref:
        if one_stocks_data_page_ref.obj.current_ticker_viewed:
            one_stocks_data_page_ref.obj.createOneStockSpreadSheet('event', current_ticker_viewed = one_stocks_data_page_ref.obj.current_ticker_viewed)
            print line_number(), one_stocks_data_page_ref.name, "has loaded a new spreadsheet"
        else:
            print line_number(), "one_stocks_data_page_ref.obj has no loaded spreadsheet"

def refresh_sale_prep_page_spreadsheet():
    # refresh sale prep page
    sale_prep_page_ref = config.GLOBAL_PAGES_DICT.get(config.SALE_PREP_PAGE_UNIQUE_ID)
    if sale_prep_page_ref:
        sale_prep_page_ref.obj.spreadSheetFill("event")
        print line_number(), sale_prep_page_ref.name, "has loaded a new spreadsheet"

def refresh_trade_page_spreadsheet():
    # refresh Trade Page spreadsheet if it exists
    trade_page_ref = config.GLOBAL_PAGES_DICT.get(config.TRADE_PAGE_UNIQUE_ID)
    if trade_page_ref:
        trade_page_ref.obj.newGridFill()
        print line_number(), trade_page_ref.name, "has loaded a new spreadsheet"

def update_all_screen_dropdowns_after_saving_a_new_screen():
    saved_screen_page_ref = config.GLOBAL_PAGES_DICT.get(config.SAVED_SCREEN_PAGE_UNIQUE_ID)
    rank_page_ref = config.GLOBAL_PAGES_DICT.get(config.RANK_PAGE_UNIQUE_ID)

    saved_screen_page_ref.obj.refreshScreens("event")
    rank_page_ref.obj.refreshScreens("event")

    # custom analysis pages are a bit more complicated
    custom_analysis_meta_page_ref = config.GLOBAL_PAGES_DICT.get(config.CUSTOM_ANALYSE_META_PAGE_UNIQUE_ID)
    custom_analysis_meta_page_index = custom_analysis_meta_page_ref.index
    possible_number_of_analysis_pages = len(config.GLOBAL_PAGES_DICT) - len(config.GLOBAL_UNIQUE_ID_LIST)
    print line_number()
    for i in range(possible_number_of_analysis_pages):
        custom_analysis_page_ref_str = str(custom_analysis_meta_page_index) + str(i + 1)
        print custom_analysis_page_ref_str
        custom_analysis_page_ref = config.GLOBAL_PAGES_DICT.get(custom_analysis_page_ref_str)
        if custom_analysis_page_ref:
            print "success"
            custom_analysis_page_ref.obj.refreshScreens("event")
####################### end: utility functions involving pages #######################################


def convert_wx_grid_data_to_html_table(wx_grid):
    #import pprint
    data_list_for_export = []

    num_cols = wx_grid.GetNumberCols()
    num_rows = wx_grid.GetNumberRows()
    if not (num_rows and num_cols):
        return
    for row in range(num_rows):
        data_list_for_export.append([])

    for row in range(num_rows):
        for col in range(num_cols):
            data = wx_grid.GetCellValue(row, col)
            if data:
                data_list_for_export[row].append(data)
            else:
                data_list_for_export[row].append("")

    #print line_number()
    #pprint.pprint(data_list_for_export)

    html_head = "<!DOCTYPE html><html><head><style>table, th, td {border: 1px solid black; border-collapse: collapse;} td {padding: 5px;}</style></head><body><table>"
    html_butt = "</table></body></html>"
    html_body = ""

    for row in data_list_for_export:
        #print line_number(), "row", row
        html_body = html_body + "<tr>"
        for col in row:
            #print line_number(), "col", str(col)
            html_body = html_body + "<td>" + str(col) + "</td>"
        html_body = html_body + "</tr>"
    html = html_head + html_body + html_butt
    #print line_number()
    #pprint.pprint(html)
    return html


############################################################################################


















