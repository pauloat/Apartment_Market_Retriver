import bs4, requests, re
from datetime import date, datetime, timedelta

page = '' #page with filters

#The headers help to avoid anti bot measures
headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
        'Accept-Language': 'en-US'
        }
 
res = requests.get(page, headers=headers)

soup = bs4.BeautifulSoup(res.text, 'html.parser')

listings = []

for i in range(len(soup.find_all('span', {'class': 'main-price'}))):
    
    price = int(re.sub(r'\D', '', soup.find_all('span', {'class': 'main-price'})[i].text))
    
    try:
        condominio = int(re.sub(r'\D', '', soup.find_all('span', {'class': 'second-price-label'})[i].text))
    except:
        condominio = 0 #If there's no condominio it gave an error, now it just gave 0
        
    total_price = price + condominio
    
        
    date_published = soup.find_all('span', {'class': 'adDate'})[i*2+1].text
      
    if date_published[:4] == 'Hoje':
        date_listing = str(date.today()) + ' ' + date_published[6:12] + ':00' #transform the date in a standard format
    elif date_published[:5] == 'Ontem':
        date_listing = str(date.today() - timedelta(days=1)) + ' ' + date_published[7:13] + ':00'
    else:
        continue    
    
    if datetime.now() - datetime.strptime(date_listing, '%Y-%m-%d %H:%M:%S') > timedelta(minutes = 30):
        continue
    
    size = int(re.sub(r'\D','', soup.find_all('span', {'aria-label': re.compile(r'\d+ metros')})[i].text))
    
    price_x_mt2 = round(total_price / size, 2)
    
    link = soup.find_all('a', {'data-ds-component' : 'DS-AdCardHorizontal'})[i].get('href')
    
    try:
        neighbor = re.findall(r'Rio de Janeiro, (\w+( \w+)?)',soup.find_all('span', {'aria-label': re.compile('localiza')})[i].text)[0][0]
    except:
        neighbor = ''
    
    res_listing = requests.get(link, headers = headers)
    
    soup_listing = bs4.BeautifulSoup(res_listing.text, 'html.parser')
    
    try:
        comments = soup_listing.find('span', {'class': 'ad__sc-1sj3nln-1 fMgwdS sc-ifAKCX cmFKIN'}).text
    except:
        comments = ''
        
    codigo = int(re.sub(r'\D', '', soup_listing.find('span', {'class' : 'ad__sc-16iz3i7-0 bTSFxO sc-ifAKCX fizSrB'}).text))
     
    date_text = soup_listing.find('span', {'class' : 'ad__sc-1oq8jzc-0 hSZkck sc-ifAKCX fizSrB'}).text

    date_regex = re.search(r'(\d{2})/(\d{2})\D+(\d{2}):(\d{2})', date_text)

    date_public = datetime(datetime.now().year, int(date_regex.group(2)), int(date_regex.group(1)), int(date_regex.group(3)), int(date_regex.group(4))) 

    
    listing = {
        "Date": date_public,
        "Price": price,
        "Condominio": condominio,
        "Total price": total_price,
        "Price / mt2" : price_x_mt2,
        "Size": size,
        "Neighbor": neighbor,
        "Link": link,
        "Codigo": codigo
        }
    
    listing_formatted = f"{listing['Codigo']},{listing['Date']},{listing['Price']},{listing['Condominio']},{listing['Total price']},{listing['Size']},{listing['Price / mt2']},{listing['Neighbor']}"    
    listings.append(listing_formatted)
    


listings_file = open('listings.txt', 'a')

for item in listings:
    
    listings_file.write("%s \n" % item)
        
listings_file.close()
