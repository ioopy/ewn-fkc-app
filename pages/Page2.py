import streamlit as st
from menu import menu_with_redirect
import pandas as pd
import plotly.express as px
from utils.load_data import get_data, get_reviews
from utils.text_editor import generate
import plotly.graph_objects as go


menu_with_redirect()
st.header(":blue[การวิเคราะห์ที่ 2]", divider=True)
st.subheader("แพลตฟอร์มใดที่มีการรีวิวเชิงบวกมากที่สุดสำหรับสินค้าที่ได้รับการลดราคา")

data = get_data()
reviews = get_reviews()

data['per_discount'] = data['per_discount'].str.replace('%', '').str.replace('-', '')
data['per_discount'] = pd.to_numeric(data['per_discount'], errors='coerce')
data_filter = data[data['per_discount'] > 0]

transformed_reviews = reviews.groupby(['marketplace','shopId', 'itemId'])['rating_star'].apply(lambda x: ','.join(map(str, x))).reset_index()
transformed_reviews = transformed_reviews.rename(columns={'rating_star': 'review_list'})

data_format = pd.merge(data_filter, transformed_reviews, on=['marketplace','shopId', 'itemId'])
data_format = data_format[['marketplace', 'store', 'per_discount', 'review_list']]

data_format['review_list'] = data_format['review_list'].str.split(',')

# Use explode to create a new row for each review
df_exploded = data_format.explode('review_list').reset_index(drop=True)

# Convert the 'Review_List' column back to integers (optional)
df_exploded['review_list'] = df_exploded['review_list'].astype(int)

# Rename the column to 'Review_Rate' (optional for clarity)
df_exploded = df_exploded.rename(columns={'review_list': 'rating_star'})


def classify_review(rate):
    if rate in [1, 2]:
        return 'แย่ (Bad)'
    elif rate == 3:
        return 'เฉย ๆ (Neutral)'
    else:
        return 'ดี (Good)'
    
df_exploded['reviews_category'] = df_exploded['rating_star'].apply(classify_review)
data_display = df_exploded[['marketplace', 'store', 'per_discount', 'rating_star']]
data_display = data_display.sort_values(by=['marketplace', 'per_discount'], ascending=True)
data_display.rename(columns={'store': 'ชื่อร้านค้า', 'per_discount': 'ส่วนลด (%)', 'rating_star': 'คะแนน'}, inplace=True)
st.dataframe(data_display, hide_index=True)

color_map = {
    'shopee': 'coral',  
    'lazada': 'magenta', 
}

bins = [0, 11, 21, 31, 41, 51]
labels = ['0-10', '11-20', '21-30', '31-40', '41-50']


df_exploded['discount_range'] = pd.cut(df_exploded['per_discount'], bins=bins, labels=labels, right=False)
grouped_data = df_exploded.groupby(['discount_range', 'reviews_category', 'marketplace']).size().reset_index(name='review_count')
# st.dataframe(grouped_data, hide_index=True)
reviews_category_order = ['ดี (Good)', 'เฉย ๆ (Neutral)', 'แย่ (Bad)']  
fig = px.scatter(grouped_data, x="discount_range", y="reviews_category",
    	        size="review_count", color="marketplace",color_discrete_map=color_map,
                    hover_name="marketplace", size_max=60, category_orders={"reviews_category": reviews_category_order},
                    hover_data={
                    'review_count': ':.0f'
                })

fig.update_layout(
    xaxis_title="ส่วนลด (%)",
    yaxis_title="",
    xaxis_tickfont_size=16,
    yaxis_tickfont_size=16,
    # margin=dict(t=35),
    font=dict(
        size=18,
    ),
    legend=dict(
        orientation="h",        # Set the legend orientation to horizontal
        yanchor="bottom",       # Anchor the legend at the bottom
        y=1,                    # Position the legend above the graph
        xanchor="center",       # Center the legend horizontally
        x=0.5                   # Set the legend to the center of the x-axis
    ),
    legend_title_text=''
)

# grouped_data_good = grouped_data[grouped_data['reviews_category'] == "ดี (Good)"]
# # st.dataframe(grouped_data_good, hide_index=True)
# line_fig = px.line(grouped_data_good, 
#                    x='discount_range', 
#                    y='review_count', color='marketplace'
#                    )

st.plotly_chart(fig)
desc_msg = '''
    **คำอธิบาย:**\n
    การวิเคราะห์รีวิวของสินค้าที่ได้รับการลดราคาพบว่า **Lazada** มีการรีวิวดี (4-5 ดาว) มากที่สุดที่ **663 รีวิว** เทียบกับ **Shopee** ที่มีเพียง **186 รีวิว** สิ่งนี้แสดงให้เห็นว่า Lazada สามารถทำให้ลูกค้าพึงพอใจได้มากกว่าเมื่อมีการลดราคา โดยการรีวิวเชิงบวกนั้นแสดงถึงความพึงพอใจของลูกค้าที่ได้รับจากประสบการณ์การซื้อสินค้าในช่วงลดราคา นอกจากนี้ รีวิวที่เป็นกลางหรือแย่ (1-2 ดาว) ของทั้งสองแพลตฟอร์มยังมีอยู่ในจำนวนเท่ากัน แต่ความแตกต่างของรีวิวเชิงบวกนั้นชัดเจนกว่า
'''
summary_msg = '''
    **สรุป:** Lazada มีการรีวิวเชิงบวกมากที่สุดสำหรับสินค้าที่ได้รับการลดราคา โดยลูกค้าแสดงถึงความพึงพอใจมากกว่าเมื่อเปรียบเทียบกับ Shopee
'''
st.markdown(desc_msg)
st.markdown(summary_msg)