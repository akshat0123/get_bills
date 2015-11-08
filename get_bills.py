from bs4 import BeautifulSoup 
import urllib2, threading, sys, time, os

def gcd(x,y) :
    while y : x,y = y,x%y
    return x

def lcm(x,y) : return (x*y)/gcd(x,y)

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

def process_bill(bill, bills, path) :
    bill_name, bill_address = get_bill_info(bill)
    page = path.split('page_',1)[1]

    bill_text = get_bill_text(bill_address)

    if bill_text != None :
        current_bill = open(path + bill_name + '.txt','w')
        current_bill.write(bill_text)
        bills.write("%s,%s,%s,%s\n" %(page, bill_name, bill_address,(BILL_DIRECTORY+bill_name+'.txt')))
    else : 
        bills.write("%s,%s,%s,%s\n" %(page, bill_name, bill_address,'NO TEXT AVAILABLE'))

if __name__ == "__main__":

    sys.setrecursionlimit(2000)

    # BILL_DIRECTORY : the directory the bill texts will be downloaded to 
    BASE_URL       = "https://www.congress.gov"
    BASE_SEARCH    = "https://www.congress.gov/legislation?pageSize=250&page="
    BILL_DIRECTORY = "/YOUR BILL DIRECTORY HERE/"
    START_TIME     = time.time()

    # THREAD COUNT : the number of threads to use 
    start_page   = 0
    number_pages = get_number_of_pages(BASE_SEARCH + '1')
    thread_count = 10 
    thread_lcm   = lcm(thread_count,25)
    hash_num     = thread_lcm/25
    bills        = open('bills.csv','a')
    records      = open('records.txt','a')

    # OUTPUT
    sys.stdout.write('\nRetrieving legislation...\n\n')

    for i in range(start_page, number_pages) :

        progress_bar = '\r    page %d of %d: ' % (i+1, number_pages)
        sys.stdout.write(progress_bar)

        soup           = get_soup(BASE_SEARCH + str(i+1))
        dirty_bills    = soup.find('ol', {'class':'results_list'}).findAll('h2')
        bill_count     = 0
        page_directory = BILL_DIRECTORY + 'page_' + str(i+1) + '/'
        page_start     = time.time()
        os.makedirs(page_directory)

        for j in range(0,250,thread_count) :

            threads = []
            bill_count += thread_count 
            if bill_count % thread_lcm == 0 :
                progress_bar += ('#'*hash_num)
                sys.stdout.write(progress_bar)
                sys.stdout.flush()

            for k in range(thread_count) :
                thread = threading.Thread(target=process_bill,\
                                          args=(dirty_bills[j+k],bills,page_directory))
                threads.append(thread)
                thread.start()

            for thread in threads : thread.join()

        records.write("Page %d, time: %s\n" % (i, (time.time() - page_start)))
        sys.stdout.write('\n')

    sys.stdout.write('\nDone!\n')
    sys.stdout.write('Retrieval took %s seconds\n' % (time.time() - START_TIME))
