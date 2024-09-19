import streamlit as st
from menu import menu_with_redirect
import pandas as pd
import plotly.express as px
from utils.load_data import get_data, get_reviews
from utils.text_editor import generate

menu_with_redirect()

st.header(":blue[การวิเคราะห์ที่ 8]", divider=True)
st.subheader("คะแนนรีวิวเฉลี่ยที่สูงสุดอยู่ในช่วงราคาสินค้าใด")

data = get_data()
reviews = get_reviews()

color_map = {
    'shopee': 'coral',  
    'lazada': 'magenta', 
}

data = data.query("amount_sold_format>0")
data = data.query("discount_price_format>0")
data['star_review'] = pd.to_numeric(data['star_review'], errors='coerce')
data = data[data['star_review'] > 0]
data = data[['marketplace', 'store', 'star_review', 'discount_price_format']]

# bins = [0, 300, 600, 900, 1200]
# labels = ['0-300', '300-600', '600-900', '900-1200']
bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1101]
labels = ['0-100', '101-200', '201-300', '301-400', '401-500', '501-600', '601-700', '701-800', '801-900', '901-1000', '1001-1100']
data['price_range'] = pd.cut(data['discount_price_format'], bins=bins, labels=labels, right=False)

data_display = data[['marketplace', 'store', 'star_review', 'discount_price_format']]
data_display.rename(columns={'store': 'ชื่อร้านค้า', 'star_review': 'คะแนนรีวิว', 'discount_price_format': 'ราคาขาย'}, inplace=True)
st.dataframe(data_display, hide_index=True)

data_group = data[['marketplace', 'star_review', 'price_range']]
bubble_data = data.groupby(['marketplace','price_range', 'star_review']).size().reset_index(name='count')

# st.write(bubble_data)

fig_bubble = px.scatter(
    bubble_data,
    x='star_review',
    y='price_range',
    size='count',
    color='marketplace',
    labels={'star_review': 'Star Review', 'price_range': 'Price Range', 'marketplace': 'Marketplace'},
    size_max=60, color_discrete_map=color_map
)
fig_bubble.update_layout(
    xaxis_title="คะแนนรีวิว",
    yaxis_title="ช่วงราคาขาย",
    xaxis_tickfont_size=16,
    yaxis_tickfont_size=16,
    margin=dict(t=20),
    font=dict(
        size=18,
    )
)
st.plotly_chart(fig_bubble, theme="streamlit")

# Create a box plot
fig = px.box(data, x='price_range', y='star_review', points='all',
             color='marketplace', color_discrete_map=color_map,
             labels={'price_range': 'Price Range (Discounted)', 'star_review': 'Star Review'})

fig.update_layout(
    xaxis_title="ช่วงราคาสินค้า (Discounted Price)",
    yaxis_title="คะแนนรีวิว",
    xaxis_tickfont_size=16,
    yaxis_tickfont_size=16,
    margin=dict(t=20),
    font=dict(
        size=18,
    )
)

# Display the plot in Streamlit
# st.plotly_chart(fig, theme="streamlit")
