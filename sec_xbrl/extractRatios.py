# Copyright 2014 Altova GmbH
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#	  http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, re, sys
from altova import xml, xsd, xbrl

sec_ns =  '/dei/'		# was: 'http://xbrl.sec.gov/dei/'
fasb_ns = '/us-gaap/'	# was: 'http://fasb.org/us-gaap/'

# We need to implement a simple locking class that allows us to avoid having 
# on_xbrl_valid called from multiple threads in RaptorXML at the same time.

if sys.platform == 'win32':
	import msvcrt

	# fcntl is not available under Windows, so we'll use a 
	# file locking function from the msvcrt library instead...

	class Lock:

		def __init__(self, filename):
			self.filename = filename
			# This will create it if it does not exist already
			self.handle = open(filename, 'w')

		# Bitwise OR fcntl.LOCK_NB if you need a non-blocking lock
		def acquire(self):
			msvcrt.locking(self.handle.fileno(), msvcrt.LK_LOCK, 1)

		def release(self):
			msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)

		def __del__(self):
			self.handle.close()

else:
	import fcntl

	# Under Linux and MacOS we can use the fcntl library to implement
	# the simple file locking mechanism...

	class Lock:

		def __init__(self, filename):
			self.filename = filename
			# This will create it if it does not exist already
			self.handle = open(filename, 'w')

		# Bitwise OR fcntl.LOCK_NB if you need a non-blocking lock
		def acquire(self):
			fcntl.flock(self.handle, fcntl.LOCK_EX)

		def release(self):
			fcntl.flock(self.handle, fcntl.LOCK_UN)

		def __del__(self):
			self.handle.close()

def camelToSpaces( label ):
	# Utility for pretty-printing the labels
	s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', label)
	return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)

def factFinder( instance, namespace, label ):
	# Locate facts in the instance document by namespace and label, ignoring facts that have a context with a segment_element
	l = []
	for f in instance.items:
		if f.qname.namespace_name.find( namespace ) and f.qname.local_name == label:
			segment = None
			try:
				entElement = f.context.entity.element
				for childElement in entElement.children:
					if childElement.local_name=="segment":
						segment = childElement
			except:
				pass
			if segment==None:
				l.append( f )
	return l

def printFacts( facts, indent=1, targetDate=None ):
	# Find the fact for the relevant target date and print it
	factValue = 0
	for fact in facts:
		if targetDate==None or fact.context.period.instant == targetDate:
			if fact.concept.item_type==fact.concept.MONETARY_ITEM_TYPE:
				factValue = fact.effective_numeric_value
				print( indent * "\t", camelToSpaces( fact.qname.local_name ).ljust(100-indent*8), "$", '{0:>16,}'.format( factValue ) )
			else:
				factValue = fact.normalized_value
				print( indent * "\t", camelToSpaces( fact.qname.local_name ).ljust(100-indent*8), factValue )
	return factValue

def on_xbrl_valid( job, instance ):

	try:
		# a portable solution to get the tmp dir
		import tempfile
		tmp = tempfile.gettempdir()
		tmplk = os.path.join( tmp, "extract_ratios_lock.tmp" )
		lock = Lock(tmplk)
		lock.acquire()

		# Create output CSV file if it doesn't exist yet
		if not os.path.isfile( "ratios.csv" ):
			with open("ratios.csv", "a") as ratiofile:
				ratiofile.write( "DocumentType,EntityName,CIK,PeriodEndDate,CurrentRatio,QuickRatio,CashRatio\n" )
				ratiofile.close()

		# Extract some basic facts from the filing, such as the effective end-date for balance sheet etc.
		docEndDate = "2013-12-31"
		documentType = factFinder( instance, sec_ns, "DocumentType" )
		documentFiscalYearFocus = factFinder( instance, sec_ns, "DocumentFiscalYearFocus" )
		documentFiscalPeriodFocus = factFinder( instance, sec_ns, "DocumentFiscalPeriodFocus" )
		documentPeriodEndDate = factFinder( instance, sec_ns, "DocumentPeriodEndDate" )
		if len(documentPeriodEndDate) > 0:
			docEndDate = documentPeriodEndDate[0].normalized_value

		# Extract Filer Name and other key data
		entityRegistrantName = factFinder( instance, sec_ns, "EntityRegistrantName" )
		entityCentralIndexKey = factFinder( instance, sec_ns, "EntityCentralIndexKey" )
		entityCommonStockSharesOutstanding = factFinder( instance, sec_ns, "EntityCommonStockSharesOutstanding" )

		# Print information about filing and entity
		print( "Document and Entity Information:" )
		docType = printFacts( documentType )
		entityName = printFacts( entityRegistrantName )
		entityCIK = printFacts( entityCentralIndexKey )
		printFacts( documentPeriodEndDate )
		printFacts( documentFiscalPeriodFocus )
		printFacts( documentFiscalYearFocus )

		if docType=="10-K" or docType=="10-Q":
			# Now let's calculate some useful ratios from the balance sheet
			print( "Analytical Ratios:" )
			print( "\tBalance Sheet:" )

			# Current Ratio
			currentRatio = 0
			print( "\t\tCurrent Ratio = Current Assets / Current Liabilities:" )
			currentAssetsFacts = factFinder( instance, fasb_ns, "AssetsCurrent" )
			currentLiabilitiesFacts = factFinder( instance, fasb_ns, "LiabilitiesCurrent" )
			currentAssets = printFacts( currentAssetsFacts, 3, docEndDate )
			currentLiabilities = printFacts( currentLiabilitiesFacts, 3, docEndDate )
			if not currentLiabilities==0:
				currentRatio = currentAssets / currentLiabilities
			print( 3 * "\t", "Current Ratio = ".ljust(100-3*8), '{0:.2f}'.format( currentRatio ) )

			# Quick Ratio
			quickRatio = 0
			print( "\t\tQuick Ratio = ( Cash + Short-Term Marketable Securities + Accounts Receivable ) / Current Liabilities:" )
			cashFacts = factFinder( instance, fasb_ns, "Cash" )
			if len(cashFacts)==0:
				cashFacts = factFinder( instance, fasb_ns, "CashAndCashEquivalentsAtCarryingValue" )
			if len(cashFacts)==0:
				cashFacts = factFinder( instance, fasb_ns, "CashCashEquivalentsAndShortTermInvestments" )
			marketableSecuritiesFacts = factFinder( instance, fasb_ns, "MarketableSecuritiesCurrent" )
			if len(marketableSecuritiesFacts)==0:
				marketableSecuritiesFacts = factFinder( instance, fasb_ns, "AvailableForSaleSecuritiesCurrent" )
			if len(marketableSecuritiesFacts)==0:
				marketableSecuritiesFacts = factFinder( instance, fasb_ns, "ShortTermInvestments" )
			if len(marketableSecuritiesFacts)==0:
				marketableSecuritiesFacts = factFinder( instance, fasb_ns, "OtherShortTermInvestments" )
			accountsReceivableFacts = factFinder( instance, fasb_ns, "AccountsReceivableNetCurrent" )
			currentLiabilitiesFacts = factFinder( instance, fasb_ns, "LiabilitiesCurrent" )
			cash = printFacts( cashFacts, 3, docEndDate )
			marketableSecurities = printFacts( marketableSecuritiesFacts, 3, docEndDate )
			accountsReceivable = printFacts( accountsReceivableFacts, 3, docEndDate )
			currentLiabilities = printFacts( currentLiabilitiesFacts, 3, docEndDate )
			if not currentLiabilities==0:
				quickRatio = ( cash + marketableSecurities + accountsReceivable ) / currentLiabilities
			print( 3 * "\t", "Quick Ratio = ".ljust(100-3*8), '{0:.2f}'.format( quickRatio ) )

			# Cash Ratio
			cashRatio = 0
			print( "\t\tCash Ratio = ( Cash + Short-Term Marketable Securities ) / Current Liabilities:" )
			cash = printFacts( cashFacts, 3, docEndDate )
			marketableSecurities = printFacts( marketableSecuritiesFacts, 3, docEndDate )
			currentLiabilities = printFacts( currentLiabilitiesFacts, 3, docEndDate )
			if not currentLiabilities==0:
				cashRatio = ( cash + marketableSecurities ) / currentLiabilities
			print( 3 * "\t", "Cash Ratio = ".ljust(100-3*8), '{0:.2f}'.format( cashRatio ) )


			# Append ratios to a CSV file for further analysis
			with open("ratios.csv", "a") as ratiofile:
				ratiofile.write( docType + ',"' + entityName + '",' + entityCIK + "," + docEndDate + "," + '{0:.2f}'.format( currentRatio ) + "," + '{0:.2f}'.format( quickRatio ) + "," + '{0:.2f}'.format( cashRatio ) + "\n" )
				ratiofile.close()

	finally:
		lock.release()
