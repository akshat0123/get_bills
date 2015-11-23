from bs4 import BeautifulSoup 
import urllib2, threading, sys, time, os, re

def gcd(x,y) :
    while y : x,y = y,x%y
    return x

def lcm(x,y) : return (x*y)/gcd(x,y)

def get_soup(url) :
    try : 
        request = urllib2.urlopen(url)
        soup    = BeautifulSoup(request.read(), 'lxml')
        request.close()
    except urllib2.HTTPError, e: soup = BeautifulSoup(e.fp.read(), 'lxml')
    return soup

# Returns total number of pages for bills in groups of 250
def get_number_of_pages(url) :
    soup    = get_soup(url) 
    num_pgs = str(soup.find('span', {'class':'results-number'})).split(' ')
    for i in range(len(num_pgs)-1, 0, -1) :
        if num_pgs[i] != '</span>' and num_pgs[i] != '':
            return int(num_pgs[i].replace(',',''))/250

# Returns the title, name, bill type (amendment/bill/resolution), sponsor,
# committees, and web address of the bill text given a bill's url
def get_bill_info(bill) :
    title  = bill.find('h2')
    name   = bill.find('h3')
    b_type = bill.find('span', {'class':'visualIndicator'})
    check, spons, comms, addr  = False, None, None, None
    if title != None :
        check  = True
        addr   = title.a.get('href') + '/text'
        title  = title.find('a').get_text().encode('utf-8')
        b_type = b_type.get_text().encode('utf-8').strip()
        spons  = bill.find('table').a.get_text().encode('utf-8')
        comms  = bill.find('table').findAll('tr')[1]
        if (comms.th.get_text().encode('utf-8') == 'Committees:') : comms = comms.td.get_text().encode('utf-8')
        else : comms = None
        name = 'NO NAME' if name == None else name.get_text().encode('utf-8');

    return(check, title, name, b_type, spons, comms, addr)

def get_bill_text(url) :
    soup     = get_soup(url)
    text     = soup.find('div', {'class': re.compile('generated-html-*')})
    if text != None : text = text.get_text().encode('utf-8')
    return text

# Gets all info for a bill, writes the info to the 'bills.csv' file, and places
# bill's text in the bill directory in a subdirectory corresponding to which
# page it was found on congress.gov
def process_bill(bill, bills, path) :
    check, title, name, b_type, spons, comms, addr = get_bill_info(bill)
    page = path.split('page_', 1)[1]
    if check == True :
        bill_text = get_bill_text(addr)
        if bill_text != None :
            current_bill = open(path + title + '.txt','w')
            current_bill.write(bill_text)
            bills.write("%s,%s,%s,%s,%s,%s,%s\n" % (page,title,name,b_type,spons,comms,(path + title + '.txt')))
        else : 
            bills.write("%s,%s,%s,%s,%s,%s,%s\n" %(page,title,name,b_type,spons,comms,'NO TEXT AVAILABLE'))

if __name__ == "__main__":

    sys.setrecursionlimit(2000)

    # BILL_DIRECTORY : the directory the bill texts will be downloaded to 
    # SEARCH_STRING  : additional string to be added to BASE_SEARCH that ensures
    #                  only bills from 1993-4 onwards are retrieved (bills
    #                  before these years aren't available in text form online)
    BILL_DIRECTORY = "/vagrant/Scrape/bills/"
    BASE_URL       = "https://www.congress.gov"
    BASE_SEARCH    = 'https://www.congress.gov/legislation?pageSize=250&page='
    SEARCH_STRING  = '&q=%7B"congress"%3A%5B"114"%2C"113"%2C"112"%2C"111"%2C"110"%2C"109"%2C"108"%2C"107"%2C"106"%2C"105"%2C"104"%2C"103"%5D%7D'
    START_TIME     = time.time()

    # THREAD COUNT : the number of threads to use 
    # bills        : bill information is written using this variable to the file
    #                'bills.csv'
    # records      : simply stores the number of seconds it takes for the
    #                program to retrieve a page (250 bills) 
    start_page   = 28 
    number_pages = 30 
    thread_count = 10
    thread_lcm   = lcm(thread_count,25)
    hash_num     = thread_lcm/25
    bills        = open('bills.csv','a')
    records      = open('records.txt','a')

    sys.stdout.write('\nRetrieving legislation...\n\n')

    for i in range(start_page, number_pages) :

        progress_bar = '\r    page %d of %d: ' % (i+1, number_pages)
        sys.stdout.write(progress_bar)

        soup           = get_soup(BASE_SEARCH + str(i+1) + SEARCH_STRING)
        dirty_bills    = soup.find('ol', {'class':'results_list'}).findAll('li')
        dirty_bills    = [bill for bill in dirty_bills if bill.find('h2') != None]
        page_directory = BILL_DIRECTORY + 'page_' + str(i+1) + '/'
        page_start     = time.time()
        bill_count     = 0
        os.makedirs(page_directory)

        # If thread_count is set to 10, this retrieves groups of 10 bills,
        # creates a thread to process each one of them and waits for the last
        # of 10 threads to finish before moving onto the next 10 bills
        for j in range(0,250,thread_count) :

            threads = []
            bill_count += thread_count 
            if bill_count % thread_lcm == 0 :
                progress_bar += ('#'*hash_num)
                sys.stdout.write(progress_bar)
                sys.stdout.flush()

            for k in range(thread_count) :
                bill   = dirty_bills[j+k]
                thread = threading.Thread(target=process_bill,args=(bill,bills,page_directory))
                threads.append(thread)
                thread.start()

            for thread in threads : thread.join()

        records.write("Page %d, time: %s\n" % (i, (time.time() - page_start)))
        sys.stdout.write('\n')

    sys.stdout.write('\nDone!\n')
    sys.stdout.write('Retrieval took %s seconds\n' % (time.time() - START_TIME))
