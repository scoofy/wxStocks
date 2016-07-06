from pywinauto.application import Application
import sys, os, time, datetime
si_path = "C:\Program Files (x86)\Stock Investor\Professional"
os.chdir(si_path)

user_id = "Matt"
num_of_save_files = 16

save_folder = "C:\Users\\" + user_id + "\Desktop\si_data_exports\\"
if not os.path.exists(save_folder):
	os.makedirs(save_folder)
current_day = datetime.datetime.today().strftime('%Y-%m-%d')
todays_save_folder = save_folder + current_day + "\\"
if not os.path.exists(todays_save_folder):
	os.makedirs(todays_save_folder)


save_id_list = [str(x) for x in range(num_of_save_files+1) if x != 0]

app = Application().Start(si_path + "\si.exe")
sic = app.si9c000000
sic.Wait('ready')

for second in range(60 *2): # 2 minutes
	try:
		menu = sic.Menu()
		menu_items = menu.Items()
		break
	except:
		time.sleep(1)

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

print "\nLooks like everything saved successfully."
print "Find your new data files at:", todays_save_folder
app.Kill_()

