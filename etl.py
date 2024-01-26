import pandas as pd
import os
import sqlite3
from slick_deal_web_scrapper import SlickDealPopularDealsScrapper, SlickDealDealsByCategoryScrapper

def extract():
    SlickDealPopularDeals = SlickDealPopularDealsScrapper()
    popular_deals = SlickDealPopularDeals.get_popular_deals()

    SlickDealDealsByCategory = SlickDealDealsByCategoryScrapper('auto')
    category_items = SlickDealDealsByCategory.get_category_deals()

    return popular_deals, category_items

def transform_deals(deals):
    df = pd.DataFrame.from_dict(data=deals, orient='index')
    df = df.reset_index()
    df = df.rename(columns={'index': 'item_name'})
    
    df['item_update_dt'] = pd.to_datetime(df['item_update_dt'])
    df['item_price'] = pd.to_numeric(df['item_price'], errors='coerce')
    df['item_price'] = df['item_price'].fillna(0)
    df['item_rating_stats'] = pd.to_numeric(df['item_rating_stats'], errors='coerce')
    df['item_rating_thumbs'] = pd.to_numeric(df['item_rating_thumbs'], errors='coerce')
    df['item_n_views'] = pd.to_numeric(df['item_n_views'], errors='coerce')
    df['item_n_comments'] = pd.to_numeric(df['item_n_comments'], errors='coerce')

    return df

def transform_category_items(category_items):
    df = pd.DataFrame.from_dict(data=category_items, orient='index')
    df = df.reset_index()
    df = df.rename(columns={'index': 'item_name'})
    
    df['item_create_date'] = pd.to_datetime(df['item_create_date'])
    df['item_price'] = pd.to_numeric(df['item_price'], errors='coerce')
    df['item_price'] = df['item_price'].fillna(0)
    df['item_thumb_upvotes'] = pd.to_numeric(df['item_thumb_upvotes'], errors='coerce')
    df['item_n_comments'] = pd.to_numeric(df['item_n_comments'], errors='coerce')

    return df



def load_deals(data):
    conn = sqlite3.connect('db/db_deals')
    print("Writing to DB")
    data.to_sql('item_deals', con=conn, if_exists='replace')
    conn.commit()
    conn.close()

def load_category_items(data):
    conn = sqlite3.connect('db/db_deals')
    print("Writing to DB")
    data.to_sql('category_items', con=conn, if_exists='replace')
    conn.commit()
    conn.close()

def main():
    popular_deals, category_items = extract()
    df_deals, df_category_items = transform_deals(popular_deals), transform_category_items(category_items)
    load_deals(df_deals)
    load_category_items(df_category_items)




if __name__ == "__main__":
    main()