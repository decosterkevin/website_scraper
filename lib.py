from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pickle
import os.path
from config import Config
from send_email import send_email

config = Config()

def trim(text):
    # trimmed = text.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '').replace('\u', '')
    return text.encode('utf-8').decode('ascii', 'ignore').strip()


def extract_table(url, classes=None, ids=None):
    print("extracting list of offers...")

    
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    filtering= {}

    if classes:
        filtering.update({'class': classes})
    if ids:
        filtering.update({'id': ids}) 
    lists = soup.findAll('ul', filtering)
    
    if len(lists)>  1:
        print("severals poissibles candidates, will choose the first one")
    if len(lists)== 0:
        raise ValueError("list not found")

    results = []
    for li in lists[0].findAll('li', recursive=False):
        tmp_result = {}
        if 'ads' not in li.get('class'):
            for div in li.find_all("div"):
                a = div.find('a')
                if a:
                    tmp_result['href']=trim(a.get('href'))
                ids = div.get('id')
                classes = div.get('class')
                text = trim(div.text)
                if ids:
                    if isinstance(ids, list):
                        field = ids[0]
                    else:
                        field = ids
                    field = trim(field)
                    tmp_result[field]= text
                # elif classes:
                #     if isinstance(classes, list):
                #         field =' '.join(classes)
                #     else:
                #         field = classes
                

            for tmp_ul in li.findAll('ul'):
                for tmp_li in tmp_ul.findAll('li'):
                    if 'item-date' in tmp_li.get('class'):
                        try:
                            tmp_result['date']= datetime.strptime(str(trim(tmp_li.text)), '%d.%m.%Y')
                            results.append(tmp_result)
                        except TypeError as error:
                            print('error' + tmp_li.text)
    return sorted(results, key=lambda k: k['date'])
    
                

def process_list(latest_results, old_results=None):
    new_offers = []
    if old_results:
        old_hrefs = [tmp['href'] for tmp in old_results]
        old_dates = [tmp['date'] for tmp in old_results]
        
        for offer in latest_results:
            if offer['href'] not in old_hrefs:
                new_offers.append(offer)
            else:
                break
    return new_offers

def send_mail(new_offers):
    if len(new_offers)> 0:
        print("new offers find, sending email...")
        str_list = '\n'.join([config.ROOT_URL + offer['href'] for offer in new_offers])
        msg = """\

            You have new offers for {0}:

            {1}
        """
        subject = "Anibis monitoring"
        send_email("kevin@decoster.io" , "decoster.kevin@outlook.com",subject, msg.format(subject, str_list))
    else:
        print("no new offers, closing...")


# url_ = 'https://www.anibis.ch/fr/immobilier-immobilier-locations-gen%c3%a8ve--418/advertlist.aspx?loc=1205+gen%c3%a8ve&aidl=868,15222&dlf=1'
# list_ = extract_table(url_, classes='listing-list')
# process_list(list_)

# str_list = '\n'.join([config.ROOT_URL + offer['href'] for offer in list_])
# msg = """\

#     You have new offers for {0}:

#     {1}
# """
# send_email("kevin@decoster.io", "decoster.kevin@outlook.com", msg.format(config.ROOT_URL,str_list))
