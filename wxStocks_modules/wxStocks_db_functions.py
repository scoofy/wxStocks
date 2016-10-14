import wx
import config
import inspect, logging, os, threading, hashlib, getpass, glob
import cPickle as pickle
from modules.pybcrypt import bcrypt

import wxStocks_classes
import wxStocks_utilities as utils

import traceback, sys

ticker_path = 'wxStocks_data/ticker.pk'
all_stocks_path = 'wxStocks_data/all_stocks_dict.pk'
all_attributes_path = 'wxStocks_data/all_attributes_set.pk'
screen_dict_path = 'wxStocks_data/screen_dict.pk'
named_screen_path = 'wxStocks_data/screen-%s.pk'
screen_name_and_time_created_tuple_list_path = 'wxStocks_data/screen_names_and_times_tuple_list.pk'
secure_file_folder = 'DO_NOT_COPY'
portfolios_path = 'DO_NOT_COPY/portfolios.%s'
portfolio_account_obj_file_path = 'DO_NOT_COPY/portfolio_%d_data.%s'
password_file_name = 'password.txt'
password_path = 'DO_NOT_COPY/' + password_file_name
test_path = 'user_data/user_functions/wxStocks_screen_functions.py'
default_test_path = 'wxStocks_modules/wxStocks_default_functions/wxStocks_default_screen_functions.py'
rank_path = 'user_data/user_functions/wxStocks_rank_functions.py'
default_rank_path = 'wxStocks_modules/wxStocks_default_functions/wxStocks_default_rank_functions.py'
csv_import_path = 'user_data/user_functions/wxStocks_csv_import_functions.py'
default_csv_import_path = 'wxStocks_modules/wxStocks_default_functions/wxStocks_default_csv_import_functions.py'
xls_import_path = 'user_data/user_functions/wxStocks_xls_import_functions.py'
default_xls_import_path = 'wxStocks_modules/wxStocks_default_functions/wxStocks_default_xls_import_functions.py'
portfolio_import_path = 'user_data/user_functions/wxStocks_portfolio_import_functions.py'
default_portfolio_import_path = 'wxStocks_modules/wxStocks_default_functions/wxStocks_default_portfolio_import_functions.py'
custom_analysis_path = 'user_data/user_functions/wxStocks_custom_analysis_spreadsheet_builder.py'
default_custom_analysis_path = 'wxStocks_modules/wxStocks_default_functions/wxStocks_default_custom_analysis_spreadsheet_builder.py'
do_not_copy_path = 'DO_NOT_COPY'
encryption_strength_path = 'wxStocks_data/encryption_strength.txt'


####################### Data Loading ###############################################
def load_all_data():
    load_GLOBAL_STOCK_DICT()
    load_GLOBAL_TICKER_LIST()
    load_all_portfolio_objects()
    load_GLOBAL_STOCK_SCREEN_DICT()
    load_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST()
# start up try/except clauses below

# Dont think these are used any more
def load_GLOBAL_TICKER_LIST():
    print line_number(), "Loading GLOBAL_TICKER_LIST"
    try:
        ticker_list = open(ticker_path, 'rb')
    except Exception, e:
        print line_number(), e
        ticker_list = open(ticker_path, 'wb')
        ticker_list = []
        with open(ticker_path, 'wb') as output:
            pickle.dump(ticker_list, output, pickle.HIGHEST_PROTOCOL)
        ticker_list = open(ticker_path, 'rb')
    config.GLOBAL_TICKER_LIST = pickle.load(ticker_list)
    ticker_list.close()
    return config.GLOBAL_TICKER_LIST
def save_GLOBAL_TICKER_LIST():
    with open(ticker_path, 'wb') as output:
        pickle.dump(config.GLOBAL_TICKER_LIST, output, pickle.HIGHEST_PROTOCOL)
def delete_GLOBAL_TICKER_LIST():
    config.GLOBAL_TICKER_LIST = []
    with open(ticker_path, 'wb') as output:
        pickle.dump(config.GLOBAL_TICKER_LIST, output, pickle.HIGHEST_PROTOCOL)
###

### Global Stock dict functions
def create_new_Stock_if_it_doesnt_exist(ticker):
    if not type(ticker) == str:
        ticker = str(ticker)
    symbol = ticker.upper()
    if symbol.isalpha():
        pass
    else:
        #print line_number(), symbol
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
                    print line_number()
                    print "illegal ticker symbol:", symbol
                    print "will replace with underscores"
                    index_to_replace_list.append(symbol.index(char))
        if index_to_replace_list:
            symbol = list(symbol)
            for index_instance in index_to_replace_list:
                symbol[index_instance] = "_"
            symbol = "".join(symbol)


    stock = config.GLOBAL_STOCK_DICT.get(symbol)
    if stock:
        #print "%s already exists." % symbol
        return stock
    else:
        stock = wxStocks_classes.Stock(symbol)
        config.GLOBAL_STOCK_DICT[symbol] = stock
        return stock
def set_Stock_attribute(Stock, attribute_name, value, data_source_suffix):
    full_attribute_name = attribute_name + data_source_suffix
    if value is not None:
        setattr(Stock, full_attribute_name, str(value))
    else:
        setattr(Stock, full_attribute_name, None)
    if not attribute_name in config.GLOBAL_ATTRIBUTE_SET:
        config.GLOBAL_ATTRIBUTE_SET.add(full_attribute_name)
def load_GLOBAL_STOCK_DICT():
    print line_number(), "\n"
    sys.stdout.write("Loading GLOBAL_STOCK_DICT: this may take a couple of minutes.")
    sys.stdout.flush()
    try:
        pickled_file = open(all_stocks_path, 'rb')
        stock_dict = pickle.load(pickled_file)
        config.GLOBAL_STOCK_DICT = stock_dict

    except Exception, e:
        print "If this is your first time opening wxStocks, please ignore the following exception, otherwise, your previously saved data may have been deleted."
        print line_number(), e
        stock_dict = config.GLOBAL_STOCK_DICT
        with open(all_stocks_path, 'wb') as output:
            pickle.dump(stock_dict, output, pickle.HIGHEST_PROTOCOL)
    load_GLOBAL_ATTRIBUTE_SET()
def save_GLOBAL_STOCK_DICT():
    save_thread = threading.Thread(name = "saving", target = save_GLOBAL_STOCK_DICT_worker)
    save_thread.start()

def save_GLOBAL_STOCK_DICT_worker():
    print line_number(), "Saving GLOBAL_STOCK_DICT"
    stock_dict = config.GLOBAL_STOCK_DICT.copy()
    with open(all_stocks_path, 'wb') as output:
        pickle.dump(stock_dict, output, pickle.HIGHEST_PROTOCOL)
    print line_number(), "GLOBAL_STOCK_DICT saved."
    stock_dict.clear()
    # save the attribute set when doing this
    save_GLOBAL_ATTRIBUTE_SET()
def load_GLOBAL_ATTRIBUTE_SET():
    print line_number(), "Loading GLOBAL_ATTRIBUTE_SET"
    try:
        pickled_file = open(all_attributes_path, 'rb')
        attribute_set = pickle.load(pickled_file)
        config.GLOBAL_ATTRIBUTE_SET = attribute_set

    except Exception, e:
        print "If this is your first time opening wxStocks, please ignore the following exception, otherwise, your previously saved data may have been deleted."
        print line_number(), e
        attribute_set = config.GLOBAL_ATTRIBUTE_SET
        with open(all_attributes_path, 'wb') as output:
            pickle.dump(attribute_set, output, pickle.HIGHEST_PROTOCOL)
def save_GLOBAL_ATTRIBUTE_SET():
    print line_number(), "Saving GLOBAL_ATTRIBUTE_SET"
    attribute_set = config.GLOBAL_ATTRIBUTE_SET
    with open(all_attributes_path, 'wb') as output:
        pickle.dump(attribute_set, output, pickle.HIGHEST_PROTOCOL)
    print line_number(), "GLOBAL_ATTRIBUTE_SET saved."

### Stock screen loading information
def load_GLOBAL_STOCK_SCREEN_DICT():
    print line_number(), "Loading GLOBAL_STOCK_SCREEN_DICT"
    try:
        existing_screen_names_file = open(screen_dict_path, 'rb')
    except Exception, exception:
        print line_number(), exception
        existing_screen_names_file = open(screen_dict_path, 'wb')
        empty_dict = {}
        with open(screen_dict_path, 'wb') as output:
            pickle.dump(empty_dict, output, pickle.HIGHEST_PROTOCOL)
        existing_screen_names_file = open(screen_dict_path, 'rb')
    existing_screen_names = pickle.load(existing_screen_names_file)
    existing_screen_names_file.close()
    config.GLOBAL_STOCK_SCREEN_DICT = existing_screen_names
def save_GLOBAL_STOCK_STREEN_DICT():
    print "Saving GLOBAL_STOCK_STREEN_DICT"
    existing_screens = config.GLOBAL_STOCK_SCREEN_DICT
    with open(screen_dict_path, 'wb') as output:
        pickle.dump(existing_screens, output, pickle.HIGHEST_PROTOCOL)
def load_named_screen(screen_name):
    print "Loading Screen: %s" % screen_name
    try:
        screen_file = open(named_screen_path % screen_name.replace(' ','_'), 'rb')
        screen_ticker_list = pickle.load(screen_file)
        screen_file.close()
    except Exception as e:
        print line_number(), e
        print "Screen: %s failed to load." % screen_name
    stock_list = []
    for ticker in screen_ticker_list:
        stock = utils.return_stock_by_symbol(ticker)
        if not stock in stock_list:
            stock_list.append(stock)
    return stock_list
def save_named_screen(screen_name, stock_list):
    print "Saving screen named: %s" % screen_name
    ticker_list = []
    for stock in stock_list:
        ticker_list.append(stock.symbol)
    with open(named_screen_path % screen_name.replace(' ','_'), 'wb') as output:
        pickle.dump(ticker_list, output, pickle.HIGHEST_PROTOCOL)
def delete_named_screen(screen_name):
    print "Deleting named screen: %s" % screen_name

    print line_number(), config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST
    config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST = [x for x in config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST if x[0] != screen_name]
    print line_number(), config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST
    save_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST()
    os.remove(named_screen_path % screen_name.replace(' ', '_'))

def load_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST():
    print line_number(), "Loading SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST"
    try:
        existing_tuple_list_file = open(screen_name_and_time_created_tuple_list_path, 'rb')
    except Exception, exception:
        print line_number(), exception
        existing_tuple_list_file = open(screen_name_and_time_created_tuple_list_path, 'wb')
        empty_list = []
        with open(screen_name_and_time_created_tuple_list_path, 'wb') as output:
            pickle.dump(empty_list, output, pickle.HIGHEST_PROTOCOL)
        existing_tuple_list_file = open(screen_name_and_time_created_tuple_list_path, 'rb')
    existing_tuple_list = pickle.load(existing_tuple_list_file)
    existing_tuple_list_file.close()
    config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST = existing_tuple_list
def save_SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST():
    print "Saving SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST"
    tuple_list = config.SCREEN_NAME_AND_TIME_CREATED_TUPLE_LIST
    with open(screen_name_and_time_created_tuple_list_path, 'wb') as output:
        pickle.dump(tuple_list, output, pickle.HIGHEST_PROTOCOL)
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


###


### Portfolio functions need encryption/decryption
def decrypt_if_possible(path):
    error = False
    data = None
    #print line_number(), "config.ENCRYPTION_POSSIBLE", config.ENCRYPTION_POSSIBLE
    if config.ENCRYPTION_POSSIBLE:
        try:
            import Crypto
            from modules.simplecrypt import encrypt, decrypt
        except:
            config.ENCRYPTION_POSSIBLE = False
            print line_number(), "Error: DATA_ABOUT_PORTFOLIOS did not load"
            return
        try:
            encrypted_file = open(path, 'r')
            print line_number(), encrypted_file
        except Exception as e:
            print line_number(), e
            print line_number(), "Decryption not possible, account file doesn't exist"
            encrypted_file = None
        if encrypted_file:
            try:
                encrypted_string = encrypted_file.read()
                print line_number(), encrypted_string
                encrypted_file.close()
            except Exception as e:
                print line_number(), e
                print line_number(), "encryption string or close error"
                encrypted_string = None
            if not encrypted_string:
                error = True
            else:
                try:
                    pickled_string = decrypt(config.PASSWORD, encrypted_string)
                except Exception as e:
                    print line_number(), e
                    print line_number(), "decrypt error"
                    pickled_string = None
                if not pickled_string:
                    error = True
                else:
                    try:
                        data = pickle.loads(pickled_string)
                    except Exception as e:
                        print line_number(), e
                        print line_number(), "depickle error"
                        print line_number(), "Decryption not possible, account file doesn't exist"
        if not data:
            try:
                unencrypted_pickle_file = open(path.replace(".txt",".pk"), 'r')
                data = pickle.load(unencrypted_pickle_file)
                unencrypted_pickle_file.close()
                print line_number(), "Decryption not possible, but unencrypted file exists and will be used instead."
            except Exception as e:
                #print line_number(), e
                error = True
    else:
        try:
            unencrypted_pickle_file = open(path.replace(".txt",".pk"), 'r')
            data = pickle.load(unencrypted_pickle_file)
            unencrypted_pickle_file.close()
        except Exception as e:
            print e
            error = True
    if not error:
        return data
    else:
        if config.ENCRYPTION_POSSIBLE:
            #print line_number(), "Error loading encrypted file"
            #print line_number(), path
            pass
        else:
            #print line_number(), "Error loading unencrypted file"
            #print line_number(), path
            pass
        return None

def create_new_Account_if_one_doesnt_exist(portfolio_id, name = None):
    # check live version
    portfolio_obj = config.PORTFOLIO_OBJECTS_DICT.get(portfolio_id)
    if not portfolio_obj: # check saved version
        portfolio_obj = load_portfolio_object(portfolio_id)
    if not portfolio_obj: # create new version
        portfolio_obj = wxStocks_classes.Account(portfolio_id, name = name)
    save_portfolio_object(portfolio_obj)
    return portfolio_obj

def save_portfolio_object(portfolio_obj):
    # First, set this object into the portfolio dict, for the first time it's saved:
    id_number = portfolio_obj.id_number
    config.PORTFOLIO_OBJECTS_DICT[str(id_number)] = portfolio_obj

    print line_number(), "config.ENCRYPTION_POSSIBLE", config.ENCRYPTION_POSSIBLE
    if config.ENCRYPTION_POSSIBLE:
        try:
            import Crypto
            from modules.simplecrypt import encrypt, decrypt
            encryption_possible = True
        except Exception as e:
            pass
    if config.ENCRYPTION_POSSIBLE:
        path = portfolio_account_obj_file_path % (id_number, "txt")
        unencrypted_pickle_string = pickle.dumps(portfolio_obj)
        encrypted_string = encrypt(config.PASSWORD, unencrypted_pickle_string)
        with open(path, 'w') as output:
            output.write(encrypted_string)
    else:
        path = portfolio_account_obj_file_path % (id_number, "pk")
        with open(path, 'w') as output:
            pickle.dump(portfolio_obj, output, pickle.HIGHEST_PROTOCOL)
def load_portfolio_object(id_number):
    print line_number(), "config.ENCRYPTION_POSSIBLE", config.ENCRYPTION_POSSIBLE
    if config.ENCRYPTION_POSSIBLE:
        path = portfolio_account_obj_file_path % (id_number, "txt")
    else:
        path = portfolio_account_obj_file_path % (id_number, "pk")
    portfolio_obj = decrypt_if_possible(path = path)

    if portfolio_obj:
        config.PORTFOLIO_OBJECTS_DICT[str(portfolio_obj.id_number)] = portfolio_obj
        print "Portfolio objects dict:", config.PORTFOLIO_OBJECTS_DICT
        return portfolio_obj
    else:
        print line_number(), "Account object failed {id_num} to load.".format(id_num = id_number)
        return
def load_all_portfolio_objects():
    num_of_py_files = len(glob.glob1(secure_file_folder,"*.pk"))
    num_of_txt_files = len(glob.glob1(secure_file_folder,"*.txt"))
    total_num_of_possible_account_files = num_of_py_files + num_of_txt_files
    print line_number(), "attempting to load", total_num_of_possible_account_files, "possible portfolios"
    for i in range(total_num_of_possible_account_files):
        portfolio_obj = load_portfolio_object(i+1)
        if portfolio_obj:
            config.PORTFOLIO_OBJECTS_DICT[str(i+1)] = portfolio_obj
def delete_portfolio_object(id_number):
    "delete account"
    print line_number(), "config.ENCRYPTION_POSSIBLE", config.ENCRYPTION_POSSIBLE
    if config.ENCRYPTION_POSSIBLE:
        path = portfolio_account_obj_file_path % (id_number, "txt")
    else:
        path = portfolio_account_obj_file_path % (id_number, "pk")
    portfolio_obj = decrypt_if_possible(path = path)
    if portfolio_obj:
        try:
            os.remove(path)
        except Exception as e:
            print line_number(), e
            if config.ENCRYPTION_POSSIBLE:
                print "Deleting encrypted file failed, will attempt to delete an unencrypted instance of the file."
                try:
                    os.remove(path.replace(".txt", ".pk"))
                except Exception as e:
                    print e
                    print line_number(), "Error: account object failed to be deleted."
                    return
            else:
                print line_number(), "Error: account object failed to be deleted."
                return
        portfolio_obj = None
        print line_number(), "Account object has been deleted."
        return True
    else:
        print line_number(), "Error: account object failed to be deleted. It may not exist."
        return False

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
        check_password =  raw_input('\nFailing to enter a password will make your data insecure.\nPlease confirm no password by leaving the following entry blank.\nIf you want to use a password, type "retry" and press enter to reset your password: ')

    if password != check_password:
        print "\nThe passwords you entered did not match.\nPlease try again\n"
        set_password()
    save_password(password)
    return password
def save_password(password, path = password_path):
    print line_number(), "Generating a secure password hash, this may take a moment..."
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
            print line_number(), file_name, "has been encrypted and saved"
        except Exception as e:
            print e
            print line_number(), "Error:", file_name, "did not save properly, and the data will need to be retrieved manually with your old password."
    config.PASSWORD = new_password_hashed

    if encryption_strength:
        config.ENCRYPTION_HARDNESS_LEVEL = encryption_strength
        save_encryption_strength(encryption_strength)

    save_password(new_password)
    print line_number(), "You have successfully changed your password."

def load_encryption_strength(path = encryption_strength_path):
    try:
        strength_file = open(path, 'r')
        strength = strength_file.read()
        strength_file.close()
        strength = int(strength)
        config.ENCRYPTION_HARDNESS_LEVEL = strength
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
        salt = bcrypt.gensalt(config.ENCRYPTION_HARDNESS_LEVEL)
    pw_hashed = bcrypt.hashpw(pw, salt)
    return '%s|%s' % (pw_hashed, salt)
def valid_pw(pw, h):
    print line_number(), "Validating your password, this may take a moment..."
    return h == make_pw_hash(pw, h.split('|')[1])
#########################################################


############################################################################################
def line_number():
    """Returns the current line number in our program."""
    return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)
# End of line...
