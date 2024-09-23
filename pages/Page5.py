import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from menu import menu_with_redirect
from utils.func import break_page, hide_header_icons
from utils.text_editor import generate
from utils.load_data import get_data, get_reviews
import plotly.express as px
import numpy as np

menu_with_redirect()
hide_header_icons()

st.header(":blue[การวิเคราะห์ที่ 5]", divider=True)
st.subheader("ตั้งราคาขายเท่าไหร่ดี")

data = get_data()
reviews = get_reviews()

data = data.query("amount_sold_format > 0")

def classify_sold_amount(sold_amount):
    if sold_amount > 1000:
        return 'High ยอดขายมากกว่า 1000'
    elif sold_amount >= 500 and sold_amount <= 1000:
        return 'Normal ยอดขาย 501-1000'
    else:
        return 'Low ยอดขายน้อยกว่า 500'
    
data['level'] = data['amount_sold_format'].apply(classify_sold_amount)
level_order = ["High ยอดขายมากกว่า 1000", "Normal ยอดขาย 501-1000", "Low ยอดขายน้อยกว่า 500"]

data = data[['marketplace', 'level', 'amount_sold_format', 'discount_price_format']]
data = data.query("discount_price_format>0")
level_order = ["Low ยอดขายน้อยกว่า 500", "Normal ยอดขาย 501-1000", "High ยอดขายมากกว่า 1000"]
data['level'] = pd.Categorical(data['level'], categories=level_order, ordered=True)

data_display = data[['marketplace', 'amount_sold_format', 'discount_price_format']]
data_display.rename(columns={'amount_sold_format': 'จำนวนที่ขายแล้ว', 'discount_price_format': 'ราคาขาย'}, inplace=True)
st.dataframe(data_display, hide_index=True)

# def calculate_statistics(group):
#     return pd.Series({
#         'max': group['discount_price_format'].max(),
#         'min': group['discount_price_format'].min(),
#         'median': group['discount_price_format'].median(),
#         'mode': group['discount_price_format'].mode().iloc[0] if not group['discount_price_format'].mode().empty else np.nan,
#         'low': np.percentile(group['discount_price_format'], 25)  # Calculating the 25th percentile as "low"
#     })
# statistics = data.groupby(['marketplace', 'level']).apply(calculate_statistics).reset_index()
# statistics['level'] = pd.Categorical(statistics['level'], categories=level_order, ordered=True)
# st.write(statistics)

descriptive_stats = data.groupby(['marketplace', 'level'])['discount_price_format'].describe().reset_index()
# descriptive_stats['skewness'] = data.groupby(['marketplace', 'level'])['discount_price_format'].skew().values
# descriptive_stats['kurtosis'] = data.groupby(['marketplace', 'level'])['discount_price_format'].apply(pd.Series.kurt).values
descriptive_stats['level'] = pd.Categorical(descriptive_stats['level'], categories=level_order, ordered=True)
data_display2 = descriptive_stats[['marketplace', 'count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
st.dataframe(data_display2, hide_index=True)

data_sorted = descriptive_stats.sort_values(by='mean')
data_sorted['CDF'] = np.arange(1, len(data_sorted) + 1) / len(data_sorted)



fig = px.box(
    data, 
    x="marketplace",    # Separate box plots by marketplace
    y="discount_price_format",          # Show price distribution
    color="level",      # Color by level (assuming 'level' is a column in your data)
    labels={"discount_price_format": "ราคาขาย", "marketplace": "Marketplace", "level": "Level"},
    category_orders={"level": level_order}
)

# for _, row in descriptive_stats.iterrows():
#     fig.add_hline(
#         y=row['mean'],
#         line_dash="dash", 
#         line_color="green", 
#         annotation_text=f"Mean: {row['mean']}",
#         annotation_position="top right",
#         annotation=dict(font_size=10),
#         row="all", 
#         col="all"
#     )


# Update layout for better visualization
fig.update_layout(
    boxmode='group',   # Group the boxes by marketplace
    xaxis_title="",
    yaxis_title="ราคาขาย",
    showlegend=True,
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

break_page()
st.plotly_chart(fig)

desc_msg = '''
    **คำอธิบาย:**\n
    Shopee และ Lazada มีราคาขายเฉลี่ยที่แตกต่างกันอย่างชัดเจน โดย **Shopee** มีราคาขายเฉลี่ยที่ **239.73 บาท** ซึ่งสูงกว่า **Lazada** ที่มีราคาขายเฉลี่ยเพียง **161.68 บาท** การตั้งราคาสำหรับสินค้าในแต่ละแพลตฟอร์มจึงควรพิจารณาตามพฤติกรรมการซื้อของลูกค้าในแพลตฟอร์มนั้นๆ หากกลุ่มลูกค้ามีกำลังซื้อสูง สามารถตั้งราคาสูงกว่าได้ Shopee อาจเป็นแพลตฟอร์มที่เหมาะสม ขณะที่สินค้าราคาย่อมเยาเหมาะกับ Lazada มากกว่า
'''
summary_msg = '''
    **สรุป:** การตั้งราคาควรพิจารณาตามกลุ่มเป้าหมาย Shopee เหมาะกับสินค้าที่สามารถตั้งราคาสูงกว่า ขณะที่ Lazada เหมาะสำหรับสินค้าราคาย่อมเยาที่ต้องการเจาะตลาดลูกค้าราคาถูก
'''
st.markdown(desc_msg)
st.markdown(summary_msg)

