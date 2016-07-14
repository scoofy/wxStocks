import sys, os, time, datetime, winsound
from pywinauto.application import Application
from pywinauto import clipboard
from dbfread import DBF

def run_si_backup():
	print "Stock Investor Pro Automated Backup\n"

	# set paths
	si_path = "C:\Program Files (x86)\Stock Investor\Professional"
	os.chdir(si_path)

	backup_folder = "C:\Program Files (x86)\Stock Investor\Backups\\"
	pywinauto_typeable_backup_folder_name = "C:\Program{SPACE}Files{SPACE}{(}x86{)}\Stock{SPACE}Investor\Backups\\"
	if not os.path.exists(backup_folder):
		os.makedirs(backup_folder)

	current_day = datetime.datetime.today().strftime('%Y-%m-%d')
	todays_backup_folder = backup_folder + current_day + "\\"
	pywinauto_typeable_todays_backup_folder = pywinauto_typeable_backup_folder_name + current_day
	if not os.path.exists(todays_backup_folder):
		os.makedirs(todays_backup_folder)


	# Launch Stock Investor Pro
	app = Application().Start(si_path + "\si_util.exe")
	siutilc = app.si_util9c000000
	siutilc.Wait('ready')
	siutilc.SetFocus()	

	for i in range(3):
		siutilc.TypeKeys("{TAB}")
		time.sleep(0.1)
	siutilc.TypeKeys("{ENTER}")
	time.sleep(0.1)
	siutilc.TypeKeys(pywinauto_typeable_todays_backup_folder)
	for i in range(2):
		siutilc.TypeKeys("{TAB}")
		time.sleep(0.1)
	siutilc.TypeKeys("{ENTER}")

	print "Backup created, exiting..."
	app.Kill_()

# set paths
si_path = "C:\Program Files (x86)\Stock Investor\Professional"
os.chdir(si_path)

# Gather custom view names
si_view_name_file_path = "C:\Program Files (x86)\Stock Investor\Professional\User\usrpts.dbf"
si_view_name_file_data = [x for x in DBF(si_view_name_file_path)]
list_of_si_views = [str(x[u"NAME"]) for x in si_view_name_file_data]
wx_view_id_list = [x for x in list_of_si_views if ((x.startswith("wx")) and x[2:].isdigit())]

# Get the index of relevant views
wx_view_index_list = []
for wx_view in wx_view_id_list:
	for si_view in list_of_si_views:
		if wx_view == si_view:
			wx_view_index = list_of_si_views.index(si_view)
			wx_view_index_list.append(wx_view_index)

# if there aren't even any existing wx views, quit
if not wx_view_index_list:
	print "No views exist, exiting..."
	sys.exit()

# if there are views, check if they've been backed up
backup_folder = "C:\Program Files (x86)\Stock Investor\Backups\\"
current_day = datetime.datetime.today().strftime('%Y-%m-%d')
todays_backup_folder = backup_folder + current_day + "\\"

# if no backup create one
if not os.path.exists(todays_backup_folder):
	run_si_backup()
	time.sleep(1)


# now that there is a backup, launch view deleter
print "Stock Investor Pro View Deleter\n"

# Launch Stock Investor Pro
app = Application().Start(si_path + "\si.exe")
sic = app.si9c000000
sic.Wait('ready')
sic.SetFocus()

# Wait for launch to load and index the si pro crap
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

# iterate over exporting views
sic.SetFocus()	
menu = sic.Menu()
menu_items = menu.Items()
edit_menu = menu_items[1]
edit_submenu = edit_menu.SubMenu().Items()
delete_menu_item = edit_submenu[13]
delete_menu_item.Click()

sic2 = sic[u'Delete']
sic2.SetFocus()

window = sic2
window.TypeKeys("{DOWN}")
window.TypeKeys("{TAB}")

first_iteration = True
match = False
number_of_views_deleted = 0
for i in range(len(list_of_si_views)):
	time.sleep(0.1)
	if match:
		for downward_clicks in range(i - number_of_views_deleted):
			window.TypeKeys("{DOWN}")
			time.sleep(0.1)
	elif first_iteration:
		first_iteration = False
	else:
		window.TypeKeys("{DOWN}")
	window.TypeKeys("{TAB}")
	window.TypeKeys("^(c)")
	text = None
	text = clipboard.GetData()
	print "text "+str(i)+" =", text
	time.sleep(0.1)
	window.TypeKeys("{TAB}")
	match = False
	if text.strip() in wx_view_id_list:
		print "deleting:", text
		time.sleep(0.5)
		window.TypeKeys("{ENTER}")
		number_of_views_deleted += 1
		match = True
	for i in range(4):
		window.TypeKeys("{TAB}")
		time.sleep(0.1)

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





