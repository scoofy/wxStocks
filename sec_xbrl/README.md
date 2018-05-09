sec-xbrl
========

Copyright 2014 Altova GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

-------------------------------------------------------------------------

<h2>XBRL.US Webinar: How to download and process SEC XBRL Data Directly from EDGAR</h2>

These are the supporting Python files for the XBRL.US Webinar that is availble
on YouTube: https://www.youtube.com/watch?v=2Oe9ZqXVGME as well as the slides
available here on SlideShare: http://www.slideshare.net/afalk42/xbrl-us-altova-webinar

See also my recent blog post: http://www.xmlaficionado.com/2014/09/how-to-download-and-process-sec-xbrl.html

Please watch the YouTube video and review the slides to see how these Python
scripts are intended to be used. Also note that these scripts were written with
Python 3.3.3 so they may require modifications if you use them with a different
version of Python.

To use this approach you will need to download and install RaptorXML+XBRL Server from
the Altova website: http://www.altova.com/download-trial-server.html and then 
request a 30-day free evaluation license key.

These sample Python scripts available here on GitHub were tested with a the MacOS
version of RaptorXML+XBRL Server, but should function with the Windows or Linux version
as well. You may need to change the file-paths pointing to the RaptorXML+XBRL Server
executable in the Python script, though, or add them to the global PATH environment
variable on your system.

In addition to the standard Python libraries, you also need to install the Python
feedparser module/library available here: https://pypi.python.org/pypi/feedparser

For more information on RaptorXML, please see here: http://www.altova.com/raptorxml.html

-------------------------------------------------------------------------

<h3>Usage Information</h3>

These scripts now require RaptorXML+XBRL v2015r3 or newer.

<h4>loadSECfilings</h4>

    loadSECfilings.py -y <year> -m <month> | -f <from_year> -t <to_year>

These creates a subdirectory sec/ and then subsequent year-based directories and months
underneath and downloads all SES XBRL filings from the EDGAR system to your local hard
disk for further processing. Please use only during off-peak hours in order to not
overload the SEC servers. This downloads the ZIPped XBRL filings, so you'll have one
ZIP file per filing submitted to the SEC on your drive. If you call this script
again for the current or any previous month at a later day, it will only download
any files that are new and have not yet been downloaded before.

<h5>Examples</h5>

    python3 loadSECfilings.py -y 2014 -m 9

This will load all SEC filing for September 2014.

    python3 loadSECfilings.py -f 2005 -t 2014

This will load all SEC filing for the start of the XBRL pilot program in 2005 until 2014.
WARNING: If you download all years available (2005-2014) this will be about 127,000 files
and take about 18GB of data on your hard disk, so please use with caution, especially 
when you are on a slow Internet connection.


<h4>valSECfilings</h4>

    valSECfilings ( -y <year> | -f <from_year> -t <to_year> ) -m <month> 
              -c <cik> -k <ticker> -s <script>

This will call RaptorXML+XBRL Server to validate the SEC filings for a specified year
and month or for a range of years. It assumes that the files have been downloaded by
the script above into a local sub-directory sec/. You can restrict the filings to just
those for a particular company or for a list of companies by providing their respective 
CIKs or ticker symbols. Optionally you can pass a Python script to RaptorXML+XBRL Server
with the -s parameter, which will then be executed by the built-in Python interpreter
inside of RaptorXML+XBRL Server to perform additional post-validation processing of
the XBRL files. As an example, there is a Python script extractRatios.py in this project
that demonstrates how to extract common financial ratios (quick ratio, cash ratio) from
the XBRL filings.

<h5>Examples</h5>

    python3 valSECfilings.py -y 2014 -m 9

This will validate all downloaded SEC filings for the month of September 2014. If a large
number of files is passed to the Python script, it will create batches of about 20 jobs
each and pass those to RaptorXML+XBRL Server in sequential batches.

    python3 valSECfilings.py -f 2013 -t 2014 -k AAPL,MSFT,ORCL

This will validate all SEC filings submitted by Apple, Microsoft, and Oracle for the
years 2013 and 2014. Positive validation messages as well as any errors or warnings
are output to the console window.

    python3 valSECfilings.py -f 2013 -t 2014 -k ORCL -s extractRatios.py

This will validate all Oracle XBRL filings for the years 2013-2014 and then perform
post-validation analysis of the filings using the supplied Python script extractRatios.py
that gets passed to RaptorXML+XBRL Server and executed by its built-in Python interpreter.
This particular example script prints document and entity information and then extracts
various balance sheet facts to calculate current ratio, quick ratio, and cash ratio as
and example of how to do post-validation XBRL processing. Furthermore, it appends those
ratios to an output file ratios.csv in the same directory.

-------------------------------------------------------------------------

<h3>Reminder</h3>

To see these scripts and a lot more in-depth explanation, please watch the
YouTube video of the webinar here: https://www.youtube.com/watch?v=2Oe9ZqXVGME
