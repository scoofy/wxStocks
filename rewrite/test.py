a = "{'a': 2, 'b':4}"

b = "[1, 2, 3, 4]"

c = [a, b]

for x in c:
	try:
		list(x)
		print "tried list!"
		print x
		print type(x)
		print ""
	except Exception, e:
		print e

	try:
		list(x)
		print "tried dict!"
		print x
		print type(x)
		print ""
	except Exception, e:
		print e