import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from menu import menu_with_redirect
from utils.text_editor import generate
from utils.load_data import get_data, get_reviews

menu_with_redirect()
st.header(":blue[การวิเคราะห์ที่ 1]", divider=True)
st.subheader("ระหว่าง _Shopee_ และ _Lazada_ แพลตฟอร์มไหนเหมาะสมกับการเปิดร้านค้าออนไลน์มากกว่ากัน")

data = get_data()
reviews = get_reviews()
# st.dataframe(reviews)

data_2023 = reviews[reviews['year'] == 2023]
grouped_data = data_2023.groupby(['shopId', 'marketplace', 'itemId']).size().reset_index(name='2023_sold')

data_2024_q1 = reviews[(reviews['year'] == 2024) & (reviews['month'] <= 3)]
grouped_data_q1 = data_2024_q1.groupby(['shopId', 'marketplace', 'itemId']).size().reset_index(name='2024_q1_sold')

data_2024_q2 = reviews[(reviews['year'] == 2024) & (reviews['month'] >= 4) & (reviews['month'] <= 6)]
grouped_data_q2 = data_2024_q2.groupby(['shopId', 'marketplace', 'itemId']).size().reset_index(name='2024_q2_sold')
# st.dataframe(grouped_data)

# data_format = pd.merge(data, grouped_data, grouped_data_q1, grouped_data_q2, on=['marketplace', 'shopId'])
data_format = pd.merge(data, grouped_data, on=['marketplace', 'shopId', 'itemId'], how='left')
data_format = pd.merge(data_format, grouped_data_q1, on=['marketplace', 'shopId', 'itemId'], how='left')
data_format = pd.merge(data_format, grouped_data_q2, on=['marketplace', 'shopId', 'itemId'], how='left')
data_format[['2023_sold', '2024_q1_sold', '2024_q2_sold']] = data_format[['2023_sold', '2024_q1_sold', '2024_q2_sold']].fillna(0)

data_format['total_2023'] = data_format['2023_sold'] * data_format['discount_price_format']
data_format['total_q1'] = data_format['2024_q1_sold'] * data_format['discount_price_format']
data_format['total_q2'] = data_format['2024_q2_sold'] * data_format['discount_price_format']

sumary_data = data_format[['marketplace', 'store', 'total_value']]

sumary_data = sumary_data.rename(columns={'itemid': 'รหัสสินค้า', 'store': 'ชื่อร้านค้า', 'amount_sold_format': 'ยอดขายทั้งหมด', 'discount_price_format': 'ราคาขาย', 'total_value': 'ยอดขายรวม', 'total_2023': 'ยอดขายปี 2023', 'total_q1': 'ยอดขายปี 2024 Q1', 'total_q2': 'ยอดขายปี 2024 Q2'})
# st.dataframe(sumary_data)

st.markdown("**จำนวนร้านค้า**")
store_count = sumary_data.groupby('marketplace')['ชื่อร้านค้า'].nunique().rename('จำนวน')
store_count = store_count.reset_index(name="จำนวน")
store_count['Total'] = (store_count['จำนวน']/store_count['จำนวน'].sum()) * 100
st.dataframe(store_count, column_config={
        "Total": st.column_config.ProgressColumn(
            "สัดส่วน", 
            format="%.2f",
            min_value=0,
            max_value=100,
        ),
    },
    hide_index=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Lazada**")
    lazada_data = sumary_data[sumary_data['marketplace'] == "lazada"]
    lazada_data = lazada_data.groupby(['marketplace', 'ชื่อร้านค้า']).sum()
    lazada_data = lazada_data.sort_values(by='ยอดขายรวม', ascending=False)
    st.dataframe(lazada_data, column_config={
        "marketplace": st.column_config.Column(
            "marketplace",
            width="small",
        ),
        "ชื่อร้านค้า": st.column_config.Column(
            "ชื่อร้านค้า",
            width="small",
        )
        
    }, use_container_width=True)

with col2:
    st.markdown("**Shopee**")
    shopee_data = sumary_data[sumary_data['marketplace'] == "shopee"]
    shopee_data = shopee_data.groupby(['marketplace', 'ชื่อร้านค้า']).sum()
    shopee_data = shopee_data.sort_values(by='ยอดขายรวม', ascending=False)
    st.dataframe(shopee_data, column_config={
        "marketplace": st.column_config.Column(
            "marketplace",
            width="small",
        )
        
    })
# st.markdown('##')
color_map = {
    'shopee': 'coral',  
    'lazada': 'magenta', 
}
colors = [color_map[platform] for platform in color_map]


def get_total_sold():
    total_value_by_marketplace = sumary_data.groupby('marketplace')['ยอดขายรวม'].sum().reset_index()
    platforms = total_value_by_marketplace['marketplace'].tolist()
    total_values = total_value_by_marketplace['ยอดขายรวม'].tolist()
    fig = go.Figure(data=[go.Bar(
        x=total_values, 
        y=platforms,
        text=total_values,
        texttemplate='%{text:.2s}', 
        textposition='auto',
        marker_color=colors,
        orientation='h',
        hovertemplate='Marketplace: %{y}<br>ยอดขายรวม: %{x:,.2f} บาท'
    )])
    
    fig.update_layout(
        xaxis_title="ยอดขาย",
        xaxis_tickfont_size=16,
        yaxis_tickfont_size=16,
        margin=dict(t=20),
        font=dict(
            size=18,
        )
    )
    st.plotly_chart(fig, theme="streamlit")

def get_total_sold_2023():
    total_value_by_marketplace = data_format.groupby('marketplace')['total_2023'].sum().reset_index()
    total_value_by_marketplace = total_value_by_marketplace.sort_values(by='total_2023', ascending=True)
    # st.write(total_value_by_marketplace)
    platforms = total_value_by_marketplace['marketplace'].tolist()
    total_values = total_value_by_marketplace['total_2023'].tolist()
    fig = go.Figure(data=[go.Bar(
        x=total_values, 
        y=platforms,
        text=total_values,
        texttemplate='%{text:.2s}', 
        textposition='auto',
        marker_color=colors,
        orientation='h'
    )])
    
    fig.update_layout(
        xaxis_title="ยอดขาย",
        xaxis_tickfont_size=16,
        yaxis_tickfont_size=16,
        margin=dict(t=20),
        font=dict(
            size=18,
        )
    )
    st.plotly_chart(fig, theme="streamlit")

def get_total_sold_q1():
    total_value_by_marketplace = data_format.groupby('marketplace')['total_q1'].sum().reset_index()
    total_value_by_marketplace = total_value_by_marketplace.sort_values(by='total_q1', ascending=True)
    st.write(total_value_by_marketplace)
    platforms = total_value_by_marketplace['marketplace'].tolist()
    total_values = total_value_by_marketplace['total_q1'].tolist()
    fig = go.Figure(data=[go.Bar(
        x=total_values, 
        y=platforms,
        text=total_values,
        texttemplate='%{text:.2s}', 
        textposition='auto',
        marker_color=colors,
        orientation='h'
    )])
    
    fig.update_layout(
        xaxis_title="ยอดขาย",
        xaxis_tickfont_size=16,
        yaxis_tickfont_size=16,
        font=dict(
            size=18,
        )
    )
    st.plotly_chart(fig, theme="streamlit")

def get_total_sold_q2():
    total_value_by_marketplace = data_format.groupby('marketplace')['total_q2'].sum().reset_index()
    total_value_by_marketplace = total_value_by_marketplace.sort_values(by='total_q2', ascending=True)
    st.write(total_value_by_marketplace)
    platforms = total_value_by_marketplace['marketplace'].tolist()
    total_values = total_value_by_marketplace['total_q2'].tolist()
    fig = go.Figure(data=[go.Bar(
        x=total_values, 
        y=platforms,
        text=total_values,
        texttemplate='%{text:.2s}', 
        textposition='auto',
        marker_color=colors,
        orientation='h'
    )])
    
    fig.update_layout(
        xaxis_title="ยอดขาย",
        xaxis_tickfont_size=16,
        yaxis_tickfont_size=16,
        font=dict(
            size=18,
        )
    )
    st.plotly_chart(fig, theme="streamlit")

def get_total_sold_q1_q2():
    total_value_q1 = data_format.groupby('marketplace')['total_q1'].sum().reset_index()
    total_value_q2 = data_format.groupby('marketplace')['total_q2'].sum().reset_index()
    merged_data = pd.merge(total_value_q1, total_value_q2, on='marketplace')
    merged_data = merged_data.sort_values(by='total_q1', ascending=True)
    # st.write(merged_data)
    platforms = merged_data['marketplace'].tolist()
    total_values_q1 = merged_data['total_q1'].tolist()
    total_values_q2 = merged_data['total_q2'].tolist()
    fig = go.Figure(data=[
        go.Bar(
            x=total_values_q1, 
            y=platforms,
            text=total_values_q1,
            texttemplate='%{text:.2s}', 
            textposition='auto',
            name='ยอดขาย 2024 Q1',
            marker_color='cyan',
            orientation='h'
        ),
        go.Bar(
            x=total_values_q2, 
            y=platforms,
            text=total_values_q2,
            texttemplate='%{text:.2s}', 
            textposition='auto',
            name='ยอดขาย 2024 Q2',
            marker_color='darkcyan',
            orientation='h'
        )
    ])
    
    # Update layout for the chart
    fig.update_layout(
        barmode='group',  # Group bars together
        xaxis_title="ยอดขาย",
        xaxis_tickfont_size=16,
        yaxis_tickfont_size=16,
        margin=dict(t=20),
        font=dict(
            size=18,
        )
    )
    
    # Display the chart in Streamlit
    st.plotly_chart(fig, theme="streamlit")

# Plot graph bar
get_total_sold()
