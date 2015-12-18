import csv, sys, os
csv.field_size_limit(sys.maxsize)

path = './bills.csv'

def get_title_type_sponsor(row) :
    i = 1
    title = []
    while 'RESOLUTION' not in row[i] and 'AMENDMENT' not in row[i] and 'LAW' not in row[i] and 'BILL' not in row[i] :
        title.append(row[i])
        i += 1
    title = ' '.join(title)
    bill_type = row[i]
    sponsor = None
    if bill_type == 'AMENDMENT' : sponsor = 'NO SPONSOR'
    else : 
        sponsor = []
        for j in range(i, len(row)-1) :
            sponsor.append(row[j])
            if ']' in row[j] or '[' in row[j] : break
        sponsor = ','.join(sponsor)
    return title, bill_type, sponsor

def get_subjects_and_address(row) :
    if   row[len(row)-1] == 'NO SUBJECTS AVAILABLE' : 
        return None, row[len(row)-2]
    elif row[len(row)-1] == '( )' : 
        return None, row[len(row)-2]
    elif row[len(row)-1] == 'None' : 
        return None, row[len(row)-2]
    else : 
        i = len(row)-2 
        subjects = []
        while '/vagrant' not in row[i] : 
            subjects.append(row[i].lstrip().rstrip())
            i -= 1
        subjects.append(row[i][1:].lstrip().rstrip())
        return subjects, row[i]
        
def create_bill(row) :
    bill = {
        'page'  : row[0]
    }
    bill['title'], bill['type'], bill['sponsor'] = get_title_type_sponsor(row)
    bill['subjects'], bill['address'] = get_subjects_and_address(row)
    return bill

def print_bill(bill) :
    print('Page:', bill['page'])
    print('Title:' , bill['title'])
    print('Sponsor:', bill['sponsor'])
    print('Type:', bill['type'])
    print('Address:', bill['address'])
    if (bill['subjects']) :
        print('Subjects:')
        for subject in bill['subjects'] : print('\t' , subject)
    else : print('Subjects: None')
    print()

def main() :

	bills = []
	with open(path, 'r') as csvfile :
	    count = 0
	    reader = csv.reader(csvfile, delimiter=',')
	    for row in reader : 
	        count+=1
	        bills.append(create_bill(row))

	bills_by_page = {}
	for bill in bills :
	    if bill['page'] in bills_by_page : bills_by_page[bill['page']].append(bill)
	    else :  bills_by_page[bill['page']] = []

        script = open('./tag.sh', 'a')
        os.mkdir('./filelists')
        os.mkdir('./tagged')

        count = 0
        for page in bills_by_page :
            count += 1
            os.mkdir('./tagged/page_' + page)
            filelist = open('./filelists/page_' + page[:-1], 'w')

            script.write('java -cp "*" -Xmx3g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner -filelist ../filelists/page_' + page + '\n')
            script.write('echo "Page ' + str(count) + ' of 780" >> out\n')

            for bill in bills_by_page[page] :
                if bill['type'] != 'AMENDMENT' and bill['subjects'] != None :
                    filelist.write('../../Scrape/' + bill['address'][16:] + '\n')

if __name__ == '__main__' :
	main()
