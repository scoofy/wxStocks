#################################################################
# 	Most of the wxPython in wxStocks is located here. 			#
# 	Table of Contents: 											#
# 		1: Imports and line_number function 					#
# 		2: Main Frame, where tab order is placed. 				#
# 		3: Tabs 												#
# 		4: Grid objects 										#
#################################################################
import wx, numpy
import config, threading, logging, sys, time, os, math
import inspect
import pprint as pp

from collections import namedtuple
from wx.lib import sheet

from wxStocks_classes import Stock, Account
import wxStocks_db_functions as db
import wxStocks_utilities as utils
import wxStocks_scrapers as scrape
import wxStocks_screen_functions as screen
import wxStocks_meta_functions as meta
import wxStocks_functions_that_process_user_functions as process_user_function

def line_number():
	"""Returns the current line number in our program."""
	line_number = inspect.currentframe().f_back.f_lineno
	line_number_string = "Line %d:" % line_number
	return line_number_string



class MainFrame(wx.Frame): # reorder tab postions here
	def __init__(self, *args, **kwargs):
		wx.Frame.__init__(self, None, title="wxStocks", *args, **kwargs)

		# There seems to be a major bug with osx at this point with message dialogs... cannot get code below functional.

		# Confirm encryption if module not installed
		# try:
		# 	import Crypto
		# 	from modules import simplecrypt
		# 	print line_number(), "Remove this and the following test line."
		# 	import force_error
		# 	yesNoAnswer = None
		# except Exception, e:
		# 	print e
		# 	print line_number(), 'Change "Error" to "Crypto" before deploying.'
		# 	confirm = wx.MessageDialog(self, 
		# 								   "Without the pycrypto module functioning, if you import your portfolios, they will not be encrypted when saved. This will leave your data vulnurable to theft, possibly exposing your positions and net worth.", 
		# 								   'You do not have pycrypto installed.', 
		# 								   style = wx.YES_NO
		# 								   )
		# 	confirm.SetYesNoLabels(("&Close"), ("&I Understand And Want To Continue Without Encryption"))
		# 	#yesNoAnswer = confirm.ShowModal()
		# 	if confirm.ShowModal() != wx.ID_YES:
		# 		yesNoAnswer = wx.ID_NO
		# 		print "No!"
		# 	else:
		# 		yesNoAnswer = wx.ID_YES
		# 		print "Yes!!!"
		# if yesNoAnswer == wx.ID_YES:
		# 	sys.exit()
		# else:
		# 	if yesNoAnswer:
		# 		confirm.Destroy()

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
		notebook = wx.Notebook(main_frame)


		# create the page windows as children of the notebook
		# add the pages to the notebook with the label to show on the tab
		self.welcome_page = WelcomePage(notebook)
		notebook.AddPage(self.welcome_page, "Welcome")

		self.ticker_list_page = TickerPage(notebook)
		notebook.AddPage(self.ticker_list_page, "Tickers")

		self.yql_scrape_page = YqlScrapePage(notebook)
		notebook.AddPage(self.yql_scrape_page, "Scrape")

		self.spreadsheet_import_page = SpreadsheetImportPage(notebook)
		notebook.AddPage(self.spreadsheet_import_page, "Import Data")

		self.all_stocks_page = AllStocksPage(notebook)
		notebook.AddPage(self.all_stocks_page, "Stocks")

		self.stock_screen_page = ScreenPage(notebook)
		notebook.AddPage(self.stock_screen_page, "Screen")

		self.saved_screen_page = SavedScreenPage(notebook)
		notebook.AddPage(self.saved_screen_page, "Saved Screens")

		self.rank_page = RankPage(notebook)
		notebook.AddPage(self.rank_page, "Rank")

		self.sale_prep_page = SalePrepPage(notebook)
		notebook.AddPage(self.sale_prep_page, "Sale Prep")

		self.trade_page = TradePage(notebook)
		notebook.AddPage(self.trade_page, "Trade")

		self.portfolio_page = PortfolioPage(notebook)
		notebook.AddPage(self.portfolio_page, "Portfolios")

		self.stock_data_page = StockDataPage(notebook)
		notebook.AddPage(self.stock_data_page, "Ticker Data")

		self.user_functions_page = UserFunctionsPage(notebook)
		notebook.AddPage(self.user_functions_page, "Functions")

		# finally, put the notebook in a sizer for the panel to manage
		# the layout


		sizer = wx.BoxSizer()
		sizer.Add(notebook, 1, wx.EXPAND)
		main_frame.SetSizer(sizer)

		print line_number(), "\n\n", "------------------------- wxStocks startup complete -------------------------", "\n"
class Tab(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

# ###################### wx tabs #########################################################
class WelcomePage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		welcome_page_text = wx.StaticText(self, -1, 
							 "Welcome to wxStocks", 
							 (10,10)
							 )
		instructions_text = '''

	Instructions: 	this program is essentially a work-flow following the tabs above.
	---------------------------------------------------------------------------------------------------------------------------------

	Tickers:		This page is where you download ticker .CSV files to create a list of tickers to scrape.

	YQL Scrape:		This page takes all tickers, and then scrapes current stock data using them.

	Stocks:		This page generates a list of all stocks that have been scraped and presents all the data about them.
				Use this page to double check your data to make sure it's accurate and up to date.

	Screen:		This page allows you to screen for stocks that fit your criteria, and save them for later.

	Saved Screens:	This page allows you to recall old screens you've saved.

	Rank:		This page allows you to rank stocks along certain criteria. 

	Sale Prep:	This page allows you to estimate the amount of funds generated from a potential stock sale.

	Trade:		This page (currently not functional) takes the stocks you plan to sell, estimates the amount of money generated, 
				and lets you estimate the volume of stocks to buy to satisfy your diversification requirements.

	Portfolio:	This page allows you to load your portfolios from which you plan on making trades.
				If you have more than one portfolio you plan on working from, you may add more.
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
		# 	self.encryption_status = "ON:"
		# 	try:
		# 		import Crypto
		# 		from modules.simplecrypt import encrypt, decrypt
		# 	except:
		# 		print line_number(), "Encryption not possible"
		# 		self.encryption_message_default = "Encryption is not possible. You should make sure pyCrypto and simplecrypt are installed to use encryption for your personal data."
		# 		self.encryption_status = ""
		# 		self.turn_encryption_off_button.Hide()
		# 	self.turn_encryption_on_button.Hide()
		# else:
		# 	self.encryption_status = "OFF:"
		# 	try:
		# 		import Crypto
		# 		from modules.simplecrypt import encrypt, decrypt
		# 	except:
		# 		print line_number(), "Encryption not possible"
		# 		self.encryption_message_default = "Encryption is not possible. You should make sure pyCrypto and simplecrypt are installed to use encryption for your personal data."
		# 		self.encryption_status = ""
		# 		self.turn_encryption_on_button.Hide()
		# 	self.turn_encryption_off_button.Hide()


		# self.encryption_message = wx.StaticText(self, -1, 
		# 							self.encryption_message_default + self.encryption_status, 
		# 							(encryption_text_horizontal_position, encryption_text_vertical_position)
		# 							)

		self.reset_password_button = None
		self.reset_password_button_horizontal_position = 10
		self.reset_password_button_vertical_position = 550
		
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

		print line_number(), "WelcomePage loaded"

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

	######################### below is not used ###########################
	# def toggleEncryption(self, event):
	# 	if config.ENCRYPTION_POSSIBLE:
	# 		remove = self.checkRemoveEncryption()
	# 		if not remove:
	# 			return
	# 	config.ENCRYPTION_POSSIBLE = not config.ENCRYPTION_POSSIBLE
	# 	if config.ENCRYPTION_POSSIBLE:
	# 		self.turn_encryption_on_button.Hide()
	# 		self.turn_encryption_off_button.Show()
	# 		self.encryption_status = "ON:"
	# 	else:
	# 		self.turn_encryption_off_button.Hide()
	# 		self.turn_encryption_on_button.Show()
	# 		self.encryption_status = "OFF:"
	# 	print line_number(), "Encryption has been turned %s." % self.encryption_status
	# 	self.encryption_message.SetLabel(self.encryption_message_default + self.encryption_status)


	# def checkRemoveEncryption(self):
	# 	confirm = wx.MessageDialog(None, 
	# 							   "Are you sure you want to remove automatic encryption?", 
	# 							   'Remove Encryption?', 
	# 							   style = wx.YES_NO
	# 							   )
	# 	confirm.SetYesNoLabels(("&Yes, Remove Encryption"), ("&Cancel"))
	# 	yesNoAnswer = confirm.ShowModal()
	# 	confirm.Destroy()
	# 	return yesNoAnswer == wx.ID_YES
	######################### above is not used ###########################


class TickerPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		text = wx.StaticText(self, -1, 
							 "Welcome to the ticker page.", 
							 (10,10)
							 )
		download_button = wx.Button(self, label="Download Tickers", pos=(5, 30), size=(-1,-1))
		download_button.Bind(wx.EVT_BUTTON, self.confirmDownloadTickers, download_button) 

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
		#	confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
		#except AttributeError:
		#	pass
		confirm.Destroy()

		if yesNoAnswer == wx.ID_YES:
			self.downloadTickers()

	def downloadTickers(self):
		print line_number(), "Begin ticker download..."
		ticker_data = scrape.download_ticker_symbols()
		self.saveTickerDataAsStocks(ticker_data)
		self.showAllTickers()
		# Update scrape page?
		# Don't want to take the time to figure this out just now.
		print line_number(), "Add function here to update scrape time."


	def saveTickerDataAsStocks(self, ticker_data_from_download):
		# first check for stocks that have fallen off the stock exchanges
		ticker_list = []
		dead_tickers = []

		# create a list of tickers
		for ticker_data_sublist in ticker_data_from_download:
			print ticker_data_sublist[0] + ":", ticker_data_sublist[1]

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
			print "Saving:", stock.ticker, stock.firm_name
		db.save_GLOBAL_STOCK_DICT()

	def showAllTickers(self):
		print line_number(), "Loading Tickers"
		ticker_list = []
		for ticker in config.GLOBAL_STOCK_DICT:
			if config.GLOBAL_STOCK_DICT[ticker].ticker_relevant:
				ticker_list.append(ticker)
		ticker_list.sort()
		self.displayTickers(ticker_list)
		self.Show()
		print line_number(), "Done"

	def displayTickers(self, ticker_list):
		ticker_list.sort()
		ticker_list_massive_str = ""
		for ticker in ticker_list:
			ticker_list_massive_str += ticker
			ticker_list_massive_str += ", "
		height_var = 100
		file_display = wx.TextCtrl(self, -1, 
									ticker_list_massive_str, 
									(10, height_var),
									size = (765, 625),
									style = wx.TE_READONLY | wx.TE_MULTILINE ,
									)
class YqlScrapePage(Tab):
	def __init__(self, parent):
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
		#	confirm.SetYesNoLabels(("&Scrape"), ("&Cancel"))
		#except AttributeError:
		#	pass
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

		#	# Every two sleep times execute a new scrape
		#	full_scrape_sleep = float(sleep_time * 2)
		#	scrape_thread.join(full_scrape_sleep)
		#	cont, skip = progress_dialog.Update(self.numScrapedStocks)
		#	if not cont:
		#		progress_dialog.Destroy()
		#		return

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
		#	self.progress_dialog.Destroy()
		#	return


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
			print "ready to loop again"
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
		wx.Panel.__init__(self, parent)
		####
		spreadsheet_page_panel = wx.Panel(self, -1, pos=(0,5), size=( wx.EXPAND, wx.EXPAND))
		spreadsheet_notebook = wx.Notebook(spreadsheet_page_panel)

		self.csv_import_page = CsvImportPage(spreadsheet_notebook)
		spreadsheet_notebook.AddPage(self.csv_import_page, "Import .CSV Data")		

		self.xls_import_page = XlsImportPage(spreadsheet_notebook)
		spreadsheet_notebook.AddPage(self.xls_import_page, "Import .XLS Data")		


		sizer2 = wx.BoxSizer()
		sizer2.Add(spreadsheet_notebook, 1, wx.EXPAND)
		self.SetSizer(sizer2)		
		####
class CsvImportPage(Tab):
	def __init__(self, parent):
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
		wx.Panel.__init__(self, parent)
		text = wx.StaticText(self, -1, 
							 "Welcome to the XLS data import page page.\nYou can make your own import functions under the function tab.", 
							 (10,10)
							 )

		default_button_horizontal_position = 0
		default_button_vertical_position = 50
		default_dropdown_horizontal_offset = 100
		default_dropdown_vertical_offset = 0

		import_button = wx.Button(self, label="import .xls", pos=(default_button_horizontal_position, default_button_vertical_position), size=(-1,-1))
		import_button.Bind(wx.EVT_BUTTON, self.importXLS, import_button)

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
class AllStocksPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		welcome_page_text = wx.StaticText(self, -1, 
							 "Full Stock List", 
							 (10,10)
							 )

		self.spreadsheet = None

		refresh_button = wx.Button(self, label="refresh", pos=(110,4), size=(-1,-1))
		refresh_button.Bind(wx.EVT_BUTTON, self.spreadSheetFillAllStocks, refresh_button)

		self.first_spread_sheet_load = True

		print line_number(), "AllStocksPage loaded"

	def spreadSheetFillAllStocks(self, event):
		if self.first_spread_sheet_load:		
			self.first_spread_sheet_load = False
		else:
			try:
				self.spreadsheet.Destroy()
			except Exception, exception:
				print line_number(), exception

		# Create correctly sized grid
		self.spreadsheet = GridAllStocks(self, -1, size=(1000,680), pos=(0,50))
		self.spreadsheet.CreateGrid(self.spreadsheet.num_rows, self.spreadsheet.num_columns)
		self.spreadsheet.EnableEditing(False)

		# Find all attribute names
		stock_list = utils.return_all_stocks()

		print "remove code below", line_number()
		stock_list = utils.return_stocks_with_data_errors()
		stock_list = stock_list + utils.return_all_stocks()
		print "and above", line_number()

		attribute_list = []
		all_attribute_list = []
		for stock in stock_list:
			all_attribute_list = all_attribute_list + list(dir(stock))
			all_attribute_list = set(all_attribute_list) # remove duplicates
			all_attribute_list = list(all_attribute_list)
		# Eliminate non-finance related attributes
		for attribute in all_attribute_list:
			if not attribute.startswith('_'):
				attribute_list.append(str(attribute))
		# Sort for readability
		pp.pprint(attribute_list)
		attribute_list.sort(key=lambda x: x.lower())
		pp.pprint(attribute_list)

		# adjust list order for important terms
		try:
			attribute_list.insert(0, attribute_list.pop(attribute_list.index('symbol')))
		except Exception, e:
			print line_number(), e
		try:
			attribute_list.insert(1, attribute_list.pop(attribute_list.index('firm_name')))
		except Exception, e:
			print line_number(), e
		#print line_number(), attribute_list

		row_count = 0
		col_count = 0

		# set first row attribute names
		for attribute in attribute_list:
			self.spreadsheet.SetColLabelValue(col_count, str(attribute))
			col_count += 1
		col_count = 0

		# fill in the stocks' values
		for stock in stock_list:
			for attribute in attribute_list:
				try:
					self.spreadsheet.SetCellValue(row_count, col_count, str(getattr(stock, attribute)))
				except:
					pass
				col_count += 1
			row_count += 1
			col_count = 0
		
		# resize calumns
		self.spreadsheet.AutoSizeColumns()
class ScreenPage(Tab):
	def __init__(self, parent):
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

		self.save_screen_button = wx.Button(self, label="save", pos=(900,4), size=(-1,-1))
		self.save_screen_button.Bind(wx.EVT_BUTTON, self.saveScreen, self.save_screen_button)
		self.save_screen_button.Hide()

		self.screen_grid = None

		self.first_spread_sheet_load = True

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
		
		if self.first_spread_sheet_load:
			self.first_spread_sheet_load = False
		else:
			try:
				self.screen_grid.Destroy()
			except Exception as e:
				print line_number(), e
		self.screen_grid = StockScreenGrid(self, -1, size=(1000,680), pos=(0,50))
		self.screen_grid.CreateGrid(self.screen_grid.num_rows, self.screen_grid.num_columns)
		self.spreadSheetFill(self.screen_grid, conforming_stocks)

		self.save_screen_button.Show()

		print line_number(), "screenStocks done!"

	def spreadSheetFill(self, spreadsheet, stock_list):
		create_spreadsheet_from_stock_list(spreadsheet, stock_list)



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

				self.save_screen_button.Hide()
				save_popup.Destroy()
				return
class SavedScreenPage(Tab):
	def __init__(self, parent):
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
			self.existing_screen_name_list = [i[0] for i in config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST]

		self.drop_down = wx.ComboBox(self, value="",
									 pos=(305, 6), 
									 choices=self.existing_screen_name_list,
									 style = wx.TE_READONLY
									 )

		self.currently_viewed_screen = None
		self.delete_screen_button = wx.Button(self, label="delete", pos=(900,4), size=(-1,-1))
		self.delete_screen_button.Bind(wx.EVT_BUTTON, self.deleteScreen, self.delete_screen_button)
		self.delete_screen_button.Hide()

		self.first_spread_sheet_load = True		
		self.screen_grid = None

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

		self.existing_screen_name_list = [i[0] for i in config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST]


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
		self.screen_grid = SavedScreenGrid(self, -1, size=(980,637), pos=(0,50))
		self.screen_grid.CreateGrid(self.screen_grid.num_rows, self.screen_grid.num_columns)
		
		create_spreadsheet_from_stock_list(self.screen_grid, config.CURRENT_SAVED_SCREEN_LIST)
		
		self.delete_screen_button.Show()

class RankPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.full_ticker_list = [] # this should hold all tickers in any spreadsheet displayed
		self.held_ticker_list = [] # not sure if this is relevant anymore
		# Changed to config.RANK_PAGE_ALL_RELEVANT_STOCKS
		self.sorted_full_ticker_list = []


		self.lists_in_ticker_list = [] # currently unused

		self.full_attribute_list = []
		self.relevant_attribute_list = []

		rank_page_text = wx.StaticText(self, -1, 
							 "Rank", 
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
			self.existing_screen_name_list = [i[0] for i in config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST] # add conditional to remove old screens
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
		self.clear_button = wx.Button(self, label="clear", pos=(900,4), size=(-1,-1))
		self.clear_button.Bind(wx.EVT_BUTTON, self.clearGrid, self.clear_button)
		self.clear_button.Hide()

		self.sort_button = wx.Button(self, label="Sort by:", pos=(420,30), size=(-1,-1))
		self.sort_button.Bind(wx.EVT_BUTTON, self.sortStocks, self.sort_button)
		self.sort_drop_down = wx.ComboBox(self, 
									 pos=(520, 31), 
									 choices=self.full_attribute_list,
									 style = wx.TE_READONLY
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
		self.screen_grid = None

		self.rank_name = None

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

		######################################
		self.screen_grid = self.createRankedSpreadSheet(ranked_tuple_list, self.rank_name)
		try:
			self.sort_drop_down.Destroy()
			self.sort_drop_down = wx.ComboBox(self, 
											 pos=(520, 31), 
											 choices = self.relevant_attribute_list,
											 style = wx.TE_READONLY
											 )
		except Exception, exception:
			pass
			#print line_number(), exception
		self.clear_button.Show()
		self.sort_button.Show()
		self.sort_drop_down.Show()
		self.rank_button.Show()
		self.rank_drop_down.Show()


		print line_number(), "rankStocks done!"

	def createRankedSpreadSheet(
		self
		, stock_value_tuple_list 
		, relevant_value_name
		, height = 637
		, width = 980
		, position = (0,60)
		, enable_editing = False
		):

		irrelevant_attributes = config.IRRELEVANT_ATTRIBUTES


		config.TICKER_AND_ATTRIBUTE_TO_UPDATE_TUPLE_LIST = [] # Clear update list


		num_rows = len(stock_value_tuple_list)
		num_columns = 0

		stock_list = [x.stock for x in stock_value_tuple_list]

		for my_tuple in stock_value_tuple_list:
			print line_number(), my_tuple.stock.symbol, my_tuple.value

		attribute_list = [relevant_value_name]
		# Here we make columns for each attribute to be included
		for stock in stock_list:
			for attribute in dir(stock):
				if not attribute.startswith('_'):
					if attribute not in config.IRRELEVANT_ATTRIBUTES:
						if attribute not in attribute_list:
							attribute_list.append(str(attribute))
			if num_columns < len(attribute_list):
				num_columns = len(attribute_list)		

		if stock_list and not attribute_list:
			print line_number(), 'Warning: attribute list empty'
			return
		# else: loading blank list

		screen_grid = wx.grid.Grid(self, -1, size=(width, height), pos=position)
		screen_grid.CreateGrid(num_rows, num_columns)
		screen_grid.EnableEditing(enable_editing)

		if attribute_list: # not empty screen loading:
			attribute_list.sort(key = lambda x: x.lower())
			# adjust list order for important terms
			attribute_list.insert(0, attribute_list.pop(attribute_list.index('symbol')))
			attribute_list.insert(1, attribute_list.pop(attribute_list.index('firm_name')))
			attribute_list.insert(2, attribute_list.pop(attribute_list.index(relevant_value_name)))

		self.full_attribute_list = attribute_list
		self.relevant_attribute_list = [attribute for attribute in attribute_list if attribute not in config.IRRELEVANT_ATTRIBUTES]



		# fill in grid
		row_count = 0
		for stock_value_tuple in stock_value_tuple_list:
			col_count = 0
			for attribute in attribute_list:
				relevant_value_col = False # reset this at the begining of iteration
				# set attributes to be labels if it's the first run through
				if row_count == 0:
					screen_grid.SetColLabelValue(col_count, str(attribute))
				if attribute == relevant_value_name:
					screen_grid.SetCellValue(row_count, col_count, str(stock_value_tuple.value))
					relevant_value_col = True
				if not relevant_value_col:
					try:
						# Try to add basic data value
						screen_grid.SetCellValue(row_count, col_count, str(getattr(stock_value_tuple.stock, attribute)))
						# Add color if relevant
						if str(stock_value_tuple.stock.ticker) in config.HELD_STOCK_TICKER_LIST:
							screen_grid.SetCellBackgroundColour(row_count, col_count, config.HELD_STOCK_COLOR_HEX)
						# Change text red if value is negative
						try:
							if utils.stock_value_is_negative(stock_value_tuple.stock, attribute):
								screen_grid.SetCellTextColour(row_count, col_count, config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)
						except Exception as exception:
							pass
							#print line_number(), exception
					except Exception as exception:
						pass
						#print line_number(), exception
				col_count += 1
			row_count += 1
		screen_grid.AutoSizeColumns()

		return screen_grid


	def createSpreadSheet(self, stock_list):
		self.screen_grid = create_spread_sheet(self, stock_list)
		try:
			self.sort_drop_down.Destroy()
			self.sort_drop_down = wx.ComboBox(self, 
											 pos=(520, 31), 
											 choices = self.relevant_attribute_list,
											 style = wx.TE_READONLY
											 )
		except Exception, exception:
			pass
			#print line_number(), exception
		self.clear_button.Show()
		self.sort_button.Show()
		self.sort_drop_down.Show()
		self.rank_button.Show()
		self.rank_drop_down.Show()


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

		self.createSpreadSheet(stock_list= config.RANK_PAGE_ALL_RELEVANT_STOCKS)


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
			self.existing_screen_name_list = [i[0] for i in config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST]
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
				print line_number(), stock.symbol, "added to config.RANK_PAGE_ALL_RELEVANT_STOCKS"
				config.RANK_PAGE_ALL_RELEVANT_STOCKS.append(stock)
			else:
				print line_number(), stock.symbol, "skipped"
		if possibly_remove_dead_stocks:
			for dead_stock in possibly_remove_dead_stocks:
				try:
					saved_screen.remove(dead_stock)
				except:
					pass
				try:
					config.RANK_PAGE_ALL_RELEVANT_STOCKS.remove(dead_stock)
				except:
					pass
			db.save_named_screen(selected_screen_name, saved_screen)

		if self.screen_grid:
			try:
				self.screen_grid.Destroy()
			except Exception, exception:
				print line_number(), exception

		self.createSpreadSheet(stock_list = config.RANK_PAGE_ALL_RELEVANT_STOCKS)

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

		try:
			self.screen_grid.Destroy()
		except Exception, exception:
			print line_number(), exception

		#self.spreadSheetFill(self.full_ticker_list)
		self.createSpreadSheet(stock_list = config.RANK_PAGE_ALL_RELEVANT_STOCKS)

	def spreadSheetFill(self, stock_list):
		pass
		# attribute_list = []
		# num_rows = len(stock_list)
		# num_columns = 0
		# for stock in stock_list:
		# 	num_attributes = 0
		# 	for attribute in dir(stock):
		# 		if not attribute.startswith('_'):
		# 			if attribute not in self.irrelevant_attributes:
		# 				num_attributes += 1
		# 	for annual_data in annual_data_list:
		# 		if str(stock.symbol) == str(annual_data.symbol):
		# 			for attribute in dir(annual_data):
		# 				if not attribute.startswith('_'):
		# 					if attribute not in self.irrelevant_attributes:
		# 						if not attribute[-4:-2] in ["20", "30"]: # this checks to see that only most recent annual data is shown. this hack is good for 200 years!!!
		# 							if str(attribute) != 'symbol': # here symbol will appear twice, once for stock, and another time for annual data, in the attribute list below it will be redundant and not added, but if will here if it's not skipped
		# 								num_attributes += 1
		# 	for estimate_data in analyst_estimate_list:
		# 		if str(stock.symbol) == str(estimate_data.symbol):
		# 			for attribute in dir(estimate_data):
		# 				if not attribute.startswith('_'):
		# 					if attribute not in self.irrelevant_attributes:
		# 						num_attributes += 1
		# 	if num_columns < num_attributes:
		# 		num_columns = num_attributes
		# self.screen_grid = StockScreenGrid(self, -1, size=(980,637), pos=(0,60))

		# self.screen_grid.CreateGrid(num_rows, num_columns)
		# self.screen_grid.EnableEditing(False)


		# for stock in stock_list:
		# 	for attribute in dir(stock):
		# 		if not attribute.startswith('_'):
		# 			if attribute not in self.irrelevant_attributes:
		# 				if attribute not in attribute_list:
		# 					attribute_list.append(str(attribute))
		# 					if str(attribute) not in self.full_attribute_list:
		# 						self.full_attribute_list.append(str(attribute)) # Reset root attribute list
		# 	for annual_data in annual_data_list:
		# 		if str(stock.symbol) == str(annual_data.symbol):
		# 			for attribute in dir(annual_data):
		# 				if not attribute.startswith('_'):
		# 					if attribute not in self.irrelevant_attributes:
		# 						if not attribute[-3:] in ["t1y", "t2y"]: # this checks to see that only most recent annual data is shown. this hack is good for 200 years!!!
		# 							if attribute not in attribute_list:
		# 								attribute_list.append(str(attribute))
		# 								if str(attribute) not in self.full_attribute_list:
		# 									self.full_attribute_list.append(str(attribute)) # Reset root attribute list					
		# 			break
		# 	for estimate_data in analyst_estimate_list:
		# 		if str(stock.symbol) == str(estimate_data.symbol):
		# 			for attribute in dir(estimate_data):
		# 				if not attribute.startswith('_'):
		# 					if attribute not in self.irrelevant_attributes:
		# 						if attribute not in attribute_list:
		# 							attribute_list.append(str(attribute))
		# 							if str(attribute) not in self.full_attribute_list:
		# 								self.full_attribute_list.append(str(attribute)) # Reset root attribute list					
		# 			break

		# #for i in self.full_attribute_list:
		# #	print line_number(), i
		# if not attribute_list:
		# 	logging.warning('attribute list empty')
		# 	return
		# attribute_list.sort()
		# # adjust list order for important terms
		# attribute_list.insert(0, attribute_list.pop(attribute_list.index('symbol')))
		# attribute_list.insert(1, attribute_list.pop(attribute_list.index('Name')))
		# #print line_number(), attribute_list

		# row_count = 0
		# for stock in stock_list:
		# 	col_count = 0
		# 	stock_annual_data = return_existing_StockAnnualData(str(stock.symbol))
		# 	stock_analyst_estimate = return_existing_StockAnalystEstimates(str(stock.symbol))
		# 	for attribute in attribute_list:
		# 		#if not attribute.startswith('_'):
		# 		if row_count == 0:
		# 			self.screen_grid.SetColLabelValue(col_count, str(attribute))
		# 			#print str(attribute)
		# 		try:
		# 			self.screen_grid.SetCellValue(row_count, col_count, str(getattr(stock, attribute)))
		# 			if str(stock.symbol) in self.held_ticker_list:
		# 				self.screen_grid.SetCellBackgroundColour(row_count, col_count, "#FAEFCF")
		# 			if str(getattr(stock, attribute)).startswith("(") or str(getattr(stock, attribute)).startswith("-"):
		# 				self.screen_grid.SetCellTextColour(row_count, col_count, "#8A0002")
		# 		except Exception, exception:
		# 			try:
		# 				self.screen_grid.SetCellValue(row_count, col_count, str(getattr(stock_annual_data, attribute)))
		# 				if str(stock.symbol) in self.held_ticker_list:
		# 					self.screen_grid.SetCellBackgroundColour(row_count, col_count, "#FAEFCF")
		# 				if str(getattr(stock_annual_data, attribute)).startswith("(") or (str(getattr(stock_annual_data, attribute)).startswith("-") and len(str(getattr(stock_annual_data, attribute))) > 1):
		# 					self.screen_grid.SetCellTextColour(row_count, col_count, "#8A0002")
		# 			except:
		# 				try:
		# 					self.screen_grid.SetCellValue(row_count, col_count, str(getattr(stock_analyst_estimate, attribute)))
		# 					if str(stock.symbol) in self.held_ticker_list:
		# 						self.screen_grid.SetCellBackgroundColour(row_count, col_count, "#FAEFCF")
		# 					if str(getattr(stock_analyst_estimate, attribute)).startswith("(") or (str(getattr(stock_analyst_estimate, attribute)).startswith("-") and len(str(getattr(stock_analyst_estimate, attribute))) > 0):
		# 						self.screen_grid.SetCellTextColour(row_count, col_count, "#8A0002")
		# 				except Exception, exception:
		# 					pass
		# 					print exception
		# 					print line_number()
		# 			#print line_number(), exception
		# 		# try:
		# 		# 	if str(getattr(stock, attribute)) in ["N/A", "-", "None"]:
		# 		# 		self.screen_grid.SetCellValue(row_count, col_count, "")
		# 		# except:
		# 		# 	try:
		# 		# 		if str(getattr(stock_annual_data, attribute)) in ["N/A", "-", "None"]:
		# 		# 			self.screen_grid.SetCellValue(row_count, col_count, "")
		# 		# 	except Exception, exception:
		# 		# 		pass
		# 		col_count += 1
		# 	row_count += 1
		# #print attribute_list
		# self.screen_grid.AutoSizeColumns()

		# try:
		# 	self.sort_drop_down.Destroy()
		# 	self.sort_drop_down = wx.ComboBox(self, 
		# 									 pos=(520, 31), 
		# 									 choices=self.full_attribute_list,
		# 									 style = wx.TE_READONLY
		# 									 )
		# except Exception, exception:
		# 	pass
		# 	#print line_number(), exception
		# self.clear_button.Show()
		# self.sort_button.Show()
		# self.sort_drop_down.Show()
	def sortStocks(self, event):
		sort_field = self.sort_drop_down.GetValue()
		do_not_sort_reversed = ["symbol", "firm_name"]
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
					float(val.replace("%",""))
					num_stock_value_list.append(stock)
				except:
					str_stock_value_list.append(stock)
			except Exception, exception:
				#print line_number(), exception
				incompatible_stock_list.append(stock)

		num_stock_value_list.sort(key = lambda x: float(getattr(x, sort_field).replace("%","")), reverse=reverse_var)
		
		str_stock_value_list.sort(key = lambda x: getattr(x, sort_field))

		incompatible_stock_list.sort(key = lambda x: x.symbol)

		self.sorted_full_ticker_list = []
		for stock in num_stock_value_list:
			self.sorted_full_ticker_list.append(stock)
		for stock in str_stock_value_list:
			self.sorted_full_ticker_list.append(stock)
		for incompatible_stock in incompatible_stock_list:
			self.sorted_full_ticker_list.append(incompatible_stock)
		#self.spreadSheetFill(self.sorted_full_ticker_list)
		self.createSpreadSheet(self.sorted_full_ticker_list)
		self.sort_drop_down.SetStringSelection(sort_field)

class SalePrepPage(Tab):
	def __init__(self, parent):
		self.default_last_trade_price_attribute_name = "LastTradePriceOnly_yf"
		self.default_average_daily_volume_attribute_name = "AverageDailyVolume_yf"

		wx.Panel.__init__(self, parent)
		trade_page_text = wx.StaticText(self, -1, 
							 "Sale Prep", 
							 (10,10)
							 )
		self.ticker_list = []		
		self.checkbox_list = []
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

		load_new_account_data_button = wx.Button(self, label="Refresh Accounts Data and Spreadsheet", pos=(110,30), size=(-1,-1))
		load_new_account_data_button.Bind(wx.EVT_BUTTON, self.refreshAccountData, load_new_account_data_button)

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
		elif (row_num, col_num) == (3, 14):
			return True
		else:
			return False

	def set_spreadsheet_values(self):
		# colors
		self.carryover_input_color_hex = "#C5DBCA"
		self.num_of_shares_input_color_hex = "#CFE8FC"
		self.percentage_of_shares_input_color_hex = "#CFFCEF"
		self.dark_cell_color_hex = "#333333"


		
		Cell_Reference = namedtuple("Cell_Reference", ["row", "col", "text"])
		
		# row 2
		self.carryover_text_cell = Cell_Reference(2, 14, "Input carryover loss (if any)")

		# row 3
		self.carryover_input_cell = Cell_Reference(3, 14, str(0.00))

		# row 5
		self.num_of_shares_cell 			= Cell_Reference(5, 1, "# of shares to sell")
		self.percent_of_shares_cell 		= Cell_Reference(5, 2, "% of shares to sell")
		self.ticker_cell					= Cell_Reference(5, 3, "Ticker")
		self.syntax_check_cell 				= Cell_Reference(5, 4, "")#Syntax Check")
		self.name_cell 						= Cell_Reference(5, 5, "Name")
		self.sale_check_cell				= Cell_Reference(5, 6, "Sale Check")
		self.number_of_shares_copy_cell 	= Cell_Reference(5, 7, "# of shares to sell")
		self.percent_of_shares_copy_cell	= Cell_Reference(5, 8, "% of shares to sell")
		self.total_shares_cell 				= Cell_Reference(5, 9, "Total # of shares")
		self.price_cell 					= Cell_Reference(5, 10, "Price")
		self.sale_value_cell				= Cell_Reference(5, 11, "Sale Value")
		self.commission_cell 				= Cell_Reference(5, 12, "Commission loss ($%s/trade)" % str(self.commission))
		self.fifo_cell 						= Cell_Reference(5, 13, "FIFO Capital Gains")
		self.adjusted_cap_gains_cell 		= Cell_Reference(5, 14, "Adjusted Capital Gains (including carryovers)")
		self.market_value_cell 				= Cell_Reference(5, 15, "Market Value")
		self.unrealized_cell 				= Cell_Reference(5, 16, "Unrealized Capital +/-")

		self.row_five_cell_list = [
			self.num_of_shares_cell,
			self.percent_of_shares_cell,
			self.ticker_cell,
			self.syntax_check_cell,
			self.name_cell,
			self.sale_check_cell,
			self.number_of_shares_copy_cell,
			self.percent_of_shares_copy_cell,
			self.total_shares_cell,
			self.price_cell,
			self.sale_value_cell,
			self.commission_cell,
			self.fifo_cell,
			self.adjusted_cap_gains_cell,
			self.market_value_cell,
			self.unrealized_cell,
			]

		self.total_number_of_columns = len(self.row_five_cell_list) + 1 # for the first empty one

		# row 7
		self.totals_cell = Cell_Reference(7, 0, "Totals:")

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
					#print not_empty
					if not_empty and not error:
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
		print config.SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE
		self.saved_text.Show()
		
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
		# print color
		# print type(color)
		# print "---------"
		# if color != (255, 255, 255, 255):
		# 	print 'it works'
		# 	self.save_button.Hide()
		# event.Skip()
		
		pass


	def spreadSheetFill(self, event):		
		try:
			self.grid.Destroy()
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

		self.grid = SalePrepGrid(self, -1, size=(1000,650), pos=(0,83))
		self.grid.CreateGrid(num_rows, num_columns)
		self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.updateGrid, self.grid)

		# for editing purposes only
		print line_number(), "remove iteration below"
		for i in range(num_columns):
			self.grid.SetCellValue(0, i, str(i))

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
		self.grid.SetCellValue(2, 0, str(time.time())) # no longer sure why i have this
		self.grid.SetCellValue(self.carryover_text_cell.row, self.carryover_text_cell.col, self.carryover_text_cell.text)
		# set row 3
		self.grid.SetCellValue(self.carryover_input_cell.row, self.carryover_input_cell.col, self.carryover_input_cell.text)

		# set row 7
		self.grid.SetCellValue(self.totals_cell.row, self.totals_cell.col, self.totals_cell.text)
		

		# set row 5
		for cell in self.row_five_cell_list:
			self.grid.SetCellValue(cell.row, cell.col, cell.text)

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
				try:
					self.grid.SetCellValue(row_count, 0, config.PORTFOLIO_NAMES[portfolio_num])
					self.grid.SetCellBackgroundColour(row_count, self.num_of_shares_cell.col, "white")
					self.grid.SetReadOnly(row_count, self.num_of_shares_cell.col, True)
					self.grid.SetCellBackgroundColour(row_count, self.percent_of_shares_cell.col, "white")
					self.grid.SetReadOnly(row_count, self.percent_of_shares_cell.col, True)
					portfolio_num += 1
					row_count += 1

					for ticker, quantity in account.stock_shares_dict.iteritems():

						# set all cell values for stock

						#if row_count == 0:
						#	self.screen_grid.SetColLabelValue(col_count, str(attribute))
						stock = utils.return_stock_by_symbol(ticker)

						cost_basis = utils.return_cost_basis_per_share(account, ticker)

						self.grid.SetCellValue(row_count, self.ticker_cell.col, stock.symbol)
						try:
							self.grid.SetCellValue(row_count, self.name_cell.col, stock.firm_name)
						except Exception, exception:
							print line_number(), exception
						self.grid.SetCellValue(row_count, self.total_shares_cell.col, str(quantity))
						try:
							self.grid.SetCellValue(row_count, self.price_cell.col, getattr(stock, self.default_last_trade_price_attribute_name))
						except Exception, exception:
							print line_number(), exception
						self.grid.SetCellValue(row_count, self.market_value_cell.col, str(float(str(quantity).replace(",","")) * float(getattr(stock, self.default_last_trade_price_attribute_name))))
						row_count += 1
				except Exception as e:
					print line_number(), e
			except Exception as e:
				print line_number(), e, ": An account appears to not be loaded, but this isn't a problem."
		self.grid.AutoSizeColumns()
	
	def updateGrid(self, event):
		row = event.GetRow()
		column = event.GetCol()
		value = self.grid.GetCellValue(row, column)
		num_shares = str(self.grid.GetCellValue(row, self.total_shares_cell.col))
		num_shares = num_shares.replace(",","")
		value = utils.strip_string_whitespace(value)
		price = self.grid.GetCellValue(row, self.price_cell.col)

		if column == self.num_of_shares_cell.col: # sell by number
			try:
				number_of_shares_to_sell = int(value)
			except Exception, exception:
				print line_number(), exception
				number_of_shares_to_sell = None
				#self.setGridError(row) # this should actually be changed below
			#print line_number(), "# of stocks to sell changed"
			self.grid.SetCellValue(row, self.percent_of_shares_cell.col, "")

			if str(number_of_shares_to_sell).isdigit() and num_shares >= number_of_shares_to_sell and number_of_shares_to_sell != 0:
				# No input errors
				self.grid.SetCellValue(row, self.number_of_shares_copy_cell.col, str(number_of_shares_to_sell))
				percent_of_total_holdings = round(100 * float(number_of_shares_to_sell)/float(num_shares))
				self.grid.SetCellValue(row, self.percent_of_shares_copy_cell.col, "%d%%" % percent_of_total_holdings)
				if int(num_shares) == int(number_of_shares_to_sell):
					self.grid.SetCellValue(row, self.sale_check_cell.col, "All")
					self.grid.SetCellTextColour(row, self.sale_check_cell.col, "black")
				else:
					self.grid.SetCellValue(row, self.sale_check_cell.col, "Some")
					self.grid.SetCellTextColour(row, self.sale_check_cell.col, "black")
				sale_value = float(number_of_shares_to_sell) * float(price)
				self.grid.SetCellValue(row, self.sale_value_cell.col, "$%.2f" % sale_value)

				percent_to_commission = 100 * self.commission/sale_value
				self.grid.SetCellValue(row, self.commission_cell.col, "%.2f%%" % percent_to_commission)

			elif value == "" or number_of_shares_to_sell == 0:
				# if zero
				self.grid.SetCellValue(row, self.number_of_shares_copy_cell.col, "")
				self.grid.SetCellValue(row, self.percent_of_shares_copy_cell.col, "")
				self.grid.SetCellValue(row, self.sale_check_cell.col, "")
				self.grid.SetCellTextColour(row, self.sale_check_cell.col, "black")

			else:
				# Bad input
				self.setGridError(row)

		if column == self.percent_of_shares_cell.col: # by % of stock held
			if "%" in value:
				value = value.strip("%")
				try:
					value = float(value)/100
				except Exception, exception:
					print line_number(), exception
					self.setGridError(row)
					return
			else:
				try:
					value = float(value)
					value = value / 100
				except Exception, exception:
					print line_number(), exception
					if value != "":
						self.setGridError(row)
						return
			percent_of_holdings_to_sell = value
			self.grid.SetCellValue(row, self.num_of_shares_cell.col, "")

			# if empty
			if percent_of_holdings_to_sell == "" or percent_of_holdings_to_sell == 0:
				self.grid.SetCellValue(row, self.number_of_shares_copy_cell.col, "")
				self.grid.SetCellValue(row, self.percent_of_shares_copy_cell.col, "")
				self.grid.SetCellValue(row, self.sale_check_cell.col, "")
				self.grid.SetCellTextColour(row, self.sale_check_cell.col, "black")

			elif percent_of_holdings_to_sell <= 1:
				self.grid.SetCellValue(row, self.percent_of_shares_copy_cell.col, "%d%%" % round(percent_of_holdings_to_sell * 100))

				number_of_shares_to_sell = int(math.floor( int(num_shares) * percent_of_holdings_to_sell ) )
				self.grid.SetCellValue(row, self.number_of_shares_copy_cell.col, str(number_of_shares_to_sell))

				if int(num_shares) == int(number_of_shares_to_sell):
					self.grid.SetCellValue(row, self.sale_check_cell.col, "All")
					self.grid.SetCellTextColour(row, self.sale_check_cell.col, "black")
				else:
					self.grid.SetCellValue(row, self.sale_check_cell.col, "Some")
					self.grid.SetCellTextColour(row, self.sale_check_cell.col, "black")
				sale_value = float(number_of_shares_to_sell) * float(price)
				self.grid.SetCellValue(row, self.sale_value_cell.col, "$%.2f" % sale_value)

				percent_to_commission = 100 * self.commission/sale_value
				self.grid.SetCellValue(row, self.commission_cell.col, "%.2f%%" % percent_to_commission)



			else:
				self.setGridError(row)
		self.saved_text.Hide()
		self.save_button.Show()
		#print "Show Me!"

	def setGridError(self, row):
		self.grid.SetCellValue(row, self.sale_check_cell.col, "Error")
		self.grid.SetCellTextColour(row, self.sale_check_cell.col, "red")

		self.grid.SetCellValue(row, self.number_of_shares_copy_cell.col, "")
		self.grid.SetCellValue(row, self.percent_of_shares_copy_cell.col, "")
		self.grid.SetCellValue(row, self.sale_value_cell.col, "")
		self.grid.SetCellValue(row, self.commission_cell.col, "")

	def setNoGridError(self, row):
		self.grid.SetCellValue(row, self.sale_check_cell.col, "")
		self.grid.SetCellTextColour(row, self.sale_check_cell.col, "black")

class TradePage(Tab):
	def __init__(self, parent):
		self.default_last_trade_price_attribute_name = "LastTradePriceOnly_yf"
		self.default_average_daily_volume_attribute_name = "AverageDailyVolume_yf"


		wx.Panel.__init__(self, parent)
		trade_page_text = wx.StaticText(self, -1, 
							 "Set up trades", 
							 (10,10)
							 )
		self.ticker_list = []
		
		self.relevant_portfolios_list = []
		self.sale_tuple_list = []

		self.default_rows_above_buy_candidates = 5
		self.default_buy_candidate_column = 7
		self.default_buy_candidate_quantity_column = 14
		self.buy_candidates = [] # this will be tickers to buy, but no quantities
		self.buy_candidate_tuples = [] # this will be tickers ROWS with quantities, if they don't appear in previous list, there will be disregarded, because data has been changed.

		self.default_columns = 19
		self.default_min_rows = 17

		import_sale_candidates_button = wx.Button(self, label="Import sale candidates and refresh spreadsheet", pos=(0,30), size=(-1,-1))
		import_sale_candidates_button.Bind(wx.EVT_BUTTON, self.importSaleCandidates, import_sale_candidates_button)

		create_grid_button = wx.Button(self, label="Create grid", pos=(500,30), size=(-1,-1))
		create_grid_button.Bind(wx.EVT_BUTTON, self.makeGridOnButtonPush, create_grid_button)
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

		print line_number(), "TradePage loaded"

	def updateStocksWithErrors(self, event):
		if not self.stocks_to_update:
			self.update_stocks_button.Hide()
			return
		if len(self.stocks_to_update) > config.SCRAPE_CHUNK_LENGTH:
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
		else:
			for chunk in ticker_chunk_list:
				for ticker in chunk:
					self.stocks_to_update.remove(ticker)
			self.updateGrid("event", cursor_positon = (0, 0))
			print line_number(), "ready to loop again"
			timer = threading.Timer(sleep_time, self.executeScrapePartOne, [ticker_chunk_list, position_of_this_chunk])
			timer.start()

	def importSaleCandidates(self, event):
		print line_number(), "Boom goes the boom!!!!!!!!"

		self.relevant_portfolios_list = config.SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[0]
		self.sale_tuple_list = config.SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[1]
		
		for portfolio in self.relevant_portfolios_list:
			id_number = portfolio.id_number
			print line_number(), "Portfolio %d:" % id_number, config.PORTFOLIO_NAMES[id_number - 1]
		print line_number(), self.sale_tuple_list

		# Now, how to refresh only parts of the list... hmmmm
	def makeGridOnButtonPush(self, event):
		self.newGridFill()
	def spreadSheetFill(self, cursor_positon = (0,0) ):
		pass # currently redundant

		# print cursor_positon
		# try:
		# 	self.grid.Destroy()
		# 	print "Destroyed grid"
		# except Exception, exception:
		# 	#pass
		# 	print line_number(), exception

		# # CREATE A GRID HERE
		# self.grid = TradeGrid(self, -1, size=(1000,650), pos=(0,83))
		# # calc rows
		# global SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE
		# 
		# relevant_portfolio_name_list = []
		# try:
		# 	self.relevant_portfolios_list = []
		# 	for account in SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[0]:
		# 		id_number = account.id_number
		# 		self.relevant_portfolios_list.append(account)
		# 		relevant_portfolio_name_list.append(config.PORTFOLIO_NAMES[(id_number - 1)])

		# 	num_rows = len(SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[1])
		# 	global DEFAULT_ROWS_ON_TRADE_PREP_PAGE_FOR_TICKERS
		# 	num_rows += DEFAULT_ROWS_ON_TRADE_PREP_PAGE_FOR_TICKERS
		# except Exception, exception:
		# 	print line_number(), exception
		# 	num_rows = 0

		# num_rows = max(num_rows, self.default_min_rows, (self.default_rows_above_buy_candidates + len(self.buy_candidates) + 1))
		# self.grid.CreateGrid(num_rows, self.default_columns)
		# self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.updateGrid, self.grid)

		# for column_num in range(self.default_columns):
		# 	for row_num in range(num_rows):
		# 		if row_num <= self.default_rows_above_buy_candidates or row_num > (self.default_rows_above_buy_candidates + len(self.buy_candidates) + 1) or column_num not in [self.default_buy_candidate_column,14]:
		# 			self.grid.SetReadOnly(row_num, column_num, True)
		# 		elif column_num == self.default_buy_candidate_column:
		# 			self.grid.SetCellBackgroundColour(row_num, column_num, "#FAEFCF")
		# 		elif column_num == 14:
		# 			self.grid.SetCellBackgroundColour(row_num, column_num, "#CFE8FC")


		# # Defining cells separately from forming them so they are easy to edit
		# # e.g. dummy_cell_var = [Row, Column, "Name/Value"]
		# # cell_list = [dummy_cell_var, dummy_cell_2, etc...]
		# # for cell in cell_list:
		# # 	self.grid.SetCellValue(cell[0],cell[1],cell[2])
		# spreadsheet_cell_list = []

		# # Start with static values (large if statement for code folding purposes only)
		# if "This section sets the static cell values by column" == "This section sets the static cell values by column":
		# 	# Column 0 (using zero-based numbering for simplicity):
		# 	this_column_number = 0

		# 	title_with_relevant_portfolios_string = "Trade Prep (" + ", ".join(relevant_portfolio_name_list) + ")"

		# 	name_of_spreadsheet_cell = [0, this_column_number, title_with_relevant_portfolios_string]
		# 	share_to_sell_cell = [2, this_column_number, "Shares to sell:"]
		# 	ticker_title_cell = [3, this_column_number, "Ticker"]

		# 	spreadsheet_cell_list.append(name_of_spreadsheet_cell)
		# 	spreadsheet_cell_list.append(share_to_sell_cell)
		# 	spreadsheet_cell_list.append(ticker_title_cell)

		# 	# Column 1:
		# 	this_column_number = 1

		# 	num_shares_cell = [3, this_column_number,"# shares"]		
		# 	spreadsheet_cell_list.append(num_shares_cell)

		# 	# Column 2:
		# 	this_column_number = 2

		# 	volume_title_cell = [3, this_column_number, "Volume"]
		# 	spreadsheet_cell_list.append(volume_title_cell)

		# 	# Column 3:
		# 	# empty

		# 	# Column 4:
		# 	this_column_number = 4

		# 	total_asset_cell = [0, this_column_number, "Total asset value ="]
		# 	approximate_surplus_cash_cell = [3, this_column_number, "Approximate surplus cash from sale ="]
		# 	percent_total_cash_cell = [6, this_column_number, "%% Total Cash After Sale"]
		# 	portfolio_cash_available_cell = [9, this_column_number, "Portfolio Cash Available ="]
		# 	num_stocks_to_look_cell = [12, this_column_number, "# of stocks to look at at for 3%% of portfolio each."]
		# 	approximate_to_spend_cell = [15, this_column_number, "Approximate to spend on each (3%) stock."]

		# 	spreadsheet_cell_list.append(total_asset_cell)
		# 	spreadsheet_cell_list.append(approximate_surplus_cash_cell)
		# 	spreadsheet_cell_list.append(percent_total_cash_cell)
		# 	spreadsheet_cell_list.append(portfolio_cash_available_cell)
		# 	spreadsheet_cell_list.append(num_stocks_to_look_cell)
		# 	spreadsheet_cell_list.append(approximate_to_spend_cell)

		# 	# Column 5:
		# 	# empty

		# 	# Column 6:
		# 	this_column_number = 6

		# 	num_symbol_cell = [5, this_column_number, "#"]
		# 	spreadsheet_cell_list.append(num_symbol_cell)

		# 	# Column 7:
		# 	this_column_number = 7

		# 	shares_to_buy_cell = [2, this_column_number, "Shares to buy:"]
		# 	input_ticker_cell = [3, this_column_number, "Input ticker"]

		# 	spreadsheet_cell_list.append(shares_to_buy_cell)
		# 	spreadsheet_cell_list.append(input_ticker_cell)

		# 	# Column 8:
		# 	# empty

		# 	# Column 9:
		# 	# empty

		# 	# Column 10:
		# 	this_column_number = 10

		# 	num_shares_to_buy_cell = [2, this_column_number, "# of shares to buy for"]
		# 	three_percent_cell = [3, this_column_number, "3%"]

		# 	spreadsheet_cell_list.append(num_shares_to_buy_cell)
		# 	spreadsheet_cell_list.append(three_percent_cell)

		# 	# Column 11:
		# 	this_column_number = 11

		# 	for_cell = [2, this_column_number, "for"]
		# 	five_percent_cell = [3, this_column_number, "5%"]

		# 	spreadsheet_cell_list.append(for_cell)
		# 	spreadsheet_cell_list.append(five_percent_cell)

		# 	# Column 12:
		# 	this_column_number = 12

		# 	for_cell_2 = [2, this_column_number, "for"]
		# 	ten_percent_cell = [3, this_column_number, "10%"]

		# 	spreadsheet_cell_list.append(for_cell_2)
		# 	spreadsheet_cell_list.append(ten_percent_cell)

		# 	# Column 13:
		# 	# empty

		# 	# Column 14:
		# 	this_column_number = 14

		# 	input_num_shares_cell = [3, this_column_number, "Input # Shares to Purchase"]
		# 	spreadsheet_cell_list.append(input_num_shares_cell)

		# 	# Column 15:
		# 	this_column_number = 15

		# 	cost_cell = [3, this_column_number, "Cost"]
		# 	spreadsheet_cell_list.append(cost_cell)

		# 	# Column 16: 
		# 	# empty

		# 	# Column 17:
		# 	this_column_number = 17

		# 	total_cost_cell = [1, this_column_number, "Total Cost ="]
		# 	adjusted_cash_cell = [2, this_column_number, "Adjusted Cash Available ="]
		# 	num_stocks_to_purchase_cell = [3, this_column_number, "Number of stocks left to purchase at 3% ="]
		# 	new_cash_percentage_cell = [4, this_column_number, "New cash %% of portfolio ="]
		# 	# this cell may be irrelevant
		# 	new_cash_total_cell = [5, this_column_number, "New cash %% of total ="]

		# 	spreadsheet_cell_list.append(total_cost_cell)
		# 	spreadsheet_cell_list.append(adjusted_cash_cell)
		# 	spreadsheet_cell_list.append(num_stocks_to_purchase_cell)
		# 	spreadsheet_cell_list.append(new_cash_percentage_cell)
		# 	spreadsheet_cell_list.append(new_cash_total_cell)

		# 	# Column 18:
		# 	# computed values only

		# if "This section sets the variable cell values with relevant data" == "This section sets the variable cell values with relevant data":

		# 	# Column 0-2 data:
		# 	this_column_number = 0
		# 	default_rows = DEFAULT_ROWS_ON_TRADE_PREP_PAGE_FOR_TICKERS # called globally above
		# 	counter = 0
		# 	for stock_tuple in SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[1]:
		# 		ticker = stock_tuple[0]
		# 		number_of_shares_to_sell = stock_tuple[1]
		# 		stock = return_stock_by_symbol(ticker)
		# 		correct_row = counter + default_rows
				
		# 		ticker_cell = [correct_row, this_column_number, ticker]
		# 		number_of_shares_to_sell_cell = [correct_row, (this_column_number + 1), str(number_of_shares_to_sell)]

		# 		spreadsheet_cell_list.append(ticker_cell)
		# 		spreadsheet_cell_list.append(number_of_shares_to_sell_cell)

		# 		try:
		# 			avg_daily_volume = stock.AverageDailyVolume
		# 			volume_cell = [correct_row, (this_column_number + 2), str(avg_daily_volume)]
		# 			spreadsheet_cell_list.append(volume_cell)
		# 		except Exception, exception:
		# 			print line_number(), exception

		# 		counter += 1

		# 	# Column 4 data:
		# 	this_column_number = 4

		# 	## total asset value
		# 	total_asset_value_row = 1

		# 	total_asset_value = 0.00
		# 	for account in self.relevant_portfolios_list:
		# 		total_asset_value += float(account.availble_cash.replace("$",""))
		# 		for stock in account.stock_list:
		# 			stock_data = return_stock_by_symbol(stock.symbol)
		# 			quantity = float(stock.quantity.replace(",",""))
		# 			last_price = float(stock_data.LastTradePriceOnly)
		# 			value_of_held_stock = last_price * quantity
		# 			total_asset_value += value_of_held_stock

		# 	total_asset_value_cell = [total_asset_value_row, this_column_number, ("$" + str(total_asset_value))]
		# 	spreadsheet_cell_list.append(total_asset_value_cell)

		# 	## approximate surplus cash
		# 	approximate_surplus_cash_row = 4

		# 	value_of_all_stock_to_sell = 0.00
		# 	for stock_tuple in SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[1]:
		# 		ticker = stock_tuple[0]
		# 		number_of_shares_to_sell = int(stock_tuple[1])
		# 		stock_data = return_stock_by_symbol(ticker)
		# 		last_price = float(stock_data.LastTradePriceOnly)
		# 		value_of_single_stock_to_sell = last_price * number_of_shares_to_sell
		# 		value_of_all_stock_to_sell += value_of_single_stock_to_sell
		# 	surplus_cash_cell = [approximate_surplus_cash_row, this_column_number, ("$" + str(value_of_all_stock_to_sell))]
		# 	spreadsheet_cell_list.append(surplus_cash_cell)

		# 	## percent of portfolio that is cash after sale
		# 	percent_cash_row = 7
			
		# 	total_cash = 0.00
		# 	for account in self.relevant_portfolios_list:
		# 		total_cash += float(account.availble_cash.replace("$",""))
		# 	total_cash += value_of_all_stock_to_sell
		# 	if total_cash != 0:
		# 		percent_cash = total_cash / total_asset_value
		# 		percent_cash = round(percent_cash * 100)
		# 		percent_cash = str(percent_cash) + "%"
		# 	else:
		# 		percent_cash = "Null"

		# 	percent_cash_cell = [percent_cash_row, this_column_number, percent_cash]
		# 	spreadsheet_cell_list.append(percent_cash_cell)

		# 	## portfolio cash available after sale
		# 	cash_after_sale_row = 10

		# 	total_cash_after_sale = total_cash # from above
		# 	total_cash_after_sale = "$" + str(total_cash_after_sale)

		# 	total_cash_after_sale_cell = [cash_after_sale_row, this_column_number, total_cash_after_sale]
		# 	spreadsheet_cell_list.append(total_cash_after_sale_cell)

		# 	## Number of stocks to purchase at 3% each
		# 	stocks_at_three_percent_row = 13

		# 	three_percent_of_all_assets = 0.03 * total_asset_value # from above
		# 	try:
		# 		number_of_stocks_at_3_percent = total_cash / three_percent_of_all_assets # total_cash defined above
		# 	except Exception, exception:
		# 		print line_number(), exception
		# 		number_of_stocks_at_3_percent = 0
		# 	number_of_stocks_at_3_percent = int(math.floor(number_of_stocks_at_3_percent)) # always round down

		# 	stocks_at_three_percent_cell = [stocks_at_three_percent_row, this_column_number, str(number_of_stocks_at_3_percent)]
		# 	spreadsheet_cell_list.append(stocks_at_three_percent_cell)

		# 	## Approximate to spend on each stock at 3%
		# 	three_percent_of_all_assets_row = 16

		# 	three_persent_in_dollars = "$" + "%.2f" % three_percent_of_all_assets # that %.2f rounds float two decimal places
		# 	three_percent_of_all_assets_cell = [three_percent_of_all_assets_row, this_column_number, three_persent_in_dollars]
		# 	spreadsheet_cell_list.append(three_percent_of_all_assets_cell)

		# # Now, add buy candidate tickers:


		# # Finally, set cell values in list:
		# for cell in spreadsheet_cell_list:
		# 	#print cell
		# 	self.grid.SetCellValue(cell[0],cell[1],cell[2])



		# self.grid.SetGridCursor(cursor_positon[0], cursor_positon[1])
		# self.grid.AutoSizeColumns()
		# print "done building self.grid"
		# self.grid_list.append(self.grid)
	def updateGrid(self, event, grid = None, cursor_positon = None):
		# this function currently creates new grids on top of each other.
		# why?
		# when i tried to update the previous grid using the data (run self.spreadSheetFill on the last line).
		# this caused a Segmentation fault: 11
		# thus, this hack... create a new grid on execution each time.

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
			#print row
			if row > self.default_rows_above_buy_candidates and grid.GetCellBackgroundColour(row, self.default_buy_candidate_column) == "#FAEFCF": # or (250, 239, 207, 255)
				#print row
				ticker = grid.GetCellValue(row, self.default_buy_candidate_column)
				#print ticker
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
		print line_number(), self.buy_candidates

		# build new grid
		self.newGridFill(cursor_positon = cursor_positon)

	def newGridFill(self, cursor_positon = (0,0) ):
		#print cursor_positon
		
		# CREATE A GRID HERE
		new_grid = TradeGrid(self, -1, size=(1000,650), pos=(0,83))
		# calc rows
		
		relevant_portfolio_name_list = []
		try:
			self.relevant_portfolios_list = []
			for account in config.SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[0]:
				id_number = account.id_number
				self.relevant_portfolios_list.append(account)
				relevant_portfolio_name_list.append(config.PORTFOLIO_NAMES[(id_number - 1)])

			num_rows = len(config.SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[1])
			num_rows += config.DEFAULT_ROWS_ON_TRADE_PREP_PAGE_FOR_TICKERS
		except Exception, exception:
			print line_number(), exception
			num_rows = 0

		num_rows = max(num_rows, self.default_min_rows, (self.default_rows_above_buy_candidates + len(self.buy_candidates) + 2))
		new_grid.CreateGrid(num_rows, self.default_columns)
		new_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, lambda event: self.updateGrid(event, grid = new_grid), new_grid) # self.updateGrid, new_grid)

		#print self.buy_candidates
		for column_num in range(self.default_columns):
			for row_num in range(num_rows):
				if row_num <= self.default_rows_above_buy_candidates or row_num > (self.default_rows_above_buy_candidates + len(self.buy_candidates) + 1) or column_num not in [self.default_buy_candidate_column,14]:
					new_grid.SetReadOnly(row_num, column_num, True)
				elif column_num == self.default_buy_candidate_column:
					new_grid.SetCellBackgroundColour(row_num, column_num, "#FAEFCF")
				elif column_num == 14:
					new_grid.SetCellBackgroundColour(row_num, column_num, "#CFE8FC")


		# Defining cells separately from forming them so they are easy to edit
		# e.g. dummy_cell_var = [Row, Column, "Name/Value"]
		# cell_list = [dummy_cell_var, dummy_cell_2, etc...]
		# for cell in cell_list:
		# 	new_grid.SetCellValue(cell[0],cell[1],cell[2])
		spreadsheet_cell_list = []

		# Start with static values (large if statement for code folding purposes only)
		if "This section sets the static cell values by column" == "This section sets the static cell values by column":
			# Column 0 (using zero-based numbering for simplicity):
			this_column_number = 0

			title_with_relevant_portfolios_string = "Trade Prep (" + ", ".join(relevant_portfolio_name_list) + ")"

			name_of_spreadsheet_cell = [0, this_column_number, title_with_relevant_portfolios_string]
			share_to_sell_cell = [2, this_column_number, "Shares to sell:"]
			ticker_title_cell = [3, this_column_number, "Ticker"]

			spreadsheet_cell_list.append(name_of_spreadsheet_cell)
			spreadsheet_cell_list.append(share_to_sell_cell)
			spreadsheet_cell_list.append(ticker_title_cell)

			# Column 1:
			this_column_number = 1

			num_shares_cell = [3, this_column_number,"# shares"]		
			spreadsheet_cell_list.append(num_shares_cell)

			# Column 2:
			this_column_number = 2

			volume_title_cell = [3, this_column_number, "Volume"]
			spreadsheet_cell_list.append(volume_title_cell)

			# Column 3:
			# empty

			# Column 4:
			this_column_number = 4

			total_asset_cell = [0, this_column_number, "Total asset value ="]
			approximate_surplus_cash_cell = [3, this_column_number, "Approximate surplus cash from sale ="]
			percent_total_cash_cell = [6, this_column_number, "%% Total Cash After Sale"]
			portfolio_cash_available_cell = [9, this_column_number, "Portfolio Cash Available ="]
			num_stocks_to_look_cell = [12, this_column_number, "# of stocks to look at at for 3%% of portfolio each."]
			approximate_to_spend_cell = [15, this_column_number, "Approximate to spend on each (3%) stock."]

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

			num_symbol_cell = [5, this_column_number, "#"]
			spreadsheet_cell_list.append(num_symbol_cell)

			# Column 7:
			this_column_number = 7

			shares_to_buy_cell = [2, this_column_number, "Shares to buy:"]
			input_ticker_cell = [3, this_column_number, "Input ticker"]

			spreadsheet_cell_list.append(shares_to_buy_cell)
			spreadsheet_cell_list.append(input_ticker_cell)

			# Column 8:
			# empty

			# Column 9:
			# empty

			# Column 10:
			this_column_number = 10

			num_shares_to_buy_cell = [2, this_column_number, "# of shares to buy for"]
			three_percent_cell = [3, this_column_number, "3%"]

			spreadsheet_cell_list.append(num_shares_to_buy_cell)
			spreadsheet_cell_list.append(three_percent_cell)

			# Column 11:
			this_column_number = 11

			for_cell = [2, this_column_number, "for"]
			five_percent_cell = [3, this_column_number, "5%"]

			spreadsheet_cell_list.append(for_cell)
			spreadsheet_cell_list.append(five_percent_cell)

			# Column 12:
			this_column_number = 12

			for_cell_2 = [2, this_column_number, "for"]
			ten_percent_cell = [3, this_column_number, "10%"]

			spreadsheet_cell_list.append(for_cell_2)
			spreadsheet_cell_list.append(ten_percent_cell)

			# Column 13:
			# empty

			# Column 14:
			this_column_number = 14

			input_num_shares_cell = [3, this_column_number, "Input # Shares to Purchase"]
			spreadsheet_cell_list.append(input_num_shares_cell)

			# Column 15:
			this_column_number = 15

			cost_cell = [3, this_column_number, "Cost"]
			spreadsheet_cell_list.append(cost_cell)

			# Column 16: 
			# empty

			# Column 17:
			this_column_number = 17

			total_cost_cell = [1, this_column_number, "Total Cost ="]
			adjusted_cash_cell = [2, this_column_number, "Adjusted Cash Available ="]
			num_stocks_to_purchase_cell = [3, this_column_number, "Number of stocks left to purchase at 3% ="]
			new_cash_percentage_cell = [4, this_column_number, "New cash %% of portfolio ="]
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
			for stock_tuple in config.SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[1]:
				ticker = stock_tuple[0]
				number_of_shares_to_sell = stock_tuple[1]
				stock = utils.return_stock_by_symbol(ticker)
				correct_row = counter + default_rows
				
				ticker_cell = [correct_row, this_column_number, ticker]
				number_of_shares_to_sell_cell = [correct_row, (this_column_number + 1), str(number_of_shares_to_sell)]

				spreadsheet_cell_list.append(ticker_cell)
				spreadsheet_cell_list.append(number_of_shares_to_sell_cell)

				try:
					avg_daily_volume = getattr(stock, self.default_average_daily_volume_attribute_name)
					volume_cell = [correct_row, (this_column_number + 2), str(avg_daily_volume)]
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
				total_asset_value += float(str(account.availble_cash).replace("$",""))
				for ticker, quantity in account.stock_shares_dict.iteritems():
					stock = utils.return_stock_by_symbol(ticker)
					quantity = float(str(quantity).replace(",",""))
					last_price = float(getattr(stock, self.default_last_trade_price_attribute_name))
					value_of_held_stock = last_price * quantity
					total_asset_value += value_of_held_stock

			total_asset_value_cell = [total_asset_value_row, this_column_number, ("$" + str(total_asset_value))]
			spreadsheet_cell_list.append(total_asset_value_cell)

			## approximate surplus cash
			approximate_surplus_cash_row = 4

			value_of_all_stock_to_sell = 0.00
			for stock_tuple in config.SALE_PREP_PORTFOLIOS_AND_SALE_CANDIDATES_TUPLE[1]:
				ticker = stock_tuple[0]
				number_of_shares_to_sell = int(stock_tuple[1])
				stock = utils.return_stock_by_symbol(ticker)
				last_price = float(getattr(stock, self.default_last_trade_price_attribute_name))
				value_of_single_stock_to_sell = last_price * number_of_shares_to_sell
				value_of_all_stock_to_sell += value_of_single_stock_to_sell
			surplus_cash_cell = [approximate_surplus_cash_row, this_column_number, ("$" + str(value_of_all_stock_to_sell))]
			spreadsheet_cell_list.append(surplus_cash_cell)

			## percent of portfolio that is cash after sale
			percent_cash_row = 7
			
			total_cash = 0.00
			for account in self.relevant_portfolios_list:
				total_cash += float(str(account.availble_cash).replace("$",""))
			total_cash += value_of_all_stock_to_sell
			if total_cash != 0:
				percent_cash = total_cash / total_asset_value
				percent_cash = round(percent_cash * 100)
				percent_cash = str(percent_cash) + "%"
			else:
				percent_cash = "Null"

			percent_cash_cell = [percent_cash_row, this_column_number, percent_cash]
			spreadsheet_cell_list.append(percent_cash_cell)

			## portfolio cash available after sale
			cash_after_sale_row = 10

			total_cash_after_sale = total_cash # from above
			total_cash_after_sale = "$" + str(total_cash_after_sale)

			total_cash_after_sale_cell = [cash_after_sale_row, this_column_number, total_cash_after_sale]
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

			stocks_at_three_percent_cell = [stocks_at_three_percent_row, this_column_number, str(number_of_stocks_at_3_percent)]
			spreadsheet_cell_list.append(stocks_at_three_percent_cell)

			## Approximate to spend on each stock at 3%
			three_percent_of_all_assets_row = 16

			three_persent_in_dollars = "$" + "%.2f" % three_percent_of_all_assets # that %.2f rounds float two decimal places
			three_percent_of_all_assets_cell = [three_percent_of_all_assets_row, this_column_number, three_persent_in_dollars]
			spreadsheet_cell_list.append(three_percent_of_all_assets_cell)

		# Now, add buy candidate tickers:

		count = 0
		# This is the a very similar iteration as above
		for column_num in range(self.default_columns):
			for row_num in range(num_rows):
				if row_num <= self.default_rows_above_buy_candidates or row_num > (self.default_rows_above_buy_candidates + len(self.buy_candidates) + 1) or column_num not in [self.default_buy_candidate_column, self.default_buy_candidate_quantity_column]:
					pass
				elif column_num == self.default_buy_candidate_column:
					if count in range(len(self.buy_candidates)):
						new_grid.SetCellValue(row_num, column_num - 1, str(count + 1))
						new_grid.SetCellValue(row_num, column_num, self.buy_candidates[count])
						
						stock = utils.return_stock_by_symbol(self.buy_candidates[count])
						new_grid.SetCellValue(row_num, column_num + 1, str(stock.firm_name))

						try:
							last_price = float(getattr(stock, self.default_last_trade_price_attribute_name))
							new_grid.SetCellValue(row_num, column_num + 2, "$" + str(last_price))
							update_error = False
						except Exception as e:
							print line_number(), e
							new_grid.SetCellValue(row_num, column_num + 2, "(Error: Update %s)" % stock.symbol)
							new_grid.SetCellTextColour(row_num, column_num + 2, config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)
							update_error = True
							self.stocks_to_update.append(stock.symbol)
							utils.remove_list_duplicates(self.stocks_to_update)
							print line_number(), self.stocks_to_update, "Row:", row_num, "Column:", column_num
							self.update_stocks_button.Show()

						column_shift = 3
						for percent in [0.03, 0.05, 0.10]:
							if not update_error:
								# total_asset_value calculated above
								#print total_asset_value
								max_cost = total_asset_value * percent
								#print max_cost
								number_of_shares_to_buy = int(math.floor(max_cost / last_price))
								#print number_of_shares_to_buy
								new_grid.SetCellValue(row_num, column_num + column_shift, str(number_of_shares_to_buy))
							else: # If error...
								new_grid.SetCellValue(row_num, column_num + column_shift, "-")
								new_grid.SetCellTextColour(row_num, column_num + column_shift, config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)
							column_shift += 1

						for this_tuple in self.buy_candidate_tuples:
							if this_tuple[0] == row_num:
								new_grid.SetCellValue(row_num, self.default_buy_candidate_quantity_column, str(this_tuple[1]))
					count += 1

		# now calculate final values
		buy_cost_column = 15

		total_buy_cost = 0.00
		for row_num in range(num_rows):
			if row_num > self.default_rows_above_buy_candidates:
				quantity = str(new_grid.GetCellValue(row_num, buy_cost_column - 1))
				if quantity:
					ticker = str(new_grid.GetCellValue(row_num, buy_cost_column - 8))
					print line_number(), ticker
					stock = utils.return_stock_by_symbol(ticker)
					if stock:
						quantity = int(quantity)
						cost = float(getattr(stock, self.default_last_trade_price_attribute_name)) * quantity
						total_buy_cost += cost
						cost_cell = [row_num, buy_cost_column, "$" + str(cost)]
						spreadsheet_cell_list.append(cost_cell)

		# column 18 (final column)
		this_column_number = 18

		total_cost_row = 1
		
		total_cost_sum_cell = [total_cost_row, this_column_number, "$" + str(total_buy_cost)]
		spreadsheet_cell_list.append(total_cost_sum_cell)

		adjusted_cash_row = 2
		adjusted_cash_result = total_cash - total_buy_cost
		if adjusted_cash_result >= 0:
			color = "black"
		else:
			color = "red"
		adjusted_cash_result_cell = [adjusted_cash_row, this_column_number, "$" + str(adjusted_cash_result)]
		spreadsheet_cell_list.append(adjusted_cash_result_cell)
		new_grid.SetCellTextColour(adjusted_cash_row, this_column_number, color)

		number_of_stocks_still_yet_to_buy_row = 3
		if total_asset_value > 0:
			number_of_stocks_still_yet_to_buy = int(math.floor(adjusted_cash_result / (total_asset_value * 0.03)))
		else:
			number_of_stocks_still_yet_to_buy = 0
		number_of_stocks_still_yet_to_buy_cell = [number_of_stocks_still_yet_to_buy_row, this_column_number, str(number_of_stocks_still_yet_to_buy)]
		spreadsheet_cell_list.append(number_of_stocks_still_yet_to_buy_cell)
		new_grid.SetCellTextColour(number_of_stocks_still_yet_to_buy_row, this_column_number, color)

		new_percent_cash_row = 4
		if adjusted_cash_result != 0:
			new_percent_cash = round(100 * adjusted_cash_result / total_asset_value)
		else:
			new_percent_cash = 0
		new_percent_cash_cell = [new_percent_cash_row, this_column_number, "%d" % int(new_percent_cash) + "%"]
		spreadsheet_cell_list.append(new_percent_cash_cell)
		new_grid.SetCellTextColour(new_percent_cash_row, this_column_number, color)

		# Finally, set cell values in list:
		for cell in spreadsheet_cell_list:
			#print cell
			new_grid.SetCellValue(cell[0],cell[1],cell[2])



		new_grid.AutoSizeColumns()
		print line_number(), "done building grid"
		new_grid.SetGridCursor(cursor_positon[0] + 1, cursor_positon[1])

		for grid in self.grid_list:
			grid.Hide()
		self.grid_list.append(new_grid)
		print line_number(), "number of grids created =", len(self.grid_list)
		new_grid.SetFocus()
		self.grid = new_grid

class PortfolioPage(Tab):
	def __init__(self, parent):
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
				portfolio_account = PortfolioAccountTab(portfolio_account_notebook, (i+1))
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

				portfolio_account = PortfolioAccountTab(portfolio_account_notebook, (i+1))
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
	def __init__(self, parent, tab_number):
		tab_panel = wx.Panel.__init__(self, parent, tab_number)
		
		self.portfolio_id = tab_number
		#print line_number(), "self.portfolio_id =", self.portfolio_id
		self.portfolio_obj = config.PORTFOLIO_OBJECTS_DICT.get(str(tab_number))

		if not self.portfolio_obj:
			if config.ENCRYPTION_POSSIBLE:
				db.load_portfolio_object(self.portfolio_id)
			else:
				try:
					db.load_portfolio_object(self.portfolio_id)
				except Exception, e:
					print line_number(), e
					self.portfolio_obj = None

		add_button = wx.Button(self, label="Add account .csv", pos=(5,0), size=(-1,-1))
		add_button.Bind(wx.EVT_BUTTON, self.addAccountCSV, add_button) 
		
		self.portfolio_import_name_list = meta.return_portfolio_import_function_short_names()
		self.drop_down = wx.ComboBox(self, pos=(11,25), choices=self.portfolio_import_name_list)

		self.triple_list = meta.return_portfolio_import_function_triple()

		self.portfolio_import_name = None


		delete_button = wx.Button(self, label="Delete this portfolio", pos=(830,0), size=(-1,-1))
		delete_button.Bind(wx.EVT_BUTTON, self.confirmDeleteAccount, delete_button) 

		rename_button = wx.Button(self, label="Rename this portfolio", pos=(355,0), size=(-1,-1))
		rename_button.Bind(wx.EVT_BUTTON, self.changeTabName, rename_button) 

		change_number_of_portfolios_button = wx.Button(self, label="Change number of portfolios", pos=(518,0), size=(-1,-1))
		change_number_of_portfolios_button.Bind(wx.EVT_BUTTON, self.changeNumberOfPortfolios, change_number_of_portfolios_button) 

		#print_portfolio_data_button = wx.Button(self, label="p", pos=(730,0), size=(-1,-1))
		#print_portfolio_data_button.Bind(wx.EVT_BUTTON, self.printData, print_portfolio_data_button) 

		self.current_account_spreadsheet = AccountDataGrid(self, -1, size=(980,637), pos=(0,50))
		if self.portfolio_obj:
			self.spreadSheetFill(self.current_account_spreadsheet, self.portfolio_obj)

		self.screen_grid = None

		print line_number(), "PortfolioAccountTab loaded"


	def printData(self, event):
		if self.account_obj:
			print line_number(),"cash:", self.account_obj.availble_cash
			for account_attribute in dir(self.account_obj):
				if not account_attribute.startswith("_"):
					print line_number(),account_attribute, ":"
					try:
						for stock_attribute in dir(getattr(self.account_obj, account_attribute)):
							if not stock_attribute.startswith("_"):
								print line_number(),stock_attribute, getattr(getattr(self.account_obj, account_attribute), stock_attribute)
					except Exception, exception:
						print line_number(),exception
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
		# 	password = self.get_password()
		db.save_DATA_ABOUT_PORTFOLIOS() #password = password)
		confirm = wx.MessageDialog(self,
								 "The number of portfolios has changed. The change will be applied the next time you launch this program.",
								 'Restart Required',
								 style = wx.ICON_EXCLAMATION
								 )
		confirm.ShowModal()
		confirm.Destroy()
	def spreadSheetFill(self, spreadsheet, portfolio_obj):
		if self.current_account_spreadsheet:
			self.current_account_spreadsheet.Destroy()
		self.screen_grid = create_account_spread_sheet(self, portfolio_obj)
		if self.screen_grid:
			self.screen_grid.Show()
		return
		
		#####################################################

		num_rows = len(portfolio_obj.stock_shares_dict) + 2
		num_columns = 0

		attribute_list = []
		# get all possible attributes
		for ticker in portfolio_obj.stock_shares_dict:
			if config.GLOBAL_STOCK_DICT.get(ticker):
				for attribute in dir(config.GLOBAL_STOCK_DICT[ticker]):
					if not attribute.startswith("_"):
						if attribute not in attribute_list:
							attribute_list.append(attribute)
		if not attribute_list:
			print line_number(), "Portfolio empty"
			num_columns = 0
		else:
			num_columns = len(attribute_list)
		
		# build spreadsheet
		spreadsheet = AccountDataGrid(self, -1, size=(980,637), pos=(0,50))
		spreadsheet.CreateGrid(num_rows, num_columns)
		spreadsheet.EnableEditing(False)

		row_count = 0
		col_count = 0
		for ticker in portfolio_obj.stock_shares_dict:
			for attribute in attribute_list:
				if row_count == 0:
					spreadsheet.SetColLabelValue(col_count, attribute)
				else:
					try:
						spreadsheet.SetCellValue(row_count, col_count, getattr(config.GLOBAL_STOCK_DICT[ticker], attribute))
					except Exception as e:
						print line_number(), e
						pass
				col_count += 1
			row_count += 1
			col_count = 0
		

		spreadsheet.AutoSizeColumns()
		self.current_account_spreadsheet = spreadsheet

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
		
		self.spreadSheetFill(self.current_account_spreadsheet, self.account_obj)
		
		# this is used in sale prep page:
		config.PORTFOLIO_OBJECTS_DICT[str(self.portfolio_id)] = self.account_obj

		print line_number(), "Portfolio CSV import complete."

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
				config.DATA_ABOUT_PORTFOLIOS[1] = new_portfolio_names

				print ""
				print line_number(), "This file opening needs to be removed."
				# password = ""
				# if config.ENCRYPTION_POSSIBLE:
				# 	password = self.get_password()
				db.save_DATA_ABOUT_PORTFOLIOS() #password = password)
				print ""
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
		# password = ""
		# if config.ENCRYPTION_POSSIBLE:
		# 	password = self.get_password()
		db.delete_portfolio_object(self.portfolio_id) #, password = password)


		# Reset to default name in data about portfolios
		default_portfolio_names = ["Primary", "Secondary", "Tertiary"]
		if self.portfolio_id < 10:
			portfolio_name = "Portfolio %d" % (self.portfolio_id+1)
		else:
			portfolio_name = "%dth" % (self.portfolio_id+1)
		if self.portfolio_id in range(len(default_portfolio_names)):
			portfolio_name = default_portfolio_names[self.portfolio_id]
		config.DATA_ABOUT_PORTFOLIOS[1][self.portfolio_id] = portfolio_name
		# password = ""
		# if config.ENCRYPTION_POSSIBLE:
		# 	password = self.get_password()
		db.save_DATA_ABOUT_PORTFOLIOS() #password = password)

		self.delete_button.Hide()

		self.portfolio_data = Account(self.portfolio_id)

		if self.current_account_spreadsheet:
			self.current_account_spreadsheet.Destroy()
			self.current_account_spreadsheet = AccountDataGrid(self, -1, size=(980,637), pos=(0,50))
			self.spreadSheetFill(self.current_account_spreadsheet, self.portfolio_data)
		self.account_obj = None
		return

class StockDataPage(Tab):
	def __init__(self, parent):
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
		#update_yql_basic_data_button = wx.Button(self, 
		#								  label="update basic data", 
		#								  pos=(300,5), 
		#								  size=(-1,-1)
		#								  )
		#update_annual_data_button = wx.Button(self, 
		#								  label="update annual data", 
		#								  pos=(430,5), 
		#								  size=(-1,-1)
		#								  )
		#update_analyst_estimates_button = wx.Button(self, 
		#								  label="update analyst estimates", 
		#								  pos=(570,5), 
		#								  size=(-1,-1)
		#								  )

		load_screen_button.Bind(wx.EVT_BUTTON, self.createOneStockSpreadSheet, load_screen_button)
		
		update_additional_data_button = wx.Button(self, 
										  label="update additional data", 
										  pos=(300,5), 
										  size=(-1,-1)
										  )
		update_additional_data_button.Bind(wx.EVT_BUTTON, self.updateAdditionalDataForOneStock, update_additional_data_button)

		#update_yql_basic_data_button.Bind(wx.EVT_BUTTON, self.update_yql_basic_data, update_yql_basic_data_button)
		#update_annual_data_button.Bind(wx.EVT_BUTTON, self.update_annual_data, update_annual_data_button)
		#update_analyst_estimates_button.Bind(wx.EVT_BUTTON, self.update_analyst_estimates_data, update_analyst_estimates_button)

		print line_number(), "StockDataPage loaded"

	def updateAdditionalDataForOneStock(self, event):
		ticker = self.ticker_input.GetValue()
		if str(ticker) == "ticker" or not ticker:
			return
		scrape.scrape_all_additional_data([ticker])
		self.createOneStockSpreadSheet("event")
	
	def createOneStockSpreadSheet(self, event):
		ticker = self.ticker_input.GetValue()
		if str(ticker) == "ticker" or not ticker:
			return
		self.screen_grid = create_spread_sheet_for_one_stock(self, str(ticker).upper())

	def update_yql_basic_data(self, event):
		ticker = self.ticker_input.GetValue()
		if str(ticker) == "ticker":
			return
		print "basic yql scrape"
		basicYQLScrapePartOne( [ [str(ticker).upper()] ] )
		self.createOneStockSpreadSheet(event = "")

	def update_annual_data(self, event):
		ticker = self.ticker_input.GetValue()
		if str(ticker) == "ticker":
			return
		print "scraping yahoo and morningstar annual data, you'll need to keep an eye on the terminal until this finishes."
		scrape_balance_sheet_income_statement_and_cash_flow( [str(ticker).upper()] )
		self.createOneStockSpreadSheet(event = "")

	def update_analyst_estimates_data(self, event):
		ticker = self.ticker_input.GetValue()
		if str(ticker) == "ticker":
			return
		print "about to scrape"
		scrape_analyst_estimates( [str(ticker).upper()] )
		self.createOneStockSpreadSheet(event = "")

class UserFunctionsPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		####
		user_function_page_panel = wx.Panel(self, -1, pos=(0,5), size=( wx.EXPAND, wx.EXPAND))
		user_function_notebook = wx.Notebook(user_function_page_panel)


		self.user_created_tests = UserCreatedTestsPage(user_function_notebook)
		user_function_notebook.AddPage(self.user_created_tests, "Screen Tests")		

		self.user_ranking_functions = UserCreatedRankFunctionPage(user_function_notebook)
		user_function_notebook.AddPage(self.user_ranking_functions, "Ranking Functions")		

		self.user_csv_import_functions = UserCreatedCsvImportFunctionPage(user_function_notebook)
		user_function_notebook.AddPage(self.user_csv_import_functions, "CSV Import Functions")

		self.user_xls_import_functions = UserCreatedXlsImportFunctionPage(user_function_notebook)
		user_function_notebook.AddPage(self.user_xls_import_functions, "XLS Import Functions")

		self.user_portfolio_import_functions = UserCreatedPortfolioImportFunctionPage(user_function_notebook)
		user_function_notebook.AddPage(self.user_portfolio_import_functions, "Portfolio Import Functions")


		sizer2 = wx.BoxSizer()
		sizer2.Add(user_function_notebook, 1, wx.EXPAND)
		self.SetSizer(sizer2)		
		####

class UserCreatedTestsPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		text = wx.StaticText(self, -1, 
							 "Welcome to the user generated test page.", 
							 (10,10)
							 )
		save_button = wx.Button(self, label="Save Tests", pos=(5, 30), size=(-1,-1))
		save_button.Bind(wx.EVT_BUTTON, self.confirmSave, save_button) 

		reset_button = wx.Button(self, label="Reset Tests to Default", pos=(5, 60), size=(-1,-1))
		reset_button.Bind(wx.EVT_BUTTON, self.confirmResetToDefault, reset_button) 

		more_text = wx.StaticText(self, -1, 
							 "Create stock screen tests to be imported into screen or rank pages.", 
							 (145,36)
							 )



		self.file_text = db.load_user_created_tests()


		self.height_var = 100
		self.file_display = wx.TextCtrl(self, -1, 
									self.file_text, 
									(10, self.height_var),
									size = (955, 580),
									style = wx.TE_MULTILINE ,
									)
		self.file_display.Show()

		print line_number(), "UserCreatedTestsPage loaded"


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
			self.saveTests()
	def saveTests(self):
		text = self.file_display.GetValue()
		db.save_user_created_tests(text)

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
		
		self.file_text = db.load_default_tests()
		db.save_user_created_tests(self.file_text)

		self.file_display = wx.TextCtrl(self, -1, 
									self.file_text, 
									(10, self.height_var),
									size = (765, 625),
									style = wx.TE_MULTILINE ,
									)
		self.file_display.Show()
class UserCreatedRankFunctionPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		text = wx.StaticText(self, -1, 
							 "Welcome to the user created ranking function page.", 
							 (10,10)
							 )
		save_button = wx.Button(self, label="Save Functions", pos=(5, 30), size=(-1,-1))
		save_button.Bind(wx.EVT_BUTTON, self.confirmSave, save_button) 

		reset_button = wx.Button(self, label="Reset Ranking Functions to Default", pos=(5, 60), size=(-1,-1))
		reset_button.Bind(wx.EVT_BUTTON, self.confirmResetToDefault, reset_button) 

		more_text = wx.StaticText(self, -1, 
							 "Create stock ranking functions to be imported into the rank page.", 
							 (145,36)
							 )



		self.file_text = db.load_user_ranking_functions()


		self.height_var = 100
		self.file_display = wx.TextCtrl(self, -1, 
									self.file_text, 
									(10, self.height_var),
									size = (955, 580),
									style = wx.TE_MULTILINE ,
									)
		self.file_display.Show()

		print line_number(), "UserCreatedRankFunctionPage loaded"


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
			self.saveRankFunctions()
	def saveRankFunctions(self):
		text = self.file_display.GetValue()
		db.save_user_ranking_functions(text)

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
		
		self.file_text = db.load_default_ranking_functions()
		db.save_user_ranking_functions(self.file_text)

		self.file_display = wx.TextCtrl(self, -1, 
									self.file_text, 
									(10, self.height_var),
									size = (765, 625),
									style = wx.TE_MULTILINE ,
									)
		self.file_display.Show()
class UserCreatedCsvImportFunctionPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		text = wx.StaticText(self, -1, 
							 "Welcome to the user created csv import function page.", 
							 (10,10)
							 )
		save_button = wx.Button(self, label="Save Functions", pos=(5, 30), size=(-1,-1))
		save_button.Bind(wx.EVT_BUTTON, self.confirmSave, save_button) 

		reset_button = wx.Button(self, label="Reset CSV Import Functions to Default", pos=(5, 60), size=(-1,-1))
		reset_button.Bind(wx.EVT_BUTTON, self.confirmResetToDefault, reset_button) 

		more_text = wx.StaticText(self, -1, 
							 "Create CSV import functions to be imported into the import page.", 
							 (145,36)
							 )



		self.file_text = db.load_user_csv_import_functions()


		self.height_var = 100
		self.file_display = wx.TextCtrl(self, -1, 
									self.file_text, 
									(10, self.height_var),
									size = (955, 580),
									style = wx.TE_MULTILINE ,
									)
		self.file_display.Show()

		print line_number(), "UserCreatedCsvImportFunctionPage loaded"


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
			self.saveCsvImportFunctions()
	def saveCsvImportFunctions(self):
		text = self.file_display.GetValue()
		db.save_user_csv_import_functions(text)

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
		
		self.file_text = db.load_default_csv_import_functions()
		db.save_user_csv_import_functions(self.file_text)

		self.file_display = wx.TextCtrl(self, -1, 
									self.file_text, 
									(10, self.height_var),
									size = (765, 625),
									style = wx.TE_MULTILINE ,
									)
		self.file_display.Show()
class UserCreatedXlsImportFunctionPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		text = wx.StaticText(self, -1, 
							 "Welcome to the user created .xls import function page.", 
							 (10,10)
							 )
		save_button = wx.Button(self, label="Save Functions", pos=(5, 30), size=(-1,-1))
		save_button.Bind(wx.EVT_BUTTON, self.confirmSave, save_button) 

		reset_button = wx.Button(self, label="Reset XLS Import Functions to Default", pos=(5, 60), size=(-1,-1))
		reset_button.Bind(wx.EVT_BUTTON, self.confirmResetToDefault, reset_button) 

		more_text = wx.StaticText(self, -1, 
							 "Create XLS import functions to be imported into the import page.", 
							 (145,36)
							 )



		self.file_text = db.load_user_xls_import_functions()


		self.height_var = 100
		self.file_display = wx.TextCtrl(self, -1, 
									self.file_text, 
									(10, self.height_var),
									size = (955, 580),
									style = wx.TE_MULTILINE ,
									)
		self.file_display.Show()

		print line_number(), "UserCreatedCsvImportFunctionPage loaded"


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
			self.saveXlsImportFunctions()
	def saveXlsImportFunctions(self):
		text = self.file_display.GetValue()
		db.save_user_xls_import_functions(text)

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
		
		self.file_text = db.load_default_xls_import_functions()
		db.save_user_xls_import_functions(self.file_text)

		self.file_display = wx.TextCtrl(self, -1, 
									self.file_text, 
									(10, self.height_var),
									size = (765, 625),
									style = wx.TE_MULTILINE ,
									)
		self.file_display.Show()
class UserCreatedPortfolioImportFunctionPage(Tab):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		text = wx.StaticText(self, -1, 
							 "Welcome to the user created portfolio import function page.", 
							 (10,10)
							 )
		save_button = wx.Button(self, label="Save Functions", pos=(5, 30), size=(-1,-1))
		save_button.Bind(wx.EVT_BUTTON, self.confirmSave, save_button) 

		reset_button = wx.Button(self, label="Reset Portfolio Import Functions to Default", pos=(5, 60), size=(-1,-1))
		reset_button.Bind(wx.EVT_BUTTON, self.confirmResetToDefault, reset_button) 

		more_text = wx.StaticText(self, -1, 
							 "Create stock portfolio import functions to be imported into the portfolio page.", 
							 (145,36)
							 )



		self.file_text = db.load_user_portfolio_import_functions()


		self.height_var = 100
		self.file_display = wx.TextCtrl(self, -1, 
									self.file_text, 
									(10, self.height_var),
									size = (955, 580),
									style = wx.TE_MULTILINE ,
									)
		self.file_display.Show()

		print line_number(), "UserCreatedPortfolioImportFunctionPage loaded"


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
			self.savePortfolioImportFunctions()
	def savePortfolioImportFunctions(self):
		text = self.file_display.GetValue()
		db.save_user_portfolio_import_functions(text)

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
		
		self.file_text = db.load_default_portfolio_import_functions()
		db.save_user_portfolio_import_functions(self.file_text)

		self.file_display = wx.TextCtrl(self, -1, 
									self.file_text, 
									(10, self.height_var),
									size = (765, 625),
									style = wx.TE_MULTILINE ,
									)
		self.file_display.Show()

# ###########################################################################################

# ###################### wx grids #######################################################
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

class SalePrepGrid(wx.grid.Grid):
	def __init__(self, *args, **kwargs):
		wx.grid.Grid.__init__(self, *args, **kwargs)
class TradeGrid(wx.grid.Grid):
	def __init__(self, *args, **kwargs):
		wx.grid.Grid.__init__(self, *args, **kwargs)
class AccountDataGrid(wx.grid.Grid):
	def __init__(self, *args, **kwargs):
		wx.grid.Grid.__init__(self, *args, **kwargs)
# ###########################################################################################

# ############ Spreadsheet Functions ########################################################
def create_spreadsheet_from_stock_list(spreadsheet, stock_list):
	spreadsheet.EnableEditing(False)


	# Find all attribute names
	attribute_list = []
	all_attribute_list = []
	for stock in stock_list:
		all_attribute_list = all_attribute_list + list(dir(stock))
		all_attribute_list = set(all_attribute_list) # remove duplicates
		all_attribute_list = list(all_attribute_list)
	# Eliminate non-finance related attributes
	for attribute in all_attribute_list:
		if not attribute.startswith('_'):
			attribute_list.append(str(attribute))
	# Sort for readability
	attribute_list.sort(key=lambda x: x.lower())

	# adjust list order for important terms
	try:
		attribute_list.insert(0, attribute_list.pop(attribute_list.index('symbol')))
	except Exception, e:
		print line_number(), e
	try:
		attribute_list.insert(1, attribute_list.pop(attribute_list.index('firm_name')))
	except Exception, e:
		print line_number(), e
	#print line_number(), attribute_list

	row_count = 0
	col_count = 0

	# set first row attribute names
	for attribute in attribute_list:
		spreadsheet.SetColLabelValue(col_count, str(attribute))
		col_count += 1
	col_count = 0

	# fill in the stocks' values
	for stock in stock_list:
		for attribute in attribute_list:
			try:
				spreadsheet.SetCellValue(row_count, col_count, str(getattr(stock, attribute)))
			except:
				pass
			col_count += 1
		row_count += 1
		col_count = 0
	
	# resize calumns
	spreadsheet.AutoSizeColumns()
	return spreadsheet

def create_spread_sheet(
	wxWindow, 
	stock_list, 
	held_ticker_list = [] # not used currentlly
	, height = 637
	, width = 980
	, position = (0,60)
	, enable_editing = False
	):

	irrelevant_attributes = config.IRRELEVANT_ATTRIBUTES


	config.TICKER_AND_ATTRIBUTE_TO_UPDATE_TUPLE_LIST = [] # Clear update list
	for stock in stock_list:
		#print line_number(), 'Here, "if not stock.last_yql_basic_scrape_update" type conditionals should be changed to be time based for better functionality'		
		for update_attribute in config.STOCK_SCRAPE_UPDATE_ATTRIBUTES:

			if not getattr(stock, update_attribute):
				config.TICKER_AND_ATTRIBUTE_TO_UPDATE_TUPLE_LIST.append([stock.symbol, update_attribute])
				#print "Stock %s's %s attribute is not up to date, you should consider updating" % (stock.symbol, update_attribute)

	print line_number(), 'Here, "if not stock.last_yql_basic_scrape_update" type conditionals should be changed to be time based for better functionality'


	# if include_analyst_estimates:
	# 	analyst_estimate_data_absent = True
	# 	for analyst_estimate_data in GLOBAL_ANALYST_ESTIMATES_STOCK_LIST:
	# 		if str(ticker) == str(analyst_estimate_data.symbol):
	# 			analyst_estimate_list.append(analyst_estimate_data)
	# 			analyst_estimate_data_absent = False
	# 	if analyst_estimate_data_absent:
	# 		logging.error('There does not appear to be analyst estimates for "%s," you should update analyst estimates' % ticker)



	num_rows = len(stock_list)
	num_columns = 0


	attribute_list = []
	# Here we make columns for each attribute to be included
	for stock in stock_list:
		for attribute in dir(stock):
			if not attribute.startswith('_'):
				if attribute not in config.IRRELEVANT_ATTRIBUTES:
					if attribute not in attribute_list:
						attribute_list.append(str(attribute))
		if num_columns < len(attribute_list):
			num_columns = len(attribute_list)		
									
		##### Below is sort of out of date but i don't want to get rid of the code incase i encounter problems with annual data later it can serve as a template
		# if include_annual_data:
		# 	for annual_data in annual_data_list:
		# 		if str(stock.symbol) == str(annual_data.symbol):
		# 			for attribute in dir(annual_data):
		# 				if not attribute.startswith('_'):
		# 					if attribute not in irrelevant_attributes:
		# 						if not attribute[-3:] in ["t1y", "t2y"]: # this checks to see that only most recent annual data is shown. this hack is good for 200 years!!!
		# 							if str(attribute) != 'symbol': # here symbol will appear twice, once for stock, and another time for annual data, in the attribute list below it will be redundant and not added, but if will here if it's not skipped
		# 								num_attributes += 1
		# 								if attribute not in attribute_list:
		# 									attribute_list.append(str(attribute))
		
		# if include_analyst_estimates:
		# 	for estimate_data in analyst_estimate_list:
		# 		if str(stock.symbol) == str(estimate_data.symbol):
		# 			for attribute in dir(estimate_data):
		# 				if not attribute.startswith('_'):
		# 					if attribute not in irrelevant_attributes:
		# 						num_attributes += 1
		# 						if attribute not in attribute_list:
		# 							attribute_list.append(str(attribute))

		##### Model if adding new data type #####
		#
		# if include_data_type:
		# 	for data in data_type:
		# 		if str(stock.symbol) == str(data_type.symbol):
		# 			for attribute in dir(data_type):
		# 				if not attribute.startswith('_'):
		# 					if attribute not in irrelevant_attributes:
		# 						num_attributes += 1
		# 						if attribute not in attribute_list:
		# 							attribute_list.append(str(attribute))

	if stock_list and not attribute_list:
		print line_number(), 'Warning: attribute list empty'
		return
	# else: loading blank list

	screen_grid = wx.grid.Grid(wxWindow, -1, size=(width, height), pos=position)
	screen_grid.CreateGrid(num_rows, num_columns)
	screen_grid.EnableEditing(enable_editing)

	if attribute_list: # not empty screen loading:
		attribute_list.sort(key = lambda x: x.lower())
		# adjust list order for important terms
		attribute_list.insert(0, attribute_list.pop(attribute_list.index('symbol')))
		attribute_list.insert(1, attribute_list.pop(attribute_list.index('firm_name')))

	wxWindow.full_attribute_list = attribute_list
	wxWindow.relevant_attribute_list = [attribute for attribute in attribute_list if attribute not in config.IRRELEVANT_ATTRIBUTES]



	# fill in grid
	row_count = 0
	for stock in stock_list:
		col_count = 0
		for attribute in attribute_list:
			# set attributes to be labels if it's the first run through
			if row_count == 0:
				screen_grid.SetColLabelValue(col_count, str(attribute))

			try:
				# Try to add basic data value
				screen_grid.SetCellValue(row_count, col_count, str(getattr(stock, attribute)))
				# Add color if relevant
				if str(stock.ticker) in config.HELD_STOCK_TICKER_LIST:
					screen_grid.SetCellBackgroundColour(row_count, col_count, config.HELD_STOCK_COLOR_HEX)
				# Change text red if value is negative
				try:
					if utils.stock_value_is_negative(stock, attribute):
						screen_grid.SetCellTextColour(row_count, col_count, config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)
				except Exception as exception:
					pass
					#print line_number(), exception
			except Exception as exception:
				pass
				#print line_number(), exception
			col_count += 1
		row_count += 1
	screen_grid.AutoSizeColumns()

	return screen_grid

def create_account_spread_sheet(
	wxWindow, 
	account_obj,
	held_ticker_list = [] # not used currentl  
	, height = 637
	, width = 980
	, position = (0,60)
	, enable_editing = False
	):
	stock_shares_dict = account_obj.stock_shares_dict
	#print line_number(), "Stock shares dict:", stock_shares_dict

	cash = account_obj.availble_cash
	#print line_number(), "Available cash:", cash

	stock_list = []
	for ticker in stock_shares_dict:
		#print line_number(), ticker
		stock = config.GLOBAL_STOCK_DICT.get(ticker)
		if stock:
			#print line_number(), "Stock:", stock.symbol
			if stock not in stock_list:
				stock_list.append(stock)
		else:
			print line_number(), "Ticker:", ticker, "not found..."
	#print line_number(), "Stock list:", stock_list

	irrelevant_attributes = config.IRRELEVANT_ATTRIBUTES

	#print line_number(), 'Here, "if not stock.last_yql_basic_scrape_update" type conditionals should be changed to be time based for better functionality'


	# if include_analyst_estimates:
	# 	analyst_estimate_data_absent = True
	# 	for analyst_estimate_data in GLOBAL_ANALYST_ESTIMATES_STOCK_LIST:
	# 		if str(ticker) == str(analyst_estimate_data.symbol):
	# 			analyst_estimate_list.append(analyst_estimate_data)
	# 			analyst_estimate_data_absent = False
	# 	if analyst_estimate_data_absent:
	# 		logging.error('There does not appear to be analyst estimates for "%s," you should update analyst estimates' % ticker)



	num_rows = len(stock_list)
	num_columns = 0


	attribute_list = []
	# Here we make columns for each attribute to be included
	for stock in stock_list:
		for attribute in dir(stock):
			if not attribute.startswith('_'):
				if attribute not in config.IRRELEVANT_ATTRIBUTES:
					if attribute not in attribute_list:
						attribute_list.append(str(attribute))
		if num_columns < len(attribute_list):
			num_columns = len(attribute_list)	
	
	num_columns += 1 # for number of shares held
	num_rows += 1 	# for cash
									
	
	if not attribute_list:
		print line_number(), 'attribute list empty'
		return


	screen_grid = wx.grid.Grid(wxWindow, -1, size=(width, height), pos=position)
	screen_grid.CreateGrid(num_rows, num_columns)
	screen_grid.EnableEditing(enable_editing)


	attribute_list.sort(key = lambda x: x.lower())
	# adjust list order for important terms
	stock_list.insert(0, "cash")
	attribute_list.insert(0, attribute_list.pop(attribute_list.index('symbol')))
	attribute_list.insert(1, attribute_list.pop(attribute_list.index('firm_name')))
	attribute_list.insert(2, "Shares Held")

	wxWindow.full_attribute_list = attribute_list
	wxWindow.relevant_attribute_list = [attribute for attribute in attribute_list if attribute not in config.IRRELEVANT_ATTRIBUTES]



	# fill in grid
	row_count = 0
	for stock in stock_list:
		col_count = 0
		for attribute in attribute_list:
			# set attributes to be labels if it's the first run through
			if row_count == 0:
				screen_grid.SetColLabelValue(col_count, str(attribute))
				if col_count == 0:
					screen_grid.SetCellValue(row_count, col_count, "Cash:")
				elif col_count == 1:
					screen_grid.SetCellValue(row_count, col_count, str(cash))


			else:
				if col_count == 2:
					screen_grid.SetCellValue(row_count, col_count, str(stock_shares_dict.get(stock.symbol)))
				else:
					try:
						# Try to add basic data value
						screen_grid.SetCellValue(row_count, col_count, str(getattr(stock, attribute)))
						# Add color if relevant
						if str(stock.ticker) in config.HELD_STOCK_TICKER_LIST:
							screen_grid.SetCellBackgroundColour(row_count, col_count, config.HELD_STOCK_COLOR_HEX)
						# Change text red if value is negative
						try:
							if utils.stock_value_is_negative(stock, attribute):
								screen_grid.SetCellTextColour(row_count, col_count, config.NEGATIVE_SPREADSHEET_VALUE_COLOR_HEX)
						except Exception as exception:
							pass
							#print line_number(), exception
					except Exception as exception:
						pass
						#print line_number(), exception
			col_count += 1
		row_count += 1
	screen_grid.AutoSizeColumns()

	return screen_grid


def create_spread_sheet_for_one_stock(
	wxWindow, 
	ticker, 
	height = 637, 
	width = 980, 
	position = (0,60), 
	enable_editing = False
	):

	stock = utils.return_stock_by_symbol(ticker)

	if not stock:
		print 'Ticker "%s" does not appear to have basic data' % ticker
		return

	attribute_list = []
	num_columns = 2 # for this we only need two columns
	num_rows = 0
	# Here we make rows for each attribute to be included
	num_attributes = 0
	if stock:
		for attribute in dir(stock):
			if not attribute.startswith('_'):
				if attribute not in attribute_list:
					num_attributes += 1
					attribute_list.append(str(attribute))
				else:
					print "%s.%s" % (ticker, attribute), "is a duplicate"

	
	if num_rows < num_attributes:
		num_rows = num_attributes

	screen_grid = wx.grid.Grid(wxWindow, -1, size=(width, height), pos=position)

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