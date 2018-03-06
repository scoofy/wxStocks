import time, datetime, inspect, config, sys
from wxStocks_modules import wxStocks_db_functions as db
from wxStocks_modules import wxStocks_utilities as utils
import wx
import persistent

# Suffix key: "_yf" = yahoo finance YHOO, "_ms" = morningstar MORN, "_aa" = AAII stock investor pro, "_nq" = Nasdaq.com data NDAQ

class Stock(persistent.Persistent):
    def __init__(self, symbol, firm_name = ""):
        self.held_list = persistent.list.PersistentList()
        # held list should take certain values into account
        # account where stock is held
        # number of shares held in that account
        # redundant information seems silly,
        # could keep the shares in the account obj only.

        # Ticker Symbol Key
        #               Class "X"   Preferred   Warrents (currently ignored)
        # wxStocks      ".X"        ".PX"       Ignored
        #
        # Nasdaq        "/X"        "^X"        "/WS","/WS/"
        # Morningstar   ".X"        "PRX"       ?
        # Yahoo         "-X"        "-PX"       "-WT"
        # AAII          ".X"        " PR"       ?
        # not yet implimented
        # Bloomberg     "/X"        "/PX"       ?
        # Google        ?           "-X"        ?

        symbol = symbol.upper()
        if symbol.isalpha():
            self.symbol = symbol

            self.nasdaq_symbol = symbol
            self.aaii_symbol = symbol
            self.yahoo_symbol = symbol
            self.morningstar_symbol = symbol

            self.yql_ticker = symbol
        elif ("." in symbol) or ("^" in symbol) or ("/" in symbol) or ("-" in symbol) or (" PR" in symbol):
            if "." in symbol:
                if ".P" in symbol:
                    # preferred
                    self.symbol = symbol

                    self.nasdaq_symbol = symbol.replace(".P", "^")
                    self.yahoo_symbol = symbol.replace(".P", "-P")
                    self.morningstar_symbol = symbol.replace(".P", "PR")
                    self.aaii_symbol = symbol.replace(".P", " PR")

                    self.yql_ticker = symbol.replace(".P", "-P")
                else:
                    # CLASS.X shares:
                    self.symbol = symbol
                    self.ticker = symbol

                    self.aaii_symbol = symbol
                    self.morningstar_symbol = symbol
                    self.nasdaq_symbol = symbol.replace(".", "/")
                    self.yahoo_symbol = symbol.replace(".", "-")

                    self.yql_ticker = symbol.replace(".", "-")
            if "^" in symbol:
                # Nasdaq preferred
                self.symbol = symbol.replace("^", ".P")

                self.nasdaq_symbol = symbol
                self.yahoo_symbol = symbol.replace("^", "-P")
                self.morningstar_symbol = symbol.replace("^", "PR")
                self.aaii_symbol = symbol.replace("^", " PR")

                self.yql_ticker = symbol.replace("^", "-P")
            if "/" in symbol:
                # Warrants currently ignored but this function should be reexamined if warrents to be included in the future
                # if "/WS" in symbol:
                #   # Nasdaq Warrent
                #   if "/WS/" in symbol:
                #       # more complicated version of the same thing
                #       self.nasdaq_symbol = symbol
                #       self.yahoo_symbol = symbol.replace("/WS/","-WT")
                #       # I don't know how morningstar does warrents
                #   else:
                #       self.nasdaq_symbol = symbol
                #       self.yahoo_symbol = symbol.replace("/WS","-WT")
                #   self.aaii_symbol = None

                # If bloomberg is integrated, this will need to be changed for preferred stock
                # if "/P" in symbol:
                #   pass

                # Nasdaq class share
                self.symbol = symbol.replace("/", ".")

                self.nasdaq_symbol = symbol
                self.aaii_symbol = symbol.replace("/", ".")
                self.morningstar_symbol = symbol.replace("/", ".")
                self.yahoo_symbol = symbol.replace("/", ".")

                self.yql_ticker = symbol.replace("/", ".")
            if "-" in symbol:
                if "-P" in symbol:
                    # Yahoo preferred
                    self.symbol = symbol.replace("-P", ".P")


                    self.yahoo_symbol = symbol
                    self.nasdaq_symbol = symbol.replace("-P", "^")
                    self.aaii_symbol = symbol.replace("-P", " PR")
                    self.morningstar_symbol = symbol.replace("-P", "PR")

                    self.yql_ticker = symbol
                else:
                    # Yahoo Class
                    self.symbol = symbol.replace("-", ".")


                    self.yahoo_symbol = symbol
                    self.nasdaq_symbol = symbol.replace("-", "/")
                    self.aaii_symbol = symbol.replace("-", ".")
                    self.morningstar_symbol = symbol.replace("-", ".")

                    self.yql_ticker = symbol
            if " PR" in symbol:
                # AAII preferred
                self.symbol = symbol.replace(" PR", ".P")


                self.aaii_symbol = symbol
                self.yahoo_symbol = symbol.replace(" PR", "-P")
                self.nasdaq_symbol = symbol.replace(" PR", "^")
                self.morningstar_symbol = symbol.replace(" PR", "PR")

                self.yql_ticker = symbol.replace(" PR", "-P")

        # Finally:
        # if morningstar preferred notation "XXXPRX", i don't know how to fix that since "PRE" is a valid ticker

        elif "_" in symbol:
            self.symbol = symbol

            self.nasdaq_symbol = None
            self.aaii_symbol = symbol
            self.yahoo_symbol = None
            self.morningstar_symbol = None
            self.yql_ticker = None

        else: #something is very broken, and must be fixed immediately
            logging.error("illegal ticker symbol: {}, {}\nThe program will now close without saving, you need to add this to the wxStocks_classes exceptions list immediately.".format(symbol, firm_name))
            sys.exit()

        self.ticker = self.symbol
        self.firm_name = firm_name

        self.epoch = float(time.time())
        self.created_epoch = float(time.time())
        self.updated = datetime.datetime.now()

        # updates

        self.last_nasdaq_scrape_update = 0.0

        self.last_yql_basic_scrape_update = 0.0

        self.last_balance_sheet_update_yf = 0.0
        self.last_balance_sheet_update_ms = 0.0

        self.last_cash_flow_update_yf = 0.0
        self.last_cash_flow_update_ms = 0.0

        self.last_income_statement_update_yf = 0.0
        self.last_income_statement_update_ms = 0.0

        self.last_key_ratios_update_ms = 0.0

        self.last_aaii_update_aa = 0.0

    def testing_reset_fields(self):
        self.last_yql_basic_scrape_update = 0.0

        self.last_balance_sheet_update_yf = 0.0
        self.last_balance_sheet_update_ms = 0.0

        self.last_cash_flow_update_yf = 0.0
        self.last_cash_flow_update_ms = 0.0

        self.last_income_statement_update_yf = 0.0
        self.last_income_statement_update_ms = 0.0

        self.last_key_ratios_update_ms = 0.0

class Account(persistent.Persistent): #portfolio
    def __init__(self, id_number, name = None, cash = 0, initial_ticker_shares_tuple_list = persistent.list.PersistentList(), initial_ticker_cost_basis_dict = {}):
        self.id_number = id_number
        self.name = name
        self.available_cash = cash # there is a ticker "CASH" that already exists, ugh
        self.stock_shares_dict = {}
        if initial_ticker_shares_tuple_list:
            for a_tuple in initial_ticker_shares_tuple_list: # ["NAME", int(NumberOfShares)]
                if a_tuple[0] not in self.stock_shares_dict.keys():
                    # ticker not already in stock share dict
                    self.stock_shares_dict["{}".format(a_tuple[0].upper())] = a_tuple[1]
                else:
                    logging.error("Error: {} is redundant, probably inproperly formatted data".format(a_tuple[0]))
        self.cost_basis_dict = initial_ticker_cost_basis_dict

    def reset_account(name = None, cash = 0, new_stock_shares_tuple_list = persistent.list.PersistentList(), new_ticker_cost_basis_dict = {}):
        self.name = name
        self.availble_cash = cash
        self.stock_shares_dict = {}
        for a_tuple in new_ticker_shares_tuple_list: # ["NAME", int(NumberOfShares)]
            if a_tuple[0].upper() not in self.stock_shares_dict.keys():
                self.stock_shares_dict["{}".format(a_tuple[0].upper())] = a_tuple[1]
            else:
                logging.error("Error: duplicate stocks in new_stock_shares_tuple_list")
        self.cost_basis_dict = new_ticker_cost_basis_dict

    def update_account(self, updated_cash, updated_stock_shares_tuple_list, updated_ticker_cost_basis_dict = {}):
        self.availble_cash = updated_cash
        for a_tuple in updated_stock_shares_tuple_list: # ["NAME", int(NumberOfShares)]
            if a_tuple[0].upper() not in self.stock_shares_dict.keys():
                self.stock_shares_dict["{}".format(a_tuple[0].upper())] = a_tuple[1]
            else: # Redundent, but i'm leaving it in here in case i need to edit this later.
                self.stock_shares_dict["{}".format(a_tuple[0].upper())] = a_tuple[1]

        if updated_ticker_cost_basis_dict:
            self.update_cost_basises(updated_ticker_cost_basis_dict)

    def update_cost_basises(self, new_ticker_cost_basis_dict):
        for ticker in new_ticker_cost_basis_dict:
            self.cost_basis_dict[ticker.upper()] = new_ticker_cost_basis_dict.get(ticker.upper())

    def return_ticker_list(self):
        ticker_list = self.stock_shares_dict.keys()
        return ticker_list

    def add_stock(stock_shares_tuple):
        if stock_shares_tuple[0].upper() not in self.stock_shares_dict.keys():
            self.stock_shares_dict["{}".format(a_tuple[0].upper())] = a_tuple[1]
        else: # Redundent, but i'm leaving it in here in case i need to edit this later.
            self.stock_shares_dict["{}".format(a_tuple[0].upper())] = a_tuple[1]

class SpreadsheetCell(object):
    def __init__(self,
        row = None,
        col = None,
        text = "",
        value = None,
        col_title = None,
        row_title = None,
        background_color = None,
        text_color = None,
        font_size = None,
        bold = False,
        function = None,
        stock = None # stock being referred to by data
        , align_right = False
        , align_center = False
        ):
        self.row = row
        self.col = col
        self.text = text
        self.value = value
        self.col_title = col_title
        self.row_title = row_title
        self.background_color = background_color
        self.text_color = text_color
        self.font_size = font_size
        self.bold = bold
        self.function = function
        self.stock = stock
        self.align_right = align_right
        self.align_center = align_center # this is bad form, but VERY few values will be centered


class SpreadsheetRow(object):
    def __init__(self,
        row,
        row_title = None,
        name = None,
        cell_dict = {} # key is col
        , account = None # for sale prep, if an account is associated with a row
        ):
        self.row = row
        self.row_title = row_title
        self.name = name
        self.cell_dict = cell_dict
        self.account = account

class PageReference(object):
    def __init__(self, name, obj = None, index = None, uid = None):
        self.name = name
        self.obj = obj
        self.index = index
        self.uid = uid # unique id

class FunctionPage(object):
    def __init__(self,
        title,
        uid_config_reference,
        general_text,
        additional_text,
        save_button_text,
        reset_button_text,
        function_that_loads_text_of_user_created_functions,
        save_function,
        function_to_load_defaults,
        ):
        self.title = title
        self.uid = uid_config_reference
        self.general_text = general_text
        self.additional_text = additional_text
        self.save_button_text = save_button_text
        self.reset_button_text = reset_button_text
        self.function_that_loads_text_of_user_created_functions = function_that_loads_text_of_user_created_functions
        self.save_function = save_function
        self.function_to_load_defaults = function_to_load_defaults

class ResearchPageRowDataList(object):
    pass

class StockBuyDialog(wx.Dialog):
    def __init__(self, ticker, number_of_shares, preset_account_choice=None, error_account=None, preset_cost_basis=None, error_cost_basis=None,):
        wx.Dialog.__init__(self, None, title="Buy Stock")
        self.Bind(wx.EVT_CLOSE, self.closeWindow)  #Bind the EVT_CLOSE event to closeWindow()

        choices = []
        for key, obj in config.PORTFOLIO_OBJECTS_DICT.items():
            choices.append(obj.name)
        choice_index = None
        if preset_account_choice:
            choice_index = choices.index(preset_account_choice)
        self.ticker = ticker
        self.number_of_shares = number_of_shares
        self.text = wx.StaticText(self, -1,
                             "You are about to buy {shares} shares of {stock}, please select the portfolio".format(shares = self.number_of_shares, stock = self.ticker),
                             )
        self.error_account_message = wx.StaticText(self, -1, "")
        if error_account:
            self.error_account_message.SetLabel(str(error_account))
        self.portfolio_dropdown = wx.ComboBox(self,
                                     choices = choices,
                                     style = wx.TE_READONLY)
        if choice_index is not None: # it will often be 0
            self.portfolio_dropdown.SetSelection(choice_index)

        self.error_cost_basis_message = wx.StaticText(self, -1, "")
        if error_cost_basis:
            self.error_cost_basis_message.SetLabel(str(error_cost_basis))

        self.cost_basis_text = wx.StaticText(self, -1,
                                             "Cost basis (optional):")
        self.cost_basis = wx.TextCtrl(self, -1,
                                   "",
                                   style=wx.TE_PROCESS_ENTER
                                   )
        if preset_cost_basis:
            self.cost_basis.SetLabel(preset_cost_basis)
        self.cost_basis.SetHint("Cost Basis")



        confirm = wx.Button(self, wx.ID_OK)
        #cancel = wx.Button(self, wx.ID_CANCEL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text, 0, wx.ALL|wx.CENTER,5)
        if error_account:
            sizer.Add(self.error_account_message, 0, wx.ALL|wx.CENTER,5)
        sizer.Add(self.portfolio_dropdown, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(self.cost_basis_text, 0, wx.ALL|wx.CENTER, 5)
        if error_cost_basis:
            sizer.Add(self.error_cost_basis_message, 0, wx.ALL|wx.CENTER,5)
        sizer.Add(self.cost_basis, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(confirm, 0, wx.ALL|wx.CENTER, 5)
        #sizer.Add(cancel, 0, wx.ALL|wx.RIGHT, 0)
        self.SetSizer(sizer)

    def closeWindow(self, event):
        self.Destroy()











