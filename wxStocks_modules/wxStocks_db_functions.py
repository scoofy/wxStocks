import wx
import ZODB, ZODB.FileStorage, BTrees.OOBTree, transaction, persistent
from BTrees.OOBTree import OOSet

import config
import inspect, logging, os, threading, hashlib, getpass, glob, time
import pickle
import bcrypt
try:
    from cryptography.fernet import Fernet
except:
    config.ENCRYPTION_POSSIBLE = False

from wxStocks_modules import wxStocks_classes
from wxStocks_modules import wxStocks_utilities as utils

import traceback, sys

###### DB ######
storage = ZODB.FileStorage.FileStorage(os.path.join('DO_NOT_COPY','mydata.fs'))
db = ZODB.DB(storage)
connection = db.open()
root = connection.root

################

secure_file_folder = 'DO_NOT_COPY'
password_file_name = 'password.txt'
password_path = os.path.join('DO_NOT_COPY', password_file_name)
test_path = os.path.join('user_data','user_functions','wxStocks_screen_functions.py')
default_test_path = os.path.join('wxStocks_modules','wxStocks_default_functions','wxStocks_default_screen_functions.py')
rank_path = os.path.join('user_data','user_functions','wxStocks_rank_functions.py')
default_rank_path = os.path.join('wxStocks_modules','wxStocks_default_functions','wxStocks_default_rank_functions.py')
csv_import_path = os.path.join('user_data','user_functions','wxStocks_csv_import_functions.py')
default_csv_import_path = os.path.join('wxStocks_modules','wxStocks_default_functions','wxStocks_default_csv_import_functions.py')
xls_import_path = os.path.join('user_data','user_functions','wxStocks_xls_import_functions.py')
default_xls_import_path = os.path.join('wxStocks_modules','wxStocks_default_functions','wxStocks_default_xls_import_functions.py')
portfolio_import_path = os.path.join('user_data','user_functions','wxStocks_portfolio_import_functions.py')
default_portfolio_import_path = os.path.join('wxStocks_modules','wxStocks_default_functions','wxStocks_default_portfolio_import_functions.py')
custom_analysis_path = os.path.join('user_data','user_functions','wxStocks_custom_analysis_spreadsheet_builder.py')
default_custom_analysis_path = os.path.join('wxStocks_modules','wxStocks_default_functions','wxStocks_default_custom_analysis_spreadsheet_builder.py')
do_not_copy_path = 'DO_NOT_COPY'
encryption_strength_path = os.path.join('wxStocks_data','encryption_strength.txt')


####################### Data Loading ###############################################
def load_all_data():
    # For first launch (if types don't exist)
    dbtype_lists = ["Account", "Stock", "GLOBAL_STOCK_SCREEN_DICT"]
    dbtype_singletons = ["GLOBAL_ATTRIBUTE_SET",
                         "GLOBAL_TICKER_LIST",
                         "SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST",]
    dbtypes = dbtype_lists + dbtype_singletons
    commit = False

    for dbtype in dbtypes:
        try:
            assert(hasattr(root, dbtype))
        except:
            logging.info("Creating DB for: {}".format(dbtype))
            if dbtype in dbtype_lists:
                setattr(root, dbtype, BTrees.OOBTree.BTree())
                commit = True
            elif dbtype in dbtype_singletons:
                if dbtype.endswith("_SET"):
                    setattr(root, dbtype, OOSet())
                    commit = True
                elif dbtype.endswith("_LIST"):
                    setattr(root, dbtype, persistent.list.PersistentList())
                    commit = True
                else:
                    logging.error("DB type {} does not conform. Exiting...".format(dbtype))
            else:
                logging.error("DB types have been changed")
                sys.exit()

    if commit:
        commit_db()
    # now load db data if they exist
    load_GLOBAL_STOCK_DICT()
    load_all_portfolio_objects()
    load_GLOBAL_STOCK_SCREEN_DICT()
    load_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST()
def savepoint_db():
    transaction.savepoint(True)
def commit_db():
    transaction.commit()

# start up try/except clauses below

# Dont think these are used any more
def load_GLOBAL_TICKER_LIST(): ###### updated
    logging.info("Loading GLOBAL_TICKER_LIST")
    try:
        config.GLOBAL_TICKER_LIST = root.GLOBAL_TICKER_LIST
    except:
        logging.error("GLOBAL_TICKER_LIST load error")
        sys.exit()
def save_GLOBAL_TICKER_LIST(): ###### updated
    logging.info("Saving GLOBAL_TICKER_LIST")
    commit_db()
def delete_GLOBAL_TICKER_LIST(): ###### updated
    logging.info("Deleting GLOBAL_TICKER_LIST")
    root.GLOBAL_TICKER_LIST = list()
    commit_db()
###

### Global Stock dict functions
def create_new_Stock_if_it_doesnt_exist(ticker):
    if not type(ticker) == str:
        ticker = str(ticker)
    symbol = ticker.upper()
    if symbol.isalpha():
        pass
    else:
        if "." in symbol:
            pass
        if "^" in symbol:
            # Nasdaq preferred
            symbol = symbol.replace("^", ".P")
        if "/" in symbol:
            # Warrants currently ignored but this function should be reexamined if warrents to be included in the future
            # if "/WS" in symbol:
            #   # Nasdaq Warrent
            #   if "/WS/" in symbol:
            #       # more complicated version of the same thing
            #       self.nasdaq_symbol = symbol
            #       self.yahoo_symbol = symbol.replace("/WS/","-WT")
            #       # I don't know how morningstar does warrents
            #   else:
            #       self.nasdaq_symbol = symbol
            #       self.yahoo_symbol = symbol.replace("/WS","-WT")
            #   self.aaii_symbol = None

            # If bloomberg is integrated, this will need to be changed for preferred stock
            # if "/P" in symbol:
            #   pass

            # Nasdaq class share
            symbol = symbol.replace("/", ".")
        if "-" in symbol:
            if "-P" in symbol:
                # Yahoo preferred
                symbol = symbol.replace("-P", ".P")
            else:
                # Yahoo Class
                symbol = symbol.replace("-", ".")
        if " PR" in symbol:
            # AAII preferred
            symbol = symbol.replace(" PR", ".P")

    # Finally:
    # if morningstar preferred notation "XXXPRX", i don't know how to fix that since "PRE" is a valid ticker
    if not symbol.isalpha():
        index_to_replace_list = []
        for char in symbol:
            if not char.isalpha():
                if char != ".": #something is very broken
                    logging.warning("illegal ticker symbol: {}\nwill replace with underscores".format(symbol))
                    index_to_replace_list.append(symbol.index(char))
        if index_to_replace_list:
            symbol = list(symbol)
            for index_instance in index_to_replace_list:
                symbol[index_instance] = "_"
            symbol = "".join(symbol)


    stock = config.GLOBAL_STOCK_DICT.get(symbol)
    if not stock:
        stock = wxStocks_classes.Stock(symbol)
        root.Stock[symbol] = stock
        transaction.savepoint(True)
    return stock
def set_Stock_attribute(Stock, attribute_name, value, data_source_suffix):
    full_attribute_name = attribute_name + data_source_suffix
    if value is not None:
        setattr(Stock, full_attribute_name, str(value))
    else:
        setattr(Stock, full_attribute_name, None)
    if not attribute_name in config.GLOBAL_ATTRIBUTE_SET:
        config.GLOBAL_ATTRIBUTE_SET.add(full_attribute_name)
def load_GLOBAL_STOCK_DICT(): ###### updated
    config.GLOBAL_STOCK_DICT = root.Stock
    load_GLOBAL_ATTRIBUTE_SET()
def load_GLOBAL_STOCK_DICT_into_active_memory():
    unpack_stock_data_thread = threading.Thread(target=load_GLOBAL_STOCK_DICT_into_active_memory_worker)
    unpack_stock_data_thread.start()
def load_GLOBAL_STOCK_DICT_into_active_memory_worker():
    start = time.time()
    unpack = [x.ticker for x in config.GLOBAL_STOCK_DICT.values()]
    finish = time.time()
    logging.info("Stocks now in active memory: {} seconds".format(round(finish-start)))
def save_GLOBAL_STOCK_DICT(): ##### no need to update
    logging.info("Saving GLOBAL_STOCK_DICT")
    commit_db()
    logging.info("GLOBAL_STOCK_DICT saved.")
def load_GLOBAL_ATTRIBUTE_SET(): ###### up
    logging.info("Loading GLOBAL_ATTRIBUTE_SET")
    try:
        config.GLOBAL_ATTRIBUTE_SET = root.GLOBAL_ATTRIBUTE_SET
    except:
        logging.error("GLOBAL_ATTRIBUTE_SET load error")
        sys.exit()
def save_GLOBAL_ATTRIBUTE_SET(): ###### updated
    logging.info("Saving GLOBAL_ATTRIBUTE_SET")
    commit_db()
    logging.info("GLOBAL_ATTRIBUTE_SET saved.")

### Stock screen loading information
def load_GLOBAL_STOCK_SCREEN_DICT(): ###### updated
    logging.info("Loading GLOBAL_STOCK_SCREEN_DICT")
    config.GLOBAL_STOCK_SCREEN_DICT = root.GLOBAL_STOCK_SCREEN_DICT
def save_GLOBAL_STOCK_STREEN_DICT(): ###### updated
    logging.info("Saving GLOBAL_STOCK_STREEN_DICT")
    commit_db()
def load_named_screen(screen_name): ###### updated
    logging.info("Loading Screen: {}".format(screen_name))
    screen_list = root.GLOBAL_STOCK_SCREEN_DICT["{}".format(screen_name)]
    stock_list = []
    for ticker in screen_ticker_list:
        stock = utils.return_stock_by_symbol(ticker)
        if not stock in stock_list:
            stock_list.append(stock)
    return stock_list
def save_named_screen(screen_name, stock_list): ###### updated
    logging.info("Saving screen named: {}".format(screen_name))
    ticker_list = []
    for stock in stock_list:
        ticker_list.append(stock.symbol)
    root.GLOBAL_STOCK_SCREEN_DICT["{}".format(screen_name)] = ticker_list
def delete_named_screen(screen_name): ###### updated
    logging.info("Deleting named screen: {}".format(screen_name))
    logging.info(config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST)
    config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST = [x for x in config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST if x[0] != screen_name]
    logging.info(config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST)
    save_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST()
    del root.GLOBAL_STOCK_SCREEN_DICT["{}".format(screen_name)]

def load_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST(): ###### updated
    logging.info("Loading SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST")
    config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST = root.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST
def save_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST(): ###### updated
    logging.info("Saving SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST")
    commit_db()
###

### Screen test functions
def load_default_tests():
    test_file = open(default_test_path, 'r')
    text = test_file.read()
    test_file.close()
    return text
def load_user_created_tests():
    try:
        test_file = open(test_path, 'r')
        text = test_file.read()
        test_file.close()
    except:
        text = load_default_tests()
    return text
def save_user_created_tests(text):
    with open(test_path, "w") as output:
        output.write(text)

def load_default_ranking_functions():
    test_file = open(default_rank_path, 'r')
    text = test_file.read()
    test_file.close()
    return text
def load_user_ranking_functions():
    try:
        function_file = open(rank_path, 'r')
        text = function_file.read()
        function_file.close()
    except:
        text = load_default_ranking_functions()
    return text
def save_user_ranking_functions(text):
    with open(rank_path, "w") as output:
        output.write(text)

def load_default_csv_import_functions():
    test_file = open(default_csv_import_path, 'r')
    text = test_file.read()
    test_file.close()
    return text
def load_user_csv_import_functions():
    try:
        function_file = open(csv_import_path, 'r')
        text = function_file.read()
        function_file.close()
    except:
        text = load_default_csv_import_functions()
    return text
def save_user_csv_import_functions(text):
    with open(csv_import_path, "w") as output:
        output.write(text)

def load_default_xls_import_functions():
    test_file = open(default_xls_import_path, 'r')
    text = test_file.read()
    test_file.close()
    return text
def load_user_xls_import_functions():
    try:
        function_file = open(xls_import_path, 'r')
        text = function_file.read()
        function_file.close()
    except:
        text = load_default_xls_import_functions()
    return text
def save_user_xls_import_functions(text):
    with open(xls_import_path, "w") as output:
        output.write(text)

def load_default_portfolio_import_functions():
    test_file = open(default_portfolio_import_path, 'r')
    text = test_file.read()
    test_file.close()
    return text
def load_user_portfolio_import_functions():
    try:
        function_file = open(portfolio_import_path, 'r')
        text = function_file.read()
        function_file.close()
    except:
        text = load_default_csv_import_functions()
    return text
def save_user_portfolio_import_functions(text):
    with open(portfolio_import_path, "w") as output:
        output.write(text)

def load_default_custom_analysis_functions():
    test_file = open(default_custom_analysis_path, 'r')
    text = test_file.read()
    test_file.close()
    return text
def load_user_custom_analysis_functions():
    try:
        function_file = open(custom_analysis_path, 'r')
        text = function_file.read()
        function_file.close()
    except:
        text = load_default_custom_analysis_functions()
    return text
def save_user_custom_analysis_functions(text):
    with open(custom_analysis_path, "w") as output:
        output.write(text)


### Portfolio functions need encryption/decryption
def decrypt_if_possible(object_type, object_name): ###### updated
    error = False
    data = None
    if config.ENCRYPTION_POSSIBLE:
        fernet_obj = Fernet(config.PASSWORD)
        try:
            encrypted_string = getattr(root, object_type)["{}".format(object_name)]
            pickled_string = fernet_obj.decrypt(str.encode(encrypted_string))
            data = pickle.loads(pickled_string)
        except Exception as e:
            logging.error(e)
            data = None
    else:
        try:
            data = getattr(root, object_type)["{}".format(object_name)]
        except Exception as e:
            logging.error(e)
            data = None
    return data

def create_new_Account_if_one_doesnt_exist(portfolio_id, name = None): ###### no need to update
    portfolio_obj = config.PORTFOLIO_OBJECTS_DICT.get(portfolio_id)
    if not portfolio_obj: # check saved version
        portfolio_obj = load_portfolio_object(portfolio_id)
    if not portfolio_obj: # create new version
        portfolio_obj = wxStocks_classes.Account(portfolio_id, name = name)
    save_portfolio_object(portfolio_obj)
    return portfolio_obj

def save_portfolio_object(portfolio_obj): ###### updated
    # First, set this object into the portfolio dict, for the first time it's saved:
    id_number = portfolio_obj.id_number
    config.PORTFOLIO_OBJECTS_DICT[str(id_number)] = portfolio_obj
    unencrypted_pickle_string = pickle.dumps(portfolio_obj)
    if config.ENCRYPTION_POSSIBLE:
        fernet_obj = Fernet(config.PASSWORD)
        encrypted_string = fernet_obj.encrypt(unencrypted_pickle_string).decode('utf-8')
        fernet_obj = None

        root.Account['Account{}'.format(id_number)] = encrypted_string
    else:
        logging.info("config.ENCRYPTION_POSSIBLE: {}".format(config.ENCRYPTION_POSSIBLE))
        root.Account['Account{}'.format(id_number)] = unencrypted_pickle_string
    commit_db()

def load_portfolio_object(id_number): ###### updated
    portfolio_obj = decrypt_if_possible("Account", "Account{}".format(id_number))
    if portfolio_obj:
        config.PORTFOLIO_OBJECTS_DICT[str(portfolio_obj.id_number)] = portfolio_obj
        #logging.info("Portfolio objects dict: {}".formatconfig.PORTFOLIO_OBJECTS_DICT))
        return portfolio_obj
    else:
        logging.warning("Account object failed {id_num} to load.".format(id_num = id_number))
        return
def load_all_portfolio_objects(): ###### updated
    if not config.ENCRYPTION_POSSIBLE:
        logging.info("config.ENCRYPTION_POSSIBLE: {}".format(config.ENCRYPTION_POSSIBLE))
    num_of_portfolios = len(root.Account.values())
    logging.info("attempting to load {} possible portfolios".format(num_of_portfolios))
    for i in range(num_of_portfolios):
        portfolio_obj = load_portfolio_object(i+1)
        if portfolio_obj:
            config.PORTFOLIO_OBJECTS_DICT[str(i+1)] = portfolio_obj
def delete_portfolio_object(id_number): ###### updated
    "delete account"
    del config.PORTFOLIO_OBJECTS_DICT[str(portfolio_obj.id_number)]
    del root.Account['Account{}'.format(id_number)]

### Password data
def is_saved_password_hash(path = password_path):
    try:
        encrypted_file = open(path, 'r')
        bcrypted_password = encrypted_file.read()
        encrypted_file.close()
        return bcrypted_password
    except IOError:
        return False
def set_password():
    password = getpass.getpass("Set your wxStocks encryption password: ")
    if password:
        check_password = getpass.getpass("\nPlease confirm your password by entering it again: ")
    else:
        check_password =  input('\nFailing to enter a password will make your data insecure.\nPlease confirm no password by leaving the following entry blank.\nIf you want to use a password, type "retry" and press enter to reset your password: ')

    if password != check_password:
        print("\nThe passwords you entered did not match.\nPlease try again\n")
        return set_password()
    else:
        save_password(password)
        return password
def save_password(password, path = password_path):
    logging.info("Generating a secure password hash, this may take a moment...")
    bcrypt_hash = make_pw_hash(password)
    with open(path, 'w') as output:
        output.write(bcrypt_hash)

def reset_all_encrypted_files_with_new_password(old_password, new_password, encryption_strength):
    old_password_hashed = hashlib.sha256(old_password).hexdigest()
    new_password_hashed = hashlib.sha256(new_password).hexdigest()

    file_names = os.listdir(do_not_copy_path)
    file_names.remove(password_file_name)

    from modules.simplecrypt import encrypt, decrypt
    for file_name in file_names:
        path = do_not_copy_path + "/" + file_name
        encrypted_file = open(path, 'r')
        encrypted_string = encrypted_file.read()
        encrypted_file.close()
        try:
            decrypted_string = decrypt(old_password_hashed, encrypted_string)
            re_encrypted_string = encrypt(new_password_hashed, decrypted_string)
            with open(path, 'w') as output:
                output.write(re_encrypted_string)
            logging.info("{} has been encrypted and saved".format(file_name))
        except Exception as e:
            logging.error(e)
            logging.error("Error: {} did not save properly, and the data will need to be retrieved manually with your old password.".format(file_name))
    config.PASSWORD = new_password_hashed

    if encryption_strength:
        config.ENCRYPTION_HARDNESS_LEVEL = encryption_strength
        save_encryption_strength(encryption_strength)

    save_password(new_password)
    logging.info("You have successfully changed your password.")

def load_encryption_strength(path = encryption_strength_path):
    try:
        strength_file = open(path, 'r')
        strength = strength_file.read()
        strength_file.close()
        strength = int(strength)
        config.ENCRYPTION_HARDNESS_LEVEL = strength
        if config.ENCRYPTION_HARDNESS_LEVEL != config.DEFAULT_ENCRYPTION_HARDNESS_LEVEL:
            logging.warning("New ENCRYPTION_HARDNESS_LEVEL of {}".format(strength))
    except:
        save_encryption_strength(config.DEFAULT_ENCRYPTION_HARDNESS_LEVEL)
def save_encryption_strength(strength, path = encryption_strength_path):
    if not strength:
        strength = str(config.DEFAULT_ENCRYPTION_HARDNESS_LEVEL)
    else:
        strength = str(strength)
    with open(path, 'w') as output:
        output.write(strength)
### Secure data wipe
def delete_all_secure_files(path = secure_file_folder):
    file_list = os.listdir(path)
    for file_name in file_list:
        os.remove(path+"/"+file_name)
############################################################################################

####################### Hashing Functions #######################
####################### SHA256
def make_sha256_hash(pw):
    return hashlib.sha256(pw).hexdigest()

####################### Bcrypt
def make_pw_hash(pw, salt=None):
    if not salt:
        salt = bcrypt.gensalt(config.ENCRYPTION_HARDNESS_LEVEL).decode("utf-8")
    pw_hashed = bcrypt.hashpw(str.encode(pw), str.encode(salt)).decode("utf-8")
    return '{}|{}'.format(pw_hashed, salt)
def valid_pw(pw, h):
    logging.info("Validating your password, this may take a moment...")
    return h == make_pw_hash(pw, h.split('|')[1])
def return_salt(h):
    salt = h.split('|')[1]
    if salt:
        return salt
    else:
        return None

#########################################################

# End of line...
