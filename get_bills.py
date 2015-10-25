from bs4 import BeautifulSoup, NavigableString 
import urllib2

def get_number_of_pages(url) :
    request = urllib2.urlopen(url)
    soup = BeautifulSoup(request) 
    request.close()

    get_number_pages = str(soup.find('span', {'class':'results-number'})).split(' ')
    for i in range(len(get_number_pages)-1, 0, -1) :
        if get_number_pages[i] != '</span>' and get_number_pages[i] != '':
            return int(get_number_pages[i].replace(',',''))/250

def get_bill_info(bill_html) :
    return (bill_html.h2.a.contents[0], (bill_html.h2.a.get('href')+'/text'))

def get_bill_text_link(url) :
    request  = urllib2.urlopen(url + '/text')
    soup     = BeautifulSoup(request)
    request.close()
    link     = soup.find('ul', {'class':'textFormats'})
    if link != None : return link.findAll('li')[1:2][0].a.get('href')
    else : return None

def get_bill_text_by_url(url) :
    request = urllib2.urlopen(url)
    soup = BeautifulSoup(request)
    request.close()
    return soup.find('body').get_text().encode('utf-8')

if __name__ == "__main__":

    BASE_URL    = "https://www.congress.gov"
    BASE_SEARCH = "https://www.congress.gov/legislation?pageSize=250&page="
    BILL_DIRECTORY = "/YOUR BILL DIRECTORY HERE/"
    page_number = 1
    bills = []

    number_pages = get_number_of_pages(BASE_SEARCH + str(page_number))

    print 'Getting Bills: [          ]'
    percent_total = number_pages/10
    percent_done  = 0
    bills = open('bills.csv','w')

    for i in range(number_pages) :
    # for i in range(1) :

        if i+1 == percent_total:
            percent_done += 1
            print 'Getting Bills: [' + ('#'*percent_done) +\
                  (' '*(10-percent_done)) + ']' + ' page ' +\
                  str(i+1) + ' of ' + str(number_pages)
            percent_total += percent_total

        request = urllib2.urlopen(BASE_SEARCH + str(page_number + i))
        soup = BeautifulSoup(request)
        request.close()

        dirty_bills = soup.find('ol', {'class':'results_list'}).findAll('li')

        for dirty_bill in dirty_bills :
            if dirty_bill.find('h2') != None :

                bill_name, bill_address = get_bill_info(dirty_bill)
                bills.write("%s,%s," % (bill_name, bill_address))

                bill_text_link = get_bill_text_link(bill_address)

                if bill_text_link != None :

                    bill_text = get_bill_text_by_url(BASE_URL + bill_text_link)

                    current_bill = open(BILL_DIRECTORY + bill_name, 'w')
                    current_bill.write(bill_text)
                    bills.write(BILL_DIRECTORY + bill_name + '\n')

                else : bills.write('NO TEXT AVAILABLE\n')

                break

    print 'Done!'
