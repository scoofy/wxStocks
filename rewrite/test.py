from wxStocks_classes import Stock, Account

a = Stock("a")
print a

a.firm_name = "A Corp."

for attribute in dir(a):
	print attribute