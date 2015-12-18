import matplotlib, csv, sys, os, math, random
import xml.etree.cElementTree as ET
matplotlib.use('Agg')
from matplotlib import pyplot as plt
csv.field_size_limit(sys.maxsize)

tpath = './tagged'
ipath = './bills.csv'
# bpath = '../Scrape/bills/'
main  = os.listdir(tpath);

################################################################################
########################### GET BILL OBJECTS ###################################
################################################################################

def get_title_type_sponsor(row) :
    i = 2
    title = []
    while 'RESOLUTION' not in row[i] and 'AMENDMENT' not in row[i] and 'LAW' not in row[i] and 'BILL' not in row[i] :
        title.append(row[i])
        i += 1
    title = ' '.join(title)
    bill_type = row[i]
    sponsor = None
    committees = None
    if bill_type == 'AMENDMENT' : sponsor = 'NO SPONSOR'
    else : 
        sponsor = []
        j = i
        # for j in range(i, len(row)-1) :
        while j < (len(row)-1) :
            if row[j] != bill_type : sponsor.append(row[j])
            if ']' in row[j] or '[' in row[j] : break
            j += 1
        j += 1
        sponsor = ','.join(sponsor)
        committees = []
        while j < (len(row)-1) :
            if '/vagrant' in row[j] : break
            committees.append(row[j].lstrip().rstrip())
            j += 1
    return title, bill_type, sponsor, committees

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
            if row[i][0] == '(' : subjects.append(row[i][1:].lstrip().rstrip())
            else : subjects.append(row[i].lstrip().rstrip())
            i -= 1
        # subjects.append(row[i][1:].lstrip().rstrip())
        return subjects, row[i]
        
def create_bill(row) :
    bill = {
        'page'  : row[0],
        'name'  : row[1]
    }
    bill['title'], bill['type'], bill['sponsor'], bill['committees'] = get_title_type_sponsor(row)
    bill['subjects'], bill['address'] = get_subjects_and_address(row)
    if bill['address'] == 'NO TEXT AVAILABLE' : bill['address'] = None
    else : 
        bill['address'] = tpath + bill['address'][21:] + '.xml'
        # bill['raw'] = bpath + bill['address'][8:-4]
    return bill

def print_bill(bill) :
    print 'Page:', bill['page']
    print 'Name:', bill['name']
    print 'Title:' , bill['title']
    print 'Sponsor:', bill['sponsor']
    print 'Type:', bill['type']
    print 'Address:', bill['address']
    if bill['committees'] :
        print 'Committees:'
        for committee in bill['committees'] : print '\t' + committee
    else : print 'Committees: None'
    if bill['subjects'] :
        print 'Subjects:'
        for subject in bill['subjects'] : print '\t' + subject
    else : print 'Subjects: None'
    # print 'Text:'
    # text = open(bill['raw'], 'r')
    # print text.read()
    print

################################################################################
########################### GET BILL OBJECTS ###################################
################################################################################



################################################################################
########################## PROCESS BILL TEXT ###################################
################################################################################

def process_sentence(sentence, wc, dstwc, twc, cwc) :
    NER = 'O'
    NER_WORD = ''
    NER_FULL = 'O'
    NER_WORD_FULL = ''
    weight = 1
    count = 1
    for word in sentence[0] :
        
        # REGULAR CASE
        if word[1].text in wc['reg'] :  wc['reg'][word[1].text] += 1 
        else :  wc['reg'][word[1].text] = 1 
            
        # DIST CASE
        cwc['dist'] += 1
        if word[1].text in wc['dist'] : 
            wc['dist'][word[1].text] += 1.0 - (float(dstwc['dist'][word[1].text])/float(twc))
        else : 
            dstwc['dist'][word[1].text] = cwc['dist']
            wc['dist'][word[1].text] = 1.0 - (float(dstwc['dist'][word[1].text])/float(twc))
            
        # NER CASE
        if word[5].text != 'O' :  
            if NER == 'O' : 
                NER = word[5].text
                NER_WORD = word[0].text
            elif word[5].text == NER :
                NER_WORD = ' '.join([NER_WORD, word[0].text])
            else : 
                NER = word[5].text
                if len(NER_WORD.split(' ')) > 1 :
                    if NER_WORD in wc['ner'] : wc['ner'][NER_WORD] += 1  
                    else : wc['ner'][NER_WORD] = 1 
                NER_WORD = word[0].text
        else :        
            if word[1].text in wc['ner'] : wc['ner'][word[1].text] += 1 
            else : wc['ner'][word[1].text] = 1 
                
        # FULL CASE        
        cwc['full'] += 1
        if count == 1 :
            if word[0].text == 'Section' : weight = 1.5
        count += 1
        if word[5].text != 'O' :  
            if NER_FULL == 'O' : 
                NER_FULL = word[5].text
                NER_WORD_FULL = word[0].text
            elif word[5].text == NER_FULL :
                NER_WORD_FULL = ' '.join([NER_WORD_FULL, word[0].text])
            else : 
                NER_FULL = word[5].text
                if len(NER_WORD_FULL.split(' ')) > 1 :
                    if NER_WORD_FULL in wc['full'] : 
                        wc['full'][NER_WORD_FULL] += weight - (float(dstwc['full'][NER_WORD_FULL])/float(twc)) 
                    else : 
                        dstwc['full'][NER_WORD_FULL] = cwc['full']
                        wc['full'][NER_WORD_FULL] = weight - (float(dstwc['full'][NER_WORD_FULL])/float(twc))
                NER_WORD_FULL = word[0].text
        else :        
            if word[1].text in wc['full'] : 
                wc['full'][word[1].text] += weight 
                wc['full'][word[1].text] += weight - (float(dstwc['full'][word[1].text])/float(twc))
            else : 
                dstwc['full'][word[1].text] = cwc['full']
                wc['full'][word[1].text] = weight - (float(dstwc['full'][word[1].text])/float(twc))

def process_doc(doc) :
    if os.path.getsize(doc) :
        tree      = ET.ElementTree(file=doc)
        sentences = tree.getroot()[0][0]
        twc = 0
        for sentence in sentences : twc += len([word for word in sentence[0]])
            
        wc_reg = {}
        cwc_reg = 0
        dstwc_reg = {}
        
        wc_ner = {}
        cwc_ner = 0
        dstwc_ner = {}
        
        wc_dist = {}
        cwc_dist = 0
        dstwc_dist = {}
        
        wc_full = {}
        cwc_full = 0
        dstwc_full = {}
        
        wc = { 'reg' : wc_reg, 'ner' : wc_ner, 'dist' : wc_dist, 'full' : wc_full }
        cwc = { 'reg' : cwc_reg, 'ner' : cwc_ner, 'dist' : cwc_dist, 'full' : cwc_full }
        dstwc = { 'reg' : dstwc_reg, 'ner' : dstwc_ner, 'dist' : dstwc_dist, 'full' : dstwc_full }
        
        for sentence in sentences :
            process_sentence(sentence, wc, dstwc, twc, cwc)

        return wc
    else : return None

def process_bills(bills) :
    count = 0
    doc_dict_reg  = {}
    doc_dict_ner  = {}
    doc_dict_dist = {}
    doc_dict_full = {}
    for bill in bills :
        if count % 1000 == 0 : print str(count)
        count += 1
        processed = process_doc(bill['address'])
        if processed['reg'] != None :
            doc_dict_reg[bill['page'][:-1] + '_' + bill['name']] = processed['reg']
            doc_dict_ner[bill['page'][:-1] + '_' + bill['name']] = processed['ner']
            doc_dict_dist[bill['page'][:-1] + '_' + bill['name']] = processed['dist']
            doc_dict_full[bill['page'][:-1] + '_' + bill['name']] = processed['full']
    return doc_dict_reg, doc_dict_ner, doc_dict_dist, doc_dict_full

def process_full(doc_dict) :
    full_dict = {}
    for item in doc_dict.items() : 
        for word in item[1] :
            if word in full_dict : full_dict[word] += 1
            else : full_dict[word] = 1
    return full_dict

################################################################################
########################## PROCESS BILL TEXT ###################################
################################################################################



################################################################################
################################ TF-IDF ########################################
################################################################################

def tf_idf(doc, doc_dict, full_dict, word) : 
    if doc_dict[doc][word] <= 0 : tf =.00000000001
    else : tf = 1 + math.log(doc_dict[doc][word])
    idf = math.log(float(len(doc_dict))/float(full_dict[word]))
    return tf * idf

def tf_idf_scores(doc, doc_dict, full_dict) :
    t_dict = {} 
    for word in doc_dict[doc] :
        t_dict[word] = tf_idf(doc, doc_dict, full_dict, word) 

    return sorted(t_dict.items(), key=lambda x:x[1] , reverse = True)

################################################################################
################################ TF-IDF ########################################
################################################################################



################################################################################
############################### EVALUATION #####################################
################################################################################

def accuracy(bill, doc_dict, full_dict, fraction_keywords) :
    path = bill['page'][:-1] + '_' + bill['name']
    keys = tf_idf_scores(path, doc_dict, full_dict)
    keys = keys[:int(len(keys)*fraction_keywords)]
    subjects = bill['subjects']
    subs = ' '.join(subjects).split(' ')
    for sub in subs :
        if sub not in subjects : subjects.append(sub)
    keys = [k[0] for k in keys]
    count = 0
    for word in keys :
        if word in subjects : count += 1
    return float(count)/len(bill['subjects'])

def recall(bill, doc_dict, full_dict, fraction_keywords) :
    acc = accuracy(bill, doc_dict, full_dict, fraction_keywords)
    if acc > 0 : return (acc/accuracy(bill, doc_dict, full_dict, 1.0))
    else : return 0.0

################################################################################
############################### EVALUATION #####################################
################################################################################

def main() :


	bills = []
	with open(ipath, 'r') as csvfile :
	    count = 0
	    reader = csv.reader(csvfile, delimiter=',')
	    for row in reader : 
	        if count >= 50000 : break
	        count+=1
	        bill = create_bill(row)
	        if bill['address']  :
	            if os.path.isfile(bill['address']) : 
        	        if os.path.getsize(bill['address']) > 0 :
        	            bills.append(bill)

	doc_dict_reg, doc_dict_ner, doc_dict_dist, doc_dict_full = process_bills(bills)

	full_dict_reg  = process_full(doc_dict_reg)
	full_dict_ner  = process_full(doc_dict_ner)
	full_dict_dist = process_full(doc_dict_dist)
	full_dict_full = process_full(doc_dict_full)

        evals_reg_1 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_reg, full_dict_reg, .10) 
            if acc > 0 : evals_reg_1.append(acc)
                
        evals_reg_2 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_reg, full_dict_reg, .20) 
            if acc > 0 : evals_reg_2.append(acc)
                
        evals_reg_3 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_reg, full_dict_reg, .30) 
            if acc > 0 : evals_reg_3.append(acc)
                
        evals_reg_4 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_reg, full_dict_reg, .40) 
            if acc > 0 : evals_reg_4.append(acc)
                
        evals_ner_1 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_ner, full_dict_ner, .10) 
            if acc > 0 : evals_ner_1.append(acc)
                
        evals_ner_2 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_ner, full_dict_ner, .20) 
            if acc > 0 : evals_ner_2.append(acc)
                
        evals_ner_3 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_ner, full_dict_ner, .30) 
            if acc > 0 : evals_ner_3.append(acc)
                
        evals_ner_4 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_ner, full_dict_ner, .40) 
            if acc > 0 : evals_ner_4.append(acc)
                
        evals_dist_1 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_dist, full_dict_dist, .10) 
            if acc > 0 : evals_dist_1.append(acc)
                
        evals_dist_2 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_dist, full_dict_dist, .20) 
            if acc > 0 : evals_dist_2.append(acc)
                
        evals_dist_3 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_dist, full_dict_dist, .30) 
            if acc > 0 : evals_dist_3.append(acc)
                
        evals_dist_4 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_dist, full_dict_dist, .40) 
            if acc > 0 : evals_dist_4.append(acc)
                
        evals_full_1 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_full, full_dict_full, .10) 
            if acc > 0 : evals_full_1.append(acc)
                
        evals_full_2 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_full, full_dict_full, .20) 
            if acc > 0 : evals_full_2.append(acc)
                
        evals_full_3 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_full, full_dict_full, .30) 
            if acc > 0 : evals_full_3.append(acc)
                
        evals_full_4 = []
        for bill in bills : 
            acc = accuracy(bill, doc_dict_full, full_dict_full, .40) 
            if acc > 0 : evals_full_4.append(acc)

        fig, ((ax1, ax2, ax3, ax4),(ax5,ax6,ax7,ax8),(ax9,ax10,ax11,ax12),(ax13,ax14,ax15,ax16)) = plt.subplots(4, 4, sharey=True)
        ax1.xaxis.set_visible(False)
        ax2.xaxis.set_visible(False)
        ax3.xaxis.set_visible(False)
        ax4.xaxis.set_visible(False)
        ax5.xaxis.set_visible(False)
        ax6.xaxis.set_visible(False)
        ax7.xaxis.set_visible(False)
        ax8.xaxis.set_visible(False)
        ax9.xaxis.set_visible(False)
        ax10.xaxis.set_visible(False)
        ax11.xaxis.set_visible(False)
        ax12.xaxis.set_visible(False)
        ax13.xaxis.set_visible(False)
        ax14.xaxis.set_visible(False)
        ax15.xaxis.set_visible(False)
        ax16.xaxis.set_visible(False)
        fig.set_size_inches(20, 20)
        p1 = ax1.plot([random.uniform(1,10) for x in range(len(evals_reg_1))], evals_reg_1, 'oy', label='reg')
        ax2.plot([random.uniform(1,10) for x in range(len(evals_reg_2))], evals_reg_2, 'oy')
        ax3.plot([random.uniform(1,10) for x in range(len(evals_reg_3))], evals_reg_3, 'oy')
        ax4.plot([random.uniform(1,10) for x in range(len(evals_reg_4))], evals_reg_4, 'oy')
        p2 = ax5.plot([random.uniform(1,10) for x in range(len(evals_ner_1))], evals_ner_1, 'ob', label='ner')
        ax6.plot([random.uniform(1,10) for x in range(len(evals_ner_2))], evals_ner_2, 'ob')
        ax7.plot([random.uniform(1,10) for x in range(len(evals_ner_3))], evals_ner_3, 'ob')
        ax8.plot([random.uniform(1,10) for x in range(len(evals_ner_4))], evals_ner_4, 'ob')
        p3 = ax9.plot([random.uniform(1,10) for x in range(len(evals_dist_1))], evals_dist_1, 'or', label='dist')
        ax10.plot([random.uniform(1,10) for x in range(len(evals_dist_2))], evals_dist_2, 'or')
        ax11.plot([random.uniform(1,10) for x in range(len(evals_dist_3))], evals_dist_3, 'or')
        ax12.plot([random.uniform(1,10) for x in range(len(evals_dist_4))], evals_dist_4, 'or')
        p4 = ax13.plot([random.uniform(1,10) for x in range(len(evals_full_1))], evals_full_1, 'og', label='full')
        ax14.plot([random.uniform(1,10) for x in range(len(evals_full_2))], evals_full_2, 'og')
        ax15.plot([random.uniform(1,10) for x in range(len(evals_full_3))], evals_full_3, 'og')
        ax16.plot([random.uniform(1,10) for x in range(len(evals_full_4))], evals_full_4, 'og')
        ax1.set_ylabel('Recall')
        ax5.set_ylabel('Recall')
        ax9.set_ylabel('Recall')
        ax13.set_ylabel('Recall')
        ax1.set_title('5%')
        ax2.set_title('10%')
        ax3.set_title('15%')
        ax4.set_title('20%')
        fig.subplots_adjust(wspace=1)
        plt.axis([0,11,0,.6])
        # yp = mpatches.Patch(color='yellow', label='TF-IDF only')
        # bp = mpatches.Patch(color='blue', label='TF-IDF and NER')
        # rp = mpatches.Patch(color='red', label='Distance only')
        # gp = mpatches.Patch(color='green', label='TF-IDF, NER, Distance, and Enhancements')
        # plt.legend(bbox_to_anchor=(0,0), handles=['reg', 'ner', 'dist', 'full'])
	plt.legend((p1[0], p2[0], p3[0], p4[0]), ('TF-IDF only', 'TF-IDF and NER', 'TF-IDF and Distance', 'TF-IDF, Distance, NER, and Enhancements'), bbox_to_anchor=(0,0))
        plt.suptitle('Recall Scores By Feature and Keyword Percentage', fontsize=15)
        plt.show()
        plt.savefig('Recall Scores By Feature and Keyword Percentage.png')

        fig, ax = plt.subplots()
        p5 = ax.plot([random.uniform(2,8) for x in range(len(evals_reg_4))], evals_reg_4, 'oy', label='TF-IDF only')
        p6 = ax.plot([random.uniform(12,18) for x in range(len(evals_ner_4))], evals_ner_4, 'ob', label='TF-IDF and NER')
        p7 = ax.plot([random.uniform(22,28) for x in range(len(evals_dist_4))], evals_dist_4, 'or', label='Distance only')
        p8 = ax.plot([random.uniform(32,38) for x in range(len(evals_full_4))], evals_full_4, 'og', label='TF-IDF, NER, Distance, and Enhancements')
        ax.xaxis.set_visible(False)
        plt.axis([0,40,0,.8])
        fig.set_size_inches(20, 20)
        # yp = mpatches.Patch(color='yellow', label='TF-IDF only')
        # bp = mpatches.Patch(color='blue', label='TF-IDF and NER')
        # rp = mpatches.Patch(color='red', label='Distance only')
        # gp = mpatches.Patch(color='green', label='TF-IDF, NER, Distance, and Enhancements')
        # plt.legend(bbox_to_anchor=(1,0), handles=[yp,bp,rp,gp])
	plt.legend((p5[0], p6[0], p7[0], p8[0]), ('TF-IDF only', 'TF-IDF and NER', 'TF-IDF and distance', 'TF-IDF, Distance, NER, and Enhancements'), bbox_to_anchor=(1,0))
        plt.title('Recall Scores by Feature', fontsize=15)
        plt.show()
        plt.savefig('Recall Scores By Feature.png')

if __name__ == '__main__' :
    main()
