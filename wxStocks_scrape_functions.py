# Add scraping functions below:
# You can also edit this file (wxStocks_scrape_functions.py) in your own text editor. 
########################################### instructions #######################################################
# functions should be of the following form:

#	def your_full_scrape_function_name(stock, attribute_suffix_that_represents_the_sorce_of_data = "underscore and two letters"): 
#		"""short name""" # <--- this will appear in import dropdowns
#
#		# import libraries if necessary (it will probably be necessary)
#		import stuff
#
#		# It's also helpful to look in the config.py file to find useful constants
#		sleep_time = config.SCRAPE_SLEEP_TIME
#
#		# add processing:
#		data = scrape a bunch of data
#		# do stuff to data
#
#		# If you want to set attributes yourself, you can look in the wxPython_classes.py file or the wxPython_utilities.py file for help and end with return None
#		# However, i'd suggest using the following dictionary method, and wxStocks can set the attributes for you.
#
#		# Always return a list of dictionaries and a properly formatted suffix for your attribute.
#		# Dictionaries should be attribute names, with whatever attribute names you want, except your_dictionary['stock']
#		# "your_dictionary['stock']" must refer to the relevant stock ticker, as a way to fetch that stock from the main database.
#		return (dict_list, attribute_suffix)

################################################################################################################
def sample_scrape(stock_list, attribute_suffix = "_yf"):

	finish this incomplete

	'''sample scrape of '''
	dict_list = []

	reader = csv.reader(csv_file)
	row_list = []
	for row in reader:
		row_list.append(row)

	for row in row_list:
		if row:
			if row == row_list[0]:
				continue
			else: # gather data
				my_dict = {}
				if row[0]:
					ticker = row[0]
					ticker = " ".join(ticker.split())
					my_dict['stock'] = ticker
				if row[1]:
					firm_name = row[1]
					my_dict['firm_name'] = firm_name
				if row[2]:
					exchange = row[2]
					my_dict['exchange'] = exchange
				if row[3]:
					location = row[3]
					my_dict['location'] = location
				if my_dict:
					dict_list.append(my_dict)

	return (dict_list, attribute_suffix)







# end of line