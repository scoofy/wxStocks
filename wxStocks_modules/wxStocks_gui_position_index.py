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
    AddSpacer = [54,0,56][config.OS_TYPE_INDEX]
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
    load_screen_button = [(200,5),(),(147,5)][config.OS_TYPE_INDEX]
    load_portfolio_button = [(191,30),(),(147,30)][config.OS_TYPE_INDEX]
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

    refresh_screen_button = [(110,5),(),(57,5)][config.OS_TYPE_INDEX]
    load_screen_button = [(200,5),(),(147,5)][config.OS_TYPE_INDEX]
    load_portfolio_button = [(191,30),(),(147,30)][config.OS_TYPE_INDEX]
    screen_drop_down = [(305, 6),(),(238,6)][config.OS_TYPE_INDEX]
    accounts_drop_down = [(305, 31),(),(238,31)][config.OS_TYPE_INDEX]
    clear_button = [(840,31),(),(default_width-133,5)][config.OS_TYPE_INDEX]
    ticker_input = [(805,8),(),(591,6)][config.OS_TYPE_INDEX]
    add_one_stock_button = [(710,5),(),(500,5)][config.OS_TYPE_INDEX]
    add_all_stocks_button = [(710,31),(),(500,31)][config.OS_TYPE_INDEX]
    analyse = [(500,31),(),(2,31)][config.OS_TYPE_INDEX]

    ticker_display_horizontal_offset = 3
    ticker_display_horizontal_size = 100



class ResearchPage(object):
    text = (10,10)
    ticker_input = [(100, 8),(),(60,6)][config.OS_TYPE_INDEX]
    add_stock_button = [(200,5),(),(173,5)][config.OS_TYPE_INDEX]
    remove_stock_button = [(300,5),(),(263,5)][config.OS_TYPE_INDEX]
    bingbong = (400,5) #loads examples for development, i love them bingbongbrothers

    research_initial_button_vertical_offset = 44
    research_initial_button_horizontal_offset = 60
    research_text_additional_vertical_offset = 6
    research_added_width = 0
    research_default_horizontal_offset = 10

    website_button_horizontal_offset = 60
    stock_initial_button_horizontal_offset = 144
    stock_initial_button_vertical_offset = [80,35,35][config.OS_TYPE_INDEX]

    stock_text_additional_vertical_offset = [6,0,0][config.OS_TYPE_INDEX]
    second_line_text_additional_offset = [18,15,15][config.OS_TYPE_INDEX]
    vertical_offset_per_stock = 40
    stock_added_width = 0
    stock_default_vertical_offset = 10

class SalePrepPage(object):
    text = (10,10)
    horizontal_offset = 0
    horizontal_offset_i_greater_than_n = 200
    checkbox_initial_offset = 600
    checkbox_vertical_offset_factor = 16
    line = (0,83)
    line_size = (1000, -1)
    refresh_button = (110,5)
    load_new_account_data_button = (110,30)
    save_button = (420,50)
    saved_text = [(433,55),(),(433,40)][config.OS_TYPE_INDEX]

    size = (800,650) #grid size
    width_adjust = 20
    height_adjust = 128
    AddSpacer = [83,0,57][config.OS_TYPE_INDEX]
    new_grid_position = [(0,83),(),(0,57)][config.OS_TYPE_INDEX]

class TradePage(object):
    trade_page_text = (10,10)
    create_grid_button = (500,0)
    clear_grid_button = [(900,0),(),(default_width-112,0)][config.OS_TYPE_INDEX]
    save_grid_button = [(900,30),(),(default_width-112,27)][config.OS_TYPE_INDEX]
    update_stocks_button = (700,30)
    stock_update_pending_text = (700,30)

    newGridFill_size = [(1000,650),(),(1000,default_height)][config.OS_TYPE_INDEX]
    width_adjust = 20
    height_adjust = 128
    new_grid_position = [(0,83),(),(0,57)][config.OS_TYPE_INDEX]
    newGridFill_AddSpacer = [83, 0, 57][config.OS_TYPE_INDEX]

class UserFunctionsPage(object):
    AddSpacer = 95
    general_text  = (10,10)
    additional_text = (145,36)
    save_button = (5,30)
    reset_button = (5,60)
    height_offset = 95
    file_display_position = (10, height_offset)
    file_display_size = (995,580)

    resetToDefault_size = (995,580) #this seems to present a problem in windows, but i'm guessing it's a sizer issue in the direct code















#spreadsheet_width_height_offset = gui_position.ScreenPage.spreadsheet_width_height_offset
