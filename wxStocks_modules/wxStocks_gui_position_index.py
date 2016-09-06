import config
print "wxStocks_gui_position_index line 2, add self. to all attributes"
#[osx, debian linux, windows]
#[osx because the o is a 0, linux because the l is a 1, and windows because it deserves to be last]

#MainFrame
MainFrame_size = [(1020,800),( config.DISPLAY_SIZE[0]*(3./4), config.DISPLAY_SIZE[1]*(3./4) ),( config.DISPLAY_SIZE[0]*(3./4), config.DISPLAY_SIZE[1]*(3./4) )][config.OS_TYPE_INDEX]
MainFrame_SetSizeHints = MainFrame_size

#shortcuts
default_width = MainFrame_size[0]
default_height = MainFrame_size[1]

class WelcomePage(object):
    welcome_page_text = (10,10)
    instructions = [(10,20),(10,30),(10,30)][config.OS_TYPE_INDEX]
    reset_password_button = [(5, 700),(default_width - 400, 0),(default_width - 400, 0)][config.OS_TYPE_INDEX]
    text_field_offset = 180
    text_field_vertical_offset = -3
    text_field_vertical_offset_small_bump = 30
    text_field_vertical_offset_medium_bump = 60
    text_field_vertical_offset_large_bump = 90
    text_field_vertical_offset_encryption_bump = 120
    text_field_vertical_offset_optional_bump = 18
    reset_password_bump = 10
    reset_password_negative_vertical_bump = -30
    delete_all_stock_data = [(835, 700),(default_width- 600, 0),(default_width- 600, 0)][config.OS_TYPE_INDEX]

#Get Data Panel
###############
class TickerPage(object):
    AddSpacer = 88 #box vertical offset
    text = (10,10)
    download_button = (5, 30)
    refresh_button = (5, 60)
    more_text = (145,36)

class YqlScrapePage(object):
    text = (10,10)
    scrape_button = (5,100)
    abort_scrape_button = (5,100)
    progress_bar = (0,200)
    progress_bar_size = [(995,-1), ((default_width- 35),-1), ((default_width- 35),-1)][config.OS_TYPE_INDEX]
    total_relevant_tickers = (10,30)
    tickers_to_scrape = (10,50)
    scrape_time_text = (10,70)

#SpreadsheetImportPage
######################
class CsvImportPage(object):
    text = (10,10)
    default_button_position = (0,50)
    default_dropdown_offset = (100,0)

class XlsImportPage(object):
    text = (10,10)
    default_button_position = (0,50)
    default_dropdown_offset = (100,0)
    aaii_offset = 28 # if aaii files in aaii import folder, this button will appear below the import dropdown #currently always shows up i think

#PortfolioPage
##############
class PortfolioAccountTab(object):
    AddSpacer = 54
    add_button = (5,0)
    drop_down = [(11,25),(6,27),(6,27)][config.OS_TYPE_INDEX]
    delete_button = [(800,0),(),(655,0)][config.OS_TYPE_INDEX]
    rename_button = [(568,22),(),(479,26)][config.OS_TYPE_INDEX]
    change_number_of_portfolios_button = [(568,0),(),(479,0)][config.OS_TYPE_INDEX]
    ticker_input = [(250,3),(),(160,1)][config.OS_TYPE_INDEX]
    share_input = [(250,25),(),(160,27)][config.OS_TYPE_INDEX]
    cost_basis_input = [(350,3),(),(273,1)][config.OS_TYPE_INDEX]
    update_button = [(346,22),(),(273,26)][config.OS_TYPE_INDEX]
    update_prices_button = [(446,22),(),(385,26)][config.OS_TYPE_INDEX]
    remove_data_button = [(446,0),(),(385,0)][config.OS_TYPE_INDEX]

#ViewDataPage
#############
class AllStocksPage(object):
    text = (10,10)
    refresh_button = (110,4)
    reset_attribute_button = [(800,4),(),(default_width- 188,4)][config.OS_TYPE_INDEX]

class StockDataPage(object):
    text = [(10,10),(),(10,5)][config.OS_TYPE_INDEX]
    ticker_input = [(110,8),(),(90,1)][config.OS_TYPE_INDEX]
    look_up_button = [(210,5),(),(202,0)][config.OS_TYPE_INDEX]
    search_data = [(110,31),(),(90,27)][config.OS_TYPE_INDEX]
    search_button = [(210,28),(),(202,26)][config.OS_TYPE_INDEX]
    update_yql_basic_data_button = [(300,5),(),(291,0)][config.OS_TYPE_INDEX]
    # there are two other buttons that have been commented out,
    # they will go here if ever reintroduced to the code
    update_additional_data_button = [(430,5),(),(406,0)][config.OS_TYPE_INDEX]

#AnalysisPage
#############
class ScreenPage(object):
    text = (10,10)
    screen_button = [(110,4),(),(90,4)][config.OS_TYPE_INDEX]
    drop_down = [(210,6),(),(180,6)][config.OS_TYPE_INDEX]
    save_screen_button = [(800,4),(),(default_width-124,4)][config.OS_TYPE_INDEX]
    #config.FULL_SPREADSHEET_SIZE_POSITION_TUPLE is referenced here... it should be moved to this file eventually, but is not causing any problems now
    spreadsheet_width_height_offset = (20,128)

class SavedScreenPage(object):
    text = (10,10)
    refresh_screen_button = (110,5)
    load_screen_button = (200,5)
    drop_down = (305,6)
    delete_screen_button = [(880,4),(),(default_width-124,4)][config.OS_TYPE_INDEX]
    #config.FULL_SPREADSHEET_SIZE_POSITION_TUPLE is referenced here... it should be moved to this file eventually, but is not causing any problems now
    spreadsheet_width_height_offset = (20,128)

class RankPage(object):
    rank_page_text = (10,10)
    refresh_screen_button = [(110,5),(),(57,5)][config.OS_TYPE_INDEX]
    load_screen_button = (147,5)
    load_portfolio_button = (147,30)
    update_additional_data_button = (5,30)
    #update_annual_data_button
    #update_analyst_estimates_button
    drop_down = [(305,6),(),(238,6)][config.OS_TYPE_INDEX]
    accounts_drop_down = [(305,31),(),(238,31)][config.OS_TYPE_INDEX]
    clear_button = [(890,4),(),(default_width-124,4)][config.OS_TYPE_INDEX]
    sort_button = (420,30)
    sort_drop_down = (520,31)
    rank_button = (420,5)
    rank_drop_down = (520,6)

class CustomAnalysisPage(object):
    spreadsheet_size=(855,578)
    spreadsheet_position=(105,58)

    ticker_sizer_AddSpacer = spreadsheet_position[1]
    grid_sizer_AddSpacer = spreadsheet_position[1]
    height_offset = spreadsheet_position[1]

    text = (10,10)
    refresh_screen_button = (110,5)
    load_screen_button = (200,5)
    load_portfolio_button = (191,30)
    screen_drop_down = (305, 6)
    accounts_drop_down = (305, 31)
    clear_button = (840,31)
    ticker_input = (805,8)
    add_one_stock_button = (710,5)
    add_all_stocks_button = (710,31)
    analyse = (500,31)

    ticker_display_horizontal_offset = 3
    ticker_display_horizontal_size = 100



class ResearchPage(object):
    text = (10,10)
    ticker_input = (100, 8)
    add_stock_button = (200,5)
    remove_stock_button = (300,5)
    bingbong = (400,5) #loads examples for development, i love them bingbongbrothers
    research_initial_button_vertical_offset = 44
    research_initial_button_horizontal_offset = 60
    research_text_additional_vertical_offset = 6
    research_added_width = 0
    research_default_horizontal_offset = 10

    website_button_horizontal_offset = 60
    stock_initial_button_horizontal_offset = 144
    stock_initial_button_vertical_offset = 80
    stock_text_additional_vertical_offset = 6
    second_line_text_additional_offset = 18
    vertical_offset_per_stock = 40
    stock_added_width = 0
    stock_default_vertical_offset = 10

class SalePrepPage(object):
    pass
class TradePage(object):
    pass
class UserFunctionsPage(object):
    pass
















#spreadsheet_width_height_offset = gui_position.ScreenPage.spreadsheet_width_height_offset
