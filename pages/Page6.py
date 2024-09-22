import streamlit as st
from menu import menu_with_redirect
import pandas as pd
import plotly.express as px
from utils.func import hide_header_icons
from utils.load_data import get_data, get_reviews
from utils.text_editor import generate, get_color_template

menu_with_redirect()
hide_header_icons()

st.header(":blue[การวิเคราะห์ที่ 6]", divider=True)
st.subheader("ความสัมพันธ์ระหว่างเปอร์เซ็นต์ส่วนลดกับยอดขายเป็นอย่างไร")

data = get_data()
reviews = get_reviews()

def classify_sold_amount(sold_amount):
    if sold_amount > 1000:
        return 'High ยอดขายมากกว่า 1000'
    elif sold_amount >= 500 and sold_amount <= 1000:
        return 'Normal ยอดขาย 501-1000'
    else:
        return 'Low ยอดขายน้อยกว่า 500'
    
data['per_discount'] = data['per_discount'].str.replace('%', '').str.replace('-', '')
data['per_discount'] = pd.to_numeric(data['per_discount'], errors='coerce')
data['per_discount'] = data['per_discount'].fillna(0)
data['level'] = data['amount_sold_format'].apply(classify_sold_amount)
data = data[['marketplace', 'level', 'per_discount', 'amount_sold_format', 'discount_price_format']]
data = data[data['per_discount'] > 0]
data = data[data['amount_sold_format'] > 0]

# st.write("raw")
# st.write(data)
# Scatter Plot: Relationship between discount percentage and amount sold
color_map = {
    'shopee': 'coral',  
    'lazada': 'magenta', 
}

scatter_fig = px.scatter(data, 
                         x='per_discount', 
                         y='amount_sold_format', 
                         color='marketplace', 
                         symbol='marketplace', 
                         color_discrete_map=color_map,
                         labels={'per_discount': 'ส่วนลด (%)', 'amount_sold_format': 'ยอดขาย'},)

scatter_fig.update_layout(
    xaxis_title="ส่วนลด (%)",
    yaxis_title="ยอดขาย",
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

# Line Chart: Trend of amount sold with discount percentage
line_fig = px.line(data.groupby('per_discount')['amount_sold_format'].sum().reset_index(), 
                   x='per_discount', 
                   y='amount_sold_format', 
                   labels={'per_discount': 'Percentage Discount', 'amount_sold_format': 'Total Amount Sold'},
                   )

line_fig.update_layout(
    xaxis_title="ส่วนลด (%)",
    yaxis_title="ยอดขาย",
    legend_title_text="Marketplace",
    xaxis_tickfont_size=16,
    yaxis_tickfont_size=16,
    margin=dict(t=20),
    font=dict(
        size=18,
    ),
    legend=dict(
        y=0.9,
    )
)

# st.write("Scatter Plot: เพื่อดูการกระจายตัวของยอดขายตามเปอร์เซ็นต์ส่วนลด")
st.plotly_chart(scatter_fig, theme="streamlit")

# st.write("Line Chart: เพื่อดูแนวโน้มยอดขายตามเปอร์เซ็นต์ส่วนลด")
# st.plotly_chart(line_fig, theme="streamlit")

fig = px.scatter(data, x="per_discount", y="discount_price_format",
    	         size="amount_sold_format", color="marketplace",color_discrete_map=color_map,
                     hover_name="marketplace", size_max=60)
fig.update_layout(
    xaxis_title="ส่วนลด (%)",
    yaxis_title="ราคาขาย (บาท)",
    legend_title_text="Marketplace",
    xaxis_tickfont_size=16,
    yaxis_tickfont_size=16,
    margin=dict(t=20),
    font=dict(
        size=18,
    ),
    legend=dict(
        y=0.9,
    )
)

# st.write("Bubble charrt:  population of sold")
# st.plotly_chart(fig, theme="streamlit")

desc_msg = '''
    **คำอธิบาย:**\n
    การวิเคราะห์ความสัมพันธ์ระหว่างเปอร์เซ็นต์ส่วนลดและยอดขายแสดงให้เห็นว่า เมื่อมีการให้ส่วนลดในช่วง **10-20%** ยอดขายจะเพิ่มขึ้นมากที่สุด ซึ่งเป็นช่วงที่ลูกค้าตอบสนองดีที่สุด ส่วนลดที่มากกว่า 20% อาจไม่ช่วยเพิ่มยอดขายมากเท่าที่ควร เนื่องจากลูกค้าอาจสงสัยในคุณภาพของสินค้าที่มีการลดราคาสูงเกินไป ดังนั้น การกำหนดส่วนลดที่เหมาะสมมีผลต่อการกระตุ้นยอดขาย
'''
summary_msg = '''
    **สรุป:** ส่วนลดในช่วง **10-20%** ส่งผลดีที่สุดต่อยอดขายทั้งใน Shopee และ Lazada การให้ส่วนลดที่เกิน 20% อาจไม่ได้ส่งผลเพิ่มยอดขายอย่างมาก
'''
st.markdown(desc_msg)
st.markdown(summary_msg)
