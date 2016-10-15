import sys, os, wx, stat, hashlib, shutil

current_dir = os.path.dirname(os.path.realpath(__file__))

app = wx.App()
info_label = "Update wxStocks"
info_text = "You are about to update wxStocks.\nFirst, this update file should be run from your existing wxStocks folder.\nNext, you will select the folder of the new version of wxStocks.\nNote that the new version's folder should not be zipped.\nRegardless, none of your data files should be changed, nor should any of your user files be changed."
info = wx.MessageBox(info_text, info_label, wx.OK | wx.ICON_INFORMATION)
dialog = wx.DirDialog(None, "Choose a directory:",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
if dialog.ShowModal() == wx.ID_OK:
    newly_downloaded_path = dialog.GetPath()
else:
    sys.exit()
dialog.Destroy()

# check to see if selected folder is a wxStocks folder
if not (os.path.isfile(newly_downloaded_path + "\\wxStocks.py") and os.path.isfile(newly_downloaded_path + "\\update_wxstocks.py")):
    # if wxStocks.py or update_wxstocks.py don't exist
    print "It appears you have not selected a wxStocks folder."
    print "Please try again, selecting an unzipped version of wxStocks."
    print "In the case of a change to the updating process, please check the wxStocks readme file in your new folder."
    sys.exit()

# get new directory split name
new_split_folder_name = (newly_downloaded_path + "\\wxStocks.py").split("\\")[-2]

# get current directory split name
for root, dirs, files in os.walk(current_dir):
    for filename in files:
        if filename.endswith("wxStocks.py"):
            current_path = os.path.join(root, filename)
            path_list = current_path.split("\\")
            old_split_folder_name = path_list[-2]
            break

# add new files
for root, dirs, files in os.walk(newly_downloaded_path):
    for filename in files:
        if root.split("\\")[-1] in ["DO_NOT_COPY", "user_data", "wxStocks_data"]:
            continue
        if filename.endswith(".py"):
            #print root
            newly_downloaded_file_path = os.path.join(root, filename)

            split_root_path =  root.split("\\" + new_split_folder_name +"\\")
            try:
                full_extention = split_root_path[1]
            except:
                full_extention = None

            #print split_root_path
            if full_extention:
                existing_file_path = "\\".join([current_dir, full_extention]) + "\\" + filename
            else:
                existing_file_path = "\\".join([current_dir, filename])
            #print existing_file_path

            try:
                checksum_new = hashlib.md5(open(str(newly_downloaded_file_path)).read()).hexdigest()
            except:
                checksum_new = None
            try:
                checksum_old = hashlib.md5(open(str(existing_file_path)).read()).hexdigest()
            except:
                checksum_old = None

            if checksum_new:
                if checksum_new != checksum_old:
                    print "UPDATING:", existing_file_path
                    shutil.copy(newly_downloaded_file_path, existing_file_path)
                    # remove existing .pyc file
                    pyc_path = os.path.splitext(existing_file_path)[0] + ".pyc"
                    try:
                        os.remove(pyc_path)
                    except:
                        pass
                    print '"' + filename + '"', "was successfully updated"

# delete nonexistant file from current directory
for root, dirs, files in os.walk(current_dir):
    for filename in files:
        if root.split("\\")[-1] in ["DO_NOT_COPY", "user_data", "wxStocks_data"]:
            continue
        if filename.endswith(".py"):
            #print root
            existing_file_path = os.path.join(root, filename)

            split_root_path =  root.split("\\" + old_split_folder_name +"\\")
            try:
                full_extention = split_root_path[1]
            except:
                full_extention = None

            #print split_root_path
            if full_extention:
                potential_new_file_path = "\\".join([newly_downloaded_path, full_extention]) + "\\" + filename
            else:
                potential_new_file_path = "\\".join([newly_downloaded_path, filename])
            if not os.path.isfile(potential_new_file_path): # file no longer exists
                print "Deleting:", existing_file_path
                print "It apparently no longer exists"
                try:
                    os.remove(existing_file_path)
                    print '"' + filename + '"', "was successfully removed"
                except:
                    pass
                # remove existing .pyc file
                pyc_path = os.path.splitext(existing_file_path)[0] + ".pyc"
                try:
                    os.remove(pyc_path)
                except:
                    pass
                # delete directory if it is empty
                if not os.listdir(root):
                    print "Removing empty directory:", root
                    os.rmdir(root)

print "Update complete"
