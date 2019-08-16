# Scraper for Idaho website

This scraper crawls through the following website to extract the information mentioned below
	[Idaho License Lookup/Verification](https://idbop.mylicense.com/verification/Search.aspx)
	
	The code outputs a csv file (in the same directory as the main.py) containing the following information about Pharmacists with last name starting with 'L'.
	*First Name
	*Middle Name
	*Last Name
	*License #
	*License Type
	*Status
	*Original Issued Date
	*Expiry
	*Renewed

##Note
1. The xpaths are hard coded instead of having a config file. The code needs to be updated whenever there is a change in the website.
2. The test only check whether a csv file is written. So, please be aware that an existing results file may be modified while running the test
3. The code writes the records to disk on the fly and does not hold the tables in memory (less space complexity)
4. code written in python 3.7.3