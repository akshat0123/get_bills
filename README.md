#Get Bills

##Description
Python script that retrieves text files of all US congressional legislation
available on https://www.congress.gov and places them in a specified directory.
Bear in mind, the script is written in a single-thread, and there are around
400,000 pieces of legislation on congress.gov, so it'll take a while to run (I
haven't downloaded all pages of links worth, but I'd estimate around 100 hrs at
least, based on how long it takes for 1-5 pages 0f 250 links each), and you're
probably going to need around 7-8 gigabytes (give or take a hundred or so
megabytes) of room. Running the program will also create two additional files,
'bills.csv', and 'records.txt', which contain some information about the bills
being downloaded.

##Dependencies
Running this file requires Python 2.7 and the python library BeautifulSoup4. On
most Debian/Ubuntu you can install BeautifulSoup4 via the package manager as
`apt-get install python-bs4`. If you'd rather use easy_install or pip, the
commands are `easy_install beautifulsoup4` or `pip install beautifulsoup4`
respectively.

##Configuration
Clone the repository, and edit the `BILL_DIRECTORY` field to specify the file
where you would like the bill text files to be placed. also make sure to edit
the `thread_count` field to set the number of threads to be run at once. I've
had the best results with using 10.

##Notes
This is a multi-threaded program that runs multiple threads in order to improve
I/O performance. The congress.gov website robots.txt specifies a crawl-delay of
2 seconds. It may not be a good idea to download all the pages of legislation at
once - either due to getting your ip blocked, or just because, despite the fact
that this is multi-threaded (at least multithreading as far as python supports
multithreading... look up python multithreading if you want to know more
about that), it will still take a looong time to run.
