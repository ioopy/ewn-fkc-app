import pandas as pd
from utils.func import convert_amount_sold

def get_data():
    shopee_data = pd.read_csv('data/Shopee-Data.csv')
    lazada_data = pd.read_csv('data/Lazada-Data.csv')

    shopee_data = shopee_data.rename(columns={'itemid': 'itemId', 'shopid': 'shopId'})
    lazada_data = lazada_data.rename(columns={'itemid': 'itemId', 'shopid': 'shopId'})

    shopee_data['amount_sold_format'] = shopee_data['amount_sold'].apply(convert_amount_sold)
    lazada_data['amount_sold_format'] = lazada_data['amount_sold'].apply(convert_amount_sold)

    lazada_data['discount_price_format'] = lazada_data['discount_price'].fillna(0)
    shopee_data['discount_price_format'] = shopee_data['discount_price'].fillna(0)

    lazada_data['total_value'] = lazada_data['amount_sold_format'] * lazada_data['discount_price_format']
    shopee_data['total_value'] = shopee_data['amount_sold_format'] * shopee_data['discount_price_format']

    lazada_data['star_review'].fillna(0, inplace=True)
    lazada_data['star_review'] = lazada_data['star_review'].apply(lambda x: f"{x:.1f}")

    shopee_data['star_review'].fillna(0, inplace=True)
    shopee_data['star_review'] = shopee_data['star_review'].apply(lambda x: f"{x:.1f}")

    return pd.concat([shopee_data, lazada_data])

def get_reviews():
    shopee_reviews = pd.read_csv('data/Shopee-Reviews.csv')
    lazada_reviews = pd.read_csv('data/Lazada-Reviews.csv')
    combined_reviews = pd.concat([shopee_reviews, lazada_reviews])

    combined_reviews['date_column'] = pd.to_datetime(combined_reviews['review_date'])
    combined_reviews['year'] = combined_reviews['date_column'].dt.year
    combined_reviews['month'] = combined_reviews['date_column'].dt.month
    combined_reviews['day'] = combined_reviews['date_column'].dt.day

    # combined_reviews['date_column'] = combined_reviews['date_column'].dt.strftime('%Y-%m-%d')

    return combined_reviews