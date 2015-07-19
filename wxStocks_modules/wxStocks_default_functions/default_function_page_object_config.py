import config
from wxStocks_modules import wxStocks_db_functions as db

user_created_test_function_page = {
    "title": "Screen Tests",
    "uid_config_reference": config.USER_CREATED_TESTS_UNIQUE_ID,
    "general_text": "Welcome to the user generated test page.",
    "save_button_text": "Save Tests",
    "reset_button_text": "Reset Tests Functions to Default",
    "additional_text": "Create stock screen tests to be imported into the screen page.",
    "function_that_loads_text_of_user_created_functions": db.load_user_created_tests,
    "save_function": db.save_user_created_tests,
    "function_to_load_defaults": db.load_default_tests,
    }
user_created_rank_function_page = {
    "title": "Ranking Functions",
    "uid_config_reference": config.USER_RANKING_FUNCTIONS_UNIQUE_ID,
    "general_text": "Welcome to the user created ranking function page.",
    "save_button_text": "Save Functions",
    "reset_button_text": "Reset Ranking Functions to Default",
    "additional_text": "Create stock ranking functions to be imported into the rank page.",
    "function_that_loads_text_of_user_created_functions": db.load_user_ranking_functions,
    "save_function": db.save_user_ranking_functions,
    "function_to_load_defaults": db.load_default_ranking_functions,
    }
user_created_csv_import_function_page = {
    "title": "CSV Import Functions",
    "uid_config_reference": config.USER_CSV_IMPORT_FUNCTIONS_UNIQUE_ID,
    "general_text": "Welcome to the user created .csv import function page.",
    "save_button_text": "Save Functions",
    "reset_button_text": "Reset CSV Import Functions to Default",
    "additional_text": "Create CSV import functions to be imported into the import page.",
    "function_that_loads_text_of_user_created_functions": db.load_user_csv_import_functions,
    "save_function": db.save_user_csv_import_functions,
    "function_to_load_defaults": db.load_default_csv_import_functions,
    }
user_created_xls_import_function_page = {
    "title": "XLS Import Functions",
    "uid_config_reference": config.USER_CSV_IMPORT_FUNCTIONS_UNIQUE_ID,
    "general_text": "Welcome to the user created .xls import function page.",
    "save_button_text": "Save Functions",
    "reset_button_text": "Reset XLS Import Functions to Default",
    "additional_text": "Create XLS import functions to be imported into the import page.",
    "function_that_loads_text_of_user_created_functions": db.load_user_xls_import_functions,
    "save_function": db.save_user_xls_import_functions,
    "function_to_load_defaults": db.load_default_xls_import_functions,
    }
user_created_portfolio_import_function_page = {
    "title": "Portfolio Import Functions",
    "uid_config_reference": config.USER_PORTFOLIO_IMPORT_FUNCTIONS_UNIQUE_ID,
    "general_text": "Welcome to the user created portfolio import function page.",
    "save_button_text": "Save Functions",
    "reset_button_text": "Reset Portfolio Import Functions to Default",
    "additional_text": "Create Portfolio import functions to be imported into the portfolio page.",
    "function_that_loads_text_of_user_created_functions": db.load_user_portfolio_import_functions,
    "save_function": db.save_user_portfolio_import_functions,
    "function_to_load_defaults": db.load_default_portfolio_import_functions,
    }
user_created_custom_anaylsis_page = {
    "title": "Custom Analysis Functions",
    "uid_config_reference": config.USER_CUSTOM_ANALYSIS_FUNCTIONS_UNIQUE_ID,
    "general_text": "Welcome to the custom analysis editor.",
    "save_button_text": "Save Functions",
    "reset_button_text": "Reset Custom Analysis Functions to Default",
    "additional_text": "Create analysis functions to be imported into the custom anyalsis page.",
    "function_that_loads_text_of_user_created_functions": db.load_user_custom_analysis_functions,
    "save_function": db.save_user_custom_analysis_functions,
    "function_to_load_defaults": db.load_default_custom_analysis_functions,
    }

user_created_function_ref_dict_list = [
    user_created_test_function_page,
    user_created_rank_function_page,
    user_created_csv_import_function_page,
    user_created_xls_import_function_page,
    user_created_portfolio_import_function_page,
    user_created_custom_anaylsis_page,
    ]