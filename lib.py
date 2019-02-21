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

def extract_id(href):
    index_1 = href.index(".aspx")
    substring = href[index_1-12:index_1]
    index_0 = substring.index("--")
    sub_refined = substring[index_0 + 2:]
    return sub_refined

def remove_url_parameters(href):
    index_1 = href.index(".aspx")
    return href[:index_1 + 5]

def extract_table(url, classes=None, ids=None):
    """ HTML extractor

    Look for list tag <ul> given a list of classes and ids
    
    Parameters
    ----------
    url : str
        URL to scrap
    classes : list, optional
        a list of classes (the default is None, which don't filter by class)
    ids : list, optional
        a list of ids (the default is None, which don't filter by ids)
    
    Raises
    ------
    ValueError
        ListNotFound if not <ul> tag are present on the webpage
    
    Returns
    -------
    list
        A list of dictionary element contening all list elements
    """

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
                    tmp_result['href']=remove_url_parameters(trim(a.get('href')))
                    tmp_result['id']= extract_id(tmp_result['href'])
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
    return sorted(results,reverse=True, key=lambda k: k['date'])
    
                

def process_list(latest_results, old_results=None):
    """ Find update in the most recent list 
    
    Parameters
    ----------
    latest_results : list
        the newest list results
    old_results : list, optional
        the backup results to be compared with (the default is None, which means no backup results are available)
    
    Returns
    -------
    list
        A list of new offers
    """

    new_offers = []
    if old_results:
        old_ids = []
        new_ids = []
        for tmp in old_results:
            if not tmp.get("id", None):
                print(tmp.get("href", None))
            old_ids.append(tmp.get("id", None))
        old_dates = [tmp['date'] for tmp in old_results]
        
        for offer in latest_results:
            if offer['id'] not in old_ids and offer['id'] not in new_ids:
                new_offers.append(offer)
                new_ids.append(offer['id'])
    return new_offers

def create_email(new_offers):
    if len(new_offers)> 0:
        print("new offers find, sending email...")
        
        str_list = '\n'.join([ config.ROOT_URL + offer['href'] for offer in new_offers])
        str_list_html = ''.join(['<li><a href="' + config.ROOT_URL + offer['href'] + '">' +  config.ROOT_URL + offer['href'] + '</a></li>' for offer in new_offers])
        msg = "You have new offers for {0} in {1}: \n {2}"
        html = """\
            <html>
            <head></head>
            <body>
                <p>You have new offers for {0} in {1}:</p>
                <p>Here is list:</p>
                <ul>
                {2}
                </ul>
                </p>
            </body>
            </html>
        """
        subject = "Anibis monitoring"
        send_email("kevin@decoster.io" , "decoster.kevin@outlook.com", subject, msg.format(subject, config.HOST, str_list), html.format(subject,config.HOST, str_list_html))
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

# x="/fr/d-immobilier-immobilier-locations-gen%c3%a8ve--418/appartement-dans-une-maison-%c3%a0-ferney-voltaire,-chemin%c3%a9e--27495936.aspx?fts=maison&loc=versoix&sdc=10&aral=834__3000,851_50_,865_2.5_&aidl=866,15222&dlf=1&view=2&fcid=418&abcate=1"
# # send_mail([{'href': x}])
# print(remove_url_parameters(x))