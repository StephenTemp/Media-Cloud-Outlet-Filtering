# Media-Cloud-Outlet-Filtering
Using ABYZ and Media-Bias Fact-Check outlet databases, I've provided outlet CSV files for both and scripts to intended to match Media Cloud files to respective outlets.  


### ___Provided Files___:


* **abyz_outlets.csv**: CSV file containing information on outlets provided by the ABYZ dataset
* **mbfc_outlets.csv**: CSV file containing information on outlets provided by the _Media-Bias Fact-Check_ dataset. Information included: **name**, **link**, and **perceived bias**. 

### ___Scripts___:
* **match_mbfc.py**: Python script intended to match _tar.xz_ files containing _MediaCloud_ articles to _Media-Bias Fact-Check_ outlets listed in _mbfc_outlet.csv_. To run this script in the command line, run the template command: "_python match_mbfc.py **{TAR.XZ FILE}**_"

⋅⋅⋅**output**: a CSV file including all matched articles with corresponding mbfc-outlet information