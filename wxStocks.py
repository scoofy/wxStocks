print("Startup may take a few moments...")
import logging
logging.basicConfig(format='  ---- %(filename)s|%(lineno)d ----\n%(message)s', level=logging.INFO)

import wxStocks_modules.wxStocks_utilities as utils
utils.start_whitespace()
print("Startup may take a few moments...\n")


# Requirements that must be installed
import wx #, numpy

# Standard Libraries
import sys, inspect, hashlib, threading, base64

# Internal libraries
import wxStocks_modules.wxStocks_db_functions as db
import wxStocks_modules.wxStocks_testing
# wxStocks_gui loaded below due to needing to get screen resolution from app

# True globals are in config
import config

# Necessary in-module functions
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    config.ENCRYPTION_POSSIBLE = True
except:
    config.ENCRYPTION_POSSIBLE = False

################################################################################################
# This is due to a serious error in wxPython that exists right now.
# There should be a popup that prompts this password AFTER the mainloop begins, in the init section.
# That does not appear to be functioning, as it freezes all dropdowns and causes other bits of havoc.
# This is a work around to prevent needing to constantly be entering your password.
# It's not the most secure solution, but for all intents and purposes here, it should be fine.

if config.ENCRYPTION_POSSIBLE:
    db.load_encryption_strength()
    import getpass
    print("\n")
    saved_hash = db.is_saved_password_hash()
    if saved_hash:
        # verify
        password = getpass.getpass("Enter your wxStocks encryption password: ")
        if not db.valid_pw(password, saved_hash):
            print("\nPassword invalid, you are not authorized to view this account.")
            reset = input('If you would like to delete all secure data and start over, please type "reset" -- otherwise, press enter: ')
            if reset == "reset":
                db.delete_all_secure_files()
                print("\nSecure files have been removed. Resart wxStocks to set a new password\n")
            else:
                print("\nSorry, but you are not authorized to view this account.\n")
            sys.exit()
        else:
            valid_salt = db.return_salt(saved_hash)
    else:
        password = db.set_password()
        valid_salt = db.return_salt(db.is_saved_password_hash())
    kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=str.encode(valid_salt),
                    iterations=100000,
                    backend=default_backend()
                    )
    config.PASSWORD = base64.urlsafe_b64encode(kdf.derive(str.encode(password)))

    print("\n")
################################################################################################
# Load data
db.load_all_data()

### START ###################################################################
def main():
    app = wx.App()
    display_size = wx.DisplaySize()
    config.DISPLAY_SIZE = display_size
    import wxStocks_modules.wxStocks_gui as gui
    gui.MainFrame().Show()
    app.MainLoop()
main()

# end of line
