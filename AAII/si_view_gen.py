import sys, os, time, datetime, winsound
from pywinauto.application import Application
from dbfread import DBF
print "Stock Investor Pro View Creator\n"

max_number_of_field_groups = 50 # adjust if they change the number of field groups to more than 50
default_company_information_index = 7 # this will just check this one first, if it fails, it'll look further.
default_custom_field_index = 8
ticker_distance_from_company_information = 19 # adjust if they change the location of "ticker" in "company information" field group


# set paths
si_path = "C:\Program Files (x86)\Stock Investor\Professional"
os.chdir(si_path)

# Gather custom view names
si_view_name_file_path = "C:\Program Files (x86)\Stock Investor\Professional\User\usrpts.dbf"
si_view_name_file_data = [x for x in DBF(si_view_name_file_path)]
list_of_si_views = [str(x[u"NAME"]) for x in si_view_name_file_data]
wxStocks_id_list = [x for x in list_of_si_views if ((x.startswith("wx")) and x[2:].isdigit())]

# Launch Stock Investor Pro
app = Application().Start(si_path + "\si.exe")
sic = app.si9c000000
sic.Wait('ready')
sic.SetFocus()

launch_success = False
for second in range(60 *2): # 2 minutes
	try:
		menu = sic.Menu()
		menu_items = menu.Items()
		launch_success = True
		break
	except:
		time.sleep(1)
if not launch_success:
	print "Something went wrong, stock investor pro did not launch properly."
	print "\nExiting..."
	sys.exit()

sic.SetFocus()	
menu = sic.Menu()
menu_items = menu.Items()
tools_menu = menu_items[2]
tools_submenu = tools_menu.SubMenu().Items()
view_editor = tools_submenu[2]
view_editor.Click()
# View Editor window
sic2 = sic[u'View Editor']
sic2.SetFocus()
window = sic2

# This is terrible form, but i don't want to make this exportor more complicated
# "window" is defined, so now the tab and return field functions will work
def click_tab(int_number_of_times):
	for clicks in range(int_number_of_times):
		window.TypeKeys("{TAB}")
	time.sleep(0.3)
def return_field_index(unicode_field_name, default_index = 0):
	field_groups_indexes_with_default_index_first = range(max_number_of_field_groups)
	field_groups_indexes_with_default_index_first.insert(0, field_groups_indexes_with_default_index_first.pop(default_index))

	for i in field_groups_indexes_with_default_index_first:
		text_success = False
		text = None
		for j in range(i+1): # range needs to add 1 as it downclicks for the 0th iteration
			window.TypeKeys("{DOWN}")
			time.sleep(0.1)
		click_tab(2)
		window.TypeKeys("{ENTER}")


		# give the save window a couple seconds to open
		for second in range(3):
			try:
				# get text to identify which attributes are being saved
				dlg = app.Dialog
				text = dlg[u"Static2"].Texts()[0]
				print text
				text_success = True
				break
			except:
				time.sleep(1)
		if not text_success:
			print "Error in checking view for ticker field, it took too long (2+ seconds)."
			print "\nExiting..."
			sys.exit()

		if unicode_field_name in text:
			# ignore, we just want to export raw data
			index = i
			dlg["&No"].Click()
			click_tab(4)
			window.TypeKeys("{ENTER}")
			break
		else:
			dlg["&No"].Click()
			click_tab(5)
			for j in range(i):
				window.TypeKeys("{UP}")
	return index

# Get company info and custom field indicies
click_tab(4)	
window.TypeKeys("{ENTER}")
company_info = u"Company Information"
company_info_index = return_field_index(company_info, default_index=default_company_information_index)

sic.SetFocus()	
menu = sic.Menu()
menu_items = menu.Items()
tools_menu = menu_items[2]
tools_submenu = tools_menu.SubMenu().Items()
view_editor = tools_submenu[2]
view_editor.Click()
# View Editor window
sic2 = sic[u'View Editor']
sic2.SetFocus()
window = sic2

custom_field = u"Custom Fields"
custom_field_index = return_field_index(custom_field, default_index=default_custom_field_index)

text = None
list_of_transfer_field_dialog_text = []

# iterate over exporting views
first_iteration = False
for i in range(max_number_of_field_groups):
	if i == custom_field_index:
		continue
	sic.SetFocus()	
	menu = sic.Menu()
	menu_items = menu.Items()
	tools_menu = menu_items[2]
	tools_submenu = tools_menu.SubMenu().Items()
	view_editor = tools_submenu[2]
	view_editor.Click()

	# View Editor window
	sic2 = sic[u'View Editor']
	sic2.SetFocus()

	window = sic2
	if first_iteration:
		click_tab(1)
		first_iteration = False
	else:
		click_tab(8)
	if i != company_info_index: # custom field already avoided above.
		# We value "ticker" is not in the fields added, add it first: 
		for j in range(company_info_index):
			window.TypeKeys("{DOWN}")
			time.sleep(0.1)
		window.TypeKeys("{SPACE}")
		for k in range(ticker_distance_from_company_information):
			window.TypeKeys("{DOWN}")
			time.sleep(0.1)
		click_tab(2)
		window.TypeKeys("{ENTER}")
		click_tab(9)
		for k in range(ticker_distance_from_company_information):
			window.TypeKeys("{UP}")
			time.sleep(0.1)
		window.TypeKeys("{SPACE}")

		difference = company_info_index - i
		for j in range(abs(difference)):
			if difference > 0:
				window.TypeKeys("{UP}")
			else:
				window.TypeKeys("{DOWN}")
			# difference cannot be equal to zero because if it's zero,
			# it'd be in the else clause below
			time.sleep(0.1)
	else:
		for value in range(i):
			window.TypeKeys("{DOWN}")
			time.sleep(0.1)
	click_tab(2)
	window.TypeKeys("{ENTER}")

	text_success = False
	text = None
	# give the save window a couple seconds to open
	for second in range(3):
		try:
			# get text to identify which attributes are being saved
			dlg = app.Dialog
			text = dlg[u"Static2"].Texts()[0]
			text_success = True
			break
		except:
			time.sleep(1)
	if not text_success:
		print "Error in saving view, it took too long (2+ seconds)."
		print "\nExiting..."
		sys.exit()
	if text not in list_of_transfer_field_dialog_text:
		# if the text were in the list of transfer field dialog texts
		# it would have already been turned into a view, thus it's a duplicate,
		# thus, if it's already there, it means we've gone through all 
		# potential views, and are done.
		list_of_transfer_field_dialog_text.append(text)
		dlg["&Yes"].Click()
		click_tab(4)
		window.TypeKeys("{ENTER}")
		index_num = None
		if i < custom_field_index:
			index_num = str(i+1)
		else:
			index_num = str(i)
		window.TypeKeys("wx" + index_num)
		click_tab(1)
		window.TypeKeys("wx" + index_num)
		click_tab(1)
		window.TypeKeys("{ENTER}")	
		click_tab(4)
		window.TypeKeys("{ENTER}")

	else:
		# we've found duplicate dialogue field text, thus all views have been created
		# and we're done and can exit our loop...
		break

print "All done, exiting..."
app.Kill_()
# play sound to indicate export was successful
sounds = ["Windows Unlock.wav", 
		  "notify.wav", 
		  "Windows Proximity Notification.wav", 
		  "Windows Exclamation.wav", 
		  "tada.wav"
		 ]
sound = sounds[4]
winsound.PlaySound("C:\Windows\Media\\"+sound, winsound.SND_FILENAME)


