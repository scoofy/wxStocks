import sys, os, wx, stat, hashlib

current_dir = os.path.dirname(os.path.realpath(__file__))

app = wx.PySimpleApp()
dialog = wx.DirDialog(None, "Choose a directory:",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
if dialog.ShowModal() == wx.ID_OK:
    newly_downloaded_path = dialog.GetPath()
    print newly_downloaded_path
dialog.Destroy()

for root, dirs, files in os.walk(current_dir):
    for filename in files:
        if filename.endswith("wxStocks.py"):
            new_path = os.path.join(root, filename)
            path_list = new_path.split("\\")
            print path_list
            key_split_folder_name = path_list[-2]
            break


for root, dirs, files in os.walk(current_dir):
    for filename in files:
        if root.split("\\")[-1] in ["DO_NOT_COPY", "user_data"]:
            continue
        else:
            print root.split("\\")[-1]
        if filename.endswith(".py"):
            existing_path = os.path.join(root, filename)

            split_root_path =  root.split("\\" + key_split_folder_name +"\\")
            try:
                full_extention = split_root_path[1]
            except:
                full_extention = None

            #print split_root
            if full_extention:
                newly_downloaded_file_path = "\\".join([newly_downloaded_path, full_extention]) + "\\" + filename
            else:
                newly_downloaded_file_path = "\\".join([newly_downloaded_path, filename])

            try:
                checksum_new = hashlib.md5(open(str(newly_downloaded_file_path)).read()).hexdigest()
            except:
                checksum_new = None
            try:
                checksum_old = hashlib.md5(open(str(existing_path)).read()).hexdigest()
            except:
                checksum_old = None
            if checksum_new != checksum_old:
                print "\n"
                print newly_downloaded_file_path
                print checksum_new
                print existing_path
                print checksum_old
                shutil.copy(newly_downloaded_file_path, existing_path)
