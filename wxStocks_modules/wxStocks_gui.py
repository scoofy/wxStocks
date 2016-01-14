#################################################################
#   Most of the wxPython in wxStocks is located here.           #
#   Table of Contents:                                          #
#       1: Imports and line_number function                     #
#       2: Main Frame, where tab order is placed.               #
#       3: Tabs                                                 #
#       4: Grid objects                                         #
#################################################################
import wx, numpy
import config, threading, logging, sys, time, os, math, webbrowser, urllib2
import inspect
import pprint as pp

from collections import namedtuple
from wx.lib import sheet

from wxStocks_classes import Stock, Account, SpreadsheetCell, SpreadsheetRow, PageReference, FunctionPage, ResearchPageRowDataList
from wxStocks_default_functions import default_function_page_object_config as functions_config
import wxStocks_db_functions as db
import wxStocks_utilities as utils
import wxStocks_scrapers as scrape
import wxStocks_screen_functions as screen
import wxStocks_meta_functions as meta
import wxStocks_functions_that_process_user_functions as process_user_function
import AAII.wxStocks_aaii_xls_data_importer as aaii
#from AAII_functions import aaii_formulas

def line_number():
    """Returns the current line number in our program."""
    return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)




class MainFrame(wx.Frame): # reorder tab postions here
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, parent = None, id = wx.ID_ANY, title="wxStocks", pos = wx.DefaultPosition, size = (1020,800))
        self.SetSizeHints(1020,800)
        self.title = "wxStocks"
        self.uid = config.MAIN_FRAME_UNIQUE_ID

        if not "failed crypto on startup, will look at later" == 1:
            pass
            # There seems to be a major bug with osx at this point with message dialogs... cannot get code below functional.

            # Confirm encryption if module not installed
            # try:
            #   import Crypto
            #   from modules import simplecrypt
            #   print line_number(), "Remove this and the following test line."
            #   import force_error
            #   yesNoAnswer = None
            # except Exception, e:
            #   print e
            #   print line_number(), 'Change "Error" to "Crypto" before deploying.'
            #   confirm = wx.MessageDialog(self,
            #                                  "Without the pycrypto module functioning, if you import your portfolios, they will not be encrypted when saved. This will leave your data vulnurable to theft, possibly exposing your positions and net worth.",
            #                                  'You do not have pycrypto installed.',
            #                                  style = wx.YES_NO
            #                                  )
            #   confirm.SetYesNoLabels(("&Close"), ("&I Understand And Want To Continue Without Encryption"))
            #   #yesNoAnswer = confirm.ShowModal()
            #   if confirm.ShowModal() != wx.ID_YES:
            #       yesNoAnswer = wx.ID_NO
            #       print "No!"
            #   else:
            #       yesNoAnswer = wx.ID_YES
            #       print "Yes!!!"
            # if yesNoAnswer == wx.ID_YES:
            #   sys.exit()
            # else:
            #   if yesNoAnswer:
            #       confirm.Destroy()

            # Workaround
            #import wx.lib.agw.genericmessagedialog as GMD
            #main_message = "Without the pycrypto module functioning,\nif you import your portfolios,\nthey will not be encrypted when saved.\nThis will leave your data vulnurable to theft,\npossibly exposing your positions and net worth."
            #
            #
            #dlg = GMD.GenericMessageDialog(None, main_message, 'You do not have pycrypto installed.',
            #                               agwStyle=wx.ICON_INFORMATION | wx.OK)
            #
            #dlg.ShowModal()
            #dlg.Destroy()

        # Here we create a panel and a notebook on the panel
        main_frame = wx.Panel(self)
        self.notebook = wx.Notebook(main_frame)


        # create the page windows as children of the notebook
        # add the pages to the notebook with the label to show on the tab
        self.welcome_page = WelcomePage(self.notebook)
        self.notebook.AddPage(self.welcome_page, self.welcome_page.title)

        self.get_data_page = GetDataPage(self.notebook)
        self.notebook.AddPage(self.get_data_page, self.get_data_page.title)

        self.portfolio_page = PortfolioPage(self.notebook)
        self.notebook.AddPage(self.portfolio_page, self.portfolio_page.title)

        self.view_data_page = ViewDataPage(self.notebook)
        self.notebook.AddPage(self.view_data_page, self.view_data_page.title)

        self.analyse_page = AnalysisPage(self.notebook)
        self.notebook.AddPage(self.analyse_page, self.analyse_page.title)

        self.research_page = ResearchPage(self.notebook)
        self.notebook.AddPage(self.research_page, self.research_page.title)

        self.sale_prep_page = SalePrepPage(self.notebook)
        self.notebook.AddPage(self.sale_prep_page, self.sale_prep_page.title)

        self.trade_page = TradePage(self.notebook)
        self.notebook.AddPage(self.trade_page, self.trade_page.title)

        self.user_functions_page = UserFunctionsMetaPage(self.notebook)
        self.notebook.AddPage(self.user_functions_page, self.user_functions_page.title)

        # finally, put the notebook in a sizer for the panel to manage
        # the layout

        sizer = wx.BoxSizer()
        sizer.Add(self.notebook, 1, wx.EXPAND)
        main_frame.SetSizer(sizer)

        # here we add all pages to the config.GLOBAL_PAGES_DICT, adding both the index and the title as key values.
        self.set_config_GLOBAL_PAGES_DICT_key_value_pairs(self.notebook)
        config.GLOBAL_PAGES_DICT[self.uid] = self
        config.GLOBAL_PAGES_DICT["0"] = self
        config.GLOBAL_PAGES_DICT[self.title] = self

        print line_number(), "done." "\n\n", "------------------------- wxStocks startup complete -------------------------", "\n"

    def set_config_GLOBAL_PAGES_DICT_key_value_pairs(self, notebook, parent_index = None):
        for child in notebook.Children:
            # sadly, have to use ordinals which is why  + 1.
            page_index = notebook.Children.index(child) + 1.
            if parent_index:
                if len(notebook.Children) > 10:
                    denominator = 100.
                elif len(notebook.Children) > 100:
                    print line_number(), "Error: far too many tabs in", notebook
                    sys.exit()
                else:
                    denominator = 10.
                # create formatted indexes
                if float(parent_index).is_integer():
                    page_index = float(int(parent_index) + (page_index/denominator))
                else: # it already has decimals
                    page_index = float(str(parent_index) + str(page_index/denominator).replace("0.", ""))
            if float(page_index).is_integer():
                page_index = int(page_index)
            page = PageReference(child.title, index = page_index, obj = child)
            config.GLOBAL_PAGES_DICT[str(page_index)] = page
            page_index = float(page_index)
            config.GLOBAL_PAGES_DICT[child.title] = page
            try: # main page (find these in the config file)
                config.GLOBAL_PAGES_DICT[child.uid] = page
                page.uid = child.uid
            except: # user created subsection
                pass
            #config.PAGES_DICT[child.title] = child
            if child.Children:
                for grandchild in child.Children:
                    if type(grandchild) is wx._windows.Panel:
                        for great_grandchild in grandchild.Children:
                            if type(great_grandchild) is wx._controls.Notebook:
                                self.set_config_GLOBAL_PAGES_DICT_key_value_pairs(great_grandchild, parent_index = page_index)

class Tab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

# ###################### wx tabs #########################################################
class WelcomePage(Tab):
    def __init__(self, parent):
        self.title = "Welcome"
        self.uid = config.WELCOME_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)

        welcome_page_text = wx.StaticText(self, -1,
                             "Welcome to wxStocks",
                             (10,10)
                             )
        instructions_text = '''

    Instructions:   this program is essentially a work-flow following the tabs above.
    ---------------------------------------------------------------------------------------------------------------------------------

    Welcome:\t\t\t\t\t\tGeneral insturction and password reset.

    Import Data:
    \tDownload Tickers:\t\t\tThis page is where you download ticker .CSV files to create a list of tickers to scrape.
    \tScrape YQL:\t\t\t\t\tThis page takes all tickers, and then scrapes current stock data using them.
    \tImport Data Spreadsheets:\t\tThis page allows you to import your own spreadsheets. You must first create functions in it's Edit Functions tab.

    Portfolios:\t\t\t\t\t\tThis page allows you to load your portfolios from which you plan on making trades.
    \t\t\t\t\t\t\t\tIf you have more than one portfolio you plan on working from, you may add more.

    View Data:
    \tView All Stocks:\t\t\t\tThis page generates a list of all stocks that have been scraped and presents all the data about them.
    \t\t\t\t\t\t\t\t-  Use this page to double check your data to make sure it's accurate and up to date.
    \tView One Stock:\t\t\t\tThis page allows you to look at all the data associated with one stock.
    \t\t\t\t\t\t\t\t-  Here you will find the attributes you may use in programming your own functions involving individual stocks.

    Analyse Data:
    \tScreen:\t\t\t\t\t\tThis page allows you to screen for stocks that fit your criteria, and save them for later.
    \tSaved Screens:\t\t\t\tThis page allows you to recall old screens you've saved.
    \tRank:\t\t\t\t\t\tThis page allows you to rank stocks along certain criteria.
    \tCustom Analysis:\t\t\t\tThis page allows you to execute your own custom analysis.
    \t\t\t\t\t\t\t\t-  You can learn about programming and interfacing with wxStocks to do your own analysis in the Edit Functions section.

    Research:\t\t\t\t\t\tDo your homework! This page allows you to easily access data for stocks you intend to buy or sell.
    \t\t\t\t\t\t\t\tYou can add different buttons in the config page if you have other sources your prefer.

    Sale Prep:\t\t\t\t\t\tThis page allows you to estimate the amount of funds generated from a potential stock sale.

    Trade:\t\t\t\t\t\t\tThis page (currently not functional) takes the stocks you plan to sell, estimates the amount of money generated,
    \t\t\t\t\t\t\t\tand lets you estimate the volume of stocks to buy to satisfy your diversification requirements.

    Edit Functions:\t\t\t\t\tHere you many view/edit/restore user created functions. You may also edit them in your own text editor.

    '''

        instructions = wx.StaticText(self, -1,
                                    instructions_text,
                                    (10,20)
                                    )

        # encryption_text_vertical_position = 550
        # encryption_button_vertical_position = encryption_text_vertical_position - 5
        # encryption_text_horizontal_position = 10
        # encryption_button_horizontal_position = encryption_text_horizontal_position + 160

        # self.turn_encryption_off_button = wx.Button(self, label="Turn encryption off.", pos=(encryption_button_horizontal_position, encryption_button_vertical_position), size=(-1,-1))
        # self.turn_encryption_off_button.Bind(wx.EVT_BUTTON, self.toggleEncryption, self.turn_encryption_off_button)

        # self.turn_encryption_on_button = wx.Button(self, label="Turn encryption on.", pos=(encryption_button_horizontal_position, encryption_button_vertical_position), size=(-1,-1))
        # self.turn_encryption_on_button.Bind(wx.EVT_BUTTON, self.toggleEncryption, self.turn_encryption_on_button)



        # self.encryption_message_default = "Encryption is turned "

        # if config.ENCRYPTION_POSSIBLE:
        #   self.encryption_status = "ON:"
        #   try:
        #       import Crypto
        #       from modules.simplecrypt import encrypt, decrypt
        #   except:
        #       print line_number(), "Encryption not possible"
        #       self.encryption_message_default = "Encryption is not possible. You should make sure pyCrypto and simplecrypt are installed to use encryption for your personal data."
        #       self.encryption_status = ""
        #       self.turn_encryption_off_button.Hide()
        #   self.turn_encryption_on_button.Hide()
        # else:
        #   self.encryption_status = "OFF:"
        #   try:
        #       import Crypto
        #       from modules.simplecrypt import encrypt, decrypt
        #   except:
        #       print line_number(), "Encryption not possible"
        #       self.encryption_message_default = "Encryption is not possible. You should make sure pyCrypto and simplecrypt are installed to use encryption for your personal data."
        #       self.encryption_status = ""
        #       self.turn_encryption_on_button.Hide()
        #   self.turn_encryption_off_button.Hide()


        # self.encryption_message = wx.StaticText(self, -1,
        #                           self.encryption_message_default + self.encryption_status,
        #                           (encryption_text_horizontal_position, encryption_text_vertical_position)
        #                           )

        self.reset_password_button = None
        self.reset_password_button_horizontal_position = 5
        self.reset_password_button_vertical_position = 700

        if config.ENCRYPTION_POSSIBLE:
            self.reset_password_button = wx.Button(self, label="Reset Password", pos=(self.reset_password_button_horizontal_position, self.reset_password_button_vertical_position), size=(-1,-1))
            self.reset_password_button.Bind(wx.EVT_BUTTON, self.resetPasswordPrep, self.reset_password_button)

        text_field_offset = 180
        text_field_vertical_offset = -3
        current_password_text = "Current Password:"
        self.current_password_static_text = wx.StaticText(self, -1, current_password_text,
                                    (self.reset_password_button_horizontal_position,
                                     self.reset_password_button_vertical_position + 30))
        self.current_password_field = wx.TextCtrl(self, -1, "",
                                       (self.reset_password_button_horizontal_position + text_field_offset,
                                        self.reset_password_button_vertical_position + text_field_vertical_offset + 30),
                                       style=wx.TE_PASSWORD ) #| wx.TE_PROCESS_ENTER)

        new_password_text = "New Password:"
        self.new_password_static_text = wx.StaticText(self, -1, new_password_text,
                                    (self.reset_password_button_horizontal_position,
                                     self.reset_password_button_vertical_position + 60))
        self.new_password_field = wx.TextCtrl(self, -1, "",
                                   (self.reset_password_button_horizontal_position + text_field_offset,
                                    self.reset_password_button_vertical_position + text_field_vertical_offset + 60),
                                   style=wx.TE_PASSWORD ) #| wx.TE_PROCESS_ENTER)

        confirm_password_text = "Confirm New Password:"
        self.confirm_password_static_text = wx.StaticText(self, -1, confirm_password_text,
                                    (self.reset_password_button_horizontal_position,
                                     self.reset_password_button_vertical_position + 90))
        self.confirm_new_password_field = wx.TextCtrl(self, -1, "",
                                           (self.reset_password_button_horizontal_position + text_field_offset,
                                            self.reset_password_button_vertical_position + text_field_vertical_offset + 90),
                                           style=wx.TE_PASSWORD ) #| wx.TE_PROCESS_ENTER)


        encryption_hardness_text = "Optional:\nEncryption Strength (1-24):"
        optional_offset = 18
        self.encryption_hardness_static_text = wx.StaticText(self, -1, encryption_hardness_text,
                                    (self.reset_password_button_horizontal_position,
                                     self.reset_password_button_vertical_position + 120))
        self.encryption_hardness_field = wx.TextCtrl(self, -1, "",
                                           (self.reset_password_button_horizontal_position + text_field_offset,
                                            self.reset_password_button_vertical_position + text_field_vertical_offset + 120 + optional_offset),
                                           ) #style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.encryption_hardness_field.SetHint("default = 8")


        self.current_password_static_text.Hide()
        self.current_password_field.Hide()
        self.new_password_static_text.Hide()
        self.new_password_field.Hide()
        self.confirm_password_static_text.Hide()
        self.confirm_new_password_field.Hide()
        self.encryption_hardness_static_text.Hide()
        self.encryption_hardness_field.Hide()

        self.reset_password_submit_button = wx.Button(self, label="Submit", pos=(self.reset_password_button_horizontal_position + text_field_offset + 10, self.reset_password_button_vertical_position), size=(-1,-1))
        self.reset_password_submit_button.Bind(wx.EVT_BUTTON, self.resetPassword, self.reset_password_submit_button)
        self.reset_password_submit_button.Hide()

        self.password_reset_status_static_text = wx.StaticText(self, -1, "",
                                    (self.reset_password_button_horizontal_position,
                                     self.reset_password_button_vertical_position - 30))


        self.delete_all_stock_data_horizontal_position = 835
        self.delete_all_stock_data_vertical_position = 700
        self.delete_all_stock_data = wx.Button(self, label="Delete All Stock Data", pos=(self.delete_all_stock_data_horizontal_position, self.delete_all_stock_data_vertical_position), size=(-1,-1))
        self.delete_all_stock_data.Bind(wx.EVT_BUTTON, self.deleteAllStockData, self.delete_all_stock_data)

        #self.function_to_test = utils.OnSaveAs
        #self.test_function_button = wx.Button(self, label="Execute", pos=(10, 10), size=(-1,-1))
        #self.test_function_button.Bind(wx.EVT_BUTTON, self.OnSaveAs, self.test_function_button)


        print line_number(), "WelcomePage loaded"

    def testFunction(self, event):
        try:
            self.function_to_test()
        except Exception as e:
            print line_number(), e

    def resetPasswordPrep(self, event):
        self.reset_password_button.Hide()

        self.current_password_field.Clear()
        self.new_password_field.Clear()
        self.confirm_new_password_field.Clear()
        self.encryption_hardness_field.Clear()

        self.current_password_static_text.Show()
        self.current_password_field.Show()
        self.new_password_static_text.Show()
        self.new_password_field.Show()
        self.confirm_password_static_text.Show()
        self.confirm_new_password_field.Show()
        self.encryption_hardness_static_text.Show()
        self.encryption_hardness_field.Show()

        self.reset_password_submit_button.Show()

    def resetPassword(self, event):
        old_password = self.current_password_field.GetValue()
        new_password = self.new_password_field.GetValue()
        confirm_password = self.confirm_new_password_field.GetValue()
        encryption_strength = self.encryption_hardness_field.GetValue()
        if encryption_strength:
            try:
                encryption_strength = int(encryption_strength)
            except:
                self.password_reset_status_static_text.SetLabel("Encryption strength must be an integer or blank.")
                self.current_password_field.Clear()
                self.new_password_field.Clear()
                self.confirm_new_password_field.Clear()
                self.encryption_hardness_field.Clear()
                return

        saved_hash = db.is_saved_password_hash()

        if new_password != confirm_password:
            self.password_reset_status_static_text.SetLabel("Your confirmation did not match your new password.")
            self.current_password_field.Clear()
            self.new_password_field.Clear()
            self.confirm_new_password_field.Clear()
            self.encryption_hardness_field.Clear()
            return

        if not db.valid_pw(old_password, saved_hash):
            self.password_reset_status_static_text.SetLabel("The password you submitted is incorrect.")
            self.current_password_field.Clear()
            self.new_password_field.Clear()
            self.confirm_new_password_field.Clear()
            self.encryption_hardness_field.Clear()
            return

        # Success!
        # reset password and all relevant files
        db.reset_all_encrypted_files_with_new_password(old_password, new_password, encryption_strength)
        self.password_reset_status_static_text.SetLabel("You have successfully change your password.")
        self.closePasswordResetFields()


    def closePasswordResetFields(self):
        self.reset_password_submit_button.Hide()

        self.current_password_field.Clear()
        self.new_password_field.Clear()
        self.confirm_new_password_field.Clear()
        self.encryption_hardness_field.Clear()

        self.current_password_static_text.Hide()
        self.current_password_field.Hide()
        self.new_password_static_text.Hide()
        self.new_password_field.Hide()
        self.confirm_password_static_text.Hide()
        self.confirm_new_password_field.Hide()
        self.encryption_hardness_static_text.Hide()
        self.encryption_hardness_field.Hide()

        self.reset_password_button.Show()

    def deleteAllStockData(self, event):
        confirm = wx.MessageDialog(None,
                                 "Caution! You are about to delete all saved stock data. Your portfolio and screen data will remain, but all stock data will be deleted. To avoid errors, the program will then update basic stock data, and shut down.",
                                 'Delete All Stock Data?',
                                 style = wx.YES_NO
                                 )
        confirm.SetYesNoLabels(("&Cancel"), ("&Yes, Delete All Stock Data and Restart"))
        yesNoAnswer = confirm.ShowModal()
        confirm.Destroy()
        if yesNoAnswer == wx.ID_NO:
            self.deleteAllStockDataConfirm()

    def deleteAllStockDataConfirm(self):
        config.GLOBAL_TICKER_LIST = []
        db.save_GLOBAL_TICKER_LIST()

        config.GLOBAL_STOCK_DICT = {}
        config.GLOBAL_ATTRIBUTE_SET = set([])
        db.save_GLOBAL_STOCK_DICT()

        print line_number(), "Data deleted."

        ticker_page = config.GLOBAL_PAGES_DICT.get(config.TICKER_PAGE_UNIQUE_ID).obj
        ticker_page.downloadTickers()

        sys.exit()

    ######################### below is not used ###########################
    # def toggleEncryption(self, event):
    #   if config.ENCRYPTION_POSSIBLE:
    #       remove = self.checkRemoveEncryption()
    #       if not remove:
    #           return
    #   config.ENCRYPTION_POSSIBLE = not config.ENCRYPTION_POSSIBLE
    #   if config.ENCRYPTION_POSSIBLE:
    #       self.turn_encryption_on_button.Hide()
    #       self.turn_encryption_off_button.Show()
    #       self.encryption_status = "ON:"
    #   else:
    #       self.turn_encryption_off_button.Hide()
    #       self.turn_encryption_on_button.Show()
    #       self.encryption_status = "OFF:"
    #   print line_number(), "Encryption has been turned %s." % self.encryption_status
    #   self.encryption_message.SetLabel(self.encryption_message_default + self.encryption_status)


    # def checkRemoveEncryption(self):
    #   confirm = wx.MessageDialog(None,
    #                              "Are you sure you want to remove automatic encryption?",
    #                              'Remove Encryption?',
    #                              style = wx.YES_NO
    #                              )
    #   confirm.SetYesNoLabels(("&Yes, Remove Encryption"), ("&Cancel"))
    #   yesNoAnswer = confirm.ShowModal()
    #   confirm.Destroy()
    #   return yesNoAnswer == wx.ID_YES
    ######################### above is not used ###########################

##
class GetDataPage(Tab):
    def __init__(self, parent):
        self.title = "Import Data"
        self.uid = config.GET_DATA_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)
        ####
        self.get_data_page_panel = wx.Panel(self, -1, pos=(0,5), size=( wx.EXPAND, wx.EXPAND))
        self.get_data_notebook = wx.Notebook(self.get_data_page_panel)

        self.ticker_page = TickerPage(self.get_data_notebook)
        self.get_data_notebook.AddPage(self.ticker_page, self.ticker_page.title)

        self.yql_scrape_page = YqlScrapePage(self.get_data_notebook)
        self.get_data_notebook.AddPage(self.yql_scrape_page, self.yql_scrape_page.title)

        self.spreadsheet_import_page = SpreadsheetImportPage(self.get_data_notebook)
        self.get_data_notebook.AddPage(self.spreadsheet_import_page, self.spreadsheet_import_page.title)

        sizer2 = wx.BoxSizer()
        sizer2.Add(self.get_data_notebook, 1, wx.EXPAND)
        self.SetSizer(sizer2)
        ####

class TickerPage(Tab):
    def __init__(self, parent):
        self.title = "Download Ticker Data"
        self.uid = config.TICKER_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddSpacer(88) # vertical offset
        self.SetSizer(self.sizer)

        text = wx.StaticText(self, -1,
                             "Welcome to the ticker page.",
                             (10,10)
                             )
        download_button = wx.Button(self, label="Download Tickers", pos=(5, 30), size=(-1,-1))
        download_button.Bind(wx.EVT_BUTTON, self.confirmDownloadTickers, download_button)

        refresh_button = wx.Button(self, label="Refresh", pos=(5, 60), size=(-1,-1))
        refresh_button.Bind(wx.EVT_BUTTON, self.refreshTickers, refresh_button)


        exchanges = ""
        for exchange_name in config.STOCK_EXCHANGE_LIST:
            if exchange_name is config.STOCK_EXCHANGE_LIST[0]:
                exchanges = exchange_name.upper()
            elif exchange_name is config.STOCK_EXCHANGE_LIST[-1]:
                if len(config.STOCK_EXCHANGE_LIST) == 2:
                    exchanges = exchanges + " and " + exchange_name.upper()
                else:
                    exchanges = exchanges + ", and " + exchange_name.upper()
            else:
                exchanges = exchanges + ", " + exchange_name.upper()

        more_text = wx.StaticText(self, -1,
                             "Currently downloads tickers from %s. To add or remove exchanges, edit the config file." % exchanges,
                             (145,36)
                             )

        self.showAllTickers()
        print line_number(), "TickerPage loaded"

    def confirmDownloadTickers(self, event):
        confirm = wx.MessageDialog(None,
                                   "You are about to make a request from Nasdaq.com. If you do this too often they may temporarily block your IP address.",
                                   'Confirm Download',
                                   style = wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Download"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        #try:
        #   confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
        #except AttributeError:
        #   pass
        confirm.Destroy()
        self.file_display.Hide()

        if yesNoAnswer == wx.ID_YES:
            download_tickers = threading.Thread(name="download tickers", target=self.downloadTickers)
            download_tickers.start()

    def downloadTickers(self):
        print line_number(), "Begin ticker download..."
        ticker_list_without_prices = scrape.nasdaq_full_ticker_list_downloader()
        uppercase_exchange_list = [x.upper() for x in config.STOCK_EXCHANGE_LIST]
        for data in ticker_list_without_prices:
            #print data
            # The following line does:
            # data[2] is exchange
            if data[2].upper() in uppercase_exchange_list:
                stock = db.create_new_Stock_if_it_doesnt_exist(data[0])
                stock.firm_name = data[1]
                stock.Exchange_na = data[2]
                stock.etf_na = data[3]

        print line_number(), "Begin price data download..."
        ticker_data = scrape.convert_nasdaq_csv_to_stock_objects()
        db.save_GLOBAL_STOCK_DICT()

        self.showAllTickers()
        # Update scrape page
        scrape_page = config.GLOBAL_PAGES_DICT.get(config.YQL_SCRAPE_PAGE_UNIQUE_ID).obj
        scrape_page.calculate_scrape_times()
        # Update view all stocks
        view_all_stocks_page = config.GLOBAL_PAGES_DICT.get(config.ALL_STOCKS_PAGE_UNIQUE_ID).obj
        view_all_stocks_page.spreadSheetFillAllStocks("event")

    # no longer used
    def saveTickerDataAsStocks(self, ticker_data_from_download):
        # first check for stocks that have fallen off the stock exchanges
        ticker_list = []
        dead_tickers = []

        # create a list of tickers
        for ticker_data_sublist in ticker_data_from_download:
            print line_number(), ticker_data_sublist[0] + ":", ticker_data_sublist[1]

            ticker_symbol_upper = utils.strip_string_whitespace(ticker_data_sublist[0]).upper()
            ticker_list.append(ticker_symbol_upper)

        # check all stocks against that list
        for ticker in config.GLOBAL_STOCK_DICT:
            if ticker in ticker_list:
                if config.GLOBAL_STOCK_DICT[ticker].ticker_relevant == False:
                    config.GLOBAL_STOCK_DICT[ticker].ticker_relevant = True
                print line_number(), ticker, "appears to be fine"
            else:
                # ticker may have been removed from exchange
                print line_number(), ticker + " appears to be dead"
                dead_tickers.append(ticker)

        # check for errors, and if not, mark stocks as no longer on exchanges:
        if len(dead_tickers) > config.NUMBER_OF_DEAD_TICKERS_THAT_SIGNALS_AN_ERROR:
            logging.error("Something went wrong with ticker download, probably a dead link")
        else:
            for dead_ticker_symbol in dead_tickers:
                print line_number(), dead_ticker_symbol
                dead_stock = utils.return_stock_by_symbol(dead_ticker_symbol)
                dead_stock.ticker_relevant = False

        # save stocks if new
        for ticker_data_sublist in ticker_data_from_download:
            ticker_symbol = utils.strip_string_whitespace(ticker_data_sublist[0])
            firm_name = ticker_data_sublist[1]

            if "$" in ticker_symbol:
                print line_number(), 'Ticker %s with "$" symbol found, not sure if ligitimate, so not saving it.' % ticker_symbol
                continue

            stock = db.create_new_Stock_if_it_doesnt_exist(ticker_symbol)
            stock.firm_name = firm_name
            print line_number(), "Saving:", stock.ticker, stock.firm_name
        db.save_GLOBAL_STOCK_DICT()
    # end no longer used

    def refreshTickers(self, event):
        self.showAllTickers()

    def showAllTickers(self):
        print line_number(), "Loading Tickers"
        ticker_list = []
        for ticker in config.GLOBAL_STOCK_DICT:
            if config.GLOBAL_STOCK_DICT[ticker].ticker_relevant:
                ticker_list.append(ticker)
        ticker_list.sort()
        self.displayTickers(ticker_list)
        self.sizer.Add(self.file_display, 1, wx.ALL|wx.EXPAND)
        self.file_display.Show()
        print line_number(), "Done"

    def displayTickers(self, ticker_list):
        ticker_list.sort()
        ticker_list_massive_str = ""
        for ticker in ticker_list:
            ticker_list_massive_str += ticker
            ticker_list_massive_str += ", "

        height_offset = 90
        size = (765, 625)
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            size = ( width - (config.HORIZONTAL_OFFSET_PER_TAB * 2) , height - height_offset - (config.VERTICAL_OFFSET_PER_TAB * 2)) # find the difference between the Frame and the grid size
        except:
            pass

        #print line_number()
        #pp.pprint(config.GLOBAL_STOCK_DICT)
        try:
            self.file_display.Destroy()
        except:
            pass
        self.file_display = wx.TextCtrl(self, -1,
                                    ticker_list_massive_str,
                                    (2, height_offset),
                                    size = size,
                                    style = wx.TE_READONLY | wx.TE_MULTILINE ,
                                    )
class YqlScrapePage(Tab):
    def __init__(self, parent):
        self.title = "Scrape YQL"
        self.uid = config.YQL_SCRAPE_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)
        text = wx.StaticText(self, -1,
                             "Welcome to the scrape page",
                             (10,10)
                             )
        self.scrape_button = wx.Button(self, label="Scrape YQL", pos=(5,100), size=(-1,-1))
        self.scrape_button.Bind(wx.EVT_BUTTON, self.confirmScrape, self.scrape_button)

        self.abort_scrape_button = wx.Button(self, label="Cancel Scrape", pos=(5,100), size=(-1,-1))
        self.abort_scrape_button.Bind(wx.EVT_BUTTON, self.abortScrape, self.abort_scrape_button)
        self.abort_scrape_button.Hide()
        self.abort_scrape = False

        self.progress_bar = wx.Gauge(self, -1, 100, size=(995, -1), pos = (0, 200))
        self.progress_bar.Hide()

        self.numScrapedStocks = 0
        self.number_of_tickers_to_scrape = 0
        self.total_relevant_tickers = 0
        self.tickers_to_scrape = 0
        self.scrape_time_text = 0
        self.number_of_unscraped_stocks = 0


        self.total_relevant_tickers = wx.StaticText(self, -1,
                             label = "Total number of tickers = %d" % (self.numScrapedStocks + self.number_of_tickers_to_scrape),
                             pos = (10,30)
                             )
        self.tickers_to_scrape = wx.StaticText(self, -1,
                             label = "Tickers that need to be scraped = %d" % self.number_of_tickers_to_scrape,
                             pos = (10,50)
                             )
        sleep_time = config.SCRAPE_SLEEP_TIME
        scrape_time_secs = (self.number_of_tickers_to_scrape/config.SCRAPE_CHUNK_LENGTH) * sleep_time * 2
        scrape_time = utils.time_from_epoch(scrape_time_secs)
        self.scrape_time_text = wx.StaticText(self, -1,
                     label = "Time = %s" % scrape_time,
                     pos = (10,70)
                     )


        self.calculate_scrape_times()

        print line_number(), "YqlScrapePage loaded"

    def calculate_scrape_times(self):
        print line_number(), "Calculating scrape times..."
        sleep_time = config.SCRAPE_SLEEP_TIME

        # calculate number of stocks and stuff to scrape
        self.numScrapedStocks = 0
        self.number_of_tickers_to_scrape = 0
        for stock in config.GLOBAL_STOCK_DICT:
            if config.GLOBAL_STOCK_DICT[stock].ticker_relevant:
                self.number_of_tickers_to_scrape += 1
                current_time = float(time.time())
                time_since_update = current_time - config.GLOBAL_STOCK_DICT[stock].last_yql_basic_scrape_update
                if (int(time_since_update) < int(config.TIME_ALLOWED_FOR_BEFORE_RECENT_UPDATE_IS_STALE) ):
                    self.numScrapedStocks += 1

        self.number_of_unscraped_stocks = self.number_of_tickers_to_scrape - self.numScrapedStocks
        total_ticker_len = len(config.GLOBAL_STOCK_DICT)
        scrape_time_secs = (self.number_of_unscraped_stocks/config.SCRAPE_CHUNK_LENGTH) * sleep_time * 2
        scrape_time = utils.time_from_epoch(scrape_time_secs)

        self.total_relevant_tickers.SetLabel("Total number of tickers = %d" % self.number_of_tickers_to_scrape)

        self.tickers_to_scrape.SetLabel("Tickers that need to be scraped = %d" % self.number_of_unscraped_stocks)

        self.scrape_time_text.SetLabel("Time = %s" % scrape_time)

        print line_number(), "Calculation done"

    def confirmScrape(self, event):
        confirm = wx.MessageDialog(None,
                                   "You are about to scrape of Yahoo's YQL database. If you do this too often Yahoo may temporarily block your IP address.",
                                   'Scrape stock data?',
                                   style = wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        #try:
        #   confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
        #except AttributeError:
        #   pass
        confirm.Destroy()

        if yesNoAnswer == wx.ID_YES:
            self.scrapeYQL()

    def scrapeYQL(self):
        chunk_list_and_percent_of_full_scrape_done_and_number_of_tickers_to_scrape = scrape.prepareYqlScrape()

        chunk_list = chunk_list_and_percent_of_full_scrape_done_and_number_of_tickers_to_scrape[0]
        percent_of_full_scrape_done = chunk_list_and_percent_of_full_scrape_done_and_number_of_tickers_to_scrape[1]
        self.number_of_tickers_to_scrape = chunk_list_and_percent_of_full_scrape_done_and_number_of_tickers_to_scrape[2]


        self.progress_bar.SetValue(percent_of_full_scrape_done)
        self.progress_bar.Show()
        self.scrape_button.Hide()
        self.abort_scrape_button.Show()

        # Process the scrape while updating a progress bar
        timer = threading.Timer(0, self.executeScrapePartOne, [chunk_list, 0])
        timer.start()

        #scrape_thread = threading.Thread(target=self.executeOneScrape, args = (ticker_chunk,))
        #scrape_thread.daemon = True
        #scrape_thread.start()
        #while scrape_thread.isAlive():

        #   # Every two sleep times execute a new scrape
        #   full_scrape_sleep = float(sleep_time * 2)
        #   scrape_thread.join(full_scrape_sleep)
        #   cont, skip = progress_dialog.Update(self.numScrapedStocks)
        #   if not cont:
        #       progress_dialog.Destroy()
        #       return

    def executeScrapePartOne(self, ticker_chunk_list, position_of_this_chunk):
        if self.abort_scrape == True:
            self.abort_scrape = False
            self.progress_bar.Hide()
            print line_number(), "Scrape canceled."
            return

        data = scrape.executeYqlScrapePartOne(ticker_chunk_list, position_of_this_chunk)

        sleep_time = config.SCRAPE_SLEEP_TIME
        timer = threading.Timer(sleep_time, self.executeScrapePartTwo, [ticker_chunk_list, position_of_this_chunk, data])
        timer.start()



    def executeScrapePartTwo(self, ticker_chunk_list, position_of_this_chunk, successful_pyql_data):
        if self.abort_scrape == True:
            self.abort_scrape = False
            self.progress_bar.Hide()
            print line_number(), "Scrape canceled."
            return

        scrape.executeYqlScrapePartTwo(ticker_chunk_list, position_of_this_chunk, successful_pyql_data)

        sleep_time = config.SCRAPE_SLEEP_TIME
        logging.warning("Sleeping for %d seconds before the next task" % sleep_time)
        #time.sleep(sleep_time)

        #self.numScrapedStocks += number_of_stocks_in_this_scrape
        #cont, skip = self.progress_dialog.Update(self.numScrapedStocks)
        #if not cont:
        #   self.progress_dialog.Destroy()
        #   return


        number_of_tickers_in_chunk_list = 0
        for chunk in ticker_chunk_list:
            for ticker in chunk:
                number_of_tickers_in_chunk_list += 1
        number_of_tickers_previously_updated = self.number_of_tickers_to_scrape - number_of_tickers_in_chunk_list
        number_of_tickers_done_in_this_scrape = 0
        for i in range(len(ticker_chunk_list)):
            if i > position_of_this_chunk:
                continue
            for ticker in ticker_chunk_list[i]:
                number_of_tickers_done_in_this_scrape += 1
        total_number_of_tickers_done = number_of_tickers_previously_updated + number_of_tickers_done_in_this_scrape
        percent_of_full_scrape_done = round( 100 * float(total_number_of_tickers_done) / float(self.number_of_tickers_to_scrape))

        position_of_this_chunk += 1
        percent_done = round( 100 * float(position_of_this_chunk) / float(len(ticker_chunk_list)) )
        print line_number(), "%d%%" % percent_done, "done this scrape execution."
        print line_number(), "%d%%" % percent_of_full_scrape_done, "done of all tickers."
        self.progress_bar.SetValue(percent_of_full_scrape_done)
        self.calculate_scrape_times()
        if position_of_this_chunk >= len(ticker_chunk_list):
            # finished
            self.abort_scrape_button.Hide()
            self.scrape_button.Show()
            self.progress_bar.SetValue(100)
            return
        else:
            print line_number(), "ready to loop again"
            timer = threading.Timer(sleep_time, self.executeScrapePartOne, [ticker_chunk_list, position_of_this_chunk])
            timer.start()

    def abortScrape(self, event):
        print line_number(), "Canceling scrape... this may take up to %d seconds." % config.SCRAPE_SLEEP_TIME
        if self.abort_scrape == False:
            self.abort_scrape = True
            self.abort_scrape_button.Hide()
            self.scrape_button.Show()
            self.calculate_scrape_times()

class SpreadsheetImportPage(Tab):
    def __init__(self, parent):
        self.title = "Import Data Spreadsheets"
        self.uid = config.SPREADSHEET_IMPORT_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)
        ####
        spreadsheet_page_panel = wx.Panel(self, -1, pos=(0,5), size=( wx.EXPAND, wx.EXPAND))
        spreadsheet_notebook = wx.Notebook(spreadsheet_page_panel)

        self.xls_import_page = XlsImportPage(spreadsheet_notebook)
        spreadsheet_notebook.AddPage(self.xls_import_page, self.xls_import_page.title)

        self.csv_import_page = CsvImportPage(spreadsheet_notebook)
        spreadsheet_notebook.AddPage(self.csv_import_page, self.csv_import_page.title)

        sizer2 = wx.BoxSizer()
        sizer2.Add(spreadsheet_notebook, 1, wx.EXPAND)
        self.SetSizer(sizer2)
        ####
class CsvImportPage(Tab):
    def __init__(self, parent):
        self.title = "Import .CSV Data"
        self.uid = config.CSV_IMPORT_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)
        text = wx.StaticText(self, -1,
                             "Welcome to the CSV data import page page.\nYou can make your own import functions under the function tab.",
                             (10,10)
                             )

        default_button_horizontal_position = 0
        default_button_vertical_position = 50
        default_dropdown_horizontal_offset = 100
        default_dropdown_vertical_offset = 0

        import_button = wx.Button(self, label="import .csv", pos=(default_button_horizontal_position, default_button_vertical_position), size=(-1,-1))
        import_button.Bind(wx.EVT_BUTTON, self.importCSV, import_button)

        self.csv_import_name_list = meta.return_csv_import_function_short_names()
        self.drop_down = wx.ComboBox(self, pos=(default_button_horizontal_position + default_dropdown_horizontal_offset, default_button_vertical_position + default_dropdown_vertical_offset), choices=self.csv_import_name_list)

        self.triple_list = meta.return_csv_import_function_triple()

        self.csv_import_name = None

    def importCSV(self, event):
        self.csv_import_name = self.drop_down.GetValue()

        # Identify the function mapped to screen name
        for triple in self.triple_list:
            if self.csv_import_name == triple.doc:
                csv_import_function = triple.function
            # in case doc string is too many characters...
            elif self.csv_import_name == triple.name:
                csv_import_function = triple.function

        if not csv_import_function:
            print line_number(), "Error, somthing went wrong locating the correct import function to use."

        # run ranking funtion on all stocks

        success = process_user_function.import_csv_via_user_created_function(self, csv_import_function)

        if not success:
            return

        if success == "fail":
            title_string = "Error"
            success_string = "This import has failed, please check make sure your function conforms to the import protocols."
            message_style = wx.ICON_ERROR
        elif success == "some":
            title_string = "Some Errors"
            success_string = "There were some errors with your import, please review your CSV file and make sure that your functions conform to the protocols, and that the ticker symbols in your csv files are the same format as wxStocks'."
            message_style = wx.ICON_EXCLAMATION
        elif success == "success":
            title_string = "Success"
            success_string = "Success! You're file has been successfully imported."
            message_style = wx.OK
        else:
            print line_number(), "Error in importCSV title and success strings"
            return

        print line_number(), "importCSV done"


        confirm = wx.MessageDialog(None,
                                   success_string,
                                   title_string,
                                   style = message_style
                                   )
        confirm.ShowModal()
class XlsImportPage(Tab):
    def __init__(self, parent):
        self.title = "Import .XLS Data"
        self.uid = config.XLS_IMPORT_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)
        text = wx.StaticText(self, -1,
                             "Welcome to the XLS data import page page.\nYou can make your own import functions under the function tab.",
                             (10,10)
                             )

        default_button_horizontal_position = 0
        default_button_vertical_position = 50
        default_dropdown_horizontal_offset = 100
        default_dropdown_vertical_offset = 0
        aaii_offset = 28 # if aaii files in aaii import folder, this button will appear below the import dropdown

        import_button = wx.Button(self, label="import .xls", pos=(default_button_horizontal_position, default_button_vertical_position), size=(-1,-1))
        import_button.Bind(wx.EVT_BUTTON, self.importXLS, import_button)

        import_all_aaii_files_button = wx.Button(self, label="import aaii files from folder", pos=(default_button_horizontal_position, default_button_vertical_position + aaii_offset), size=(-1,-1))
        import_all_aaii_files_button.Bind(wx.EVT_BUTTON, self.import_AAII_files, import_all_aaii_files_button)

        self.xls_import_name_list = meta.return_xls_import_function_short_names()
        self.drop_down = wx.ComboBox(self, pos=(default_button_horizontal_position + default_dropdown_horizontal_offset, default_button_vertical_position + default_dropdown_vertical_offset), choices=self.xls_import_name_list)

        self.triple_list = meta.return_xls_import_function_triple()

        self.xls_import_name = None

    def importXLS(self, event):
        self.xls_import_name = self.drop_down.GetValue()

        # Identify the function mapped to screen name
        for triple in self.triple_list:
            if self.xls_import_name == triple.doc:
                xls_import_function = triple.function
            # in case doc string is too many characters...
            elif self.xls_import_name == triple.name:
                xls_import_function = triple.function

        if not xls_import_function:
            print line_number(), "Error, somthing went wrong locating the correct import function to use."

        # run ranking funtion on all stocks

        success = process_user_function.import_xls_via_user_created_function(self, xls_import_function)

        if not success:
            return

        if success == "fail":
            title_string = "Error"
            success_string = "This import has failed, please check make sure your function conforms to the import protocols."
            message_style = wx.ICON_ERROR
        elif success == "some":
            title_string = "Some Errors"
            success_string = "There were some errors with your import, please review your XLS file and make sure that your functions conform to the protocols, and that the ticker symbols in your xls files are the same format as wxStocks'."
            message_style = wx.ICON_EXCLAMATION
        elif success == "success":
            title_string = "Success"
            success_string = "Success! You're file has been successfully imported."
            message_style = wx.OK
        else:
            print line_number(), "Error in importXLS title and success strings"
            return

        print line_number(), "importXLS done"


        confirm = wx.MessageDialog(None,
                                   success_string,
                                   title_string,
                                   style = message_style
                                   )
        confirm.ShowModal()

    def import_AAII_files(self, event):
        print line_number(), "Remove argument below this line after debugging"
        path = None
        aaii_data_folder_dialogue = wx.DirDialog(self, "Choose a directory:")
        if aaii_data_folder_dialogue.ShowModal() == wx.ID_OK:
            path = aaii_data_folder_dialogue.GetPath()
            print line_number(), path
        aaii_data_folder_dialogue.Destroy()
        if path:
            aaii.import_aaii_files_from_data_folder(path=path, time_until_data_needs_update = 100000000000)
##
class PortfolioPage(Tab):
    def __init__(self, parent):
        self.title = "Portfolios"
        self.uid = config.PORTFOLIO_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)
        ####
        portfolio_page_panel = wx.Panel(self, -1, pos=(0,5), size=( wx.EXPAND, wx.EXPAND))
        portfolio_account_notebook = wx.Notebook(portfolio_page_panel)

        #print line_number(), "DATA_ABOUT_PORTFOLIOS:", config.DATA_ABOUT_PORTFOLIOS
        portfolios_that_already_exist = config.DATA_ABOUT_PORTFOLIOS[1]

        default_portfolio_names = ["Primary", "Secondary", "Tertiary"]
        if not portfolios_that_already_exist:
            config.NUMBER_OF_PORTFOLIOS = config.NUMBER_OF_DEFAULT_PORTFOLIOS
            new_portfolio_name_list = []
            for i in range(config.NUMBER_OF_PORTFOLIOS):
                print line_number(), i
                portfolio_name = None
                if config.NUMBER_OF_PORTFOLIOS < 10:
                    portfolio_name = "Portfolio %d" % (i+1)
                else:
                    portfolio_name = "%dth" % (i+1)
                if i in range(len(default_portfolio_names)):
                    portfolio_name = default_portfolio_names[i]
                portfolio_account = PortfolioAccountTab(portfolio_account_notebook, (i+1), portfolio_name)
                portfolio_account.title = portfolio_name
                portfolio_account_notebook.AddPage(portfolio_account, portfolio_name)

                new_portfolio_name_list.append(portfolio_name)

                config.DATA_ABOUT_PORTFOLIOS[0] = config.NUMBER_OF_PORTFOLIOS
                config.DATA_ABOUT_PORTFOLIOS[1] = new_portfolio_name_list
                print line_number(), config.DATA_ABOUT_PORTFOLIOS
            db.save_DATA_ABOUT_PORTFOLIOS()
        else:
            need_to_save = False
            for i in range(config.NUMBER_OF_PORTFOLIOS):
                #print line_number(), i
                try:
                    portfolio_name = portfolios_that_already_exist[i]
                except Exception, exception:
                    print line_number(), exception
                    if i < 3:
                        number_words = ["Primary", "Secondary", "Tertiary"]
                        portfolio_name = number_words[i]
                    else:
                        portfolio_name = "Portfolio %d" % (i+1)
                    portfolios_that_already_exist.append(portfolio_name)
                    need_to_save = True

                portfolio_account = PortfolioAccountTab(portfolio_account_notebook, (i+1), portfolio_name)
                portfolio_account.title = portfolio_name
                portfolio_account_notebook.AddPage(portfolio_account, portfolio_name)
            if need_to_save == True:
                config.DATA_ABOUT_PORTFOLIOS[1] = portfolios_that_already_exist
                db.save_DATA_ABOUT_PORTFOLIOS()

        sizer2 = wx.BoxSizer()
        sizer2.Add(portfolio_account_notebook, 1, wx.EXPAND)
        self.SetSizer(sizer2)
        ####

        print line_number(), "PortfolioPage loaded"
class PortfolioAccountTab(Tab):
    def __init__(self, parent, tab_number, portfolio_name):
        self.title = None
        tab_panel = wx.Panel.__init__(self, parent, tab_number)

        self.portfolio_id = tab_number
        self.name = portfolio_name
        #print line_number(), "self.portfolio_id =", self.portfolio_id
        self.portfolio_obj = config.PORTFOLIO_OBJECTS_DICT.get(str(tab_number))

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddSpacer(50)
        self.SetSizer(self.sizer)

        if not self.portfolio_obj:
            if config.ENCRYPTION_POSSIBLE:
                db.load_portfolio_object(self.portfolio_id)
            else:
                try:
                    db.load_portfolio_object(self.portfolio_id)
                except Exception, e:
                    print line_number(), e
                    self.portfolio_obj = None

        self.add_button = wx.Button(self, label="Update from file", pos=(5,0), size=(-1,-1))
        self.add_button.Bind(wx.EVT_BUTTON, self.addAccountCSV, self.add_button)

        self.portfolio_import_name_list = meta.return_portfolio_import_function_short_names()
        self.drop_down = wx.ComboBox(self, pos=(11,25), choices=self.portfolio_import_name_list)

        self.triple_list = meta.return_portfolio_import_function_triple()

        self.portfolio_import_name = None


        self.delete_button = wx.Button(self, label="Delete this portfolio", pos=(800,0), size=(-1,-1))
        self.delete_button.Bind(wx.EVT_BUTTON, self.confirmDeleteAccount, self.delete_button)

        self.rename_button = wx.Button(self, label="Rename this portfolio", pos=(568,22), size=(-1,-1))
        self.rename_button.Bind(wx.EVT_BUTTON, self.changeTabName, self.rename_button)

        self.change_number_of_portfolios_button = wx.Button(self, label="Change number of portfolios", pos=(568,0), size=(-1,-1))
        self.change_number_of_portfolios_button.Bind(wx.EVT_BUTTON, self.changeNumberOfPortfolios, self.change_number_of_portfolios_button)

        #print_portfolio_data_button = wx.Button(self, label="p", pos=(730,0), size=(-1,-1))
        #print_portfolio_data_button.Bind(wx.EVT_BUTTON, self.printData, print_portfolio_data_button)

        self.current_account_spreadsheet = None
        if self.portfolio_obj:
            self.spreadSheetFill(self.portfolio_obj)
        self.screen_grid = None

        self.ticker_input = wx.TextCtrl(self, -1, "", (250, 3))
        self.ticker_input.SetHint("ticker")

        self.share_input = wx.TextCtrl(self, -1, "", (250, 25))
        self.share_input.SetHint("# shares")

        self.cost_basis_input = wx.TextCtrl(self, -1, "", (350, 3))
        self.cost_basis_input.SetHint("Cash/Cost")

        self.update_button = wx.Button(self, label="Update Data", pos=(346,22), size=(-1,-1))
        self.update_button.Bind(wx.EVT_BUTTON, self.updateManually, self.update_button)

        self.update_prices_button = wx.Button(self, label="Update Prices", pos=(446,22), size=(-1,-1))
        self.update_prices_button.Bind(wx.EVT_BUTTON, self.confirmUpdatePrices, self.update_prices_button)

        self.remove_data_button = wx.Button(self, label="Remove Data", pos = (446, 0), size = (-1,-1))
        self.remove_data_button.Bind(wx.EVT_BUTTON, self.confirmRemoveData, self.remove_data_button)

        print line_number(), "PortfolioAccountTab loaded"

    def confirmRemoveData(self, event):
        ticker = self.ticker_input.GetValue()
        cost_basis = self.cost_basis_input.GetValue()
        shares = self.share_input.GetValue()
        if not ticker:
            return
        if shares:
            try:
                shares = float(shares)
            except:
                print line_number(), "Shares must be a number."
                return


        stock = utils.return_stock_by_symbol(ticker)
        if not stock:
            print line_number(), "Stock %s does not appear to exist. If you want to delete cash, you must set it to zero. It cannot be None" % ticker
            return

        if ticker and not (cost_basis or shares):
            confirm_message = "You are about to remove %s from your portfolio." % stock.symbol
        elif ticker and shares and cost_basis:
            confirm_message = "You are about to remove %s's share and cost basis data from your portfolio." % stock.symbol
        elif ticker and shares:
            if shares <= self.portfolio_obj.stock_shares_dict.get(stock.symbol):
                confirm_message = "You are about to remove " + str(shares) + " of %s's shares from your portfolio." % stock.symbol
            else:
                print line_number(), "Error: invalid number of shares."
                print "You currently have", str(self.portfolio_obj.stock_shares_dict.get(stock.symbol)), "shares."
                print "You tried to remove", str(shares) + "."
                return
        elif ticker and cost_basis:
            confirm_message = "You are about to remove %s's cost basis data from your portfolio." % stock.symbol
        else:
            print line_number(), "Invalid input"
            return

        confirm = wx.MessageDialog(None,
                                   confirm_message,
                                   'Delete Data',
                                   style = wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Delete"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        #try:
        #   confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
        #except AttributeError:
        #   pass
        confirm.Destroy()

        if yesNoAnswer == wx.ID_YES:
            self.removeData(self.portfolio_obj, stock, shares, cost_basis)


    def removeData(self, Account_object, stock, shares_to_remove = None, cost_basis = None):
        if cost_basis or shares_to_remove:
            if cost_basis:
                Account_object.cost_basis_dict.pop(stock.symbol, None)
            if shares_to_remove:
                current_shares = Account_object.stock_shares_dict.get(stock.symbol)
                new_shares = current_shares - shares_to_remove
                Account_object.stock_shares_dict[stock.symbol] = new_shares
        else: # remove stock
            Account_object.cost_basis_dict.pop(stock.symbol, None)
            Account_object.stock_shares_dict.pop(stock.symbol, None)
        db.save_portfolio_object(Account_object)
        utils.update_all_dynamic_grids()

        self.ticker_input.SetValue("")
        self.cost_basis_input.SetValue("")
        self.share_input.SetValue("")


    def changeNumberOfPortfolios(self, event):
        num_of_portfolios_popup = wx.NumberEntryDialog(None,
                                      "What would you like to call this portfolio?",
                                      "Rename tab",
                                      "Caption",
                                      config.NUMBER_OF_PORTFOLIOS,
                                      0,
                                      10
                                      )
        if num_of_portfolios_popup.ShowModal() != wx.ID_OK:
            return

        new_number_of_portfolios = num_of_portfolios_popup.GetValue()
        num_of_portfolios_popup.Destroy()

        config.NUMBER_OF_PORTFOLIOS = new_number_of_portfolios
        config.DATA_ABOUT_PORTFOLIOS[0] = new_number_of_portfolios
        # password = ""
        # if config.ENCRYPTION_POSSIBLE:
        #   password = self.get_password()
        db.save_DATA_ABOUT_PORTFOLIOS() #password = password)
        confirm = wx.MessageDialog(self,
                                 "The number of portfolios has changed. The change will be applied the next time you launch this program.",
                                 'Restart Required',
                                 style = wx.ICON_EXCLAMATION
                                 )
        confirm.ShowModal()
        confirm.Destroy()

    def fillSpreadsheetWithCurrentPortfolio(self):
        portfolio_obj = self.portfolio_obj
        if portfolio_obj:
            self.spreadSheetFill(portfolio_obj = portfolio_obj)

    def spreadSheetFill(self, portfolio_obj):
        if self.current_account_spreadsheet:
            self.current_account_spreadsheet.Destroy()

        size = config.PORTFOLIO_PAGE_SPREADSHEET_SIZE_POSITION_TUPLE[0]
        height_offset = 52
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            size = ( width - (config.HORIZONTAL_OFFSET_PER_TAB * 2) , height - height_offset - (config.VERTICAL_OFFSET_PER_TAB * 2)) # find the difference between the Frame and the grid size
        except:
            pass
        self.current_account_spreadsheet = create_account_spread_sheet(self, portfolio_obj, size = size)
        self.current_account_spreadsheet.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.loadStockDataFromGridIntoUpdateSection, self.current_account_spreadsheet)

        if self.current_account_spreadsheet:
            self.sizer.Add(self.current_account_spreadsheet, 1, wx.ALL|wx.EXPAND)
            self.current_account_spreadsheet.Show()
        return

    def loadStockDataFromGridIntoUpdateSection(self, event):
        row = event.GetRow()
        total_rows = self.current_account_spreadsheet.GetNumberRows()
        column = event.GetCol()
        total_cols = self.current_account_spreadsheet.GetNumberCols()
        value = self.current_account_spreadsheet.GetCellValue(row, column)

        ticker = None
        shares = None
        cost_basis = None
        cash = None

        if row <= (total_rows - 6): # 5 extra nonequity rows below, editble
            ticker = self.current_account_spreadsheet.GetCellValue(row, 0)
            shares = self.current_account_spreadsheet.GetCellValue(row, 2)
            cost_basis = self.current_account_spreadsheet.GetCellValue(row, 5)
        elif row == (total_rows - 3): # cash row
            cash = self.current_account_spreadsheet.GetCellValue(row, 4)
        else: # Nothing relevant selected
            self.ticker_input.SetValue("")
            self.share_input.SetValue("")
            self.cost_basis_input.SetValue("")


        if ticker:
            self.ticker_input.SetValue(ticker)
        else:
            self.ticker_input.SetValue("")

        if shares:
            self.share_input.SetValue(shares)
        else:
            self.share_input.SetValue("")

        if cost_basis and not cash:
            self.cost_basis_input.SetValue(cost_basis)
        else:
            self.cost_basis_input.SetValue("")

        if cash:
            self.ticker_input.SetValue("")
            self.share_input.SetValue("")
            self.cost_basis_input.SetValue(cash)


    def addAccountCSV(self, event):
        '''append a csv to current ticker list'''
        self.portfolio_import_name = self.drop_down.GetValue()

        # Identify the function mapped to screen name
        for triple in self.triple_list:
            if self.portfolio_import_name == triple.doc:
                portfolio_import_function = triple.function
            # in case doc string is too many characters...
            elif self.portfolio_import_name == triple.name:
                portfolio_import_function = triple.function

        if not portfolio_import_function:
            print line_number(), "Error, somthing went wrong locating the correct import function to use."

        self.account_obj = process_user_function.import_portfolio_via_user_created_function(self, self.portfolio_id, portfolio_import_function)

        print line_number(), type(self.account_obj)

        self.spreadSheetFill(self.current_account_spreadsheet, self.account_obj)

        # this is used in sale prep page:
        config.PORTFOLIO_OBJECTS_DICT[str(self.portfolio_id)] = self.account_obj

        utils.update_all_dynamic_grids()

        print line_number(), "Portfolio CSV import complete."

    def updateAccountViaCSV(self, event):
        self.portfolio_update_name = self.drop_down.GetValue()
        # Identify the function mapped to screen name
        for triple in self.triple_list:
            if self.portfolio_import_name == triple.doc:
                portfolio_import_function = triple.function
            # in case doc string is too many characters...
            elif self.portfolio_import_name == triple.name:
                portfolio_import_function = triple.function
        utils.update_all_dynamic_grids()


    def updateManually(self, event):
        ticker = utils.strip_string_whitespace(self.ticker_input.GetValue())
        cost_basis_or_cash = self.cost_basis_input.GetValue()
        shares = str(self.share_input.GetValue()).replace(",", "")

        if (not (ticker or cost_basis_or_cash)) or ((cost_basis_or_cash and shares) and not ticker) or (ticker and not (cost_basis_or_cash or shares)):
            # basically if the entered data cannot be parsed
            print line_number(), "invalid entry"
            return
        if cost_basis_or_cash and not (ticker or shares):
            # User is updating cash in account
            cash = cost_basis_or_cash
            cash = utils.money_text_to_float(cash)
            if not self.portfolio_obj:
                self.portfolio_obj = db.create_new_Account_if_one_doesnt_exist(self.portfolio_id, name = self.name)
            self.portfolio_obj.available_cash = cash
        else:
            # updating an individual stock
            if not self.portfolio_obj:
                self.portfolio_obj = db.create_new_Account_if_one_doesnt_exist(self.portfolio_id, name = self.name)

            cost_basis = cost_basis_or_cash

            try:
                ticker = ticker.upper()
            except Exception, e:
                print line_number(), e, "invalid ticker: %s" % ticker

            stock = utils.return_stock_by_symbol(ticker)
            if not stock:
                print line_number(), "stock with ticker %s does not appear to exist, do you want to create it?" % ticker
                confirm_update = self.confirmCreateMissingStock(ticker)
                if confirm_update:
                    db.create_new_Stock_if_it_doesnt_exist(ticker)
                    stock = utils.return_stock_by_symbol(ticker)
                else:
                    # cancel adding stock
                    print line_number(), "Canceling portfolio update"
                    return

            if shares:
                try:
                    shares = float(shares)
                    self.portfolio_obj.stock_shares_dict[ticker] = shares
                except Exception, e:
                    print line_number(), e, "Error: shares data is improperly formatted"

            if cost_basis:
                cost_basis = utils.money_text_to_float(cost_basis)
                self.portfolio_obj.cost_basis_dict[ticker] = cost_basis


        db.save_portfolio_object(self.portfolio_obj)
        self.spreadSheetFill(self.portfolio_obj)
        self.ticker_input.SetValue("")
        self.cost_basis_input.SetValue("")
        self.share_input.SetValue("")
        utils.update_all_dynamic_grids()


    def confirmCreateMissingStock(self, ticker):
        ticker = ticker.upper()
        confirm = wx.MessageDialog(None,
                                   "Stock with ticker %s does not appear to exist, do you want to create a stock with ticker %s?" % (ticker, ticker),
                                   'Create Stock With Ticker %s?' % ticker,
                                   style = wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Create"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        #try:
        #   confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
        #except AttributeError:
        #   pass
        confirm.Destroy()
        return yesNoAnswer == wx.ID_YES
    def confirmUpdateMissingStock(self):
        confirm = wx.MessageDialog(None,
                                   "You are about to make a request from Yahoo Finance. If you do this too often they may temporarily block your IP address. This will require an update delay to prevent rate limiting.",
                                   'Confirm Update Stock Data?',
                                   style = wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Download"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        #try:
        #   confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
        #except AttributeError:
        #   pass
        confirm.Destroy()
        return yesNoAnswer == wx.ID_YES
    def confirmUpdateMultipleMissingStocks(self):
        confirm = wx.MessageDialog(None,
                                   "Some of the stocks you are updating cannot be updated via Nasdaq. You are about to make a request from Yahoo Finance. If you do this too often they may temporarily block your IP address. This will require an update delay to prevent rate limiting.",
                                   'Confirm Update Stock Data?',
                                   style = wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Download"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        #try:
        #   confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
        #except AttributeError:
        #   pass
        confirm.Destroy()
        return yesNoAnswer == wx.ID_YES

    def confirmUpdatePrices(self, event):
        confirm = wx.MessageDialog(None,
                                   "You are about to make a request from Nasdaq.com. If you do this too often they may temporarily block your IP address.",
                                   'Confirm Download',
                                   style = wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Download"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        #try:
        #   confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
        #except AttributeError:
        #   pass
        confirm.Destroy()

        if yesNoAnswer == wx.ID_YES:
            self.updatePrices()

    def updatePrices(self):
        print line_number(), "Begin ticker download..."

        ticker_data = scrape.convert_nasdaq_csv_to_stock_objects()
        current_time = time.time()

        tickers_that_need_yql_update = []

        for ticker in self.portfolio_obj.stock_shares_dict:
            stock = config.GLOBAL_STOCK_DICT.get(ticker)
            if stock:
                last_update_for_last_close = utils.return_last_close_and_last_update_tuple(stock)[1]
                if last_update_for_last_close:
                    if (current_time - last_update_for_last_close) < config.PORTFOLIO_PRICE_REFRESH_TIME:
                        #fresh data
                        pass
                    else:
                        #update
                        tickers_that_need_yql_update.append(stock.symbol)
                else:
                    #update
                    tickers_that_need_yql_update.append(stock.symbol)


        if tickers_that_need_yql_update:
            confirm = self.confirmUpdateMultipleMissingStocks()
            print line_number(), tickers_that_need_yql_update
            if confirm:
                scrape.scrape_loop_for_missing_portfolio_stocks(ticker_list = tickers_that_need_yql_update, update_regardless_of_recent_updates = True)

        utils.update_all_dynamic_grids()

        print line_number(), "Not sure if necessary, but saving here after update."
        db.save_GLOBAL_STOCK_DICT()

        #self.saveTickerDataAsStocks(ticker_data) # no longer used
        # Update scrape page?
        # Don't want to take the time to figure this out just now.
        print line_number(), "Add function here to update scrape time."


    def changeTabName(self, event):
        old_name = self.GetLabel()
        rename_popup = wx.TextEntryDialog(None,
                                      "What would you like to call this portfolio?",
                                      "Rename tab",
                                      str(self.GetLabel())
                                      )
        rename_popup.ShowModal()
        new_name = str(rename_popup.GetValue())
        rename_popup.Destroy()


        portfolio_name_list = config.DATA_ABOUT_PORTFOLIOS[1]
        new_portfolio_names = []
        if new_name != old_name:
            if new_name not in portfolio_name_list:
                for i in portfolio_name_list:
                    if i == old_name:
                        new_portfolio_names.append(new_name)
                    else:
                        new_portfolio_names.append(i)

                self.name = new_name
                self.portfolio_obj.name = new_name
                config.DATA_ABOUT_PORTFOLIOS[1] = new_portfolio_names

                print line_number(), "This file opening needs to be removed."
                # password = ""
                # if config.ENCRYPTION_POSSIBLE:
                #   password = self.get_password()
                db.save_DATA_ABOUT_PORTFOLIOS() #password = password)
                db.save_portfolio_object(self.portfolio_obj)
                print line_number(), config.DATA_ABOUT_PORTFOLIOS
                confirm = wx.MessageDialog(self,
                                         "This portfolio's name has been changed. The change will be applied the next time you launch this program.",
                                         'Restart Required',
                                         style = wx.ICON_EXCLAMATION
                                         )
                confirm.ShowModal()
                confirm.Destroy()

            else:
                error = wx.MessageDialog(self,
                                         'Each portfolio must have a unique name.',
                                         'Name Error',
                                         style = wx.ICON_ERROR
                                         )
                error.ShowModal()
                error.Destroy()

    def confirmDeleteAccount(self, event):
        confirm = wx.MessageDialog(None,
                                   "You are about to delete your current account data. Are you sure you want to delete this data?",
                                   'Delete Portfolio Data?',
                                   wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Delete"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        confirm.Destroy()

        if yesNoAnswer == wx.ID_YES:
            self.deleteAccountList()

    def deleteAccountList(self):
        '''delete account'''

        try:
            # Reset to default name in data about portfolios
            default_portfolio_names = ["Primary", "Secondary", "Tertiary"]
            if self.portfolio_id < 10:
                portfolio_name = "Portfolio %d" % (self.portfolio_id+1)
            else:
                portfolio_name = "%dth" % (self.portfolio_id+1)
            if self.portfolio_id in range(len(default_portfolio_names)):
                portfolio_name = default_portfolio_names[self.portfolio_id]
            config.DATA_ABOUT_PORTFOLIOS[1][self.portfolio_id] = portfolio_name
        except Exception as e:
            print line_number(), e


        # password = ""
        # if config.ENCRYPTION_POSSIBLE:
        #   password = self.get_password()



        # password = ""
        # if config.ENCRYPTION_POSSIBLE:
        #   password = self.get_password()

        deleted = db.delete_portfolio_object(self.portfolio_id) #, password = password)

        if not deleted:
            print line_number(), "Trying to remove default portfolio."
            print line_number(), config.DATA_ABOUT_PORTFOLIOS
            try:
                print line_number(), self.portfolio_id
                portfolio_to_remove_index = self.portfolio_id - 1 # can't have a zero tab number i think
                del config.DATA_ABOUT_PORTFOLIOS[1][portfolio_to_remove_index] # see if index is out of range
                config.DATA_ABOUT_PORTFOLIOS[0] = config.DATA_ABOUT_PORTFOLIOS[0] - 1
                print line_number(), "Delete success."
                print line_number(), config.DATA_ABOUT_PORTFOLIOS
                deleted = True
            except Exception as e:
                print line_number(), e
                print line_number(), "Something weird is going on with deleting a portfolio."

        db.save_DATA_ABOUT_PORTFOLIOS() #password = password)

        self.portfolio_obj = Account(self.portfolio_id, name = portfolio_name)

        if deleted:
            confirm = wx.MessageDialog(self,
                             "The number of portfolios has changed. The change will be applied the next time you launch this program.",
                             'Restart Required',
                             style = wx.ICON_EXCLAMATION
                             )
            confirm.ShowModal()
            confirm.Destroy()

        if self.current_account_spreadsheet:
            self.current_account_spreadsheet.Destroy()
            self.current_account_spreadsheet = AccountDataGrid(self, -1, size=(980,637), pos=(0,50))
            utils.update_all_dynamic_grids()
        return
###
class ViewDataPage(Tab):
    def __init__(self, parent):
        self.title = "View Data"
        self.uid = config.VIEW_DATA_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)
        ####
        view_data_page_panel = wx.Panel(self, -1, pos=(0,5), size=( wx.EXPAND, wx.EXPAND))
        view_data_notebook = wx.Notebook(view_data_page_panel)

        self.all_stocks_page = AllStocksPage(view_data_notebook)
        view_data_notebook.AddPage(self.all_stocks_page, self.all_stocks_page.title)

        self.stock_data_page = StockDataPage(view_data_notebook)
        view_data_notebook.AddPage(self.stock_data_page, self.stock_data_page.title)

        sizer2 = wx.BoxSizer()
        sizer2.Add(view_data_notebook, 1, wx.EXPAND)
        self.SetSizer(sizer2)
        ####
class AllStocksPage(Tab):
    def __init__(self, parent):
        self.title = "View All Stocks"
        self.uid = config.ALL_STOCKS_PAGE_UNIQUE_ID
        self.parent = parent
        wx.Panel.__init__(self, parent)
        welcome_page_text = wx.StaticText(self, -1,
                             "Full Stock List",
                             (10,10)
                             )

        self.spreadsheet = None

        refresh_button = wx.Button(self, label="refresh", pos=(110,4), size=(-1,-1))
        refresh_button.Bind(wx.EVT_BUTTON, self.spreadSheetFillAllStocks, refresh_button)

        reset_attribute_button = wx.Button(self, label="reset attributes displayed", pos=(800,4), size=(-1,-1))
        reset_attribute_button.Bind(wx.EVT_BUTTON, self.resetGlobalAttributeSet, reset_attribute_button)


        self.first_spread_sheet_load = True

        # commented out below to speed up testing
        #self.spreadSheetFillAllStocks("event")

        print line_number(), "AllStocksPage loaded"

    def spreadSheetFillAllStocks(self, event):
        if self.first_spread_sheet_load:
            self.first_spread_sheet_load = False
        else:
            try:
                self.spreadsheet.Destroy()
            except Exception, exception:
                print line_number(), exception

        # Find all attribute names
        stock_list = utils.return_all_stocks()

        #You need this code to resize
        size = config.FULL_SPREADSHEET_SIZE_POSITION_TUPLE[0]
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            print line_number(), width, height
            size = (width-20, height-128) # find the difference between the Frame and the grid size
        except Exception, e:
            print line_number(), e
        self.sizer = None
        self.inner_sizer = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer.AddSpacer(config.FULL_SPREADSHEET_SIZE_POSITION_TUPLE[1][1])

        new_grid = create_megagrid_from_stock_list(stock_list, self, size = size)

        self.inner_sizer.Add(new_grid, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(self.inner_sizer)
        self.sizer.Add(self, 1, wx.EXPAND|wx.ALL)
        ##
        self.spreadsheet = new_grid

        self.spreadsheet.Show()

    def resetGlobalAttributeSet(self, event):
        temp_global_stock_list = utils.return_all_stocks()
        temp_global_attribute_set = set()
        for stock in temp_global_stock_list:
            for attribute in dir(stock):
                if attribute not in temp_global_attribute_set:
                    if not attribute.startswith("_"):
                        if attribute not in config.CLASS_ATTRIBUTES:
                            temp_global_attribute_set.add(attribute)
        config.GLOBAL_ATTRIBUTE_SET = temp_global_attribute_set
        db.save_GLOBAL_ATTRIBUTE_SET()
class StockDataPage(Tab):
    def __init__(self, parent):
        self.title = "View One Stock"
        self.uid = config.STOCK_DATA_PAGE_UNIQUE_ID
        self.parent = parent
        wx.Panel.__init__(self, parent)

        rank_page_text = wx.StaticText(self, -1,
                             "Data for stock:",
                             (10,10)
                             )
        self.ticker_input = wx.TextCtrl(self, -1,
                                   "",
                                   (110, 8),
                                   style=wx.TE_PROCESS_ENTER
                                   )
        self.ticker_input.SetHint("ticker")
        self.ticker_input.Bind(wx.EVT_TEXT_ENTER, self.createOneStockSpreadSheet)

        load_screen_button = wx.Button(self,
                                          label="look up",
                                          pos=(210,5),
                                          size=(-1,-1)
                                          )
        load_screen_button.Bind(wx.EVT_BUTTON, self.createOneStockSpreadSheet, load_screen_button)


        self.search_data = wx.TextCtrl(self, -1,
                                   "",
                                   (110, 31),
                                   style=wx.TE_PROCESS_ENTER
                                   )
        self.search_data.SetHint("search data")
        self.search_data.Bind(wx.EVT_KEY_UP, self.searchData)
        self.search_button = wx.Button(self,
                                         label="search",
                                          pos=(210, 28),
                                         size=(-1,-1)
                                         )
        self.search_button.Bind(wx.EVT_BUTTON, self.searchData, self.search_button)


        update_yql_basic_data_button = wx.Button(self,
                                         label="update basic data",
                                         pos=(300,5),
                                         size=(-1,-1)
                                         )
        #update_annual_data_button = wx.Button(self,
        #                                 label="update annual data",
        #                                 pos=(430,5),
        #                                 size=(-1,-1)
        #                                 )
        #update_analyst_estimates_button = wx.Button(self,
        #                                 label="update analyst estimates",
        #                                 pos=(570,5),
        #                                 size=(-1,-1)
        #                                 )


        update_additional_data_button = wx.Button(self,
                                          label="update additional data",
                                          pos=(430,5),
                                          size=(-1,-1)
                                          )

        self.current_ticker_viewed = None
        self.current_search_term = None

        update_additional_data_button.Bind(wx.EVT_BUTTON, self.updateAdditionalDataForOneStock, update_additional_data_button)

        update_yql_basic_data_button.Bind(wx.EVT_BUTTON, self.update_yql_basic_data, update_yql_basic_data_button)
        #update_annual_data_button.Bind(wx.EVT_BUTTON, self.update_annual_data, update_annual_data_button)
        #update_analyst_estimates_button.Bind(wx.EVT_BUTTON, self.update_analyst_estimates_data, update_analyst_estimates_button)

        print line_number(), "StockDataPage loaded"

    def searchData(self, event, search_term = None):
        current_ticker_viewed = self.current_ticker_viewed
        if not current_ticker_viewed:
            return

        if not search_term:
            search_term = self.search_data.GetValue() # if loading via text input
        self.current_search_term = search_term

        self.createOneStockSpreadSheet("event", current_ticker_viewed = current_ticker_viewed, search_term = search_term)



    def updateAdditionalDataForOneStock(self, event):
        ticker = self.ticker_input.GetValue()
        if str(ticker) == "ticker" or not ticker:
            return
        scrape.scrape_all_additional_data_prep([ticker])
        self.createOneStockSpreadSheet("event")

    def createOneStockSpreadSheet(self, event, current_ticker_viewed = None, search_term = None):
        if not current_ticker_viewed:
            ticker = self.ticker_input.GetValue() # if loading via text input
        else:
            ticker = current_ticker_viewed # if reloading spreadsheet

        if str(ticker) == "ticker" or not ticker:
            return

        #You need this code to resize
        size = config.FULL_SPREADSHEET_SIZE_POSITION_TUPLE[0]
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            print line_number(), width, height
            size = (width-20, height-128) # find the difference between the Frame and the grid size
        except Exception, e:
            print line_number(), e
        self.sizer = None
        self.inner_sizer = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer.AddSpacer(60)

        new_grid = create_spread_sheet_for_one_stock(self, str(ticker).upper(), size = size, search_term = search_term)

        self.inner_sizer.Add(new_grid, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(self.inner_sizer)
        self.sizer.Add(self, 1, wx.EXPAND|wx.ALL)
        ##
        self.screen_grid = new_grid
        self.current_ticker_viewed = ticker.upper()

    def update_yql_basic_data(self, event):
        ticker = self.ticker_input.GetValue()
        if str(ticker) == "ticker":
            return
        print line_number(), "basic yql scrape"
        chunk_list_and_percent_of_full_scrape_done_and_number_of_tickers_to_scrape = scrape.prepareYqlScrape([str(ticker).upper()])
        chunk_list = chunk_list_and_percent_of_full_scrape_done_and_number_of_tickers_to_scrape[0]
        data = scrape.executeYqlScrapePartOne(chunk_list, 0)
        scrape.executeYqlScrapePartTwo(chunk_list, 0, data)
        self.createOneStockSpreadSheet(event = "")

    def update_annual_data(self, event):
        ticker = self.ticker_input.GetValue()
        if str(ticker) == "ticker":
            return
        print line_number(), "scraping yahoo and morningstar annual data, you'll need to keep an eye on the terminal until this finishes."
        scrape_balance_sheet_income_statement_and_cash_flow( [str(ticker).upper()] )
        self.createOneStockSpreadSheet(event = "")

    def update_analyst_estimates_data(self, event):
        ticker = self.ticker_input.GetValue()
        if str(ticker) == "ticker":
            return
        print line_number(), "about to scrape"
        scrape_analyst_estimates( [str(ticker).upper()] )
        self.createOneStockSpreadSheet(event = "")
###

####

#####
class AnalysisPage(Tab):
    def __init__(self, parent):
        self.title = "Analyse Data"
        self.uid = config.ANALYSE_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)
        ####

        analyse_panel = wx.Panel(self, -1, pos=(0,5), size=( wx.EXPAND, wx.EXPAND))
        analyse_notebook = wx.Notebook(analyse_panel)

        self.screen_page = ScreenPage(analyse_notebook)
        analyse_notebook.AddPage(self.screen_page, self.screen_page.title)

        self.saved_screen_page = SavedScreenPage(analyse_notebook)
        analyse_notebook.AddPage(self.saved_screen_page, self.saved_screen_page.title)

        self.rank_page = RankPage(analyse_notebook)
        analyse_notebook.AddPage(self.rank_page, self.rank_page.title)

        self.custom_analyse_meta_page = CustomAnalysisMetaPage(analyse_notebook)
        analyse_notebook.AddPage(self.custom_analyse_meta_page, self.custom_analyse_meta_page.title)

        sizer2 = wx.BoxSizer()
        sizer2.Add(analyse_notebook, 1, wx.EXPAND)
        self.SetSizer(sizer2)

class ScreenPage(Tab):
    def __init__(self, parent):
        self.title = "Screen"
        self.uid = config.SCREEN_PAGE_UNIQUE_ID
        self.parent = parent
        wx.Panel.__init__(self, parent)
        welcome_page_text = wx.StaticText(self, -1,
                             "Screen Stocks",
                             (10,10)
                             )
        screen_button = wx.Button(self, label="screen", pos=(110,4), size=(-1,-1))
        screen_button.Bind(wx.EVT_BUTTON, self.screenStocks, screen_button)

        self.screen_name_list = meta.return_screen_function_short_names()
        self.drop_down = wx.ComboBox(self, pos=(210, 6), choices=self.screen_name_list)

        self.triple_list = meta.return_screen_function_triple()

        self.save_screen_button = wx.Button(self, label="save", pos=(800,4), size=(-1,-1))
        self.save_screen_button.Bind(wx.EVT_BUTTON, self.saveScreen, self.save_screen_button)
        self.save_screen_button.Hide()

        self.screen_grid = None

        self.first_spread_sheet_load = True

        self.ticker_col = 0

        print line_number(), "ScreenPage loaded"

    def screenStocks(self, event):
        screen_name = self.drop_down.GetValue()

        # Identify the function mapped to screen name
        for triple in self.triple_list:
            if screen_name == triple.doc:
                screen_function = triple.function
            # in case doc string is too many characters...
            elif screen_name == triple.name:
                screen_function = triple.function
        if not screen_function:
            print line_number(), "Error, somthing went wrong locating the correct screen to use."

        # run screen
        conforming_stocks = []
        for ticker in config.GLOBAL_STOCK_DICT:
            stock = config.GLOBAL_STOCK_DICT.get(ticker)
            result = screen_function(stock)
            if result is True:
                conforming_stocks.append(stock)

        config.CURRENT_SCREEN_LIST = conforming_stocks

        self.createSpreadsheet(conforming_stocks)

        self.save_screen_button.Show()



    def createSpreadsheet(self, stock_list):
        if self.first_spread_sheet_load:
            self.first_spread_sheet_load = False
        else:
            try:
                self.screen_grid.Destroy()
            except Exception as e:
                print line_number(), e

        stock_list.sort(key = lambda x: (x is None, x.symbol))

        #You need this code to resize
        size = config.FULL_SPREADSHEET_SIZE_POSITION_TUPLE[0]
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            print line_number(), width, height
            size = (width-20, height-128) # find the difference between the Frame and the grid size
        except Exception, e:
            print line_number(), e
        self.sizer = None
        self.inner_sizer = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer.AddSpacer(config.FULL_SPREADSHEET_SIZE_POSITION_TUPLE[1][1])


        new_grid = create_megagrid_from_stock_list(stock_list, self, size = size)


        self.inner_sizer.Add(new_grid, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(self.inner_sizer)
        self.sizer.Add(self, 1, wx.EXPAND|wx.ALL)
        ##

        self.screen_grid = new_grid
        self.screen_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, lambda event: self.addStockToResearchPage(event), self.screen_grid)


    def saveScreen(self, event):
        current_screen_dict = config.GLOBAL_STOCK_SCREEN_DICT
        screen_name_tuple_list = config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST
        existing_screen_names = [i[0] for i in screen_name_tuple_list]

        if not current_screen_dict:
            db.load_GLOBAL_STOCK_SCREEN_DICT()
            current_screen_dict = config.GLOBAL_STOCK_SCREEN_DICT
            # current_screen_dict must at least be {}

        save_popup = wx.TextEntryDialog(None,
                                          "What would you like to name this group?",
                                          "Save Screen",
                                          "%s screen saved at %s" % (str(time.strftime("%Y-%m-%d")),str(time.strftime("%H:%M:%S")))
                                         )
        if save_popup.ShowModal() == wx.ID_OK:
            saved_screen_name = str(save_popup.GetValue())

            # files save with replace(" ", "_") so you need to check if any permutation of this patter already exists.
            if saved_screen_name in existing_screen_names or saved_screen_name.replace(" ", "_") in existing_screen_names or saved_screen_name.replace("_", " ") in existing_screen_names:
                save_popup.Destroy()
                error = wx.MessageDialog(self,
                                         'Each saved screen must have a unique name. Would you like to try saving again with a different name.',
                                         'Error: Name already exists',
                                         style = wx.YES_NO
                                         )
                error.SetYesNoLabels(("&Rename"), ("&Don't Save"))
                yesNoAnswer = error.ShowModal()
                error.Destroy()
                if yesNoAnswer == wx.ID_YES:
                    # Recursion
                    print line_number(), "Recursion event in saveScreen"
                    self.saveScreen(event="event")
                return
            else:
                config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST.append([saved_screen_name, float(time.time())])
                #print line_number(), config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST

                # Save global dict
                db.save_GLOBAL_STOCK_STREEN_DICT()
                # Save screen name results
                db.save_named_screen(saved_screen_name, config.CURRENT_SCREEN_LIST)
                # Save SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST
                db.save_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST()

                utils.update_all_screen_dropdowns_after_saving_a_new_screen()

                self.save_screen_button.Hide()
                save_popup.Destroy()
                return

    def addStockToResearchPage(self, event):
        row = event.GetRow()
        col = event.GetCol()
        if int(col) == self.ticker_col:
            ticker = self.screen_grid.GetCellValue(row, col)
            utils.add_ticker_to_research_page(str(ticker))

class SavedScreenPage(Tab):
    def __init__(self, parent):
        self.title = "View Saved Screens"
        self.uid = config.SAVED_SCREEN_PAGE_UNIQUE_ID
        self.parent = parent
        wx.Panel.__init__(self, parent)
        welcome_page_text = wx.StaticText(self, -1,
                             "Saved screens",
                             (10,10)
                             )
        refresh_screen_button = wx.Button(self, label="refresh list", pos=(110,5), size=(-1,-1))
        refresh_screen_button.Bind(wx.EVT_BUTTON, self.refreshScreens, refresh_screen_button)

        load_screen_button = wx.Button(self, label="load screen", pos=(200,5), size=(-1,-1))
        load_screen_button.Bind(wx.EVT_BUTTON, self.loadScreen, load_screen_button)



        self.existing_screen_name_list = []
        if config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST:
            self.existing_screen_name_list = [i[0] for i in reversed(config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST)]

        self.drop_down = wx.ComboBox(self, value="",
                                     pos=(305, 6),
                                     choices=self.existing_screen_name_list,
                                     style = wx.TE_READONLY
                                     )

        self.currently_viewed_screen = None
        self.delete_screen_button = wx.Button(self, label="delete", pos=(880,4), size=(-1,-1))
        self.delete_screen_button.Bind(wx.EVT_BUTTON, self.deleteScreen, self.delete_screen_button)
        self.delete_screen_button.Hide()

        self.first_spread_sheet_load = True
        self.spreadsheet = None

        self.ticker_col = 0

        print line_number(), "SavedScreenPage loaded"

    def deleteScreen(self, event):
        confirm = wx.MessageDialog(None,
                                   "You are about to delete this screen.",
                                   'Are you sure?',
                                   wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Delete"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        confirm.Destroy()


        print line_number(), self.screen_grid
        if yesNoAnswer != wx.ID_YES:
            return
        try:
            print line_number(), self.currently_viewed_screen

            db.delete_named_screen(self.currently_viewed_screen)

            self.screen_grid.Destroy()
            self.currently_viewed_screen = None

        except Exception, exception:
            print line_number(), exception
            error = wx.MessageDialog(self,
                                     "Something went wrong. File was not deleted, because this file doesn't seem to exist.",
                                     'Error: File Does Not Exist',
                                     style = wx.ICON_ERROR
                                     )
            error.ShowModal()
            error.Destroy()
            return
        self.refreshScreens('event')

    def refreshScreens(self, event):
        self.drop_down.Hide()
        self.drop_down.Destroy()

        # Why did i put this here? Leave a note next time moron...
        time.sleep(2)

        self.existing_screen_name_list = [i[0] for i in reversed(config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST)]


        self.drop_down = wx.ComboBox(self,
                                     pos=(305, 6),
                                     choices=self.existing_screen_name_list,
                                     style = wx.TE_READONLY
                                     )

    def loadScreen(self, event):
        selected_screen_name = self.drop_down.GetValue()
        try:
            config.CURRENT_SAVED_SCREEN_LIST = db.load_named_screen(selected_screen_name)
        except Exception, exception:
            print line_number(), exception
            error = wx.MessageDialog(self,
                                     "Something went wrong. This file doesn't seem to exist.",
                                     'Error: File Does Not Exist',
                                     style = wx.ICON_ERROR
                                     )
            error.ShowModal()
            error.Destroy()
            return
        self.currently_viewed_screen = selected_screen_name

        if self.first_spread_sheet_load:
            self.first_spread_sheet_load = False
        else:
            if self.screen_grid:
                try:
                    self.screen_grid.Destroy()
                except Exception, exception:
                    print line_number(), exception

        self.spreadSheetFill()

    def spreadSheetFill(self):
        #You need this code to resize
        size = config.FULL_SPREADSHEET_SIZE_POSITION_TUPLE[0]
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            #print line_number(), width, height
            size = (width-20, height-128) # find the difference between the Frame and the grid size
        except Exception, e:
            print line_number(), e
        self.sizer = None
        self.inner_sizer = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer.AddSpacer(config.FULL_SPREADSHEET_SIZE_POSITION_TUPLE[1][1])


        new_grid = create_megagrid_from_stock_list(config.CURRENT_SAVED_SCREEN_LIST, self, size = size)


        self.inner_sizer.Add(new_grid, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(self.inner_sizer)
        self.sizer.Add(self, 1, wx.EXPAND|wx.ALL)
        ##
        self.spreadsheet = new_grid
        self.spreadsheet.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, lambda event: self.addStockToResearchPage(event), self.spreadsheet)


        self.spreadsheet.Show()

        self.delete_screen_button.Show()

    def addStockToResearchPage(self, event):
        row = event.GetRow()
        col = event.GetCol()
        if int(col) == self.ticker_col:
            ticker = self.spreadsheet.GetCellValue(row, col)
            utils.add_ticker_to_research_page(str(ticker))

class RankPage(Tab):
    def __init__(self, parent):
        self.title = "Rank"
        self.uid = config.RANK_PAGE_UNIQUE_ID
        self.parent = parent
        wx.Panel.__init__(self, parent)

        self.full_ticker_list = [] # this should hold all tickers in any spreadsheet displayed
        self.held_ticker_list = [] # not sure if this is relevant anymore

        self.full_attribute_list = list(config.GLOBAL_ATTRIBUTE_SET)

        rank_page_text = wx.StaticText(self, -1,
                             self.title,
                             (10,10)
                             )

        refresh_screen_button = wx.Button(self, label="refresh", pos=(110,5), size=(-1,-1))
        refresh_screen_button.Bind(wx.EVT_BUTTON, self.refreshScreens, refresh_screen_button)

        load_screen_button = wx.Button(self, label="add screen", pos=(200,5), size=(-1,-1))
        load_screen_button.Bind(wx.EVT_BUTTON, self.loadScreen, load_screen_button)

        load_portfolio_button = wx.Button(self, label="add account", pos=(191,30), size=(-1,-1))
        load_portfolio_button.Bind(wx.EVT_BUTTON, self.loadAccount, load_portfolio_button)

        update_additional_data_button = wx.Button(self, label="update additional data", pos=(5,30), size=(-1,-1))
        update_additional_data_button.Bind(wx.EVT_BUTTON, self.updateAdditionalData, update_additional_data_button)



        #update_annual_data_button = wx.Button(self, label="update annual data", pos=(5,5), size=(-1,-1))
        #update_annual_data_button.Bind(wx.EVT_BUTTON, self.updateAnnualData, update_annual_data_button)

        #update_analyst_estimates_button = wx.Button(self, label="update analysts estimates", pos=(5,30), size=(-1,-1))
        #update_analyst_estimates_button.Bind(wx.EVT_BUTTON, self.updateAnalystEstimates, update_analyst_estimates_button)



        self.existing_screen_name_list = []
        if config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST:
            self.existing_screen_name_list = [i[0] for i in reversed(config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST)] # add conditional to remove old screens
        self.drop_down = wx.ComboBox(self,
                                     pos=(305, 6),
                                     choices=self.existing_screen_name_list,
                                     style = wx.TE_READONLY
                                     )


        self.portfolio_name_tuple_list = []
        for i in range(len(config.PORTFOLIO_NAMES)):
            tuple_to_append = [config.PORTFOLIO_NAMES[i], (i+1)]
            self.portfolio_name_tuple_list.append(tuple_to_append)
            #print line_number(), self.portfolio_name_tuple_list

        self.accounts_drop_down = wx.ComboBox(self,
                                     pos=(305, 31),
                                     choices=config.PORTFOLIO_NAMES,
                                     style = wx.TE_READONLY
                                     )


        self.currently_viewed_screen = None
        self.clear_button = wx.Button(self, label="clear", pos=(890,4), size=(-1,-1))
        self.clear_button.Bind(wx.EVT_BUTTON, self.clearGrid, self.clear_button)
        self.clear_button.Hide()

        self.sort_button = wx.Button(self, label="Sort by:", pos=(420,30), size=(-1,-1))
        self.sort_button.Bind(wx.EVT_BUTTON, self.sortStocks, self.sort_button)

        sort_drop_down_width = -1
        if [attribute for attribute in config.GLOBAL_ATTRIBUTE_SET if (len(str(attribute)) > 50)]:
            sort_drop_down_width = 480

        self.sort_drop_down = wx.ComboBox(self,
                                     pos=(520, 31),
                                     choices=self.full_attribute_list,
                                     style = wx.TE_READONLY,
                                     size = (sort_drop_down_width, -1)
                                     )
        self.sort_button.Hide()
        self.sort_drop_down.Hide()

        self.rank_triple_list = meta.return_rank_function_triple()
        self.rank_name_list = meta.return_rank_function_short_names()
        self.rank_button =  wx.Button(self, label="Rank by:", pos=(420, 5), size=(-1,-1))
        self.rank_button.Bind(wx.EVT_BUTTON, self.rankStocks, self.rank_button)
        self.rank_drop_down = wx.ComboBox(self,
                                     pos=(520, 6),
                                     choices=self.rank_name_list,
                                     style = wx.TE_READONLY
                                     )
        self.rank_button.Hide()
        self.rank_drop_down.Hide()

        self.fade_opacity = 255
        self.spreadsheet = None

        self.rank_name = None

        self.ticker_col = 0

        print line_number(), "RankPage loaded"

    def rankStocks(self, event):
        self.rank_name = self.rank_drop_down.GetValue()

        # Identify the function mapped to screen name
        for triple in self.rank_triple_list:
            if self.rank_name == triple.doc:
                rank_function = triple.function
            # in case doc string is too many characters...
            elif self.rank_name == triple.name:
                rank_function = triple.function

        if not rank_function:
            print line_number(), "Error, somthing went wrong locating the correct screen to use."

        # run ranking funtion on all stocks

        ranked_tuple_list = process_user_function.return_ranked_list_from_rank_function(config.RANK_PAGE_ALL_RELEVANT_STOCKS, rank_function)

        self.createRankedSpreadsheet(ranked_tuple_list, self.rank_name)

    def createUnrankedSpreadsheet(self, stock_list=None):
        self.full_attribute_list = list(config.GLOBAL_ATTRIBUTE_SET)
        self.sort_drop_down.Set(self.full_attribute_list)

        if stock_list is None:
            stock_list = config.RANK_PAGE_ALL_RELEVANT_STOCKS
        if self.spreadsheet:
            try:
                self.spreadsheet.Destroy()
            except Exception, exception:
                print line_number(), exception

        stock_list.sort(key = lambda x: x.symbol)

        #You need this code to resize
        size = config.RANK_PAGE_SPREADSHEET_SIZE_POSITION_TUPLE[0]
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            #print line_number(), width, height
            size = (width-20, height-128) # find the difference between the Frame and the grid size
        except Exception, e:
            print line_number(), e
        self.sizer = None
        self.inner_sizer = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer.AddSpacer(config.RANK_PAGE_SPREADSHEET_SIZE_POSITION_TUPLE[1][1])


        new_grid = create_megagrid_from_stock_list(stock_list, self, size = size, pos=config.RANK_PAGE_SPREADSHEET_SIZE_POSITION_TUPLE[1])


        self.inner_sizer.Add(new_grid, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(self.inner_sizer)
        self.sizer.Add(self, 1, wx.EXPAND|wx.ALL)
        ##
        self.spreadsheet = new_grid
        self.spreadsheet.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, lambda event: self.addStockToResearchPage(event), self.spreadsheet)


        self.clear_button.Show()
        self.sort_button.Show()
        self.sort_drop_down.Show()
        self.rank_button.Show()
        self.rank_drop_down.Show()

        self.spreadsheet.Show()

    def createRankedSpreadsheet(self, ranked_tuple_list, rank_name):
        self.full_attribute_list = list(config.GLOBAL_ATTRIBUTE_SET)
        self.sort_drop_down.Set(self.full_attribute_list)



        #You need this code to resize
        size = config.RANK_PAGE_SPREADSHEET_SIZE_POSITION_TUPLE[0]
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            print line_number(), width, height
            size = (width-20, height-128) # find the difference between the Frame and the grid size
        except Exception, e:
            print line_number(), e
        self.sizer = None
        self.inner_sizer = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer.AddSpacer(config.RANK_PAGE_SPREADSHEET_SIZE_POSITION_TUPLE[1][1])


        new_grid = create_ranked_megagrid_from_tuple_list(ranked_tuple_list, self, rank_name, size = size)


        self.inner_sizer.Add(new_grid, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(self.inner_sizer)
        self.sizer.Add(self, 1, wx.EXPAND|wx.ALL)
        ##
        self.spreadsheet = new_grid
        self.spreadsheet.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, lambda event: self.addStockToResearchPage(event), self.spreadsheet)


        ######################################

        self.clear_button.Show()
        self.sort_button.Show()
        self.sort_drop_down.Show()
        self.rank_button.Show()
        self.rank_drop_down.Show()


        print line_number(), "rankStocks done!"
        self.spreadsheet.Show()

    def updateAdditionalData(self, event):
        ticker_list = []
        for stock in config.RANK_PAGE_ALL_RELEVANT_STOCKS:
            ticker_list.append(stock.symbol)
        scrape.scrape_all_additional_data_prep(ticker_list)

        self.createSpreadSheet(stock_list = config.RANK_PAGE_ALL_RELEVANT_STOCKS)

    def clearGrid(self, event):
        confirm = wx.MessageDialog(None,
                                   "You are about to clear this grid.",
                                   'Are you sure?',
                                   wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Clear"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        confirm.Destroy()
        if yesNoAnswer != wx.ID_YES:
            return

        print line_number(), "Clearing the Grid"

        config.RANK_PAGE_ALL_RELEVANT_STOCKS = []
        self.full_attribute_list = []
        self.relevant_attribute_list = []

        self.full_ticker_list = []
        self.held_ticker_list = []

        self.createUnrankedSpreadsheet()

        self.clear_button.Hide()
        self.sort_button.Hide()
        self.sort_drop_down.Hide()

    def refreshScreens(self, event):
        self.drop_down.Hide()
        self.drop_down.Destroy()

        self.accounts_drop_down.Hide()
        self.accounts_drop_down.Destroy()

        time.sleep(2)

        db.load_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST()
        self.existing_screen_name_list = []
        if config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST:
            self.existing_screen_name_list = [i[0] for i in reversed(config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST)]
        self.drop_down = wx.ComboBox(self,
                                     pos=(305, 6),
                                     choices=self.existing_screen_name_list,
                                     style = wx.TE_READONLY
                                     )



        self.portfolio_name_tuple_list = []
        for i in range(len(config.PORTFOLIO_NAMES)):
            tuple_to_append = [config.PORTFOLIO_NAMES[i], (i+1)]
            self.portfolio_name_tuple_list.append(tuple_to_append)
            print line_number(), self.portfolio_name_tuple_list

        self.accounts_drop_down = wx.ComboBox(self,
                                     pos=(305, 31),
                                     choices=config.PORTFOLIO_NAMES,
                                     style = wx.TE_READONLY
                                     )
    def loadScreen(self, event):
        selected_screen_name = self.drop_down.GetValue()
        try:
            saved_screen = db.load_named_screen(selected_screen_name)
        except Exception, exception:
            print line_number(), exception
            error = wx.MessageDialog(self,
                                     "Something went wrong. This file doesn't seem to exist.",
                                     'Error: File Does Not Exist',
                                     style = wx.ICON_ERROR
                                     )
            error.ShowModal()
            error.Destroy()
            return

        self.currently_viewed_screen = selected_screen_name

        possibly_remove_dead_stocks = []
        for stock in saved_screen:
            if not stock:
                possibly_remove_dead_stocks.append(stock)
                print line_number(), "One of the stocks in this screen does not appear to exist."
            elif stock not in config.RANK_PAGE_ALL_RELEVANT_STOCKS:
                #print line_number(), stock.symbol, "added to config.RANK_PAGE_ALL_RELEVANT_STOCKS"
                config.RANK_PAGE_ALL_RELEVANT_STOCKS.append(stock)
            else:
                print line_number(), stock.symbol, "skipped"
        self.createUnrankedSpreadsheet()


    def loadAccount(self, event):
        selected_account_name = self.accounts_drop_down.GetValue()
        tuple_not_found = True
        for this_tuple in self.portfolio_name_tuple_list:
            if selected_account_name == this_tuple[0]:
                tuple_not_found = False
                try:
                    saved_account = db.load_portfolio_object(id_number = this_tuple[1])
                except Exception, exception:
                    print line_number(), exception
                    error = wx.MessageDialog(self,
                                             "Something went wrong. This file doesn't seem to exist.",
                                             'Error: File Does Not Exist',
                                             style = wx.ICON_ERROR
                                             )
                    error.ShowModal()
                    error.Destroy()
                    return
        if tuple_not_found:
            error = wx.MessageDialog(self,
                                     "Something went wrong. This data doesn't seem to exist.",
                                     'Error: Data Does Not Exist',
                                     style = wx.ICON_ERROR
                                     )
            error.ShowModal()
            error.Destroy()
            return

        for ticker in saved_account.stock_shares_dict:
            stock = utils.return_stock_by_symbol(ticker)

            if stock not in config.RANK_PAGE_ALL_RELEVANT_STOCKS:
                config.RANK_PAGE_ALL_RELEVANT_STOCKS.append(stock)

            if str(stock.symbol) not in self.held_ticker_list:
                self.held_ticker_list.append(str(stock.symbol))
            if str(stock.symbol) not in self.full_ticker_list:
                self.full_ticker_list.append(str(stock.symbol))

        self.createUnrankedSpreadsheet()


    def sortStocks(self, event):
        sort_field = self.sort_drop_down.GetValue()
        do_not_sort_reversed = config.RANK_PAGE_ATTRIBUTES_THAT_DO_NOT_SORT_REVERSED
        if sort_field in do_not_sort_reversed:
            reverse_var = False
        else:
            reverse_var = True

        num_stock_value_list = []
        str_stock_value_list = []
        incompatible_stock_list = []
        for stock in config.RANK_PAGE_ALL_RELEVANT_STOCKS:
            try:
                val = getattr(stock, sort_field)
                try:
                    float_val = float(val.replace("%",""))
                    rank_tuple = Ranked_Tuple_Reference(float_val, stock)
                    num_stock_value_list.append(rank_tuple)
                except:
                    rank_tuple = Ranked_Tuple_Reference(val, stock)
                    str_stock_value_list.append(rank_tuple)
            except Exception, exception:
                #print line_number(), exception
                rank_tuple = Ranked_Tuple_Reference(None, stock)
                incompatible_stock_list.append(rank_tuple)

        num_stock_value_list.sort(key = lambda x: x.value, reverse=reverse_var)

        str_stock_value_list.sort(key = lambda x: x.value)

        incompatible_stock_list.sort(key = lambda x: x.stock.symbol)

        sorted_tuple_list = num_stock_value_list + str_stock_value_list + incompatible_stock_list

        self.createRankedSpreadsheet(sorted_tuple_list, sort_field)

        self.sort_drop_down.SetStringSelection(sort_field)

    def addStockToResearchPage(self, event):
        row = event.GetRow()
        col = event.GetCol()
        if int(col) == self.ticker_col:
            ticker = self.spreadsheet.GetCellValue(row, col)
            utils.add_ticker_to_research_page(str(ticker))

class CustomAnalysisMetaPage(Tab):
    def __init__(self, parent):
        self.title = "Custom Analysis"
        self.uid = config.CUSTOM_ANALYSE_META_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)
        ####
        personal_analyse_panel = wx.Panel(self, -1, pos=(0,5), size=( wx.EXPAND, wx.EXPAND))
        meta_analyse_notebook = wx.Notebook(personal_analyse_panel)

        self.user_created_function_page_triples = meta.return_custom_analysis_function_triple()
        self.user_created_function_page_triples.sort(key = lambda x: x.doc)
        # print line_number()
        # for triple in self.user_created_function_page_triples:
        #    for attribute in dir(triple):
        #        if not attribute.startswith("_"):
        #            print line_number(), getattr(triple, attribute)
        for triple in self.user_created_function_page_triples:
            self.this_page = CustomAnalysisPage(meta_analyse_notebook, triple, self.user_created_function_page_triples.index(triple) + 1)
            doc_string = triple.doc
            function_name = triple.name
            # name custom analysis page
            if doc_string:
                self.this_page.title = doc_string
            elif len(function_name) < 30:
                self.this_page.title = function_name
            else:
                self.this_page.title = "Custom Analysis " + str(self.user_created_function_page_triples.index(triple) + 1)
            meta_analyse_notebook.AddPage(self.this_page, self.this_page.title)



        sizer2 = wx.BoxSizer()
        sizer2.Add(meta_analyse_notebook, 1, wx.EXPAND)
        self.SetSizer(sizer2)

class CustomAnalysisPage(Tab):
    def __init__(self, parent, function_triple, page_index):
        self.title = None
        self.parent = parent
        wx.Panel.__init__(self, parent)
        self.doc_string = function_triple.doc
        self.function_name = function_triple.name
        self.custom_spreadsheet_builder = function_triple.function

        self.page_index = page_index
        self.panel_name = None

        self.sizer = wx.FlexGridSizer(rows=1, cols=2, hgap = 1, vgap = 0)
        self.ticker_sizer = wx.BoxSizer(wx.VERTICAL)
        self.grid_sizer = wx.BoxSizer(wx.VERTICAL)

        self.ticker_sizer.AddSpacer(config.CUSTOM_ANALYSIS_SPREADSHEET_SIZE_POSITION_TUPLE[1][1])
        self.grid_sizer.AddSpacer(config.CUSTOM_ANALYSIS_SPREADSHEET_SIZE_POSITION_TUPLE[1][1])

        self.sizer.Add(self.ticker_sizer, 0, wx.BOTTOM|wx.EXPAND)
        self.sizer.Add(self.grid_sizer, 1, wx.ALL|wx.EXPAND)

        self.sizer.AddGrowableRow(0, 1)
        self.sizer.SetFlexibleDirection(wx.VERTICAL)
        self.sizer.AddGrowableCol(1, 1)
        self.sizer.SetFlexibleDirection(wx.BOTH)

        self.SetSizer(self.sizer)


        #self.inner_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #self.inner_sizer.AddSpacer(config.CUSTOM_ANALYSIS_SPREADSHEET_SIZE_POSITION_TUPLE[1][0])


        if self.doc_string:
            self.panel_name = self.doc_string
        elif len(self.function_name) < 30:
            self.panel_name = self.function_name
        else:
            self.panel_name = "Custom Analysis " + str(self.page_index)
        welcome_page_text = wx.StaticText(self, -1,
                             self.panel_name,
                             (10,10)
                             )

        self.refresh_screen_button = wx.Button(self, label="refresh", pos=(110,5), size=(-1,-1))
        self.refresh_screen_button.Bind(wx.EVT_BUTTON, self.refreshScreens, self.refresh_screen_button)

        self.load_screen_button = wx.Button(self, label="add screen", pos=(200,5), size=(-1,-1))
        self.load_screen_button.Bind(wx.EVT_BUTTON, self.loadScreen, self.load_screen_button)

        self.load_portfolio_button = wx.Button(self, label="add account", pos=(191,30), size=(-1,-1))
        self.load_portfolio_button.Bind(wx.EVT_BUTTON, self.loadAccount, self.load_portfolio_button)

        self.existing_screen_name_list = []
        if config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST:
            self.existing_screen_name_list = [i[0] for i in reversed(config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST)] # add conditional to remove old screens
        self.screen_drop_down = wx.ComboBox(self,
                                     pos=(305, 6),
                                     choices=self.existing_screen_name_list,
                                     style = wx.TE_READONLY
                                     )


        self.portfolio_name_tuple_list = []
        for i in range(len(config.PORTFOLIO_NAMES)):
            tuple_to_append = [config.PORTFOLIO_NAMES[i], (i+1)]
            self.portfolio_name_tuple_list.append(tuple_to_append)
            #print line_number(), self.portfolio_name_tuple_list

        self.accounts_drop_down = wx.ComboBox(self,
                                     pos=(305, 31),
                                     choices=config.PORTFOLIO_NAMES,
                                     style = wx.TE_READONLY
                                     )


        self.clear_button = wx.Button(self, label="clear", pos=(840,31), size=(-1,-1))
        self.clear_button.Bind(wx.EVT_BUTTON, self.clearSpreadsheet, self.clear_button)
        self.clear_button.Hide()


        self.fade_opacity = 255
        self.custom_spreadsheet = None

        self.ticker_input = wx.TextCtrl(self, -1,
                                   "",
                                   (805, 8),
                                   style=wx.TE_PROCESS_ENTER
                                   )
        self.ticker_input.SetHint("ticker")
        self.ticker_input.Bind(wx.EVT_TEXT_ENTER, self.addOneStock)

        self.add_one_stock_button = wx.Button(self,
                                          label="Add stock:",
                                          pos=(710,5),
                                          size=(-1,-1)
                                          )
        self.add_one_stock_button.Bind(wx.EVT_BUTTON, self.addOneStock, self.add_one_stock_button)

        self.add_all_stocks_button = wx.Button(self,
                                          label="Add all stocks",
                                          pos=(710,31),
                                          size=(-1,-1)
                                          )
        self.add_all_stocks_button.Bind(wx.EVT_BUTTON, self.loadAllStocks, self.add_all_stocks_button)

        self.analyse = wx.Button(self,
                                          label="Analyse",
                                          pos=(500,31),
                                          size=(-1,-1)
                                          )
        self.analyse.Bind(wx.EVT_BUTTON, self.loadCustomSpreadsheet, self.analyse)
        self.analyse.Hide()


        self.all_stocks_currently_included = []

        self.ticker_display = None
        self.screen_grid = None

        print line_number(), self.panel_name + " loaded"


    def addOneStock(self, event):
        ticker = self.ticker_input.GetValue()
        if str(ticker) == "ticker" or not ticker:
            return
        stock = utils.return_stock_by_symbol(ticker)
        if stock is None:
            print line_number(), "Error: Stock %s doesn't appear to exist" % ticker
            return
        if stock in self.all_stocks_currently_included:
            # it's already included
            return
        self.all_stocks_currently_included.append(stock)
        self.showStocksCurrentlyUsed()
        self.ticker_input.SetValue("")

    def clearSpreadsheet(self, event):
        self.all_stocks_currently_included = []
        self.ticker_input.SetValue("")
        try:
            self.ticker_display.Destroy()
        except Exception, e:
            print line_number(), e
        try:
            self.screen_grid.Destroy()
        except Exception, e:
            print line_number(), e
        self.clear_button.Hide()
        self.analyse.Hide()

    def loadAllStocks(self, event):
        self.all_stocks_currently_included = utils.return_all_stocks()
        self.showStocksCurrentlyUsed(self.all_stocks_currently_included)

    def showStocksCurrentlyUsed(self, stock_list = None):
        if not stock_list and not self.all_stocks_currently_included:
            return

        try:
            self.ticker_display.Destroy()
        except Exception, e:
            print line_number(), e

        if not stock_list:
            stock_list = self.all_stocks_currently_included
        stock_list.sort(key = lambda x: x.symbol)
        ticker_list_massive_str = ""
        for stock in stock_list:
            ticker_list_massive_str += stock.symbol
            ticker_list_massive_str += "\n"
        height_offset = config.CUSTOM_ANALYSIS_SPREADSHEET_SIZE_POSITION_TUPLE[1][1]
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            #print line_number(), width, height
            height = height - height_offset - (config.VERTICAL_OFFSET_PER_TAB * 3) # find the difference between the Frame and the grid size
        except Exception, e:
            print line_number(), e
        #print line_number()
        #pp.pprint(config.GLOBAL_STOCK_DICT)
        self.ticker_display = wx.TextCtrl(self, -1,
                                    ticker_list_massive_str,
                                    (3, height_offset),
                                    size = (100, height),
                                    style = wx.TE_READONLY | wx.TE_MULTILINE ,
                                    )
        self.ticker_sizer.Add(self.ticker_display, 1, wx.BOTTOM|wx.EXPAND)
        self.ticker_display.Show()
        self.analyse.Show()
        self.clear_button.Show()


    def refreshScreens(self, event):
        self.screen_drop_down.Hide()
        self.screen_drop_down.Destroy()

        # Why did i put this here? Leave a note next time moron...
        time.sleep(2)

        self.existing_screen_name_list = [i[0] for i in reversed(config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST)]


        self.screen_drop_down = wx.ComboBox(self,
                                     pos=(305, 6),
                                     choices=self.existing_screen_name_list,
                                     style = wx.TE_READONLY
                                     )

    def loadScreen(self, event):
        selected_screen_name = self.screen_drop_down.GetValue()
        try:
            screen_stock_list = db.load_named_screen(selected_screen_name)
        except Exception, exception:
            print line_number(), exception
            error = wx.MessageDialog(self,
                                     "Something went wrong. This file doesn't seem to exist.",
                                     'Error: File Does Not Exist',
                                     style = wx.ICON_ERROR
                                     )
            error.ShowModal()
            error.Destroy()
            return
        for stock in screen_stock_list:
            if stock:
                if stock not in self.all_stocks_currently_included:
                    self.all_stocks_currently_included.append(stock)
        self.showStocksCurrentlyUsed()

    def loadCustomSpreadsheet(self, event):
        # notes: so here, we have a 2d grid, so it seems reasonable, that a tuple would
        # function quite well for position. Perhaps a sort of limiting row, where everything
        # below it dumps data. Now, the x dimention is fixed, so that's easy to deal with,
        # the y dimention is not fixed, so dealing with that may be tricky. Maybe use
        # data types, like fixed-attribute, or custome attibute, and have custom come first
        # allow iterating at the attribute terminus

        if not self.all_stocks_currently_included:
            return

        try:
            self.custom_spreadsheet.Destroy()
        except Exception, e:
            print line_number(), e

        list_of_spreadsheet_cells = process_user_function.process_custom_analysis_spreadsheet_data(self.all_stocks_currently_included, self.custom_spreadsheet_builder)
        #print line_number(), list_of_spreadsheet_cells

        #You need this code to resize
        size = config.CUSTOM_ANALYSIS_SPREADSHEET_SIZE_POSITION_TUPLE[0]
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            print line_number(), width, height
            size = (width-165, height-200) # find the difference between the Frame and the grid size
        except Exception, e:
            print line_number(), e
        self.inner_inner_sizer = None


        new_grid = self.create_custom_analysis_spread_sheet(list_of_spreadsheet_cells, size = size)

        self.grid_sizer.Add(new_grid, 1, wx.ALL|wx.EXPAND)
        ##
        self.custom_spreadsheet = new_grid

        self.custom_spreadsheet.Show()

    def create_custom_analysis_spread_sheet(self,
        cell_list,
        held_ticker_list = [] # not used currently
        , size = config.CUSTOM_ANALYSIS_SPREADSHEET_SIZE_POSITION_TUPLE[0]
        , position = config.CUSTOM_ANALYSIS_SPREADSHEET_SIZE_POSITION_TUPLE[1]
        , enable_editing = False
        ):

        #print line_number()
        #pp.pprint(cell_list)

        num_rows = 0
        num_columns = 0
        for cell in cell_list:
            if cell.row > num_rows:
                num_rows = cell.row
            if cell.col > num_columns:
                num_columns = cell.col

        num_columns += 1 # check and see if it's ordinal or cardinal
        num_rows += 1   # ditto

        self.screen_grid = wx.grid.Grid(self, -1, size=size, pos=position)
        self.screen_grid.CreateGrid(num_rows, num_columns)
        self.screen_grid.EnableEditing(enable_editing)


        # fill in grid
        for cell in cell_list:
            self.screen_grid.SetCellValue(cell.row, cell.col, str(cell.text))
            # Add color if relevant
            if cell.background_color is not None:
                self.screen_grid.SetCellBackgroundColour(cell.row, cell.col, cell.background_color)
            if cell.text_color is not None:
                self.screen_grid.SetCellTextColour(cell.row, cell.col, cell.text_color)
            if cell.col_title is not None:
                self.screen_grid.SetColLabelValue(cell.col, cell.col_title)
            if cell.row_title is not None:
                self.screen_grid.SetRowLabelValue(cell.row, cell.row_title)
            if cell.align_right:
                self.screen_grid.SetCellAlignment(cell.row, cell.col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)

        self.screen_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, lambda event: self.addStockToResearchPage(event), self.screen_grid)
        self.screen_grid.AutoSizeColumns()
        # deal with colors and shit later, also held stocklist
        return self.screen_grid

    def addStockToResearchPage(self, event):
        row = event.GetRow()
        col = event.GetCol()
        # is there a way to draw out which cells are ticker cells using the function provided by users? Currently unsure.
        ticker = self.screen_grid.GetCellValue(row, col)
        utils.add_ticker_to_research_page(str(ticker))

    def loadAccount(self, event):
        account_name = self.accounts_drop_down.GetValue()
        account_index = config.DATA_ABOUT_PORTFOLIOS[1].index(account_name)# this needs to be fixed,
        # adding one to the index for no reason is dumb
        account_index = str(account_index + 1)
        portfolio_obj = config.PORTFOLIO_OBJECTS_DICT.get(account_index)
        for ticker in portfolio_obj.stock_shares_dict:
            stock = utils.return_stock_by_symbol(ticker)
            if stock:
                if stock not in self.all_stocks_currently_included:
                    self.all_stocks_currently_included.append(stock)
        self.showStocksCurrentlyUsed()

#### Research
class ResearchPage(Tab):
    def __init__(self, parent):
        self.title = "Research"
        self.panel_name = "Research"
        self.uid = config.RESEARCH_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)
        welcome_page_text = wx.StaticText(self, -1,
                             self.title,
                             (10,10)
                             )

        self.ticker_input = wx.TextCtrl(self, -1,
                                   "",
                                   (100, 8),
                                   style=wx.TE_PROCESS_ENTER
                                   )
        self.ticker_input.SetHint("ticker")
        self.ticker_input.Bind(wx.EVT_TEXT_ENTER, self.addStock, self.ticker_input)

        self.add_stock_button = wx.Button(self,
                                          label="add",
                                          pos=(200,5),
                                          size=(-1,-1)
                                          )
        self.add_stock_button.Bind(wx.EVT_BUTTON, self.addStock, self.add_stock_button)
        self.remove_stock_button = wx.Button(self,
                                          label="remove",
                                          pos=(300,5),
                                          size=(-1,-1)
                                          )
        self.remove_stock_button.Bind(wx.EVT_BUTTON, self.confirmRemove, self.remove_stock_button)

        self.stock_list = []
        self.rows_dict = {}

        self.development_sample_stocks = ['googl', 'aapl', 'msft', 'gs', 'att', 'luv']
        self.bingbong = wx.Button(self,
                                  label="Load examples for development",
                                  pos=(400,5),
                                  size=(-1,-1)
                                  )
        self.bingbong.Bind(wx.EVT_BUTTON, self.development_examples_load_into_page, self.bingbong)


        print line_number(), "ResearchPage loaded"
    def development_examples_load_into_page(self, event):
        for ticker in self.development_sample_stocks:
            utils.add_ticker_to_research_page(ticker)


    def addStock(self, event, ticker=None):
        if not ticker:
            ticker = self.ticker_input.GetValue()

        if str(ticker) == "ticker" or not ticker:
            return

        stock = utils.return_stock_by_symbol(ticker)
        if not stock:
            print line_number(), "Stock with symbol %s does not appear to exist" % ticker.upper()
            return

        self.stock_list.append(stock)
        self.stock_list = utils.remove_list_duplicates(self.stock_list)
        # remember to sort by symbol at the end of adding a stock!
        self.stock_list.sort(key=lambda x: x.ticker)


        self.generateShownStockList("event")
        self.ticker_input.SetValue("")

    def confirmRemove(self, event):
        ticker = self.ticker_input.GetValue()

        if str(ticker) == "ticker" or not ticker:
            return

        stock = utils.return_stock_by_symbol(ticker)
        if not stock:
            print line_number(), "Stock with symbol %s does not appear to exist" % ticker.upper()
            return

        confirm = wx.MessageDialog(None,
                                   "You are about to remove %s from your research list. Are you sure you want to remove %s?" % (stock.ticker, stock.ticker),
                                   'Remove %s' % stock.ticker,
                                   style = wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Remove"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        confirm.Destroy()

        if yesNoAnswer == wx.ID_YES:
            self.removeStock(stock)

    def removeStock(self, stock):
        self.stock_list.remove(stock)
        self.generateShownStockList("event")
        self.ticker_input.SetValue("")

    def openButtonURL(self, event, row_obj, index):
        index = str(index)
        button_dict = getattr(row_obj, "button_dict" + index)
        url = button_dict.get("url")
        lambda_function = button_dict.get("lambda_function")

        # Replace ticker
        try:
            stock = row_obj.stock
        except:
            stock = None
        if stock:
            ticker = stock.ticker
            firm_name = stock.firm_name.replace(" ", "%20")
            exchange = utils.return_stocks_exchange_if_possible(stock)
            url = url % {"ticker": ticker, "exchange": exchange, "firm_name": firm_name}
        if lambda_function:
            url = lambda_function(url)
        # Replace exchange if possible
        webbrowser.open(url, new=1, autoraise=True)

    def openWebsiteOnButtonClick(self, event, row_obj):
        url = utils.return_stocks_website_if_possible(row_obj.stock)
        webbrowser.open(url, new=1, autoraise=True)

    def generateGeneralResearchRow(self):
        row_object = ResearchPageRowDataList()
        initial_button_vertical_offset = 44
        initial_button_horizontal_offset = 60
        text_additional_vertical_offset = 6
        added_width = 0

        row_object.ticker_textctrl = wx.StaticText(self, -1,
                             "General:",
                             (10, initial_button_vertical_offset + text_additional_vertical_offset)
                             )

        for button_dict in config.GENERAL_RESEARCH_PAGE_DICT_LIST:
            button = None
            lambda_function = None
            button_index = config.GENERAL_RESEARCH_PAGE_DICT_LIST.index(button_dict)
            button_width = button_dict.get("width")
            if not button_width:
                button_width = -1
            button = wx.Button(self,
                          label=str(button_dict.get("button_text")),
                          pos=(initial_button_horizontal_offset + added_width, (button_index) + initial_button_vertical_offset),
                          size=(button_width, -1)
                          )
            added_width += button.GetSize()[0]

            lambda_function = button_dict.get("lambda_function")
            if lambda_function:
                setattr(row_object, "lambda_function", lambda_function)

            button.Bind(wx.EVT_BUTTON, lambda event, row_obj = row_object, index = button_index: self.openButtonURL(event, row_obj, index), button)
            button_name_for_row_object = "button" + str(button_index) + ''.join(char for char in button_dict.get("button_text") if char.isalnum())
            setattr(row_object, button_name_for_row_object, button)

            button_dict_name = "button_dict" + str(button_index)
            setattr(row_object, button_dict_name, button_dict)

        return row_object



    def generateStockRow(self, index, stock=None):
        row_object = ResearchPageRowDataList()
        website_button_horizontal_offset = 60
        initial_button_horizontal_offset = 144
        initial_button_vertical_offset = 80
        text_additional_vertical_offset = 6
        second_line_text_additional_offset = 18
        vertical_offset_per_stock = 40
        added_width = 0

        if stock:
            row_object.stock = stock
            row_object.ticker_textctrl = wx.StaticText(self, -1,
                             stock.ticker,
                             (10, (index*vertical_offset_per_stock) + initial_button_vertical_offset + text_additional_vertical_offset)
                             )
            if utils.return_stocks_website_if_possible(stock):
                row_object.website_button = wx.Button(self,
                              label="website",
                              pos=(website_button_horizontal_offset,(index*vertical_offset_per_stock) + initial_button_vertical_offset),
                              size=(-1,-1)
                              )
                row_object.website_button.Bind(wx.EVT_BUTTON, lambda event, row_obj = row_object: self.openWebsiteOnButtonClick(event, row_obj), row_object.website_button)

            row_object.firm_name_textctrl = wx.StaticText(self, -1,
                             stock.firm_name,
                             (10, (index*vertical_offset_per_stock) + initial_button_vertical_offset + text_additional_vertical_offset + second_line_text_additional_offset),
                             size = (100, -1)
                             )
            for button_dict in config.RESEARCH_PAGE_DICT_LIST:
                button = None
                lambda_function = None
                button_index = config.RESEARCH_PAGE_DICT_LIST.index(button_dict)
                button_width = button_dict.get("width")
                if not button_width:
                    button_width = -1
                button = wx.Button(self,
                              label=str(button_dict.get("button_text")),
                              pos=(initial_button_horizontal_offset + added_width, (index*vertical_offset_per_stock) + initial_button_vertical_offset),
                              size=(button_width, -1)
                              )
                added_width += button.GetSize()[0]

                lambda_function = button_dict.get("lambda_function")
                if lambda_function:
                    setattr(row_object, "lambda_function", lambda_function)

                button.Bind(wx.EVT_BUTTON, lambda event, row_obj = row_object, index = button_index: self.openButtonURL(event, row_obj, index), button)
                button_name_for_row_object = "button" + str(button_index) + ''.join(char for char in button_dict.get("button_text") if char.isalnum())
                setattr(row_object, button_name_for_row_object, button)

                button_dict_name = "button_dict" + str(button_index)
                setattr(row_object, button_dict_name, button_dict)

            self.rows_dict[str(index)] = row_object
        else:
            row_object = None

        return row_object

    def generateShownStockList(self, event):
        for i in range(len(self.rows_dict)):
            row_obj = self.rows_dict.get(str(i))
            for attribute in dir(row_obj):
                if not attribute.startswith("__"):
                    try:
                        wx_obj = getattr(row_obj, attribute)
                        wx_obj.Destroy()
                    except:
                        pass
            del row_obj
        self.rows_dict = {}

        for index, stock in enumerate(self.stock_list):
            row_obj = self.generateStockRow(index, stock=stock)





####

class SalePrepPage(Tab):
    def __init__(self, parent):
        self.title = "Sale Prep"
        self.uid = config.SALE_PREP_PAGE_UNIQUE_ID
        self.parent = parent
        wx.Panel.__init__(self, parent)
        trade_page_text = wx.StaticText(self, -1,
                             "Sale Prep",
                             (10,10)
                             )
        self.ticker_list = []
        self.checkbox_list = []
        self.rows_dict = {}

        for i in range(config.NUMBER_OF_PORTFOLIOS):
            portfolio_exists = config.PORTFOLIO_OBJECTS_DICT.get(str(i+1))
            if not portfolio_exists:
                continue

            horizontal_offset = 0
            if i>=5:
                horizontal_offset = 200
            checkbox_to_add = wx.CheckBox(self, -1,
                                          config.PORTFOLIO_NAMES[i],
                                          pos=((600+ horizontal_offset), (16*i)),
                                          size=(-1,-1)
                                          )
            checkbox_to_add.SetValue(True)
            self.checkbox_list.append(checkbox_to_add)

        line = wx.StaticLine(self, -1, pos=(0,83), size=(1000,-1))

        refresh_button = wx.Button(self, label="Clear and Refresh Spreadsheet", pos=(110,5), size=(-1,-1))
        refresh_button.Bind(wx.EVT_BUTTON, self.spreadSheetFill, refresh_button)

        self.load_new_account_data_button = wx.Button(self, label="Refresh Accounts Data and Spreadsheet", pos=(110,30), size=(-1,-1))
        self.load_new_account_data_button.Bind(wx.EVT_BUTTON, self.refreshAccountData, self.load_new_account_data_button)

        self.save_button = wx.Button(self, label="Export for Trade Window", pos=(420,50), size=(-1,-1))
        self.save_button.Bind(wx.EVT_BUTTON, self.exportSaleCandidates, self.save_button)
        self.save_button.Hide()

        self.saved_text = wx.StaticText(self, -1,
                                        "Data is now in memory.",
                                        (433,55)
                                        )
        self.saved_text.Hide()

        self.commission = config.DEFAULT_COMMISSION

        self.set_spreadsheet_values()
        self.grid = None
        for i in range(len(self.checkbox_list)):
            box = self.checkbox_list[i]
            if box:
                is_checked = box.GetValue()
                #print line_number(), is_checked
                if is_checked:
                    self.spreadSheetFill('event')
                    break



        print line_number(), "SalePrepPage loaded"

    def cell_is_writable(self, row_num, col_num):
        default_rows = config.DEFAULT_ROWS_ON_SALE_PREP_PAGE

        if ((row_num >= default_rows) and col_num in [self.num_of_shares_cell.col, self.percent_of_shares_cell.col]):
            return True
        elif (row_num, col_num) == (3, self.carryover_input_cell.col):
            return True
        else:
            return False

    def set_spreadsheet_values(self):
        # colors
        self.carryover_input_color_hex = "#C5DBCA"
        self.num_of_shares_input_color_hex = "#CFE8FC"
        self.percentage_of_shares_input_color_hex = "#CFFCEF"
        self.dark_cell_color_hex = "#333333"




        # row 5
        self.first_cell                     = SpreadsheetCell(row = 5, col = 0, text = "")

        self.num_of_shares_cell             = SpreadsheetCell(row = 4, col = 1, text = "# of shares", align_center = True)
        self.num_of_shares_cell_2           = SpreadsheetCell(row = 5, col = 1, text = "to sell",     align_center = True)

        self.percent_of_shares_cell         = SpreadsheetCell(row = 4, col = 2, text = "%" + " of shares", align_center = True)
        self.percent_of_shares_cell_2       = SpreadsheetCell(row = 5, col = 2, text = "to sell", align_center = True)

        self.ticker_cell                    = SpreadsheetCell(row = 5, col = 3, text = "Ticker")
        self.syntax_check_cell              = SpreadsheetCell(row = 5, col = 4, text = "")#Syntax Check")
        self.name_cell                      = SpreadsheetCell(row = 5, col = 5, text = "Name")

        self.sale_check_cell                = SpreadsheetCell(row = 4, col = 6, text = "Sale", align_center = True)
        self.sale_check_cell_2              = SpreadsheetCell(row = 5, col = 6, text = "Check", align_center = True)

        self.number_of_shares_copy_cell     = SpreadsheetCell(row = 4, col = 7, text = "# of shares", align_center = True)
        self.number_of_shares_copy_cell_2   = SpreadsheetCell(row = 5, col = 7, text = "to sell", align_center = True)

        self.percent_of_shares_copy_cell    = SpreadsheetCell(row = 4, col = 8, text = "%" + " of shares", align_center = True)
        self.percent_of_shares_copy_cell_2  = SpreadsheetCell(row = 5, col = 8, text = "to sell", align_center = True)

        self.total_shares_cell              = SpreadsheetCell(row = 4, col = 9, text = "Total # of", align_center = True)
        self.total_shares_cell_2            = SpreadsheetCell(row = 5, col = 9, text = "shares", align_center = True)

        self.price_cell                     = SpreadsheetCell(row = 5, col = 10, text = "Price")
        self.sale_value_cell                = SpreadsheetCell(row = 5, col = 11, text = "Sale Value")

        self.commission_cell                = SpreadsheetCell(row = 4, col = 12, text = "Commission loss", align_center = True)
        self.commission_cell_2              = SpreadsheetCell(row = 5, col = 12, text = "($%.2f/trade)" % float(self.commission), align_center = True)
        self.cost_basis_cell                = SpreadsheetCell(row = 4, col = 13, text = "Cost basis", align_center = True)
        self.cost_basis_cell_2              = SpreadsheetCell(row = 5, col = 13, text = "per share", align_center = True)
        self.capital_gains_cell             = SpreadsheetCell(row = 4, col = 14, text = "Capital", align_center = True)
        self.capital_gains_cell_2           = SpreadsheetCell(row = 5, col = 14, text = "Gains", align_center = True)
        self.adjusted_cap_gains_cell        = SpreadsheetCell(row = 4, col = 15, text = "Adjusted Capital Gains", align_center = True)
        self.adjusted_cap_gains_cell_2      = SpreadsheetCell(row = 5, col = 15, text = "(including carryovers)", align_center = True)

        self.row_four_cell_list = [
            self.num_of_shares_cell,
            self.percent_of_shares_cell,
            self.sale_check_cell,
            self.number_of_shares_copy_cell,
            self.percent_of_shares_copy_cell,
            self.total_shares_cell,
            self.commission_cell,
            self.cost_basis_cell,
            self.capital_gains_cell,
            self.adjusted_cap_gains_cell,

            ]
        self.row_five_cell_list = [
            self.first_cell,

            self.num_of_shares_cell_2,
            self.percent_of_shares_cell_2,

            self.ticker_cell,
            self.syntax_check_cell,
            self.name_cell,

            self.sale_check_cell_2,
            self.number_of_shares_copy_cell_2,
            self.percent_of_shares_copy_cell_2,
            self.total_shares_cell_2,

            self.price_cell,
            self.sale_value_cell,

            self.commission_cell_2,
            self.cost_basis_cell_2,
            self.capital_gains_cell_2,
            self.adjusted_cap_gains_cell_2,

            ]

        self.total_number_of_columns = len(self.row_five_cell_list)


        # row 2
        self.carryover_text_cell = SpreadsheetCell(row = 2, col = self.adjusted_cap_gains_cell.col, text = "Input carryover loss (if any)")

        # row 3
        self.carryover_input_cell = SpreadsheetCell(row = 3, col = self.carryover_text_cell.col, text = 0., value = 0., align_right = True)

        # row 7
        self.totals_cell = SpreadsheetCell(row = 7, col = 0, text = "Totals:")


    def exportSaleCandidates(self, event):
        self.save_button.Hide()

        num_columns = self.grid.GetNumberCols()
        num_rows = self.grid.GetNumberRows()

        default_rows = config.DEFAULT_ROWS_ON_SALE_PREP_PAGE

        sell_tuple_list = [] # this will end up being a list of tuples for each stock to sell
        for column_num in range(num_columns):
            for row_num in range(num_rows):
                if not row_num >= default_rows:
                    continue
                elif column_num == self.number_of_shares_copy_cell.col:
                    not_empty = self.grid.GetCellValue(row_num, column_num)
                    error = self.grid.GetCellValue(row_num, column_num - 1) # error column is one less than stock column
                    if error != "Error":
                        error = None
                    print line_number(), not_empty
                    if not_empty and not error:
                        if int(not_empty):
                            ticker = str(self.grid.GetCellValue(row_num, self.ticker_cell.col))
                            number_of_shares_to_sell = int(self.grid.GetCellValue(row_num, self.number_of_shares_copy_cell.col))
                            sell_tuple = (ticker, number_of_shares_to_sell)
                            sell_tuple_list.append(sell_tuple)
                    elif error:
                        print line_number(), "ERROR: Could not save sell list. There are errors in quantity syntax."
                        return
        for i in sell_tuple_list:
            print line_number(), i


        # Here, i'm not sure whether to save to file or not (currently not saving to file, obviously)
        relevant_portfolios_list = []
        for i in range(len(self.checkbox_list)):
            box = self.checkbox_list[i]
            is_checked = box.GetValue()
            if is_checked:
                relevant_portfolios_list.append(config.PORTFOLIO_OBJECTS_DICT[str(i+1)])

        config.SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE= [
                                                                relevant_portfolios_list,
                                                                sell_tuple_list
                                                                ]
        print line_number(), config.SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE
        self.saved_text.Show()

        trade_page = config.GLOBAL_PAGES_DICT.get(config.TRADE_PAGE_UNIQUE_ID).obj
        trade_page.importSaleCandidates("event")

    def refreshAccountData(self, event):
        ######## Rebuild Checkbox List in case of new accounts

        for i in self.checkbox_list:
            try:
                i.Destroy()
            except Exception, exception:
                print line_number(), exception
        self.checkbox_list = []
        for i in range(config.NUMBER_OF_PORTFOLIOS):
            if not portfolio_obj:
                continue

            horizontal_offset = 0
            if i>=5:
                horizontal_offset = 200
            checkbox_to_add = wx.CheckBox(self, -1,
                                          config.PORTFOLIO_NAMES[i],
                                          pos=((600 + horizontal_offset), (16*i)),
                                          size=(-1,-1)
                                          )

            portfolio_obj = config.PORTFOLIO_OBJECTS_DICT.get(str(i+1))
            checkbox_to_add.SetValue(True)
            self.checkbox_list.append(checkbox_to_add)
        self.spreadSheetFill("event")

    def hideSaveButtonWhileEnteringData(self, event):
        # This function has been deactivated, unfortunately it causes too many false positives...

        # color = self.grid.GetCellBackgroundColour(event.GetRow(), event.GetCol())
        # print line_number(), color
        # print type(color)
        # print "---------"
        # if color != (255, 255, 255, 255):
        #   print 'it works'
        #   self.save_button.Hide()
        # event.Skip()

        pass


    def spreadSheetFill(self, event):
        try:
            self.grid.Hide() # destroying grid will throw a segmentation fault for some reason
        except Exception, exception:
            pass
            #print line_number(), exception

        relevant_portfolios_list = []
        for i in range(len(self.checkbox_list)):
            box = self.checkbox_list[i]
            is_checked = box.GetValue()
            if is_checked:
                relevant_portfolios_list.append(config.PORTFOLIO_OBJECTS_DICT[str(i+1)])

        default_columns = self.total_number_of_columns
        default_rows = config.DEFAULT_ROWS_ON_SALE_PREP_PAGE

        num_columns = default_columns
        num_rows = default_rows
        for account in relevant_portfolios_list:
            try:
                num_rows += 1 # for account name
                num_stocks = len(account.stock_shares_dict)
                num_rows += num_stocks
                #print line_number(), num_rows
            except Exception, exception:
                print line_number(), exception

        # set size for grid
        size = (800, 650)
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            print line_number(), width, height
            size = (width-20, height-128) # find the difference between the Frame and the grid size
        except Exception, e:
            print line_number(), e
        self.sizer = None
        self.inner_sizer = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer.AddSpacer(83)

        new_grid = SalePrepGrid(self, -1, size=size, pos=(0,83))
        new_grid.CreateGrid(num_rows, num_columns)
        new_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.updateGrid, new_grid)
        #You need this code to resize
        self.inner_sizer.Add(new_grid, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(self.inner_sizer)
        self.sizer.Add(self, 1, wx.EXPAND|wx.ALL)
        ##

        self.grid = new_grid

        # I deactivated this binding because it caused too much confusion if you don't click on a white square after entering data
        # self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK ,self.hideSaveButtonWhileEnteringData, self.grid)



        for column_num in range(num_columns):
            for row_num in range(num_rows):
                if not self.cell_is_writable(row_num, column_num):
                    self.grid.SetReadOnly(row_num, column_num, True)
                else: # fill in writable column number spaces
                    if column_num == self.carryover_input_cell.col:
                        self.grid.SetCellBackgroundColour(row_num, column_num, self.carryover_input_color_hex)
                    elif column_num == self.num_of_shares_cell.col:
                        self.grid.SetCellBackgroundColour(row_num, column_num, self.num_of_shares_input_color_hex)
                    elif column_num == self.percent_of_shares_cell.col:
                        self.grid.SetCellBackgroundColour(row_num, column_num, self.percentage_of_shares_input_color_hex)

        # set row 2
        self.grid.SetCellValue(self.carryover_text_cell.row, self.carryover_text_cell.col, self.carryover_text_cell.text)
        # set row 3
        self.grid.SetCellValue(self.carryover_input_cell.row, self.carryover_input_cell.col, config.locale.currency(self.carryover_input_cell.text, grouping = True))
        if self.carryover_input_cell.align_right:
            self.grid.SetCellAlignment(self.carryover_input_cell.row, self.carryover_input_cell.col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)

        # set row 7
        self.grid.SetCellValue(self.totals_cell.row, self.totals_cell.col, self.totals_cell.text)


        # set row 4 & 5
        for cell in self.row_five_cell_list + self.row_four_cell_list:
            self.grid.SetCellValue(cell.row, cell.col, cell.text)
            if cell.align_center:
                self.grid.SetCellAlignment(cell.row, cell.col, horiz = wx.ALIGN_CENTRE, vert = wx.ALIGN_BOTTOM)


        # rows 6 and 8
        for i in range(num_columns):
            self.grid.SetCellBackgroundColour(6, i, self.dark_cell_color_hex)
            self.grid.SetCellBackgroundColour(8, i, self.dark_cell_color_hex)

        # load account data
        portfolio_num = 0
        row_count = default_rows
        col_count = 0

        for account in relevant_portfolios_list:
            try:
                throw_error = account.stock_shares_dict
                # intentionally throws an error if account hasn't been imported
            except Exception as e:
                print line_number(), e, ": An account appears to not be loaded, but this isn't a problem."
                continue

            # set portfolio name
            portfolio_name = config.PORTFOLIO_NAMES[portfolio_num]
            self.grid.SetCellValue(row_count, self.first_cell.col, portfolio_name)
            self.grid.SetCellBackgroundColour(row_count, self.num_of_shares_cell.col, "white")
            self.grid.SetReadOnly(row_count, self.num_of_shares_cell.col, True)
            self.grid.SetCellBackgroundColour(row_count, self.percent_of_shares_cell.col, "white")
            self.grid.SetReadOnly(row_count, self.percent_of_shares_cell.col, True)
            portfolio_num += 1
            row_count += 1

            for ticker in sorted(account.stock_shares_dict):
                row_obj_already_exists = False
                row_obj = self.rows_dict.get(str(ticker)+str(relevant_portfolios_list.index(account)))
                if row_obj:
                    row_obj.row = row_count
                    row_obj_already_exists = True
                else:
                    quantity = account.stock_shares_dict.get(ticker)
                    stocks_last_price = None
                    sale_value = None
                    stocks_capital_gains = None


                    #print line_number()
                    #print ticker
                    # set all cell values for stock
                    stock = utils.return_stock_by_symbol(ticker)

                    if not stock:
                        print line_number(), "Stock %s does not appear to exist" % ticker
                        continue
                    # set account index cell
                    account_index_cell = SpreadsheetCell(row = row_count, col = self.first_cell.col, text = str(relevant_portfolios_list.index(account)), text_color = "white")

                    # set ticker cell
                    stocks_ticker_cell = SpreadsheetCell(row = row_count, col = self.ticker_cell.col, text = stock.symbol, stock = stock)
                    # return and set cost basis per share
                    cost_basis_per_share = utils.return_cost_basis_per_share(account, stock.symbol)
                    if cost_basis_per_share:
                        try:
                            cost_basis_per_share = str(cost_basis_per_share).replace("$", "").replace(",","")
                            if cost_basis_per_share:
                                cost_basis_per_share = float(cost_basis_per_share)
                                stocks_cost_basis_cell = SpreadsheetCell(row = row_count, col = self.cost_basis_cell.col, text = config.locale.currency(cost_basis_per_share, grouping = True), value = (cost_basis_per_share), align_right = True)
                        except Exception as e:
                            print line_number(), e
                            cost_basis_per_share = None

                    # set firm name cell
                    stocks_firm_name_cell = SpreadsheetCell(row = row_count, col = self.name_cell.col, text = stock.firm_name, value = stock.firm_name)

                    # set quantity cell
                    quantity_text = str(quantity)
                    if quantity.is_integer():
                        quantity_text = str(int(quantity))
                    stocks_quantity_cell = SpreadsheetCell(row = row_count, col = self.total_shares_cell.col, text = quantity_text, value = int(quantity), align_right = True)

                    # set last price
                    try:
                        stocks_last_price = float(utils.return_last_price_if_possible(stock))
                        stocks_last_price_cell = SpreadsheetCell(row = row_count, col = self.price_cell.col, text = config.locale.currency(stocks_last_price, grouping = True), value = stocks_last_price, align_right = True)
                    except Exception, exception:
                        print line_number(), exception

                    # set capital gains
                    if cost_basis_per_share:
                        # this needs to be set via a row dict, which may not exist on startup
                        try:
                            this_row = self.rows_dict.get(str(row_count))
                        except:
                            this_row = None
                        if this_row:
                            try:
                                sale_value = row_obj.cell_dict.get(str(self.sale_value_cell.col)).value
                            except:
                                pass
                            if sale_value is not None:
                                stocks_capital_gains = float(sale_value - cost_basis_per_share)
                                if stocks_capital_gains < 0.:
                                    stocks_capital_gains = 0.
                                    stocks_capital_gains_cell = SpreadsheetCell(row = row_count, col = self.capital_gains_cell.col, text = config.locale.currency(stocks_capital_gains, grouping = True), value = stocks_capital_gains, align_right = True)
                    # set carryover reduction
                    if self.carryover_input_cell.value:
                        if stocks_capital_gains:
                            if self.carryover_input_cell.value > stocks_capital_gains:
                                new_carryover_value = self.carryover_input_cell.value - stocks_capital_gains
                                self.carryover_input_cell.value = new_carryover_value
                                reduction = -(stocks_capital_gains)
                            else:
                                reduction = stocks_capital_gains - self.carryover_input_cell.value
                                self.carryover_input_cell.value = 0.

                            stocks_capital_gains_adjustment_cell = SpreadsheetCell(row = row_count, col = self.adjusted_cap_gains_cell.col, text = config.locale.currency(reduction, grouping = True), value = reduction)
                        else:
                            stocks_capital_gains_adjustment_cell = SpreadsheetCell(row = row_count, col = self.adjusted_cap_gains_cell.col, text = "", value = None)
                    else:
                        stocks_capital_gains_adjustment_cell = SpreadsheetCell(row = row_count, col = self.adjusted_cap_gains_cell.col, text = "", value = None)



                    # set row
                    if cost_basis_per_share and stocks_last_price and stocks_capital_gains:
                        #print line_number(), ticker, "3: cost_basis_per_share and stocks_last_price and stocks_capital_gains"
                        try:
                            this_row = self.rows_dict.get(str(stock.symbol) + str(relevant_portfolios_list.index(account)))
                        except Exception as e:
                            print line_number(), e
                        if not this_row:
                            this_row = SpreadsheetRow(row_count, name = stock.symbol, account = account, cell_dict = {})
                        this_row.cell_dict[account_index_cell.col] = account_index_cell
                        this_row.cell_dict[stocks_ticker_cell.col] = stocks_ticker_cell
                        this_row.cell_dict[stocks_firm_name_cell.col] = stocks_firm_name_cell
                        this_row.cell_dict[stocks_quantity_cell.col] = stocks_quantity_cell
                        this_row.cell_dict[stocks_cost_basis_cell.col] = stocks_cost_basis_cell
                        this_row.cell_dict[stocks_last_price_cell.col] = stocks_last_price_cell
                        this_row.cell_dict[stocks_capital_gains_cell.col] = stocks_capital_gains_cell
                        this_row.cell_dict[stocks_capital_gains_adjustment_cell.col] = stocks_capital_gains_adjustment_cell

                    elif cost_basis_per_share and stocks_last_price:
                        #print line_number(), ticker, "2: cost_basis_per_share and stocks_last_price"
                        try:
                            this_row = self.rows_dict.get(str(stock.symbol) + str(relevant_portfolios_list.index(account)))
                        except Exception as e:
                            print line_number(), e
                        if not this_row:
                            this_row = SpreadsheetRow(row_count, name = stock.symbol, account = account, cell_dict = {})
                        this_row.cell_dict[account_index_cell.col] = account_index_cell
                        this_row.cell_dict[stocks_ticker_cell.col] = stocks_ticker_cell
                        this_row.cell_dict[stocks_firm_name_cell.col] = stocks_firm_name_cell
                        this_row.cell_dict[stocks_quantity_cell.col] = stocks_quantity_cell
                        this_row.cell_dict[stocks_cost_basis_cell.col] = stocks_cost_basis_cell
                        this_row.cell_dict[stocks_last_price_cell.col] = stocks_last_price_cell
                        #print line_number(), this_row.cell_dict

                    elif cost_basis_per_share:
                        #print line_number(), ticker, "cost_basis_per_share"
                        try:
                            this_row = self.rows_dict.get(str(stock.symbol) + str(relevant_portfolios_list.index(account)))
                        except Exception as e:
                            print line_number(), e
                        if not this_row:
                            this_row = SpreadsheetRow(row_count, name = stock.symbol, account = account, cell_dict = {})
                        this_row.cell_dict[account_index_cell.col] = account_index_cell
                        this_row.cell_dict[stocks_ticker_cell.col] = stocks_ticker_cell
                        this_row.cell_dict[stocks_firm_name_cell.col] = stocks_firm_name_cell
                        this_row.cell_dict[stocks_quantity_cell.col] = stocks_quantity_cell
                        this_row.cell_dict[stocks_cost_basis_cell.col] = stocks_cost_basis_cell
                    elif stocks_last_price:
                        #print line_number(), ticker, "stocks_last_price"
                        try:
                            this_row = self.rows_dict.get(str(stock.symbol) + str(relevant_portfolios_list.index(account)))
                        except Exception as e:
                            print line_number(), e
                        if not this_row:
                            this_row = SpreadsheetRow(row_count, name = stock.symbol, account = account, cell_dict = {})
                        this_row.cell_dict[account_index_cell.col] = account_index_cell
                        this_row.cell_dict[stocks_ticker_cell.col] = stocks_ticker_cell
                        this_row.cell_dict[stocks_firm_name_cell.col] = stocks_firm_name_cell
                        this_row.cell_dict[stocks_quantity_cell.col] = stocks_quantity_cell
                        this_row.cell_dict[stocks_last_price_cell.col] = stocks_last_price_cell

                    else:
                        #print line_number(), ticker, "else"
                        try:
                            this_row = self.rows_dict.get(str(stock.symbol) + str(relevant_portfolios_list.index(account)))
                        except Exception as e:
                            print line_number(), e
                        if not this_row:
                            this_row = SpreadsheetRow(row_count, name = stock.symbol, account = account, cell_dict = {})
                        this_row.cell_dict[account_index_cell.col] = account_index_cell
                        this_row.cell_dict[stocks_ticker_cell.col] = stocks_ticker_cell
                        this_row.cell_dict[stocks_firm_name_cell.col] = stocks_firm_name_cell
                        this_row.cell_dict[stocks_quantity_cell.col] = stocks_quantity_cell


                    self.rows_dict[str(stock.symbol) + str(relevant_portfolios_list.index(account))] = this_row
                this_row = None
                stock = None
                row_count += 1
        # iterate over cells to fill in grid
        for ticker, row_obj in self.rows_dict.iteritems():
            for col_num, cell_obj in row_obj.cell_dict.iteritems():
                #print line_number()
                #print cell_obj.row, cell_obj.col, cell_obj.text

                # check if row moved:
                if cell_obj.row != row_obj.row:
                    cell_obj.row = row_obj.row
                self.grid.SetCellValue(cell_obj.row, cell_obj.col, cell_obj.text)
                if cell_obj.align_right:
                    self.grid.SetCellAlignment(cell_obj.row, cell_obj.col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
                if cell_obj.text_color:
                    self.grid.SetCellTextColour(cell_obj.row, cell_obj.col, cell_obj.text_color)

        total_sale_value = None
        total_sale_value_relevant = True
        total_commission_loss = None
        total_capital_gains = None
        total_capital_gains_relevant = True

        ### Set Totals ###
        # set total sale
        for ticker, row_obj in self.rows_dict.iteritems():
            cell_obj = row_obj.cell_dict.get(self.number_of_shares_copy_cell.col)
            if cell_obj:
                if cell_obj.text is not None and cell_obj.text is not "":
                    # set total sale
                    if total_sale_value_relevant:
                        row_sale_value_cell = row_obj.cell_dict.get(self.sale_value_cell.col)
                        if row_sale_value_cell:
                            if row_sale_value_cell.value is not None and row_sale_value_cell.value is not "":
                                if total_sale_value is None:
                                    total_sale_value = 0.
                                total_sale_value += float(row_sale_value_cell.value)
                            else:
                                total_sale_value = None
                                total_sale_value_relevant = False
        if total_sale_value is not None:
            self.grid.SetCellValue(self.totals_cell.row, self.sale_value_cell.col, config.locale.currency(total_sale_value, grouping = True))
            self.grid.SetCellAlignment(self.totals_cell.row, self.sale_value_cell.col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
        else:
            self.grid.SetCellValue(self.totals_cell.row, self.sale_value_cell.col, "")

        # set total commission
        if config.DEFAULT_COMMISSION:
            num_trades = 0.
            for row, row_obj in self.rows_dict.iteritems():
                cell_obj = row_obj.cell_dict.get(self.number_of_shares_copy_cell.col)
                if cell_obj:
                    if cell_obj.text is not None and cell_obj.text is not "":
                        # set stocks with commission
                        num_trades += 1
        if config.DEFAULT_COMMISSION and num_trades:
            total_commission_loss = num_trades * config.DEFAULT_COMMISSION
            self.grid.SetCellValue(self.totals_cell.row, self.commission_cell.col, config.locale.currency(total_commission_loss, grouping = True))
            self.grid.SetCellAlignment(self.totals_cell.row, self.commission_cell.col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)

        else:
            self.grid.SetCellValue(self.totals_cell.row, self.commission_cell.col, "")

        # set captial gains
        for ticker, row_obj in self.rows_dict.iteritems():
            cell_obj = row_obj.cell_dict.get(self.number_of_shares_copy_cell.col)
            if cell_obj:
                if cell_obj.text is not None and cell_obj.text is not "":
                    # set total sale
                    if total_capital_gains_relevant:
                        capital_gains_cell = row_obj.cell_dict.get(self.capital_gains_cell.col)
                        if capital_gains_cell:
                            if capital_gains_cell.value is not None and capital_gains_cell.value is not "":
                                if total_capital_gains is None:
                                    total_capital_gains = 0.
                                total_capital_gains += float(capital_gains_cell.value)
                            else:
                                total_capital_gains = None
                                total_capital_gains_relevant = False
        if total_capital_gains is not None:
            self.grid.SetCellValue(self.totals_cell.row, self.capital_gains_cell.col, config.locale.currency(total_capital_gains, grouping = True))
            self.grid.SetCellAlignment(self.totals_cell.row, self.capital_gains_cell.col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
        else:
            self.grid.SetCellValue(self.totals_cell.row, self.capital_gains_cell.col, "")

        # carryover adjustments
        if self.carryover_input_cell.value and total_capital_gains:
            adjusted_capital_gains = max(total_capital_gains - self.carryover_input_cell.value, 0.)
            self.grid.SetCellValue(self.totals_cell.row, self.carryover_input_cell.col, config.locale.currency(adjusted_capital_gains, grouping = True))
            self.grid.SetCellAlignment(self.totals_cell.row, self.carryover_input_cell.col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
        else:
            self.grid.SetCellValue(self.totals_cell.row, self.carryover_input_cell.col, "")

        if self.carryover_input_cell.value and total_capital_gains:
            adjustment_left = self.carryover_input_cell.value
            for row, row_obj in sorted(self.rows_dict.iteritems()):
                cell_obj = row_obj.cell_dict.get(self.number_of_shares_copy_cell.col)
                if cell_obj:
                    if cell_obj.text is not None and cell_obj.text is not "":
                        # set capital gains adjustment
                        capital_gains_cell = row_obj.cell_dict.get(self.capital_gains_cell.col)
                        if capital_gains_cell:
                            if capital_gains_cell.value and adjustment_left:
                                adjusted_capital_gains = max(capital_gains_cell.value - adjustment_left, 0.)
                                adjustment_left = max(adjustment_left - capital_gains_cell.value, 0.)

                                self.grid.SetCellValue(cell_obj.row, self.carryover_input_cell.col, config.locale.currency(adjusted_capital_gains, grouping = True))
                                self.grid.SetCellAlignment(cell_obj.row, self.carryover_input_cell.col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
                            else:
                                self.grid.SetCellValue(cell_obj.row, self.carryover_input_cell.col, config.locale.currency(capital_gains_cell.value, grouping = True))
                                self.grid.SetCellAlignment(cell_obj.row, self.carryover_input_cell.col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)

        self.grid.AutoSizeColumns()

    def updateGrid(self, event, refresh = None):
        row = event.GetRow()
        column = event.GetCol()
        value = self.grid.GetCellValue(row, column)
        value = utils.strip_string_whitespace(value)

        if int(row) == self.carryover_input_cell.row and int(column) == self.carryover_input_cell.col:
            # updating carryover losses
            value = value.replace("$", "")
            try:
                value = float(value)
            except:
                print line_number(), "Error: invalid carryover input."
                return
            self.carryover_input_cell.text = value
            self.carryover_input_cell.value = value

            self.saved_text.Hide()
            self.save_button.Show()
            self.exportSaleCandidates("event")
            self.spreadSheetFill("event")
            return

        ticker = str(self.grid.GetCellValue(row, self.ticker_cell.col))
        account_index = str(self.grid.GetCellValue(row, self.first_cell.col))
        num_shares = str(self.grid.GetCellValue(row, self.total_shares_cell.col))
        num_shares = num_shares.replace(",","")

        sale_value = None
        percent_to_commission = None

        row_obj = self.rows_dict.get(str(ticker)+str(account_index))
        #if row_obj:
        #    print line_number()
        #    print row_obj.cell_dict
        #    for ref, cell_obj in row_obj.cell_dict.iteritems():
        #        print cell_obj.text
        stocks_ticker_cell = row_obj.cell_dict.get(str(self.ticker_cell.col))
        if stocks_ticker_cell:
            ticker = stocks_ticker_cell.text
        else:
            ticker = str(self.grid.GetCellValue(row, self.ticker_cell.col))
            if not ticker:
                print line_number()
                print "Error: something went wrong here"


        print line_number()
        print ticker
        stock = utils.return_stock_by_symbol(ticker)
        if not stock:
            print line_number(), "Error, stock %s doesn't appear to exist" % ticker
            return

        stocks_price_cell = row_obj.cell_dict.get(str(self.price_cell.col))
        if stocks_price_cell:
            price = stocks_price_cell.value
        else:
            try:
                price = float(utils.return_last_price_if_possible(stock))
            except:
                price = None

        stocks_num_of_shares_cell = row_obj.cell_dict.get(str(self.num_of_shares_cell.col))
        stocks_percent_of_shares_cell = row_obj.cell_dict.get(str(self.percent_of_shares_cell.col))
        stocks_num_of_shares_copy_cell = row_obj.cell_dict.get(str(self.number_of_shares_copy_cell.col))
        stocks_percent_of_shares_copy_cell = row_obj.cell_dict.get(str(self.percent_of_shares_copy_cell.col))
        stocks_sale_check_cell = row_obj.cell_dict.get(str(self.sale_check_cell.col))
        stocks_sale_value_cell = row_obj.cell_dict.get(str(self.sale_value_cell.col))
        stocks_percent_to_commission_cell = row_obj.cell_dict.get(str(self.commission_cell.col))
        stocks_cost_basis_per_share_cell = row_obj.cell_dict.get(str(self.cost_basis_cell.col))
        stocks_capital_gains_cell = row_obj.cell_dict.get(str(self.capital_gains_cell.col))

        #print line_number()
        #print stocks_num_of_shares_cell
        #print stocks_percent_of_shares_cell
        #print stocks_num_of_shares_copy_cell

        if not stocks_num_of_shares_cell:
            stocks_num_of_shares_cell = SpreadsheetCell(row = row, col = self.num_of_shares_cell.col, align_right = True)
            row_obj.cell_dict[self.num_of_shares_cell.col] = stocks_num_of_shares_cell
        if not stocks_percent_of_shares_cell:
            stocks_percent_of_shares_cell = SpreadsheetCell(row = row, col = self.percent_of_shares_cell.col, align_right = True)
            row_obj.cell_dict[self.percent_of_shares_cell.col] = stocks_percent_of_shares_cell
        if not stocks_num_of_shares_copy_cell:
            stocks_num_of_shares_copy_cell = SpreadsheetCell(row = row, col = self.number_of_shares_copy_cell.col, align_right = True)
            row_obj.cell_dict[self.number_of_shares_copy_cell.col] = stocks_num_of_shares_copy_cell
        if not stocks_percent_of_shares_copy_cell:
            stocks_percent_of_shares_copy_cell = SpreadsheetCell(row = row, col = self.percent_of_shares_copy_cell.col, align_right = True)
            row_obj.cell_dict[self.percent_of_shares_copy_cell.col] = stocks_percent_of_shares_copy_cell
        if not stocks_sale_check_cell:
            stocks_sale_check_cell = SpreadsheetCell(row = row, col = self.sale_check_cell.col)
            row_obj.cell_dict[self.sale_check_cell.col] = stocks_sale_check_cell
        if not stocks_sale_value_cell:
            stocks_sale_value_cell = SpreadsheetCell(row = row, col = self.sale_value_cell.col, align_right = True)
            row_obj.cell_dict[self.sale_value_cell.col] = stocks_sale_value_cell
        if not stocks_percent_to_commission_cell:
            stocks_percent_to_commission_cell = SpreadsheetCell(row = row, col = self.commission_cell.col, align_right = True)
            row_obj.cell_dict[self.commission_cell.col] = stocks_percent_to_commission_cell
        if not stocks_cost_basis_per_share_cell:
            stocks_cost_basis_per_share_cell = SpreadsheetCell(row = row, col = self.cost_basis_cell.col, align_right = True)
            row_obj.cell_dict[self.cost_basis_cell.col] = stocks_cost_basis_per_share_cell
        if not stocks_capital_gains_cell:
            stocks_capital_gains_cell = SpreadsheetCell(row = row, col = self.capital_gains_cell.col, align_right = True)
            row_obj.cell_dict[self.capital_gains_cell.col] = stocks_capital_gains_cell

        #print line_number(), row_obj.cell_dict


        if column == self.num_of_shares_cell.col: # sell by number
            try:
                number_of_shares_to_sell = int(value)
            except Exception, exception:
                print line_number(), exception
                number_of_shares_to_sell = None
                #self.setGridError(row) # this should actually be changed below
            #print line_number(), "# of stocks to sell changed"

            # blank percentage of shares col
            #self.grid.SetCellValue(row, self.percent_of_shares_cell.col, "")
            stocks_percent_of_shares_cell.text = ""
            stocks_percent_of_shares_cell.value = None

            if str(number_of_shares_to_sell).isdigit() and float(num_shares) >= float(number_of_shares_to_sell) and float(number_of_shares_to_sell) != 0.:
                # No input errors
                #self.grid.SetCellValue(row, self.number_of_shares_copy_cell.col, str(number_of_shares_to_sell))
                stocks_num_of_shares_cell.text = str(number_of_shares_to_sell)
                stocks_num_of_shares_cell.value = number_of_shares_to_sell

                stocks_num_of_shares_copy_cell.text = str(number_of_shares_to_sell)
                stocks_num_of_shares_copy_cell.value = number_of_shares_to_sell

                percent_of_total_holdings = float(number_of_shares_to_sell)/float(num_shares)
                percent_of_total_holdings_text = str(int(round(100 * percent_of_total_holdings))) + "%"
                #self.grid.SetCellValue(row, self.percent_of_shares_copy_cell.col, ("%d" % percent_of_total_holdings) + "%")
                stocks_percent_of_shares_copy_cell.text = percent_of_total_holdings_text
                stocks_percent_of_shares_copy_cell.value = percent_of_total_holdings

                if float(num_shares) == float(number_of_shares_to_sell):
                    #self.grid.SetCellValue(row, self.sale_check_cell.col, "All")
                    stocks_sale_check_cell.text = "All"
                    #self.grid.SetCellTextColour(row, self.sale_check_cell.col, "black")
                    stocks_sale_check_cell.text_color = "black"
                else:
                    #self.grid.SetCellValue(row, self.sale_check_cell.col, "Some")
                    stocks_sale_check_cell.text = "Some"
                    #self.grid.SetCellTextColour(row, self.sale_check_cell.col, "black")
                    stocks_sale_check_cell.text_color = "black"

            elif value == "" or number_of_shares_to_sell == 0:
                # if zero
                #self.grid.SetCellValue(row, self.number_of_shares_copy_cell.col, "")
                stocks_num_of_shares_cell.text = ""
                stocks_num_of_shares_cell.value = 0.
                #self.grid.SetCellValue(row, self.percent_of_shares_copy_cell.col, "")
                stocks_percent_of_shares_cell.text = ""
                stocks_percent_of_shares_cell.value = None
                #self.grid.SetCellValue(row, self.sale_check_cell.col, "")
                stocks_sale_check_cell.text = ""
                #self.grid.SetCellTextColour(row, self.sale_check_cell.col, "black")
                stocks_sale_check_cell.text_color = "black"
            else:
                # Bad input
                self.setGridError(row, number = number_of_shares_to_sell)
                return

        if column == self.percent_of_shares_cell.col: # by % of stock held
            if "%" in value:
                value = value.strip("%")
                try:
                    value = float(value)/100
                except Exception, exception:
                    print line_number(), exception
                    self.setGridError(row, percentage = value)
                    return
            else:
                try:
                    value = float(value)
                    if value >= 1:
                        value = value / 100
                except Exception, exception:
                    print line_number(), exception
                    if value != "":
                        self.setGridError(row, percentage = value)
                        return
            percent_of_holdings_to_sell = value

            if float(value).is_integer():
                value = int(value)
            stocks_percent_of_shares_cell.text = str(value*100) + "%"
            stocks_percent_of_shares_cell.value = value
            #self.grid.SetCellValue(row, self.num_of_shares_cell.col, "")
            stocks_num_of_shares_cell.text = ""
            stocks_num_of_shares_cell.value = None

            # if empty
            if percent_of_holdings_to_sell == "" or percent_of_holdings_to_sell == 0:
                number_of_shares_to_sell = 0
                stocks_num_of_shares_copy_cell.text = ""
                stocks_num_of_shares_copy_cell.value = 0
                stocks_percent_of_shares_copy_cell = ""
                stocks_percent_of_shares_copy_cell = None
                stocks_sale_check_cell.text = ""
                stocks_sale_check_cell.text_color = "black"

            elif percent_of_holdings_to_sell <= 1:


                number_of_shares_to_sell = int(math.floor( int(num_shares) * percent_of_holdings_to_sell ) )
                stocks_num_of_shares_copy_cell.text = str(number_of_shares_to_sell)
                stocks_num_of_shares_copy_cell.value = number_of_shares_to_sell

                if number_of_shares_to_sell:
                    stocks_percent_of_shares_copy_cell.text = str(percent_of_holdings_to_sell * 100) + "%"
                    stocks_percent_of_shares_copy_cell.value = percent_of_holdings_to_sell
                    if int(num_shares) == int(number_of_shares_to_sell):
                        stocks_sale_check_cell.text = "All"
                        stocks_sale_check_cell.text_color = "black"
                    else:
                        stocks_sale_check_cell.text = "Some"
                        stocks_sale_check_cell.text_color = "black"
                else: # percentage is too small, because no shares can be sold at that percentage
                    stocks_percent_of_shares_copy_cell.text = str(0.) + "%"
                    stocks_percent_of_shares_copy_cell.value = 0.
            else:
                self.setGridError(row, percentage = percent_of_holdings_to_sell)
                return

        if price is not None and number_of_shares_to_sell:
            sale_value = float(number_of_shares_to_sell) * float(price)

            stocks_sale_value_cell.text = config.locale.currency(sale_value, grouping = True)
            stocks_sale_value_cell.value = sale_value
            if sale_value:
                percent_to_commission = self.commission/sale_value
            else:
                percent_to_commission = 0

            if percent_to_commission:
                stocks_percent_to_commission_cell.text = ("%.2f" % float(percent_to_commission * 100)) + "%"
                stocks_percent_to_commission_cell.value = percent_to_commission


        #if sale_value:
        #    self.grid.SetCellValue(row, self.sale_value_cell.col, "$%.2f" % sale_value)
        #if percent_to_commission:
        #    self.grid.SetCellValue(row, self.commission_cell.col, ("%.2f" % percent_to_commission) + "%")



        cost_basis_per_share = utils.return_cost_basis_per_share(row_obj.account, stock.symbol)
        if cost_basis_per_share is not None:
            stocks_cost_basis_per_share_cell.text = config.locale.currency(cost_basis_per_share, grouping = True)
            stocks_cost_basis_per_share_cell.value = cost_basis_per_share

        if cost_basis_per_share is not None and price is not None and number_of_shares_to_sell:
            capital_gain_per_share = price - cost_basis_per_share
            capital_gains = (capital_gain_per_share * number_of_shares_to_sell) - float(config.DEFAULT_COMMISSION)
            #self.grid.SetCellValue(row, self.capital_gains_cell.col, "$%.2f" % capital_gains)
            #self.grid.SetCellAlignment(row, self.capital_gains_cell.col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
            stocks_capital_gains_cell.text = config.locale.currency(capital_gains, grouping = True)
            stocks_capital_gains_cell.value = capital_gains
            if stocks_capital_gains_cell.value < 0:
                stocks_capital_gains_cell.text_color = config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX

        self.saved_text.Hide()
        self.save_button.Show()
        self.spreadSheetFill("event")
        self.exportSaleCandidates("event")


    def setGridError(self, row, number = None, percentage = None):
        row_obj = self.rows_dict.get(str(row))

        stocks_num_of_shares_copy_cell = row_obj.cell_dict.get(str(self.number_of_shares_copy_cell.col))
        stocks_percent_of_shares_copy_cell = row_obj.cell_dict.get(str(self.percent_of_shares_copy_cell.col))
        stocks_sale_check_cell = row_obj.cell_dict.get(str(self.sale_check_cell.col))
        stocks_sale_value_cell = row_obj.cell_dict.get(str(self.sale_value_cell.col))
        stocks_percent_to_commission_cell = row_obj.cell_dict.get(str(self.commission_cell.col))
        stocks_capital_gains_cell = row_obj.cell_dict.get(str(self.capital_gains_cell.col))



        if stocks_num_of_shares_copy_cell:
            stocks_num_of_shares_copy_cell.text = ""
            stocks_num_of_shares_copy_cell.value = None
        if stocks_percent_of_shares_copy_cell:
            stocks_percent_of_shares_copy_cell.text = ""
            stocks_percent_of_shares_copy_cell.value = None

        stocks_sale_check_cell = SpreadsheetCell(row = row, col = self.sale_check_cell.col, text = "Error", text_color = config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)
        row_obj.cell_dict[self.sale_check_cell.col] = stocks_sale_check_cell

        if stocks_sale_value_cell:
            stocks_sale_value_cell.text = ""
            stocks_sale_value_cell.value = None
        if stocks_percent_to_commission_cell:
            stocks_percent_to_commission_cell.text = ""
            stocks_percent_to_commission_cell.value = None
        if stocks_capital_gains_cell:
            stocks_capital_gains_cell.text = ""
            stocks_capital_gains_cell.value = None

        if number:
            stocks_num_of_shares_cell = SpreadsheetCell(row = row, col = self.num_of_shares_cell.col, text = str(number), text_color = config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX, align_right = True)
            row_obj.cell_dict[self.num_of_shares_cell.col] = stocks_num_of_shares_cell
        if percentage:
            stocks_percent_of_shares_cell = SpreadsheetCell(row = row, col = self.percent_of_shares_cell.col, text = str(percentage), text_color = config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX, align_right = True)
            row_obj.cell_dict[self.percent_of_shares_cell.col] = stocks_percent_of_shares_cell
        #self.grid.SetCellValue(row, self.sale_check_cell.col, "Error")
        #self.grid.SetCellTextColour(row, self.sale_check_cell.col, "red")

        #self.grid.SetCellValue(row, self.number_of_shares_copy_cell.col, "")
        #self.grid.SetCellValue(row, self.percent_of_shares_copy_cell.col, "")
        #self.grid.SetCellValue(row, self.sale_value_cell.col, "")
        #self.grid.SetCellValue(row, self.commission_cell.col, "")
        self.spreadSheetFill("event")

    def setNoGridError(self, row):
        self.grid.SetCellValue(row, self.sale_check_cell.col, "")
        self.grid.SetCellTextColour(row, self.sale_check_cell.col, "black")

class TradePage(Tab):
    def __init__(self, parent):
        self.title = "Trade"
        self.uid = config.TRADE_PAGE_UNIQUE_ID
        self.parent = parent
        self.default_average_daily_volume_attribute_name = config.DEFAULT_AVERAGE_DAILY_VOLUME_ATTRIBUTE_NAME


        wx.Panel.__init__(self, parent)
        trade_page_text = wx.StaticText(self, -1,
                             "Set up trades",
                             (10,10)
                             )
        self.ticker_list = []

        self.relevant_portfolios_list = []
        self.relevant_portfolio_name_list = []
        self.sale_tuple_list = []

        self.default_rows_above_buy_candidates = 5
        self.default_buy_candidate_column = 7
        self.default_buy_candidate_color = "#FAEFCF"
        self.default_not_entered_buy_candidate_color = "#FBF7EC"
        self.default_buy_candidate_quantity_column = 14
        self.default_buy_candidate_quantity_color = "#CFE8FC"
        self.default_not_entered_buy_candidate_quantity_color = "#E9F4FD"

        self.buy_candidates = [] # this will be tickers to buy, but no quantities
        self.buy_candidate_tuples = [] # this will be tickers ROWS with quantities, if they don't appear in previous list, there will be disregarded, because data has been changed.

        self.default_columns = 19
        self.default_min_rows = 17

        # no longer used
        #import_sale_candidates_button = wx.Button(self, label="Import sale candidates and refresh spreadsheet", pos=(0,30), size=(-1,-1))
        #import_sale_candidates_button.Bind(wx.EVT_BUTTON, self.importSaleCandidates, import_sale_candidates_button)

        self.create_grid_button = wx.Button(self, label="Create grid", pos=(500,0), size=(-1,-1))
        self.create_grid_button.Bind(wx.EVT_BUTTON, self.makeGridOnButtonPush, self.create_grid_button)
        self.create_grid_button.Hide()

        self.clear_grid_button = wx.Button(self, label="Clear", pos=(900,0), size=(-1,-1))
        self.clear_grid_button.Bind(wx.EVT_BUTTON, self.clearGrid, self.clear_grid_button)

        self.save_grid_button = wx.Button(self, label="Print", pos=(900,30), size=(-1,-1))
        self.save_grid_button.Bind(wx.EVT_BUTTON, self.saveGridAs, self.save_grid_button)


        self.grid_list = []

        self.update_stocks_button = wx.Button(self, label="Update stocks with errors.", pos=(700,30), size=(-1,-1))
        self.update_stocks_button.Bind(wx.EVT_BUTTON, self.updateStocksWithErrors, self.update_stocks_button)
        self.update_stocks_button.Hide()
        self.stocks_to_update = []
        self.number_of_tickers_to_scrape = 0

        self.stock_update_pending_text = wx.StaticText(self, -1,
                             "Currently Updating Stocks",
                             (700,30)
                             )
        self.stock_update_pending_text.Hide()

        self.grid = None

        self.makeGridOnButtonPush("event")

        print line_number(), "TradePage loaded"

    def updateStocksWithErrors(self, event):
        utils.remove_list_duplicates(self.stocks_to_update)
        if not self.stocks_to_update:
            self.update_stocks_button.Hide()
            return
        if len(self.stocks_to_update) > config.SCRAPE_CHUNK_LENGTH:
            print line_number(), "You should be able to remove this prompt by using newer scraping functions here."
            error_message = wx.MessageDialog(None,
                                   "The number of stocks to scrape is too large. Please use the Scrape tab to perform a full scrape.",
                                   'Scrape Too Large',
                                   style = wx.ICON_EXCLAMATION
                                   )
            error_message.ShowModal()
            confirm.Destroy()
            return

        self.update_stocks_button.Hide()
        self.stock_update_pending_text.Show()

        chunk_list_and_percent_of_full_scrape_done_and_number_of_tickers_to_scrape = scrape.prepareYqlScrape(self.stocks_to_update)

        chunk_list = chunk_list_and_percent_of_full_scrape_done_and_number_of_tickers_to_scrape[0]
        percent_of_full_scrape_done = chunk_list_and_percent_of_full_scrape_done_and_number_of_tickers_to_scrape[1]
        self.number_of_tickers_to_scrape = chunk_list_and_percent_of_full_scrape_done_and_number_of_tickers_to_scrape[2]

        timer = threading.Timer(0, self.executeUpdatePartOne, [chunk_list, 0])
        timer.start()
    def executeUpdatePartOne(self, ticker_chunk_list, position_of_this_chunk):
        data = scrape.executeYqlScrapePartOne(ticker_chunk_list, position_of_this_chunk)

        sleep_time = config.SCRAPE_SLEEP_TIME
        timer = threading.Timer(sleep_time, self.executeUpdatePartTwo, [ticker_chunk_list, position_of_this_chunk, data])
        timer.start()
    def executeUpdatePartTwo(self, ticker_chunk_list, position_of_this_chunk, successful_pyql_data):
        scrape.executeYqlScrapePartTwo(ticker_chunk_list, position_of_this_chunk, successful_pyql_data)

        sleep_time = config.SCRAPE_SLEEP_TIME
        logging.warning("Sleeping for %d seconds before the next task" % sleep_time)



        number_of_tickers_in_chunk_list = 0
        for chunk in ticker_chunk_list:
            for ticker in chunk:
                number_of_tickers_in_chunk_list += 1
        number_of_tickers_previously_updated = self.number_of_tickers_to_scrape - number_of_tickers_in_chunk_list
        number_of_tickers_done_in_this_scrape = 0
        for i in range(len(ticker_chunk_list)):
            if i > position_of_this_chunk:
                continue
            for ticker in ticker_chunk_list[i]:
                number_of_tickers_done_in_this_scrape += 1
        total_number_of_tickers_done = number_of_tickers_previously_updated + number_of_tickers_done_in_this_scrape
        percent_of_full_scrape_done = round( 100 * float(total_number_of_tickers_done) / float(self.number_of_tickers_to_scrape))

        position_of_this_chunk += 1
        percent_done = round( 100 * float(position_of_this_chunk) / float(len(ticker_chunk_list)) )
        print line_number(), "%d%%" % percent_done, "done this scrape execution."
        print line_number(), "%d%%" % percent_of_full_scrape_done, "done of all tickers."

        if position_of_this_chunk >= len(ticker_chunk_list):
            for chunk in ticker_chunk_list:
                for ticker in chunk:
                    self.stocks_to_update.remove(ticker)
            self.updateGrid("event", cursor_positon = (0, 0))
            self.stock_update_pending_text.Hide()
            print line_number(), "finished!"
            self.newGridFill()
        else:
            for chunk in ticker_chunk_list:
                for ticker in chunk:
                    self.stocks_to_update.remove(ticker)
            self.updateGrid("event", cursor_positon = (0, 0))
            print line_number(), "ready to loop again"
            timer = threading.Timer(sleep_time, self.executeScrapePartOne, [ticker_chunk_list, position_of_this_chunk])
            timer.start()

    def clearGrid(self, event):
        self.relevant_portfolios_list = []
        self.sale_tuple_list = []
        self.ticker_list = []
        self.buy_candidates = []
        self.buy_candidate_tuples = []
        self.stocks_to_update = []
        self.newGridFill()
        sale_prep_page = config.GLOBAL_PAGES_DICT.get(config.SALE_PREP_PAGE_UNIQUE_ID).obj
        sale_prep_page.saved_text.Hide()
        sale_prep_page.save_button.Show()

    def importSaleCandidates(self, event):
        print line_number(), "Boom goes the boom!!!!!!!!" # My favorite logging text, please don't remove :(

        self.relevant_portfolios_list = config.SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[0]
        self.sale_tuple_list = config.SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[1]

        for portfolio in self.relevant_portfolios_list:
            id_number = portfolio.id_number
            print line_number(), "Portfolio %d:" % id_number, config.PORTFOLIO_NAMES[id_number - 1]
        print line_number(), self.sale_tuple_list
        self.makeGridOnButtonPush("event")

        # Now, how to refresh only parts of the list... hmmmm
    def makeGridOnButtonPush(self, event):
        self.newGridFill()

    def updateGrid(self, event, grid = None, cursor_positon = None):
        # this function currently creates new grids on top of each other.
        # why?
        # when i tried to update the previous grid using the data (run self.spreadSheetFill on the last line).
        # this caused a Segmentation fault: 11
        # thus, this hack... create a new grid on execution each time.
        # it will tell you how many grids have loaded, but it shouldn't affect performance (i think).

        if not grid:
            print line_number(), "no grid"
            grid = self.grid
        else:
            print line_number(), grid

        if not cursor_positon:
            row = event.GetRow()
            column = event.GetCol()
            cursor_positon = (int(row), int(column))

        buy_candidates_len = len(self.buy_candidates)
        print line_number(), buy_candidates_len
        print line_number(), buy_candidates_len + 1 + self.default_rows_above_buy_candidates + 1
        self.buy_candidates = []
        self.buy_candidate_tuples = []
        for row in (range(buy_candidates_len + 1 + self.default_rows_above_buy_candidates + 1)):
            #print line_number()
            #print line_number(), row
            if row > self.default_rows_above_buy_candidates and grid.GetCellBackgroundColour(row, self.default_buy_candidate_column) in [self.default_buy_candidate_color, self.default_not_entered_buy_candidate_color]:
                #print line_number()
                #print line_number(),  row
                ticker = grid.GetCellValue(row, self.default_buy_candidate_column)
                #print line_number()
                #print line_number(), ticker
                if ticker:
                    stock = utils.return_stock_by_symbol(ticker)
                    if stock:
                        self.buy_candidates.append(str(stock.symbol))
                        quantity = grid.GetCellValue(row, self.default_buy_candidate_quantity_column)
                        if quantity:
                            if str(quantity).isdigit():
                                quantity = int(quantity)
                                ticker_row = row
                                self.buy_candidate_tuples.append((ticker_row, quantity))
                    else:
                        print line_number(), ticker, "doesn't seem to exist"
                        self.grid.SetCellValue(row, column, ticker)
                        self.grid.SetCellAlignment(row, column, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
                        self.grid.SetCellValue(row, column + 1, "Error")
                        self.grid.SetCellAlignment(row, column + 1, horiz = wx.ALIGN_CENTER, vert = wx.ALIGN_BOTTOM)
                        self.grid.SetCellTextColour(row, column + 1, config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)
                        return
        print line_number(), self.buy_candidates

        # build new grid
        self.newGridFill(cursor_positon = cursor_positon)

    def newGridFill(self, cursor_positon = (0,0)):
        #print line_number(), cursor_positon
        size = (1000, 650)
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            #print line_number(), width, height
            size = (width-20, height-128) # find the difference between the Frame and the grid size
        except:
            pass
        # CREATE A GRID HERE
        new_grid = TradeGrid(self, -1, size=size, pos=(0,83))
        # calc rows

        self.relevant_portfolio_name_list = []
        try:
            # set initial rows, buy candidate rows checked below
            print line_number(), "relevant_portfolios_list"
            for account in self.relevant_portfolios_list:
                id_number = account.id_number
                self.relevant_portfolio_name_list.append(config.PORTFOLIO_NAMES[(id_number - 1)])
                print line_number(), "relevant_portfolio_name_list:", self.relevant_portfolio_name_list

            num_rows = len(self.sale_tuple_list)
            num_rows += config.DEFAULT_ROWS_ON_TRADE_PREP_PAGE_FOR_TICKERS
        except Exception, exception:
            print line_number(), exception
            print line_number(), "Error in loading trade grid, num_rows will be reset to zero."
            num_rows = 0

        num_rows = max(num_rows, self.default_min_rows, (self.default_rows_above_buy_candidates + len(self.buy_candidates) + 2))
        new_grid.CreateGrid(num_rows, self.default_columns)
        new_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, lambda event: self.updateGrid(event, grid = new_grid), new_grid)

        #You need this code to resize
        self.sizer = None
        self.inner_sizer = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer.AddSpacer(83)

        self.inner_sizer.Add(new_grid, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(self.inner_sizer)
        self.sizer.Add(self, 1, wx.EXPAND|wx.ALL)
        ##

        #print line_number(), self.buy_candidates
        for column_num in range(self.default_columns):
            for row_num in range(num_rows):
                if row_num <= self.default_rows_above_buy_candidates or row_num > (self.default_rows_above_buy_candidates + len(self.buy_candidates) + 1) or column_num not in [self.default_buy_candidate_column,14]:
                    new_grid.SetReadOnly(row_num, column_num, True)
                elif column_num == self.default_buy_candidate_column:
                    if int(row_num) == int(self.default_rows_above_buy_candidates + len(self.buy_candidates) + 1):
                        new_grid.SetCellBackgroundColour(row_num, column_num, self.default_not_entered_buy_candidate_color)
                    else:
                        new_grid.SetCellBackgroundColour(row_num, column_num, self.default_buy_candidate_color)
                elif column_num == 14:
                    if int(row_num) == int(self.default_rows_above_buy_candidates + len(self.buy_candidates) + 1):
                        new_grid.SetCellBackgroundColour(row_num, column_num, self.default_not_entered_buy_candidate_quantity_color)
                    else:
                        new_grid.SetCellBackgroundColour(row_num, column_num, self.default_buy_candidate_quantity_color)


        # Defining cells separately from forming them so they are easy to edit
        # e.g. dummy_cell_var = [Row, Column, "Name/Value"]
        # cell_list = [dummy_cell_var, dummy_cell_2, etc...]
        # for cell in cell_list:
        #   new_grid.SetCellValue(cell[0],cell[1],cell[2])
        spreadsheet_cell_list = []

        # Start with static values (large if statement for code folding purposes only)
        if "This section sets the static cell values by column" == "This section sets the static cell values by column":
            # Column 0 (using zero-based numbering for simplicity):
            this_column_number = 0

            title_with_relevant_portfolios_string = "Trade Prep (" + ",\n".join(self.relevant_portfolio_name_list) + ")"

            name_of_spreadsheet_cell = SpreadsheetCell(row = 0, col = this_column_number, text=title_with_relevant_portfolios_string)
            share_to_sell_cell = SpreadsheetCell(row = 2, col = this_column_number, text = "Sell:")
            ticker_title_cell = SpreadsheetCell(row = 3, col = this_column_number, text = "Ticker")

            spreadsheet_cell_list.append(name_of_spreadsheet_cell)
            spreadsheet_cell_list.append(share_to_sell_cell)
            spreadsheet_cell_list.append(ticker_title_cell)

            # Column 1:
            this_column_number = 1

            num_shares_cell = SpreadsheetCell(row = 3, col = this_column_number, text = "# shares")
            spreadsheet_cell_list.append(num_shares_cell)

            # Column 2:
            this_column_number = 2

            volume_title_cell = SpreadsheetCell(row = 3, col = this_column_number, text = "Volume")
            spreadsheet_cell_list.append(volume_title_cell)

            # Column 3:
            # empty

            # Column 4:
            this_column_number = 4

            total_asset_cell = SpreadsheetCell(             row = 0,  col = this_column_number, text = "Total asset value =")
            approximate_surplus_cash_cell = SpreadsheetCell(row = 3,  col = this_column_number, text = "Approximate surplus cash from sale =")
            percent_total_cash_cell = SpreadsheetCell(      row = 6,  col = this_column_number, text = "%" + " Total Cash After Sale")
            portfolio_cash_available_cell = SpreadsheetCell(row = 9,  col = this_column_number, text = "Portfolio Cash Available =")
            num_stocks_to_look_cell = SpreadsheetCell(      row = 12, col = this_column_number, text = "# of stocks to look at for 3%" + " of portfolio each.")
            approximate_to_spend_cell = SpreadsheetCell(    row = 15, col = this_column_number, text = "Approximate to spend on each (3%) stock.")

            spreadsheet_cell_list.append(total_asset_cell)
            spreadsheet_cell_list.append(approximate_surplus_cash_cell)
            spreadsheet_cell_list.append(percent_total_cash_cell)
            spreadsheet_cell_list.append(portfolio_cash_available_cell)
            spreadsheet_cell_list.append(num_stocks_to_look_cell)
            spreadsheet_cell_list.append(approximate_to_spend_cell)

            # Column 5:
            # empty

            # Column 6:
            this_column_number = 6

            num_symbol_cell = SpreadsheetCell(row = 5, col = this_column_number, text = "#")
            spreadsheet_cell_list.append(num_symbol_cell)

            # Column 7:
            this_column_number = 7

            shares_to_buy_cell = SpreadsheetCell(row = 2, col = this_column_number, text = "To buy:")
            input_ticker_cell = SpreadsheetCell(row = 3, col = this_column_number, text = "Input ticker")

            spreadsheet_cell_list.append(shares_to_buy_cell)
            spreadsheet_cell_list.append(input_ticker_cell)

            # Column 8:
            # empty

            # Column 9:
            # empty

            # Column 10:
            this_column_number = 10

            num_shares_to_buy_cell = SpreadsheetCell(row = 2, col = this_column_number, text = "# shares for")
            three_percent_cell = SpreadsheetCell(row = 3, col = this_column_number, text = "3%")

            spreadsheet_cell_list.append(num_shares_to_buy_cell)
            spreadsheet_cell_list.append(three_percent_cell)

            # Column 11:
            this_column_number = 11

            for_cell = SpreadsheetCell(row = 2, col = this_column_number, text = "for")
            five_percent_cell = SpreadsheetCell(row = 3, col = this_column_number, text = "5%")

            spreadsheet_cell_list.append(for_cell)
            spreadsheet_cell_list.append(five_percent_cell)

            # Column 12:
            this_column_number = 12

            for_cell_2 = SpreadsheetCell(row = 2, col = this_column_number, text = "for")
            ten_percent_cell = SpreadsheetCell(row = 3, col = this_column_number, text = "10%")

            spreadsheet_cell_list.append(for_cell_2)
            spreadsheet_cell_list.append(ten_percent_cell)

            # Column 13:
            # empty

            # Column 14:
            this_column_number = 14

            input_num_shares_cell = SpreadsheetCell(row = 2, col = this_column_number, text = "Input # Shares")
            input_num_shares_cell_2 = SpreadsheetCell(row = 3, col = this_column_number, text = "to Purchase")
            spreadsheet_cell_list.append(input_num_shares_cell)
            spreadsheet_cell_list.append(input_num_shares_cell_2)

            # Column 15:
            this_column_number = 15

            cost_cell = SpreadsheetCell(row = 3, col = this_column_number, text = "Cost")
            spreadsheet_cell_list.append(cost_cell)

            # Column 16:
            # empty

            # Column 17:
            this_column_number = 17

            total_cost_cell = SpreadsheetCell(row = 1, col = this_column_number, text = "Total Cost =")
            adjusted_cash_cell = SpreadsheetCell(row = 2, col = this_column_number, text = "Adjusted Cash Available =")
            num_stocks_to_purchase_cell = SpreadsheetCell(row = 3, col = this_column_number, text = "# Stocks left to purchase at 3%")
            new_cash_percentage_cell = SpreadsheetCell(row = 4, col = this_column_number, text = "New cash %" + " of portfolio =")
            # this cell may be irrelevant
            # new_cash_total_cell = [5, this_column_number, "New cash %% of total ="]

            spreadsheet_cell_list.append(total_cost_cell)
            spreadsheet_cell_list.append(adjusted_cash_cell)
            spreadsheet_cell_list.append(num_stocks_to_purchase_cell)
            spreadsheet_cell_list.append(new_cash_percentage_cell)
            # spreadsheet_cell_list.append(new_cash_total_cell)

            # Column 18:
            # computed values only

        if "This section sets the variable cell values with relevant data" == "This section sets the variable cell values with relevant data":

            # Column 0-2 data:
            this_column_number = 0
            default_rows = config.DEFAULT_ROWS_ON_TRADE_PREP_PAGE_FOR_TICKERS
            counter = 0
            for stock_tuple in self.sale_tuple_list:
                ticker = stock_tuple[0]
                number_of_shares_to_sell = stock_tuple[1]
                stock = utils.return_stock_by_symbol(ticker)
                correct_row = counter + default_rows

                ticker_cell = SpreadsheetCell(row = correct_row, col = this_column_number, text = ticker)
                number_of_shares_to_sell_cell = SpreadsheetCell(row = correct_row, col = this_column_number+1, text = str(number_of_shares_to_sell), value = number_of_shares_to_sell, align_right = True)

                spreadsheet_cell_list.append(ticker_cell)
                spreadsheet_cell_list.append(number_of_shares_to_sell_cell)

                try:
                    avg_daily_volume = utils.return_daily_volume_if_possible(stock)
                    if not avg_daily_volume:
                        avg_daily_volume = "Update Volume"
                        color = config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX
                        self.stocks_to_update.append(stock.ticker)
                        self.update_stocks_button.Show()
                    else:
                        color = None
                    volume_cell = SpreadsheetCell(row = correct_row, col = this_column_number + 2, text = str(avg_daily_volume), value = avg_daily_volume, align_right = True, text_color = color)
                    spreadsheet_cell_list.append(volume_cell)
                except Exception, exception:
                    print line_number(), exception

                counter += 1

            # Column 4 data:
            this_column_number = 4

            ## total asset value
            total_asset_value_row = 1

            total_asset_value = 0.00
            for account in self.relevant_portfolios_list:
                total_asset_value += float(str(account.available_cash).replace("$",""))
                for ticker, quantity in account.stock_shares_dict.iteritems():
                    stock = utils.return_stock_by_symbol(ticker)
                    quantity = float(str(quantity).replace(",",""))
                    last_price = utils.return_last_price_if_possible(stock)
                    try:
                        last_price = float(last_price)
                        value_of_held_stock = last_price * quantity
                        total_asset_value += value_of_held_stock
                    except Exception as e:
                        print line_number(), e
                        print "No last price:", last_price, type(last_price)
                        try:
                            print "quantity", quantity, type(quantity)
                        except:
                            print "no quantity!"
                        try:
                            print "value_of_held_stock:", value_of_held_stock, type(value_of_held_stock)
                        except:
                            print "No value_of_held_stock available"
                        print "total_asset_value:", total_asset_value, type(total_asset_value)

            total_asset_value_cell = SpreadsheetCell(row = total_asset_value_row, col = this_column_number, text = config.locale.currency(total_asset_value, grouping = True), value = total_asset_value, align_right = True)
            spreadsheet_cell_list.append(total_asset_value_cell)

            ## approximate surplus cash
            approximate_surplus_cash_row = 4

            value_of_all_stock_to_sell = 0.00
            for stock_tuple in self.sale_tuple_list:
                ticker = stock_tuple[0]
                number_of_shares_to_sell = int(stock_tuple[1])
                stock = utils.return_stock_by_symbol(ticker)
                last_price = utils.return_last_price_if_possible(stock)
                try:
                    value_of_single_stock_to_sell = float(last_price) * float(number_of_shares_to_sell)
                    value_of_all_stock_to_sell += value_of_single_stock_to_sell
                except Exception as e:
                    print line_number(), e
                    print "No last price:", last_price, type(last_price)
                    print "number_of_shares_to_sell:", number_of_shares_to_sell, type(number_of_shares_to_sell)
                    print "value_of_all_stock_to_sell:", value_of_all_stock_to_sell, type(value_of_all_stock_to_sell)
            surplus_cash_cell = SpreadsheetCell(row = approximate_surplus_cash_row, col = this_column_number, text = config.locale.currency(value_of_all_stock_to_sell, grouping = True), value = value_of_all_stock_to_sell, align_right = True)
            spreadsheet_cell_list.append(surplus_cash_cell)

            ## percent of portfolio that is cash after sale
            percent_cash_row = 7

            total_cash = 0.00
            for account in self.relevant_portfolios_list:
                total_cash += float(str(account.available_cash).replace("$",""))
            total_cash += value_of_all_stock_to_sell
            if total_cash != 0 and total_asset_value != 0:
                percent_cash = total_cash / total_asset_value
                percent_cash = round(percent_cash * 100)
                percent_cash = str(percent_cash) + "%"
            else:
                percent_cash = "Null"

            percent_cash_cell = SpreadsheetCell(row = percent_cash_row, col = this_column_number, text = percent_cash, align_right = True)
            spreadsheet_cell_list.append(percent_cash_cell)

            ## portfolio cash available after sale
            cash_after_sale_row = 10

            total_cash_after_sale = total_cash # from above

            total_cash_after_sale_cell = SpreadsheetCell(row = cash_after_sale_row, col = this_column_number, text = config.locale.currency(total_cash_after_sale, grouping = True), value = total_cash_after_sale, align_right = True)
            spreadsheet_cell_list.append(total_cash_after_sale_cell)

            ## Number of stocks to purchase at 3% each
            stocks_at_three_percent_row = 13

            three_percent_of_all_assets = 0.03 * total_asset_value # from above
            try:
                number_of_stocks_at_3_percent = total_cash / three_percent_of_all_assets # total_cash defined above
            except Exception, exception:
                print line_number(), exception
                number_of_stocks_at_3_percent = 0
            number_of_stocks_at_3_percent = int(math.floor(number_of_stocks_at_3_percent)) # always round down

            stocks_at_three_percent_cell = SpreadsheetCell(row = stocks_at_three_percent_row, col = this_column_number, text = str(number_of_stocks_at_3_percent), value = number_of_stocks_at_3_percent, align_right = True)
            spreadsheet_cell_list.append(stocks_at_three_percent_cell)

            ## Approximate to spend on each stock at 3%
            three_percent_of_all_assets_row = 16

            three_percent_of_all_assets_cell = SpreadsheetCell(row = three_percent_of_all_assets_row, col = this_column_number, text = config.locale.currency(three_percent_of_all_assets, grouping = True), value = three_percent_of_all_assets, align_right = True)
            spreadsheet_cell_list.append(three_percent_of_all_assets_cell)

        # Now, add buy candidate tickers:

        count = 0
        # This is the a very similar iteration as above
        for column_num in range(self.default_columns):
            for row_num in range(num_rows):
                # iterate over all cells
                if row_num <= self.default_rows_above_buy_candidates or row_num > (self.default_rows_above_buy_candidates + len(self.buy_candidates) + 1) or column_num not in [self.default_buy_candidate_column, self.default_buy_candidate_quantity_column]:
                    # basically skip all irrelevant rows for these purposes
                    pass
                elif column_num == self.default_buy_candidate_column:
                    if count in range(len(self.buy_candidates)):
                        this_ticker = self.buy_candidates[count]
                        company_to_buy_number = SpreadsheetCell(row = row_num, col = column_num - 1, text = str(count + 1))
                        company_to_buy_ticker = SpreadsheetCell(row = row_num, col = column_num, text = this_ticker)
                        spreadsheet_cell_list.append(company_to_buy_number)
                        spreadsheet_cell_list.append(company_to_buy_ticker)

                        stock = utils.return_stock_by_symbol(this_ticker)
                        if stock:
                            company_to_buy_firm_name = SpreadsheetCell(row = row_num, col = column_num + 1, text = str(stock.firm_name))
                            spreadsheet_cell_list.append(company_to_buy_firm_name)

                        try:
                            last_price = float(utils.return_last_price_if_possible(stock))
                            company_to_buy_price = SpreadsheetCell(row = row_num, col = column_num + 2, text = config.locale.currency(last_price, grouping = True), value = last_price, align_right = True)
                            spreadsheet_cell_list.append(company_to_buy_price)

                            update_error = False
                        except Exception as e:
                            print line_number(), e

                            company_to_buy_price_error = SpreadsheetCell( row = row_num, col = column_num + 2, text = "(Error: Update %s)" % stock.symbol, text_color = config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)
                            spreadsheet_cell_list.append(company_to_buy_price_error)


                            update_error = True
                            self.stocks_to_update.append(stock.symbol)
                            utils.remove_list_duplicates(self.stocks_to_update)
                            print line_number(), self.stocks_to_update, "Row:", row_num, "Column:", column_num
                            self.update_stocks_button.Show()

                        column_shift = 3
                        for percent in [0.03, 0.05, 0.10]:
                            color = None
                            if not update_error:
                                # total_asset_value calculated above
                                #print total_asset_value
                                max_cost = total_asset_value * percent
                                #print max_cost
                                number_of_shares_to_buy = int(math.floor(max_cost / last_price))
                            else:
                                number_of_shares_to_buy = "-"
                                color = config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX
                                #print number_of_shares_to_buy
                            number_of_shares_to_buy_cell = SpreadsheetCell(row = row_num, col = column_num + column_shift, text = str(number_of_shares_to_buy), value = number_of_shares_to_buy, align_right = True, text_color = color)
                            spreadsheet_cell_list.append(number_of_shares_to_buy_cell)

                            column_shift += 1

                        for this_tuple in self.buy_candidate_tuples:
                            if this_tuple[0] == row_num:
                                quantity = this_tuple[1]

                                buy_candidate_quantity_cell = SpreadsheetCell(row = row_num, col = self.default_buy_candidate_quantity_column, text = str(quantity), value = quantity, align_right = False) # align right looks bad here, though it is an int
                                spreadsheet_cell_list.append(buy_candidate_quantity_cell)
                    count += 1

        # now calculate final values
        buy_cost_column = 15

        total_buy_cost = 0.00

        for row_num in range(num_rows):
            if row_num > self.default_rows_above_buy_candidates:
                quantity_cell = [cell for cell in spreadsheet_cell_list if (cell.row == row_num and cell.col == (buy_cost_column - 1))]
                if quantity_cell:
                    if len(quantity_cell) > 1:
                        print line_number(), "Error: too many cells returned for cell list"
                        return
                    quantity = quantity_cell[0].text
                else:
                    quantity = None
                if quantity is not None:
                    ticker_cell = [cell for cell in spreadsheet_cell_list if (cell.row == row_num and cell.col == (buy_cost_column - 8))]
                    if ticker_cell:
                        if len(ticker_cell) > 1:
                            print line_number(), "Error: too many cells returned for cell list"
                            return
                        ticker = ticker_cell[0].text
                    else:
                        ticker = None
                    print line_number(), ticker
                    stock = utils.return_stock_by_symbol(ticker)
                    if stock:
                        quantity = int(quantity)
                        cost = float(utils.return_last_price_if_possible(stock)) * quantity

                        total_buy_cost += cost
                        cost_cell = SpreadsheetCell(row = row_num, col = buy_cost_column, text = config.locale.currency(cost, grouping = True), value = cost, align_right = True)
                        spreadsheet_cell_list.append(cost_cell)

        # column 18 (final column)
        this_column_number = 18

        total_cost_row = 1

        total_cost_sum_cell = SpreadsheetCell(row = total_cost_row, col = this_column_number, text = config.locale.currency(total_buy_cost, grouping = True), value = total_buy_cost, align_right = True)
        spreadsheet_cell_list.append(total_cost_sum_cell)

        adjusted_cash_row = 2
        adjusted_cash_result = total_cash - total_buy_cost
        if adjusted_cash_result >= 0:
            color = "black"
        else:
            color = config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX
        adjusted_cash_result_cell = SpreadsheetCell(row = adjusted_cash_row, col = this_column_number, text = config.locale.currency(adjusted_cash_result, grouping = True), value = adjusted_cash_result, align_right = True, text_color = color)
        spreadsheet_cell_list.append(adjusted_cash_result_cell)

        number_of_stocks_still_yet_to_buy_row = 3
        if total_asset_value > 0:
            number_of_stocks_still_yet_to_buy = int(math.floor(adjusted_cash_result / (total_asset_value * 0.03)))
        else:
            number_of_stocks_still_yet_to_buy = 0
        number_of_stocks_still_yet_to_buy_cell = SpreadsheetCell(row = number_of_stocks_still_yet_to_buy_row, col = this_column_number, text = str(number_of_stocks_still_yet_to_buy), value = number_of_stocks_still_yet_to_buy, align_right = True, text_color = color)
        spreadsheet_cell_list.append(number_of_stocks_still_yet_to_buy_cell)

        new_percent_cash_row = 4
        if adjusted_cash_result != 0 and total_asset_value != 0:
            new_percent_cash = round(100 * adjusted_cash_result / total_asset_value)
        else:
            new_percent_cash = 0
        new_percent_cash_cell = SpreadsheetCell(row = new_percent_cash_row, col = this_column_number, text = "%d" % int(new_percent_cash) + "%", align_right = True, text_color = color)
        spreadsheet_cell_list.append(new_percent_cash_cell)

        # Finally, set cell values in list:
        for cell in spreadsheet_cell_list:
            #print line_number(), cell
            new_grid.SetCellValue(cell.row, cell.col, cell.text)
            if cell.align_right:
                new_grid.SetCellAlignment(cell.row, cell.col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
            if cell.text_color:
                new_grid.SetCellTextColour(cell.row, cell.col, cell.text_color)


        new_grid.AutoSizeColumns()
        print line_number(), "done building grid"
        new_grid.SetGridCursor(cursor_positon[0] + 1, cursor_positon[1])

        for grid in self.grid_list:
            grid.Hide()
        self.grid_list.append(new_grid)
        print line_number(), "number of grids created =", len(self.grid_list)
        new_grid.SetFocus()
        self.grid = new_grid

    def saveGridAs(self, event):
        html = utils.convert_wx_grid_data_to_html_table(self.grid)

        saveFileDialog = wx.FileDialog(self, "Save Trade Prep to file", "", 'TradePrep%s' % str(time.strftime("%I.%M.%S%p")),
                                       "HTML file|.html", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...
        # save the current contents in the file
        # this can be done with e.g. wxPython output streams:
        output_file = open(saveFileDialog.GetPath(), "w")
        output_file.write(html)
        output_file.close()


class UserFunctionsMetaPage(Tab):
    def __init__(self, parent):
        self.title = "Edit Functions"
        self.uid = config.USER_FUNCTIONS_PAGE_UNIQUE_ID
        wx.Panel.__init__(self, parent)
        ####
        user_function_page_panel = wx.Panel(self, -1, pos=(0,5), size=( wx.EXPAND, wx.EXPAND))
        user_function_notebook = wx.Notebook(user_function_page_panel)

        for function_page_dict in functions_config.user_created_function_ref_dict_list:
            function_page_obj = FunctionPage(
                title                       = function_page_dict.get("title"),
                uid_config_reference        = function_page_dict.get("uid_config_reference"),
                general_text                = function_page_dict.get("general_text"),
                additional_text             = function_page_dict.get("additional_text"),
                save_button_text            = function_page_dict.get("save_button_text"),
                reset_button_text           = function_page_dict.get("reset_button_text"),
                function_that_loads_text_of_user_created_functions = function_page_dict.get("function_that_loads_text_of_user_created_functions"),
                save_function               = function_page_dict.get("save_function"),
                function_to_load_defaults   = function_page_dict.get("function_to_load_defaults"),
                )
            new_functions_page = UserFunctionsPage(user_function_notebook, function_page_obj)
            user_function_notebook.AddPage(new_functions_page, function_page_obj.title)

        sizer2 = wx.BoxSizer()
        sizer2.Add(user_function_notebook, 1, wx.EXPAND)
        self.SetSizer(sizer2)
        ####

class UserFunctionsPage(Tab):
    def __init__(self, parent, function_page_obj):
        self.title = function_page_obj.title
        self.uid = function_page_obj.uid
        self.parent = parent

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddSpacer(95)

        wx.Panel.__init__(self, parent)

        self.general_text = wx.StaticText(self, -1, function_page_obj.general_text, (10,10))
        self.additional_text = wx.StaticText(self, -1, function_page_obj.additional_text, (145,36))

        self.save_button = wx.Button(self, label=function_page_obj.save_button_text, pos=(5, 30), size=(-1,-1))
        self.save_button.Bind(wx.EVT_BUTTON, self.confirmSave, self.save_button)

        self.reset_button = wx.Button(self, label=function_page_obj.reset_button_text, pos=(5, 60), size=(-1,-1))
        self.reset_button.Bind(wx.EVT_BUTTON, self.confirmResetToDefault, self.reset_button)

        self.function_file_text = function_page_obj.function_that_loads_text_of_user_created_functions()

        self.height_offset = 95

        self.file_display = wx.TextCtrl(self, -1,
                                    self.function_file_text,
                                    (10, self.height_offset),
                                    size = (955, 580),
                                    style = wx.TE_MULTILINE ,
                                    )

        self.sizer.Add(self.file_display, 1, wx.ALL|wx.EXPAND)
        self.file_display.Show()

        self.SetSizer(self.sizer)

        print line_number(), "%s loaded" % function_page_obj.title

    def confirmSave(self, event):
        confirm = wx.MessageDialog(None,
                                   "Are you sure you want to save your work? This action cannot be undone.",
                                   'Confirm Save',
                                   style = wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Save"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        confirm.Destroy()

        if yesNoAnswer == wx.ID_YES:
            self.saveFunctionsFile()

    def saveFunctionsFile(self):
        text_to_save = self.file_display.GetValue()
        function_page_obj.save_function(text_to_save)

    def confirmResetToDefault(self, event):
        confirm = wx.MessageDialog(None,
                                   "Are you sure you reset to file default? This action cannot be undone.",
                                   'Confirm Reset',
                                   style = wx.YES_NO
                                   )
        confirm.SetYesNoLabels(("&Reset"), ("&Cancel"))
        yesNoAnswer = confirm.ShowModal()
        confirm.Destroy()

        if yesNoAnswer == wx.ID_YES:
            self.resetToDefault()

    def resetToDefault(self):
        self.file_display.Destroy()

        self.function_file_text = function_page_obj.function_to_load_defaults()
        function_page_obj.saveFunctionsFile(self.function_file_text)

        size = (955, 580)
        try:
            width, height = config.GLOBAL_PAGES_DICT.get(config.MAIN_FRAME_UNIQUE_ID).GetClientSizeTuple()
            size = ( width - (config.HORIZONTAL_OFFSET_PER_TAB * 2) , height - self.height_offset - (config.VERTICAL_OFFSET_PER_TAB * 2)) # find the difference between the Frame and the grid size
        except:
            pass

        self.file_display = wx.TextCtrl(self, -1,
                                    self.function_file_text,
                                    (10, self.height_offset),
                                    size = size,
                                    style = wx.TE_MULTILINE ,
                                    )
        self.file_display.Show()
# ###########################################################################################

# ###################### wx grids #######################################################

## no longer used i think, will remove soon.
class GridAllStocks(wx.grid.Grid):
    def __init__(self, *args, **kwargs):
        wx.grid.Grid.__init__(self, *args, **kwargs)
        self.num_rows = len(config.GLOBAL_STOCK_DICT)
        self.num_columns = 0
        for stock in utils.return_all_stocks():
            num_attributes = 0
            for attribute in dir(stock):
                if not attribute.startswith('_'):
                    num_attributes += 1
            if self.num_columns < num_attributes:
                self.num_columns = num_attributes
        #print line_number(), "Number of rows: %d" % self.num_rows
        #print line_number(), "Number of columns: %d" % self.num_columns
class StockScreenGrid(wx.grid.Grid):
    def __init__(self, *args, **kwargs):
        wx.grid.Grid.__init__(self, *args, **kwargs)
        #############################################
        stock_list = config.CURRENT_SCREEN_LIST
        #############################################
        self.num_rows = len(stock_list)
        self.num_columns = 0
        for stock in stock_list:
            num_attributes = 0
            for attribute in dir(stock):
                if not attribute.startswith('_'):
                    num_attributes += 1
            if self.num_columns < num_attributes:
                self.num_columns = num_attributes
class SavedScreenGrid(wx.grid.Grid):
    # literally the only difference is the config call
    def __init__(self, *args, **kwargs):
        wx.grid.Grid.__init__(self, *args, **kwargs)
        #############################################
        stock_list = config.CURRENT_SAVED_SCREEN_LIST
        #############################################
        self.num_rows = len(stock_list)
        self.num_columns = 0
        for stock in stock_list:
            num_attributes = 0
            for attribute in dir(stock):
                if not attribute.startswith('_'):
                    num_attributes += 1
            if self.num_columns < num_attributes:
                self.num_columns = num_attributes

class RankPageGrid(wx.grid.Grid):
    # literally the only difference is the config call
    def __init__(self, *args, **kwargs):
        wx.grid.Grid.__init__(self, *args, **kwargs)
        #############################################
        stock_list = config.CURRENT_SAVED_SCREEN_LIST
        #############################################
        self.num_rows = len(stock_list)
        self.num_columns = 0
        for stock in stock_list:
            num_attributes = 0
            for attribute in dir(stock):
                if not attribute.startswith('_'):
                    num_attributes += 1
            if self.num_columns < num_attributes:
                self.num_columns = num_attributes
# end should remove, probably

class SalePrepGrid(wx.grid.Grid):
    def __init__(self, *args, **kwargs):
        wx.grid.Grid.__init__(self, *args, **kwargs)
class TradeGrid(wx.grid.Grid):
    def __init__(self, *args, **kwargs):
        wx.grid.Grid.__init__(self, *args, **kwargs)
class AccountDataGrid(wx.grid.Grid):
    def __init__(self, *args, **kwargs):
        wx.grid.Grid.__init__(self, *args, **kwargs)

class MegaTable(wx.grid.PyGridTableBase):
    """
    A custom wxGrid Table using user supplied data
    """
    def __init__(self, data, colnames, plugins = {}):
        """data is a list of the form
        [(rowname, dictionary),
        dictionary.get(colname, None) returns the data for column
        colname
        """
        # The base class must be initialized *first*
        wx.grid.PyGridTableBase.__init__(self)
        self.data = data
        self.colnames = colnames
        self.plugins = plugins or {}
        # XXX
        # we need to store the row length and collength to
        # see if the table has changed size
        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

    def GetNumberCols(self):
        return len(self.colnames)

    def GetNumberRows(self):
        return len(self.data)

    def GetColLabelValue(self, col):
        return self.colnames[col]

    def GetRowLabelValues(self, row):
        return self.data[row][0]

    def GetValue(self, row, col):
        return str(self.data[row][1].get(self.GetColLabelValue(col), ""))

    def GetRawValue(self, row, col):
        return self.data[row][1].get(self.GetColLabelValue(col), "")

    def SetValue(self, row, col, value):
        self.data[row][1][self.GetColLabelValue(col)] = value

    def ResetView(self, grid):
        """
        (wxGrid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        grid.BeginBatch()
        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(), wxGRIDTABLE_NOTIFY_ROWS_DELETED, wxGRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(), wxGRIDTABLE_NOTIFY_COLS_DELETED, wxGRIDTABLE_NOTIFY_COLS_APPENDED),
        ]:
            if new < current:
                msg = wxGridTableMessage(self,delmsg,new,current-new)
                grid.ProcessTableMessage(msg)
            elif new > current:
                msg = wxGridTableMessage(self,addmsg,new-current)
                grid.ProcessTableMessage(msg)
                self.UpdateValues(grid)
        grid.EndBatch()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()
        # update the column rendering plugins
        self._updateColAttrs(grid)

        # XXX
        # Okay, this is really stupid, we need to "jiggle" the size
        # to get the scrollbars to recalibrate when the underlying
        # grid changes.
        h,w = grid.GetSize()
        grid.SetSize((h+1, w))
        grid.SetSize((h, w))
        grid.ForceRefresh()

    def UpdateValues(self, grid):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = wxGridTableMessage(self, wxGRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)

    def _updateColAttrs(self, grid):
        """
        wxGrid -> update the column attributes to add the
        appropriate renderer given the column name.  (renderers
        are stored in the self.plugins dictionary)

        Otherwise default to the default renderer.
        """
        col = 0
        for colname in self.colnames:
            attr = wxGridCellAttr()
            if colname in self.plugins:
                renderer = self.plugins[colname](self)
                if renderer.colSize:
                    grid.SetColSize(col, renderer.colSize)
                if renderer.rowSize:
                    grid.SetDefaultRowSize(renderer.rowSize)
                attr.SetReadOnly(true)
                attr.SetRenderer(renderer)
            grid.SetColAttr(col, attr)
            col += 1

    # ------------------------------------------------------
    # begin the added code to manipulate the table (non wx related)
    def AppendRow(self, row):
        entry = {}
        for name in self.colnames:
            entry[name] = "Appended_%i"%row
        # XXX Hack
        # entry["A"] can only be between 1..4
        entry["A"] = random.choice(range(4))
        self.data.insert(row, ["Append_%i"%row, entry])

    def DeleteCols(self, cols):
        """
        cols -> delete the columns from the dataset
        cols hold the column indices
        """
        # we'll cheat here and just remove the name from the
        # list of column names.  The data will remain but
        # it won't be shown
        deleteCount = 0
        cols = cols[:]
        cols.sort()
        for i in cols:
            self.colnames.pop(i-deleteCount)
            # we need to advance the delete count
            # to make sure we delete the right columns
            deleteCount += 1
        if not len(self.colnames):
            self.data = []

    def DeleteRows(self, rows):
        """
        rows -> delete the rows from the dataset
        rows hold the row indices
        """
        deleteCount = 0
        rows = rows[:]
        rows.sort()
        for i in rows:
            self.data.pop(i-deleteCount)
            # we need to advance the delete count
            # to make sure we delete the right rows
            deleteCount += 1

    def SortColumn(self, col):
        """
        col -> sort the data based on the column indexed by col
        """
        name = self.colnames[col]
        _data = []
        for row in self.data:
            rowname, entry = row
            _data.append((entry.get(name, None), row))

        _data.sort()
        self.data = []
        for sortvalue, row in _data:
            self.data.append(row)

    # end table manipulation code
    # ----------------------------------------------------------
class MegaGrid(wx.grid.Grid):
    def __init__(self, parent, data, colnames, plugins=None, size=(1000,680), pos=(0,50), enable_editing = False
        ):
        """parent, data, colnames, plugins=None
        Initialize a grid using the data defined in data and colnames
        (see MegaTable for a description of the data format)
        plugins is a dictionary of columnName -> column renderers.
        """

        # The base class must be initialized *first*
        wx.grid.Grid.__init__(self, parent, -1, size = size, pos = pos)
        self._table = MegaTable(data, colnames, plugins)
        self.SetTable(self._table)
        self._plugins = plugins

        wx.grid.EVT_GRID_LABEL_RIGHT_CLICK(self, self.OnLabelRightClicked)
        self.EnableEditing(enable_editing)

    def Reset(self):
        """reset the view based on the data in the table.  Call
        this when rows are added or destroyed"""
        self._table.ResetView(self)

    def OnLabelRightClicked(self, evt):
        # Did we click on a row or a column?
        row, col = evt.GetRow(), evt.GetCol()
        if row == -1: self.colPopup(col, evt)
        elif col == -1: self.rowPopup(row, evt)

    def rowPopup(self, row, evt):
        """(row, evt) -> display a popup menu when a row label is right clicked"""
        appendID = wxNewId()
        deleteID = wxNewId()
        x = self.GetRowSize(row)/2
        if not self.GetSelectedRows():
            self.SelectRow(row)
        menu = wxMenu()
        xo, yo = evt.GetPosition()
        menu.Append(appendID, "Append Row")
        menu.Append(deleteID, "Delete Row(s)")

        def append(event, self=self, row=row):
            self._table.AppendRow(row)
            self.Reset()

        def delete(event, self=self, row=row):
            rows = self.GetSelectedRows()
            self._table.DeleteRows(rows)
            self.Reset()

        EVT_MENU(self, appendID, append)
        EVT_MENU(self, deleteID, delete)
        self.PopupMenu(menu, wxPoint(x, yo))
        menu.Destroy()

    def colPopup(self, col, evt):
        """(col, evt) -> display a popup menu when a column label is
        right clicked"""
        x = self.GetColSize(col)/2
        menu = wxMenu()
        id1 = wxNewId()
        sortID = wxNewId()

        xo, yo = evt.GetPosition()
        self.SelectCol(col)
        cols = self.GetSelectedCols()
        self.Refresh()
        menu.Append(id1, "Delete Col(s)")
        menu.Append(sortID, "Sort Column")

        def delete(event, self=self, col=col):
            cols = self.GetSelectedCols()
            self._table.DeleteCols(cols)
            self.Reset()

        def sort(event, self=self, col=col):
            self._table.SortColumn(col)
            self.Reset()

        EVT_MENU(self, id1, delete)
        if len(cols) == 1:
            EVT_MENU(self, sortID, sort)
        self.PopupMenu(menu, wxPoint(xo, 0))
        menu.Destroy()

# --------------------------------------------------------------------
# Sample wxGrid renderers

# ###########################################################################################

# ############ Spreadsheet Functions ########################################################

# # Had to switch to mega grids because data got too large!
def create_megagrid_from_stock_list(stock_list, parent, size=config.FULL_SPREADSHEET_SIZE_POSITION_TUPLE[0], pos=config.FULL_SPREADSHEET_SIZE_POSITION_TUPLE[1]):
    # Find all attribute names
    attribute_list = list(config.GLOBAL_ATTRIBUTE_SET)
    attribute_list.sort(key=lambda x: x.lower())

    # adjust list order for important terms
    try:
        attribute_list.insert(0, 'symbol')
    except Exception, e:
        print line_number(), e
    try:
        attribute_list.insert(1, 'firm_name')
    except Exception, e:
        print line_number(), e


    # Create correctly sized grid
    """data is a list of the form
    [(rowname, dictionary),
    dictionary.get(colname, None) returns the data for column
    colname
    """
    data = [("",{})]
    # remove stocks that failed to load
    stock_list = [stock for stock in stock_list if stock is not None]
    if stock_list:
        try:
            data = [(stock_list.index(stock), stock.__dict__) for stock in stock_list]
        except Exception, e:
            print line_number(), e
            pp.pprint(stock_list)
    spreadsheet = MegaGrid(parent = parent, data = data, colnames = attribute_list, size=size, pos=pos)
    #spreadsheet.SetColSize(1, renderer.colSize)
    spreadsheet.AutoSizeColumn(1)
    return spreadsheet

Ranked_Tuple_Reference = namedtuple("Ranked_Tuple_Reference", ["value", "stock"])
def create_ranked_megagrid_from_tuple_list(ranked_tuple_list, parent, rank_name, size=config.RANK_PAGE_SPREADSHEET_SIZE_POSITION_TUPLE[0], pos=config.RANK_PAGE_SPREADSHEET_SIZE_POSITION_TUPLE[1]):
    'ranked named_tuple reference: ["value", "stock"], rank_name should be obtained from a dropdown'

    # Find all attribute names
    attribute_list = list(config.GLOBAL_ATTRIBUTE_SET)

    # adjust list order for important terms
    try:
        attribute_list.insert(0, 'symbol')
    except Exception, e:
        print line_number(), e
    try:
        attribute_list.insert(1, 'firm_name')
    except Exception, e:
        print line_number(), e
    attribute_list.insert(2, rank_name)


    # Create correctly sized grid
    """data is a list of the form
    [(rowname, dictionary),
    dictionary.get(colname, None) returns the data for column
    colname
    """
    data = []
    for this_tuple in ranked_tuple_list:
        index = ranked_tuple_list.index(this_tuple)
        stock_dict = this_tuple.stock.__dict__
        stock_dict[rank_name] = this_tuple.value
        data.append((index, stock_dict))

    spreadsheet = MegaGrid(parent = parent, data = data, colnames = attribute_list, size=size, pos=pos)
    #spreadsheet.SetColSize(1, renderer.colSize)
    spreadsheet.AutoSizeColumn(1)
    return spreadsheet

def create_account_spread_sheet(
    wxWindow,
    account_obj,
    held_ticker_list = [] # not used currentl
    , size = config.PORTFOLIO_PAGE_SPREADSHEET_SIZE_POSITION_TUPLE[0]
    , position = config.PORTFOLIO_PAGE_SPREADSHEET_SIZE_POSITION_TUPLE[1]
    , enable_editing = False
    ):

    stock_list = []
    for ticker in account_obj.stock_shares_dict:
        #print line_number(), ticker
        stock = config.GLOBAL_STOCK_DICT.get(ticker)
        if stock:
            #print line_number(), "Stock:", stock.symbol
            if stock not in stock_list:
                stock_list.append(stock)
        else:
            print line_number(), "Ticker:", ticker, "not found..."
    stock_list.sort(key = lambda x: x.ticker)

    attribute_list = ['symbol', 'firm_name', "Shares Held", "Last Close", "Value", "Cost Basis", "Change"]

    num_columns = len(attribute_list)
    num_rows = len(stock_list)
    num_rows += 5   # one for cash, two for totals, two for portfolio totals

    if num_columns < 2:
        # if there are no stocks in the portfolio
        num_columns = 2

    screen_grid = wx.grid.Grid(wxWindow, -1, size=size, pos=position)
    screen_grid.CreateGrid(num_rows, num_columns)
    screen_grid.EnableEditing(enable_editing)

    # fill in grid
    for attribute in attribute_list:
        screen_grid.SetColLabelValue(attribute_list.index(attribute), str(attribute))

    row_count = 0
    total_equity_value = 0.
    total_cost_basis = 0.
    total_equity_value_change = 0.
    total_equity_value_fail = False
    cost_basis_fail = False
    current_time = time.time()
    for stock in stock_list:
        col_count = 0

        ticker = stock.symbol
        if ticker:
            screen_grid.SetCellValue(row_count, 0, ticker)

        firm_name = stock.firm_name
        if firm_name:
            screen_grid.SetCellValue(row_count, 1, firm_name)

        shares_held = account_obj.stock_shares_dict.get(stock.symbol)
        if shares_held:
            if shares_held.is_integer():
                shares_held = int(shares_held)
            screen_grid.SetCellValue(row_count, 2, str(shares_held))
            screen_grid.SetCellAlignment(row_count, 2, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)


        last_close_and_update_tuple = utils.return_last_close_and_last_update_tuple(stock)

        last_close = last_close_and_update_tuple[0]
        last_update_for_last_close = last_close_and_update_tuple[1]
        if last_close:
            if (current_time - last_update_for_last_close) < config.PORTFOLIO_PRICE_REFRESH_TIME:
                screen_grid.SetCellValue(row_count, 3, config.locale.currency(last_close, grouping = True))
                screen_grid.SetCellAlignment(row_count, 3, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
            else:
                screen_grid.SetCellValue(row_count, 3, "update prices")
                screen_grid.SetCellAlignment(row_count, 3, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
                screen_grid.SetCellTextColour(row_count, 3, config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)
                last_close = None


        calc_equity_value = False
        try:
            shares_held = float(shares_held)
            last_close = float(last_close)
            calc_equity_value = True
        except:
            pass
        equity_value = None
        if calc_equity_value:
            equity_value = shares_held * last_close
        if equity_value:
            screen_grid.SetCellValue(row_count, 4, config.locale.currency(equity_value, grouping = True))
            screen_grid.SetCellAlignment(row_count, 4, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
            total_equity_value += equity_value
        else:
            total_equity_value_fail = True

        cost_basis = account_obj.cost_basis_dict.get(stock.symbol)
        if cost_basis:
            screen_grid.SetCellValue(row_count, 5, config.locale.currency(cost_basis, grouping = True))
            screen_grid.SetCellAlignment(row_count, 5, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
            total_cost_basis += cost_basis
        else:
            cost_basis_fail = True

        calc_equity_profit = False
        try:
            cost_basis = float(cost_basis)
            equity_value = float(equity_value)
            calc_equity_profit = True
        except:
            pass
        equity_value_change = None
        if calc_equity_profit:
            equity_value_change = ((equity_value/cost_basis) - 1) * 100
        if equity_value_change:
            screen_grid.SetCellValue(row_count, 6, "%.2f" % (equity_value_change) + "%")
            if equity_value_change < 0:
                screen_grid.SetCellTextColour(row_count, 6, config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)
            screen_grid.SetCellAlignment(row_count, 6, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
        row_count += 1

    row_count += 1 # empty row

    if total_equity_value or total_cost_basis:
        screen_grid.SetCellValue(row_count, 1, "Equity Totals:")
    if (not total_equity_value_fail) and total_equity_value:
        screen_grid.SetCellValue(row_count, 4, config.locale.currency(total_equity_value, grouping = True))
        screen_grid.SetCellAlignment(row_count, 4, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)

    if (not cost_basis_fail) and total_cost_basis:
        screen_grid.SetCellValue(row_count, 5, config.locale.currency(total_cost_basis, grouping = True))
        screen_grid.SetCellAlignment(row_count, 5, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)

    if (not (total_equity_value_fail or cost_basis_fail)) and total_cost_basis:
        total_equity_value_change = ((total_equity_value/total_cost_basis) - 1) * 100
        screen_grid.SetCellValue(row_count, 6, "%.2f" % (total_equity_value_change) + "%")
        if total_equity_value_change < 0:
            screen_grid.SetCellTextColour(row_count, 6, config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)
        screen_grid.SetCellAlignment(row_count, 6, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)

    total_portfolio_value = None
    if not total_equity_value_fail:
        total_portfolio_value = total_equity_value + account_obj.available_cash

    row_count += 1
    screen_grid.SetCellValue(row_count, 1, "Cash:")
    if total_portfolio_value:
        percentage_cash = (float(account_obj.available_cash) / total_portfolio_value) * 100
        screen_grid.SetCellValue(row_count, 2, "%.2f" % (percentage_cash) + "%")
        screen_grid.SetCellAlignment(row_count, 2, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)
    screen_grid.SetCellValue(row_count, 4, config.locale.currency(account_obj.available_cash, grouping = True))
    screen_grid.SetCellAlignment(row_count, 4, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)


    row_count += 2
    screen_grid.SetCellValue(row_count, 1, "Total Portfolio Value:")
    if total_portfolio_value:
        screen_grid.SetCellValue(row_count, 4, config.locale.currency(total_portfolio_value, grouping = True))
        screen_grid.SetCellAlignment(row_count, 4, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_BOTTOM)


    screen_grid.AutoSizeColumns()

    return screen_grid


def create_spread_sheet_for_one_stock(
    wxWindow,
    ticker,
    size = (980, 637),
    position = (0,60),
    enable_editing = False,
    search_term = None
    ):

    stock = utils.return_stock_by_symbol(ticker)

    if not stock:
        print line_number(), 'Ticker "%s" does not appear to have basic data' % ticker
        return

    attribute_list = []
    num_columns = 2 # for this we only need two columns
    num_rows = 0
    # Here we make rows for each attribute to be included
    num_attributes = 0
    if stock:
        for attribute in dir(stock):
            if not attribute.startswith('_'):
                if attribute not in config.CLASS_ATTRIBUTES:
                    if search_term: # this is for searching within stock data, will be None on normal load.
                        if str(search_term).lower() in str(attribute).lower() or str(search_term).lower() in str(getattr(stock, attribute)).lower():
                            pass
                        else:
                            if attribute in ['symbol', 'firm_name']:
                                pass
                            else:
                                continue
                    if attribute not in attribute_list:
                        num_attributes += 1
                        attribute_list.append(str(attribute))
                    else:
                        print line_number(), "%s.%s" % (ticker, attribute), "is a duplicate"


    if num_rows < num_attributes:
        num_rows = num_attributes

    screen_grid = wx.grid.Grid(wxWindow, -1, size=size, pos=position)

    screen_grid.CreateGrid(num_rows, num_columns)
    screen_grid.EnableEditing(enable_editing)

    if not attribute_list:
        logging.warning('attribute list empty')
        return
    attribute_list.sort(key = lambda x: x.lower())
    # adjust list order for important terms
    attribute_list.insert(0, attribute_list.pop(attribute_list.index('symbol')))
    attribute_list.insert(1, attribute_list.pop(attribute_list.index('firm_name')))

    # fill in grid
    col_count = 1 # data will go on the second row
    row_count = 0
    for attribute in attribute_list:
        # set attributes to be labels if it's the first run through
        if row_count == 0:
            screen_grid.SetColLabelValue(0, "attribute")
            screen_grid.SetColLabelValue(1, "data")

        try:
            # Add attribute name
            screen_grid.SetCellValue(row_count, col_count-1, str(attribute))

            # Try to add basic data value
            screen_grid.SetCellValue(row_count, col_count, str(getattr(stock, attribute)))

            # Change text red if value is negative
            if str(getattr(stock, attribute)).startswith("(") or str(getattr(stock, attribute)).startswith("-") and len(str(getattr(stock, attribute))) > 1:
                screen_grid.SetCellTextColour(row_count, col_count, config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)

        except Exception as e:
            print line_number(), e

        row_count += 1

    screen_grid.AutoSizeColumns()

    return screen_grid
# ###########################################################################################
# ###################### Screening functions ###############################################
def screen_pe_less_than_10():
    global GLOBAL_STOCK_LIST
    screen = []
    for stock in GLOBAL_STOCK_LIST:
        try:
            if stock.PERatio:
                if float(stock.PERatio) < 10:
                    screen.append(stock)
        except Exception, e:
            print line_number(),e
    return screen
# ###########################################################################################

# end of line