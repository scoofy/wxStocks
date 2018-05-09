# Copyright 2014 Altova GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import glob
import os.path
import sys, getopt
import time
from datetime import datetime
from subprocess import call
import zipfile
from multiprocessing import Pool
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET

joblist = []
job_limit = 20						# number of simultaneous jobs passed to Raptor per batch
usage_string = 'valSECfilings ( -y <year> | -f <from_year> -t <to_year> ) -m <month> -c <cik> -k <ticker> -s <script>'

def lookup_cik(ticker, name=None):
	# Given a ticker symbol, retrieves the CIK.
	good_read = False
	ticker = ticker.strip().upper()
	url = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&count=10&output=xml'.format(cik=ticker)

	try:
		xmlFile = urlopen( url )
		try:
			xmlData = xmlFile.read()
			good_read = True
		finally:
			xmlFile.close()
	except HTTPError as e:
		print( "HTTP Error:", e.code )
	except URLError as e:
		print( "URL Error:", e.reason )
	except TimeoutError as e:
		print( "Timeout Error:", e.reason )
	except socket.timeout:
		print( "Socket Timeout Error" )
	if not good_read:
		print( "Unable to lookup CIK for ticker:", ticker )
		return
	try:
		root = ET.fromstring(xmlData)
	except ET.ParseError as perr:
		print( "XML Parser Error:", perr )

	try:
		cikElement = list(root.iter( "CIK" ))[0]
		return int(cikElement.text)
	except StopIteration:
		pass

def chunks(l, n):
    # Yield successive n-sized chunks from l
    for i in range(0, len(l), n):
        yield l[i:i+n]

def appendjoblist( year, month, cik=None ):
	target_dir = "sec/" + str(year) + '/' + str(month).zfill(2) + '/'
	cikPattern = None
	if not cik==None:
		cikStr = list(map( str, cik ))
		cikPattern = tuple(cs.zfill(10) for cs in cikStr)
	try:
		for filename in os.listdir( target_dir ):
			add_file = False
			if os.path.splitext(filename)[1] == ".zip":
				if cik == None:
					add_file = True
				else:
					if filename.startswith( cikPattern ):
						add_file = True
				if add_file:
					zipname = target_dir+filename
					joblist.append( zipname )
	except FileNotFoundError as fe:
		print( 'Error: no SEC filings found in directory', target_dir )


def validatejob( joblist, script=None ):
	result = None
	if script==None:
		result = call(["raptorxmlxbrl", "xbrl", "--listfile", joblist] )	#  "--verbose=true",
	else:
		result = call(["raptorxmlxbrl", "xbrl", "--script-api-version=1", "--script="+script,
						"--listfile", joblist] )
	return result

def xbrlname( zipname ):
	result = None
	z = zipfile.ZipFile( zipname )
	xmllist = [ f for f in z.namelist() if f.endswith('.xml') ]
	filtered = [ v for v in xmllist if not v.startswith('defnref') ]			# shortest xml filename may not always work
	xbrlname = min( filtered, key=len )
	return zipname+"|zip/"+xbrlname

def partitionjoblist(joblist, script=None):
	partition_count = 0
	for c in chunks( joblist, job_limit ):
		partition_count += 1
		print( "Partition:", partition_count )
		runjoblist( c, script )

def runjoblist(joblist, script=None):
	jobfile = open( "valSECfilings.jobs", "w" )
	try:
		for job in joblist:
			jobfile.write( xbrlname( job ) )
			jobfile.write( "\n" )
	finally:
		jobfile.close()
	print( "Running batch of", len(joblist), "validation jobs..." )
	validatejob( "valSECfilings.jobs", script )

def main(argv):
	year = 1999
	month = 0
	from_year = 1999
	to_year = 1999
	year_range = False
	one_cik = False
	script = None
	cik = None
	ticker = None
	if not os.path.exists( "sec" ):
		os.makedirs( "sec" )
	start_time  = time.time()
	try:
		opts, args = getopt.getopt(argv,"hy:m:f:t:c:k:s:",["year=","month=","from=","to=","cik=","ticker=","script="])
	except getopt.GetoptError:
		print( usage_string )
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print( usage_string )
			sys.exit()
		elif opt in ("-y", "--year"):
			year = int(arg)
		elif opt in ("-m", "--month"):
			month = int(arg)
		elif opt in ("-f", "--from"):
			from_year = int(arg)
			year_range = True
		elif opt in ("-t", "--to"):
			to_year = int(arg)
			year_range = True
		elif opt in ("-c", "--cik"):
			cik = list(map(int, arg.split(',')))
		elif opt in ("-k", "--ticker"):
			ticker = arg.split(',')
			cik = list(map( lookup_cik, ticker ))
		elif opt in ("-s", "--script"):
			script = arg
	if not ticker==None:
		print( "Tickers: ", ticker )
	if not cik==None:
		print( "CIKs: ", cik )
	if not year_range and month==0 and not year==1999:
		from_year=year
		to_year=year
		year_range=True
	if year_range:
		if from_year == 1999:
			from_year = to_year
		if to_year == 1999:
			to_year = from_year
		if from_year < 2005:
			print( 'Error: SEC filings only started in 2005' )
			print( 'Please specify a year > 2005 for -y or -f argument' )
			print( usage_string )
			sys.exit(2)
		for year in range( from_year, to_year+1 ):
			last_month = 12
			if year==datetime.today().year:
				last_month=datetime.today().month
			for month in range( 1, last_month+1 ):
				appendjoblist( year, month, cik )
	else:
		if year < 2005:
			print( 'Error: SEC filings only started in 2005' )
			print( 'Please specify a year > 2005 for -y or -f argument' )
			print( usage_string )
			sys.exit(2)
		appendjoblist( year, month, cik )
	print( len(joblist), "validation jobs queued up for RaptorXML+XBRL" )
	if len(joblist) > job_limit:
		partitionjoblist(joblist, script)
	else:
		runjoblist(joblist, script)
	end_time = time.time()
	print( "Elapsed real time:", end_time - start_time, "seconds" )

if __name__ == "__main__":
	main(sys.argv[1:])
