import sys, os, time, datetime, subprocess, winsound
from pywinauto.application import Application
from dbfread import DBF
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
# play sound to indicate backup was successful
sounds = ["Windows Unlock.wav", 
		  "notify.wav", 
		  "Windows Proximity Notification.wav", 
		  "Windows Exclamation.wav", 
		  "tada.wav"
		 ]
sound = sounds[4]
winsound.PlaySound("C:\Windows\Media\\"+sound, winsound.SND_FILENAME)







