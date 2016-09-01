import config

#[osx, debian linux, windows]
#[osx because the o is a 0, linux because the l is a 1, and windows because it deserves to be last]

#MainFrame
MainFrame_size = [(1020,800),( config.DISPLAY_SIZE[0]*(3./4), config.DISPLAY_SIZE[1]*(3./4) ),( config.DISPLAY_SIZE[0]*(3./4), config.DISPLAY_SIZE[1]*(3./4) )][config.SYSTEM_INDEX]
MainFrame_SetSizeHints = MainFrame_size

#WelcomePage
WelcomePage_welcome_page_text = (10,10)
WelcomePage_instructions = [(10,20),(10,30),(10,30)][config.SYSTEM_INDEX]
WelcomePage_reset_password_button = [(5, 700),(MainFrame_size[0] - 400, 0),(MainFrame_size[0] - 400, 0)][config.SYSTEM_INDEX]
WelcomePage_text_field_offset = 180
WelcomePage_text_field_vertical_offset = -3
WelcomePage_text_field_vertical_offset_small_bump = 30
WelcomePage_text_field_vertical_offset_medium_bump = 60
WelcomePage_text_field_vertical_offset_large_bump = 90
WelcomePage_text_field_vertical_offset_encryption_bump = 120
WelcomePage_text_field_vertical_offset_optional_bump = 18
WelcomePage_reset_password_bump = 10
WelcomePage_reset_password_negative_vertical_bump = -30
WelcomePage_delete_all_stock_data = [(835, 700),(MainFrame_size[0]- 600, 0),(MainFrame_size[0]- 600, 0)][config.SYSTEM_INDEX]

