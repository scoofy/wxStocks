# Add csv import functions below:
# You can also edit this file (wxStocks_csv_import_functions.py) in your own text editor. 
import csv
########################################### instructions #######################################################
# functions should be of the following form:

#	def your_full_csv_import_function_name(csv_file, attribute_suffix = "underscore and two letters"): 
#		"""short name""" # <--- this will appear in import dropdowns
#
#		# add some csv processing:
#		data = csv.reader(csv_file)
#		# do stuff to data
#
#		# Always return a list of dictionaries and an properly formatted suffix for your attribute.
#		# Dictionaries should be attribute names, with whatever attribute names you want, except your_dictionary['stock']
#		# "your_dictionary['stock']" must refer to the relevant stock ticker, as a way to fetch that stock from the main database.
#		return (dict_list, attribute_suffix)

################################################################################################################
def process_sample_csv_dot_csv(csv_file, attribute_suffix = "_my"):
	'''import sample_import_csv.csv'''
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