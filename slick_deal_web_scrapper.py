import requests 
from bs4 import BeautifulSoup
from datetime import date, datetime
from datetime import timedelta
import csv
import pandas as pd
from dateutil.parser import parse


class SlickDealPopularDealsScrapper():
    def __init__(self):
        self.url = 'https://slickdeals.net/deals/'
        self.data = {}
        
    def get_num_pages(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        total_pages = soup.find_all("span", {"id": "totalPageNum"})[0].text
        return int(total_pages)
    
    
    def get_popular_deals(self):
        for page in range(1, self.get_num_pages()+1):
            url = f"{self.url}?page={page}&sort=recent"
            print(f"Scraping {url}")
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            deals = soup.find_all("div", {"class": "dealRow"})
            for deal in deals:
                hash = {}
                item_name = deal.find("div", {"class": "dealTitle"}).find('a').string
                item_store = deal.find("div", {"class": "dealLinks"}).text.replace("\n", "").split("Deals")[0].split("More")[1]
                item_detail_url = f"https://slickdeals.net{deal.find("div", {"class": "dealTitle"}).find('a')['href']}"
                item_update_dt = deal.find("div", {"class": "dealLinks"}).text.replace("\n", "").split("More")[0].strip()
                if item_update_dt == 'Posted Today':
                    item_update_dt = date.today()
                elif item_update_dt == 'Posted Yesterday':
                    item_update_dt = date.today() - timedelta(days = 1)
                else:
                    date_string = item_update_dt.split("Posted")[1].strip()
                    item_update_dt = datetime.strptime(date_string, '%m-%d-%Y').date()
                item_price = deal.find("div", {"class": "price"}).text.replace("\n", "").replace("$", "").replace(",", "").strip()
                if item_price == 'FREE':
                    item_price = None
                
                
                item_rating_stats = deal.find("div", {"class": "num"}).text.replace("+", "").strip()
                item_rating_thumbs = deal.find("span", {"class": "ratingFull"})['class'][1].split("rate")[1]
                item_n_views = deal.findAll("div", {"class": "activity"})[0].text.replace("\n", "").replace("Views", "").replace(",", "").strip()
                item_n_comments = deal.findAll("div", {"class": "activity"})[1].text.replace("\n", "").replace("Comments", "").strip()
   
   
                hash['item_store'] = item_store
                hash['item_detail_url'] = item_detail_url
                hash['item_update_dt'] = item_update_dt
                hash['item_price'] = item_price
                hash['item_rating_stats'] = item_rating_stats
                hash['item_rating_thumbs'] = item_rating_thumbs
                hash['item_n_views'] = item_n_views
                hash['item_n_comments'] = item_n_comments
                
                self.data[item_name] = hash
                
                
        #Save data to CSV
        with open('data/slickdeals_featured.csv', 'w', newline='') as csvfile:
            columns = ['item_name', 'item_store', 'item_detail_url', 'item_update_dt', 'item_price', 'item_rating_stats', 'item_rating_thumbs', 'item_n_views', 'item_n_comments']
            writer = csv.DictWriter(csvfile, fieldnames=columns)

            # Write header
            writer.writeheader()

            # Write data
            print("Writing Data to CSV")
            for row_key, inner_dict in self.data.items():
                row_data = {'item_name': row_key, **inner_dict}
                writer.writerow(row_data)
                
                
                
        return self.data

            
                
    
    
    
class SlickDealDealsByCategoryScrapper():
    def __init__(self, category):
        self.category = category.lower()
        self.url = f"https://slickdeals.net/deals/{category.lower()}/"
        self.data = {}
        
    def get_category_deals(self):
        page_num = 1
        
        while page_num:
            url = f"{self.url}?page={page_num}"  
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            page = soup.find("ul", {"class": "bp-p-filterGrid_items"})
            if page is not None:
                item_list = page.findAll("li", {"class": "bp-p-blueberryDealCard"})
                print(f"Scraping {url}")
                for item in item_list:
                    hash = {}
                    item_name = item.find("div", {"class": "bp-c-card_content"}).findAll("a")[1].text
                    item_detail_url = f"https://slickdeals.net{item.find("div", {"class": "bp-c-card_content"}).findAll("a")[1]['href']}"
                    item_price = item.find("span", {"class": "bp-p-dealCard_price"}).text.replace("$", "").replace(",", "").strip()
                    if item_price == 'FREE':
                        item_price = None
                    
                    if item.find("span", {"class": "bp-c-card_subtitle"}) is not None:
                        item_store = item.find("span", {"class": "bp-c-card_subtitle"}).text
                    else:
                        item_store = None
                        
                    r = requests.get(item_detail_url)
                    detail_dt_soup = BeautifulSoup(r.text, 'html.parser')
                    if detail_dt_soup.find("span", {"class": "date"}) is not None:
                        item_create_date_string = detail_dt_soup.find("span", {"class": "date"}).text.strip()
                        if item_create_date_string == 'Today':
                            item_create_date = date.today()
                        elif item_create_date_string == 'Yesterday':
                            item_create_date = date.today() - timedelta(days = 1)
                        else:
                            item_create_date = parse(item_create_date_string).date()
                    else:
                        item_create_date = None
                        
                    item_thumb_upvotes = item.find("span", {"class": "bp-p-votingThumbsPopup_voteCount js-votingThumbsPopup_voteCount"}).text
                    item_n_comments = item.find("a", {"class": "bp-p-blueberryDealCard_comments bp-c-link"}).text.replace("\n","").strip()

                    hash['item_category'] = self.category
                    hash['item_detail_url'] = item_detail_url         
                    hash['item_price'] = item_price
                    hash['item_store'] = item_store
                    hash['item_create_date'] = item_create_date
                    hash['item_thumb_upvotes'] = item_thumb_upvotes
                    hash['item_n_comments'] = item_n_comments
                    
                    self.data[item_name] = hash
            
            
            else:
                print("No More Pages to Scrape")
                break
            page_num += 1
        
        with open(f'data/slickdeals_{self.category}.csv', 'w', newline='') as csvfile:
            columns = ['item_name', 'item_category', 'item_detail_url', 'item_price', 'item_store', 'item_create_date', 'item_thumb_upvotes', 'item_n_comments']
            writer = csv.DictWriter(csvfile, fieldnames=columns)

            # Write header
            writer.writeheader()

            # Write data
            print("Writing Data to CSV")
            for row_key, inner_dict in self.data.items():
                row_data = {'item_name': row_key, **inner_dict}
                writer.writerow(row_data)
                
        
        return self.data
        
            

            


    
