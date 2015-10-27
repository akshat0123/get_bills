#Get Bills

##Description
Python script that retrieves text files of all US congressional legislation
available on https://www.congress.gov and places them in a specified directory.
Bear in mind, the script is written in a single-thread, and there are around
400,000 pieces of legislation on congress.gov, so it'll take a while to run, and
you're probably going to need about a gigabyte (give or take a hundred or so
megabytes) of room.

##Dependencies
Running this file requires Python 2.7 and the python library BeautifulSoup4. On
most Debian/Ubuntu you can install BeautifulSoup4 via the package manager as
`apt-get install python-bs4`. If you'd rather use easy_install or pip, the
commands are `easy_install beautifulsoup4` or `pip install beautifulsoup4`
respectively.

##Configuration
Clone the repository, and edit the `BILL_DIRECTORY` field to specify the file
where you would like the bill text files to be placed. 

##Notes
Stay tuned for a multi-process version!
