from bs4 import BeautifulSoup, NavigableString 
import urllib2

BASE_URL = "https://www.congress.gov/legislation?pageSize=250&page="
page_number = 1
bills = []

request = urllib2.urlopen(BASE_URL + str(page_number))
soup = BeautifulSoup(request) 
number_pages = None

# GET NUMBER OF PAGES
get_number_pages = str(soup.find('span', {'class':'results-number'})).split(' ')
for i in range(len(get_number_pages)-1, 0, -1) :
    if get_number_pages[i] != '</span>' and get_number_pages[i] != '':
        number_pages = int(get_number_pages[i].replace(',',''))/250
        break

print 'Getting Bills: [          ]'
percent_total = number_pages/10
percent_done  = 0
f = open('bills.csv','w')

for i in range(number_pages) :

    if i+1 == percent_total:
        percent_done += 1
        print 'Getting Bills: [' + ('#'*percent_done) +\
              (' '*(10-percent_done)) + ']' + ' page ' +\
              str(i+1) + ' of ' + str(number_pages)
        percent_total += percent_total

    request = urllib2.urlopen(BASE_URL + str(page_number + i))
    soup = BeautifulSoup(request)

    dirty_bills = soup.find('ol', {'class':'results_list'}).findAll('li')

    for dirty_bill in dirty_bills :
        if dirty_bill.find('h2') != None :

            # BILL NAME
            f.write(dirty_bill.h2.a.contents[0] + ',')

            # BILL TEXT ADDRESS
            f.write(',' + dirty_bill.h2.a.get('href') + '/text\n')

print 'Done!'
