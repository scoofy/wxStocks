ticker_list = [x for x in range(20)]
function_list = [x for x in range(3)]

gap = 2

f_loop_count = 0
t_loop_count = 0
count = 1

for f in function_list:
	t_loop_count = 0
	for t in ticker_list:
		# 2 second sleep per scrape of (3 stocks, 3 functions)
		# 1st_function (0) + 1st_ticker (0) + count (1) = 1sec delay
		#count = (f * len(ticker_list)) + t + 1
		output = (count * gap) - (gap - 1)
		print output
		count += 1
	print ""
