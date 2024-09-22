import streamlit as st
from menu import menu_with_redirect
import pandas as pd
import plotly.express as px
from utils.func import hide_header_icons
from utils.load_data import get_data, get_reviews
from utils.text_editor import generate
import plotly.graph_objects as go

menu_with_redirect()
hide_header_icons()

def categorize_retention(count):
    if count == 2:
        return '2-times'
    elif count == 3:
        return '3-times'
    elif count == 4:
        return '4-times'
    elif count >= 5:
        return 'more 5-times'
    else:
        return '1-time'


st.header(":blue[การวิเคราะห์ที่ 3]", divider=True)
st.subheader("Retention Rate ของลูกค้าเป็นอย่างไร")
#shopId, review_date, cust_id

data = get_data()
reviews = get_reviews()

reviews = reviews[['marketplace', 'shopId', 'itemId', 'cust_id']]
# st.write("raw")
# st.dataframe(reviews, hide_index=True)

cust_counts = reviews.groupby(['marketplace', 'cust_id']).size().reset_index(name='count')
reviews_retention = pd.merge(reviews, cust_counts, on=['marketplace', 'cust_id'], how='left')
# st.dataframe(reviews_retention, hide_index=True)

distinct_cust_count = reviews.groupby('marketplace')['cust_id'].nunique()
distinct_cust_count_df = distinct_cust_count.reset_index()

cust_counts['retention_category'] = cust_counts['count'].apply(categorize_retention)
retention_summary = cust_counts.groupby(['marketplace', 'retention_category'])['cust_id'].count().unstack(fill_value=0)
retention_summary = pd.merge(distinct_cust_count_df, retention_summary, on=['marketplace'], how='left')
data_display = retention_summary[['marketplace', 'cust_id', '1-time', '2-times', '3-times', '4-times', 'more 5-times']]
data_display.rename(columns={'cust_id': 'จำนวนลูกค้า', '1-time': 'ซื้อครั้งเดียว', '2-times': 'ซื้อซ้ำ 2 ครั้ง', '3-times': 'ซื้อซ้ำ 3 ครั้ง', '4-times': 'ซื้อซ้ำ 4 ครั้ง', 'more 5-times': 'ซื้อซ้ำมากกว่า 5 ครั้ง'}, inplace=True)
st.dataframe(data_display, hide_index=True)

shopee_data = retention_summary[retention_summary['marketplace'] == "shopee"]
lazada_data = retention_summary[retention_summary['marketplace'] == "lazada"]

custom_colors = ['magenta', 'coral']

stages = ["ซื้อซ้ำ 2 ครั้ง", "ซื้อซ้ำ 3 ครั้ง", "ซื้อซ้ำ 4 ครั้ง", "ซื้อซ้ำมากกว่า 5 ครั้ง"]
shopee = pd.DataFrame({
    'number': [
        # int(shopee_data['cust_id']),
        int(shopee_data['2-times']),
        int(shopee_data['3-times']),
        int(shopee_data['4-times']),
        int(shopee_data['more 5-times'])
    ],
    'percent': [
        int(shopee_data['2-times']) / int(shopee_data['cust_id']) * 100,
        int(shopee_data['3-times']) / int(shopee_data['cust_id']) * 100,
        int(shopee_data['4-times']) / int(shopee_data['cust_id']) * 100,
        int(shopee_data['more 5-times']) / int(shopee_data['cust_id']) * 100
    ],
    'stage': stages
})

shopee['maketplace'] = 'Shopee'

lazada = pd.DataFrame({
    'number': [
        # int(lazada_data['cust_id']),
        int(lazada_data['2-times']),
        int(lazada_data['3-times']),
        int(lazada_data['4-times']),
        int(lazada_data['more 5-times'])
    ],
    'percent': [
        int(lazada_data['2-times']) / int(lazada_data['cust_id']) * 100,
        int(lazada_data['3-times']) / int(lazada_data['cust_id']) * 100,
        int(lazada_data['4-times']) / int(lazada_data['cust_id']) * 100,
        int(lazada_data['more 5-times']) / int(lazada_data['cust_id']) * 100
    ],
    'stage': stages
})
lazada['maketplace'] = 'Lazada'

retention_all = pd.concat([lazada, shopee], axis=0)
retention_funnel = px.funnel(retention_all, x='number', y='stage', color='maketplace',
                            # text='percent',
                            color_discrete_sequence=custom_colors)
retention_funnel.update_traces(
    textposition='auto', 
    selector=dict(marker_color=custom_colors[0]) 
)

retention_funnel.update_traces(
    textposition='auto', 
    selector=dict(marker_color=custom_colors[1]) 
)

retention_funnel.update_layout(
    xaxis_title="",
    yaxis_title="",
    xaxis_tickfont_size=16,
    yaxis_tickfont_size=16,
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

st.plotly_chart(retention_funnel)
desc_msg = '''
    **คำอธิบาย:**\n
    Retention Rate เป็นตัวชี้วัดความสามารถในการรักษาฐานลูกค้าให้กลับมาซื้อซ้ำ หลังจากการวิเคราะห์พบว่า **Lazada** มี Retention Rate สูงกว่าที่ **37.66%** ในขณะที่ Shopee มีเพียง **14.72%** ซึ่งแสดงให้เห็นว่า Lazada มีลูกค้าที่มีความภักดีมากกว่า กลับมาซื้อสินค้าบนแพลตฟอร์มบ่อยครั้ง อาจเป็นเพราะการให้บริการที่ดี หรือการมีส่วนลดและสิทธิพิเศษที่น่าสนใจ ซึ่งเป็นสิ่งที่ช่วยสร้างความผูกพันระหว่างแพลตฟอร์มและลูกค้า
'''
summary_msg = '''
    **สรุป:** Lazada มี Retention Rate สูงกว่า Shopee แสดงถึงความสามารถในการรักษาฐานลูกค้าให้กลับมาซื้อซ้ำได้ดีกว่า
'''
st.markdown(desc_msg)
st.markdown(summary_msg)
