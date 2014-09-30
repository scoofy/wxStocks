from modules.simplecrypt import encrypt, decrypt
import cPickle as pickle
import sys


big_dict = {"key": "value","key2": "value2","key3": "value3","key4": "value4"}

print big_dict.keys()






test_path = 'wxStocks_modules/wxStocks_data/test_data.txt'
password = "blah"

class TestObj(object):
	def __init__(self):
		self.a = "a"
		self.b = "boomtown"

def encrypt_file():
	a = TestObj()


	b = pickle.dumps(a)

	print type(b)
	print b

	c = encrypt(password, b)

	print type(c)
	print c

	with open(test_path, 'w') as output:
		output.write(c)
def decrypt_file():
	a = open(test_path, 'r')
	a = a.read()

	b = decrypt(password, a)

	print b

	c = pickle.loads(b)

	print type(c)

	print c.b

#print "end"