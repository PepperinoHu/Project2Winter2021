#################################
##### Name:Jiaoyang Hu
##### Uniqname: ivanhujy
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import re


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self,category='',name = '',address='',zipcode='',phone=''):
        ''' initialize the NationalSite class"

        Parameters
        ----------
        category: string
            the category of a national site (e.g. 'National Park', '')
            some sites have blank category.
    
        name: string
            the name of a national site (e.g. 'Isle Royale')

        address: string
            the city and state of a national site (e.g. 'Houghton, MI')

        zipcode: string
            the zip-code of a national site (e.g. '49931', '82190-0168')

        phone: string
            the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')

        Returns
        -------
        None
        '''
        self.category=category
        self.name = name
        self.address= address
        self.zipcode = zipcode
        self.phone = phone
    def info(self):
        ''' print NationalSite information"

        Parameters
        ----------
        self

        Returns
        -------
        String
            a string that contains name,category,address and zipcode of NationalSite
        '''
        return self.name + ' ('+self.category+'): '+self.address+' '+self.zipcode


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    url_dict = {}
    html = requests.get('https://www.nps.gov/index.htm').text
    soup = BeautifulSoup(html, 'html.parser')
    all_list_items = soup.find_all('li')
    regex = '[^\s]*[\s]*[^\s]*\"([^\s]*)\">([^\s]*[\s]*[^\s]*[\s]*[^\s]*[\s]*[^\s]*)<[^\s]*<[^\s]*'
    for item in all_list_items:
        item_string = str(item)
        if 'state' in item_string:
            match_object = re.search(regex,item_string)
            if match_object:
                url_dict[match_object.group(2).lower()] = 'https://www.nps.gov'+ match_object.group(1)
    return url_dict
       

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    html = requests.get(site_url).text
    soup = BeautifulSoup(html, 'html.parser')
    all_head_items = soup.find_all('head')   

    #reading header
    regex_head = r'.*<title>(.*)\(.*\)</title>.*'
    match_object = re.search(regex_head,str(all_head_items))
    if match_object:
        head_list = match_object.group(1).split()
    name = ''
    category = ''
    try:
        ind = head_list.index('National')
        for i in range(ind):
            name = name + head_list[i] + ' '
        name = name[:-1]
        for i in range(ind,len(head_list)):
            category = category + head_list[i] + ' '
        category = category[:-1]
    except:
        for i in range(len(head_list)):
            name = head_list[i] + ' '
        name = name[:-1]
    
    #reading footer
    all_span_items = soup.find_all('span')
    phone=''
    address=''
    zipcode=''
    for item in all_span_items:
        item_string = str(item)
        regex_phone = r'.*\n(.*)[\n\s]*<\/span>'
        regex_zip = r'.*>(.*)\s*<\/span>'
        regex_address = r'.*\"addressLocality\">(.*)<\/span>.*\"addressRegion\">(.*)<\/span>.*'
        if 'telephone' in item_string:
            match_object = re.search(regex_phone,item_string)
            if match_object:
                phone=match_object.group(1)
        if 'postal-code' in item_string:
            match_object = re.search(regex_zip,item_string)
            if match_object:
                zipcode=match_object.group(1).strip()
        if ('addressRegion' in item_string)&('addressLocality' in item_string):
            match_object = re.search(regex_address,item_string)
            if match_object:
                address=match_object.group(1)+', '+match_object.group(2)

    return NationalSite(category,name,address,zipcode,phone)

def open_cache(cache_name):
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(cache_name, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict,cache_name):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(cache_name,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    state_dict = open_cache('state_cache.json')
    sites_info_list = []
    ns_list = []
    try:
        sites_info_list = state_dict[state_url]
        for site_info in sites_info_list:
            print('Using cache')
            ns_list.append(NationalSite(site_info[0],site_info[1],site_info[2],site_info[3],site_info[4]))
    except:
        html = requests.get(state_url).text
        soup = BeautifulSoup(html, 'html.parser')
        regex = '<h3><a\shref\=\"\/(.*)\/\">.*'
        match_object_list = re.findall(regex,str(soup.find_all('body')))
        for site in match_object_list:
            print('Fetching')
            ns_list.append(get_site_instance('https://www.nps.gov/'+site+'/index.htm'))
        
        for site in ns_list:
            sites_info_list.append([site.category,site.name,site.address,site.zipcode,site.phone])
        state_dict[state_url] = sites_info_list
        save_cache(state_dict,'state_cache.json')
    return ns_list




def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    place_dict = open_cache('place_cache.json')
    try:
        response = place_dict[site_object.zipcode]
        print('Using cache')
    except:
        print('Fetching')
        response = requests.get('http://www.mapquestapi.com/search/v2/radius?key='+secrets.API_KEY+'&maxMatches=10&origin='+site_object.zipcode+'&radius=10&ambiguities=ignore&outFormat=json').json()
        place_dict[site_object.zipcode] = response
        save_cache(place_dict,'place_cache.json')
    return response

if __name__ == "__main__":
    url_dict = build_state_url_dict()
    while(True):
        state_name = input('Enter a state name (e.g. Michigan,michigan) or "exit":')
        if state_name == 'exit':
            break
        try:
            ns_list = get_sites_for_state(url_dict[state_name.lower()])
        except:
            print('[Error] Enter proper state name')
            continue
        i = 1
        print('---------------------------------------')
        print('List of national sites in '+state_name)
        print('---------------------------------------')        
        for ns in ns_list:
            print('['+str(i)+'] '+ns.info())
            i+=1
        exit = False
        while(True):
            second_input = input('Choose the number for detail search or "exit" or "back":')
            if second_input == 'back':
                break
            elif second_input == 'exit':
                exit = True
                break
            elif (second_input.isnumeric() == False):
                print('Error')
                continue
            elif (int(second_input)>len(ns_list)):
                print('Error')
                continue
            site =   ns_list[int(second_input)-1]
            print('---------------------------------------')
            print('Places near '+site.name)
            print('---------------------------------------')
            response = get_nearby_places(site)
            for place in response['searchResults']:
                address = 'no address' if (place['fields']['address'] == '') else place['fields']['address']
                category = 'no category' if (place['fields']['group_sic_code_name_ext'] == '') else place['fields']['group_sic_code_name_ext']
                city = 'no city' if (place['fields']['city'] == '') else place['fields']['city']
                if place['fields']['address'] == '':
                    address = 'no address'
                else:
                    address = place['fields']['address']
                print('- '+place['name']+ ' ('+category+'): '+address+','+city)
        if exit:
            break
    