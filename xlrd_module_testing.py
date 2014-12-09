from modules import xlrd

xls_files = ["sample_aaii.xls", "tiny.xls"]
test_file = xls_files[1]

workbook = xlrd.open_workbook(test_file)
print "The number of worksheets is", workbook.nsheets


def return_relevant_spreadsheet_list_from_workbook(xlrd_workbook):
	relevant_sheets = []
	for i in range(workbook.nsheets):
		sheet = workbook.sheet_by_index(i)
		print sheet.name
		if sheet.nrows or sheet.ncols:
			print "rows x cols:", sheet.nrows, sheet.ncols
			relevant_sheets.append(sheet)
		else:
			print "is empty"
		print ""
	return relevant_sheets

def return_xls_cell_value(xlrd_spreadsheet, row, column):
	return xlrd_spreadsheet.cell_value(rowx=row, colx=column)

relevant_sheets = return_relevant_spreadsheet_list_from_workbook(workbook)

print "The number of relevant worksheets is", len(relevant_sheets)

print "Worksheet name(s):", [x.name for x in relevant_sheets]

my_spreadsheet = relevant_sheets[0]
print my_spreadsheet.name, my_spreadsheet.nrows, my_spreadsheet.ncols
print "Cell D5 is", my_spreadsheet.cell_value(rowx=4, colx=3)
for this_row in range(my_spreadsheet.nrows):
    print my_spreadsheet.row(this_row)
    print ""
# Refer to docs for more details.
# Feedback on API is welcomed.
