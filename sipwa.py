import sys, os, time, datetime, subprocess, winsound
from pywinauto.application import Application
from dbfread import DBF
print "Stock Investor Pro Exporter\n"

# Config
user_id = "Default"
open_save_folder = True

# set paths
si_path = "C:\Program Files (x86)\Stock Investor\Professional"
os.chdir(si_path)
save_folder = "C:\Users\\" + user_id + "\Desktop\si_data_exports\\"
if not os.path.exists(save_folder):
	os.makedirs(save_folder)
current_day = datetime.datetime.today().strftime('%Y-%m-%d')
todays_save_folder = save_folder + current_day + "\\"
if not os.path.exists(todays_save_folder):
	os.makedirs(todays_save_folder)

# Gather custom view names
si_view_name_file_path = "C:\Program Files (x86)\Stock Investor\Professional\User\usrpts.dbf"
si_view_name_file_data = [x for x in DBF(si_view_name_file_path)]
list_of_si_views = [str(x[u"NAME"]) for x in si_view_name_file_data]
save_id_list = [x for x in list_of_si_views if not x.startswith("*")]



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

# iterate over exporting views
for save_id in save_id_list:
	sic.SetFocus()
	menu = sic.Menu()
	menu_items = menu.Items()
	file_menu = menu_items[0]
	file_submenu = file_menu.SubMenu().Items()
	export = file_submenu[9]
	export.Click()

	sic2 = sic[u'Export Data']
	sic2.SetFocus()

	window = sic2
	window.TypeKeys(str(save_id))
	for clicks in range(4):
		window.TypeKeys("{TAB}")
	time.sleep(1)
	window.TypeKeys("{ENTER}")

	save_window = app.Dialog
	save_window.Wait('ready')
	save_window.SetFocus()
	save_window.TypeKeys(todays_save_folder + str(save_id))
	save_window.TypeKeys("{ENTER}")
	for tabs in range(4):
		window.TypeKeys("{TAB}")
	window.TypeKeys("{ENTER}")

	save_success = False
	for second in range(60 *5): # 5 minutes
		try:
			dlg = app.Dialog
			button = dlg.OK
			button.Click()
			save_success = True
			break
		except:
			time.sleep(1)
	if not save_success:
		print "Error in saving file", str(save_id)+".XLS, it took too long (5+ minutes)."
		print "\nExiting..."
		sys.exit()

# print success and open relevant folder, if set to do so
print "\nLooks like everything saved successfully."
print "Find your new data files at:", todays_save_folder
if open_save_folder:
	first_save_id_name_alphabetically = [x for x in sorted(save_id_list)][0]
	subprocess.Popen(r'explorer /select,' + todays_save_folder + first_save_id_name_alphabetically.upper() + ".XLS")

# play sound to indicate export was successful
sounds = ["Windows Unlock.wav",
		  "notify.wav",
		  "Windows Proximity Notification.wav",
		  "Windows Exclamation.wav",
		  "tada.wav"
		 ]
sound = sounds[2]
winsound.PlaySound("C:\Windows\Media\\"+sound, winsound.SND_FILENAME)

# Close SIpro
app.Kill_()

