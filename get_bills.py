from bs4 import BeautifulSoup 
import urllib2, threading, sys, time

def get_soup(url) :
    try : 
        request = urllib2.urlopen(url)
        soup    = BeautifulSoup(request.read())
        request.close()
    except urllib2.HTTPError, e: soup = BeautifulSoup(e.fp.read())
    return soup

def get_number_of_pages(url) :
    soup    = get_soup(url) 
    num_pgs = str(soup.find('span', {'class':'results-number'})).split(' ')
    for i in range(len(num_pgs)-1, 0, -1) :
        if num_pgs[i] != '</span>' and num_pgs[i] != '':
            return int(num_pgs[i].replace(',',''))/250

def get_bill_info(bill_html) :
    return (bill_html.a.contents[0], (bill_html.a.get('href')+'/text'))

def get_bill_text(url) :
    soup     = get_soup(url)
    text     = soup.find('div', {'class':'generated-html-container'})
    if text != None : text = text.get_text().encode('utf-8')
    return text

def process_bill(bill, bills) :
    bill_name, bill_address = get_bill_info(bill)
    bills.write("%s,%s," % (bill_name, bill_address))

    bill_text = get_bill_text(bill_address)

    if bill_text != None :
        current_bill = open(BILL_DIRECTORY + bill_name + '.txt','w')
        current_bill.write(bill_text)
        bills.write("%s,%s,%s\n" %(bill_name, bill_address,(BILL_DIRECTORY+bill_name+'.txt')))
    else : 
        bills.write("%s,%s,%s\n" %(bill_name, bill_address,'NO TEXT AVAILABLE'))

if __name__ == "__main__":

    sys.setrecursionlimit(2000)

    BASE_URL       = "https://www.congress.gov"
    BASE_SEARCH    = "https://www.congress.gov/legislation?pageSize=250&page="
    BILL_DIRECTORY = "/YOUR BILL DIRECTORY HERE/"
    START_TIME     = time.time()

    number_pages = get_number_of_pages(BASE_SEARCH + '1')
    bills = open('bills.csv','w')

    # OUTPUT
    sys.stdout.write('\nRetrieving legislation...\n\n')

    for i in range(number_pages) :

        progress_bar = '\r    page %d of %d: ' % (i+1, number_pages)
        sys.stdout.write(progress_bar)

        soup        = get_soup(BASE_SEARCH + str(i+1))
        dirty_bills = soup.find('ol', {'class':'results_list'}).findAll('h2')
        bill_count  = 0

        for b1,b2,b3,b4,b5,b6,b7,b8,b9,b10 in (dirty_bills[i:i+10] for i in range (0,250,10)) :

            dbs = [b1,b2,b3,b4,b5,b6,b7,b8,b9,b10]
            threads = []

            bill_count += 10
            if bill_count % 50 == 0 :
                progress_bar += '##' 
                sys.stdout.write(progress_bar)
                sys.stdout.flush()

            delay_start = time.time()
            for db in dbs :
                thread = threading.Thread(target=process_bill, args=(db,bills))
                threads.append(thread) 
                thread.start()

            for thread in threads : thread.join()

            if (time.time() - delay_start) < 2.0 : time.sleep(2)

    sys.stdout.write('\nDone!\n')
    sys.stdout.write('Retrieval took %s seconds\n' % (time.time() - START_TIME))
