import streamlit as st
from menu import menu_with_redirect
import pandas as pd
import plotly.express as px
from utils.func import hide_header_icons
from utils.load_data import get_data, get_reviews
from utils.text_editor import generate, get_color_template

menu_with_redirect()
hide_header_icons()

thai_months = {
    1: "มกราคม",
    2: "กุมภาพันธ์",
    3: "มีนาคม",
    4: "เมษายน",
    5: "พฤษภาคม",
    6: "มิถุนายน",
    7: "กรกฎาคม",
    8: "สิงหาคม",
    9: "กันยายน",
    10: "ตุลาคม",
    11: "พฤศจิกายน",
    12: "ธันวาคม"
}
thai_month_order = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

legend_mapping = {
    'is_double_day': 'Double Day',
    'is_pre_double_day': 'Pre Double Day',
    'is_normal_day': 'Normal Day'
}

st.header(":blue[การวิเคราะห์ที่ 7]", divider=True) 
st.subheader("ปริมาณการขายเพิ่มขึ้นในช่วง Double Day หรือไม่")

reviews = get_reviews()
# reviews = reviews[reviews['year'] == '2023']

def find_double_day(row):
    # Extract year, month, and day
    year = row['date_column'].year
    month = row['date_column'].month
    
    # Create the double day (YYYY-MM-Month)
    double_day = pd.Timestamp(year=year, month=month, day=month)
    
    return double_day


def process_reviews(reviews, marketplace_name, thai_months, thai_month_order):
    column_selected = ['marketplace', 'date_column', 'year', 'month', 'day']
    
    # Filter by marketplace and select relevant columns
    marketplace_reviews = reviews[reviews['marketplace'] == marketplace_name]
    marketplace_reviews = marketplace_reviews[column_selected]
    marketplace_reviews['double_day'] = marketplace_reviews.apply(find_double_day, axis=1)
    marketplace_reviews['month_start'] = marketplace_reviews['date_column'] - pd.offsets.MonthBegin(1)
    marketplace_reviews['month_end'] = marketplace_reviews['date_column'] + pd.offsets.MonthEnd(0)

    # Calculate double day and other related fields
    marketplace_reviews['double_day1'] = marketplace_reviews['double_day'] + pd.Timedelta(days=3)
    marketplace_reviews['double_day2'] = marketplace_reviews['double_day'] + pd.Timedelta(days=5)

    # marketplace_reviews['pre_double_day'] = marketplace_reviews['double_day2'] + pd.Timedelta(days=1)

    marketplace_reviews['is_double_day'] = (marketplace_reviews['date_column'] >= marketplace_reviews['double_day1']) & (marketplace_reviews['date_column'] <= marketplace_reviews['double_day2'])
    marketplace_reviews['is_pre_double_day'] = (marketplace_reviews['date_column'] >= marketplace_reviews['month_start']) & (marketplace_reviews['date_column'] < marketplace_reviews['double_day1'])
    marketplace_reviews['is_normal_day'] = (marketplace_reviews['date_column'] > marketplace_reviews['double_day2']) & (marketplace_reviews['date_column'] <= marketplace_reviews['month_end'])
    
    # Map Thai month names
    marketplace_reviews['thai_month'] = marketplace_reviews['month'].map(thai_months)
    
    # Summarize the data by Thai month
    reviews_summary = marketplace_reviews.groupby('thai_month')[['is_double_day', 'is_pre_double_day', 'is_normal_day']].sum()
    reviews_summary.index = pd.Categorical(reviews_summary.index, categories=thai_month_order, ordered=True)
    reviews_summary = reviews_summary.sort_index()
    
    # Calculate percentages
    reviews_clean = reviews_summary.reset_index()
    total_days = (reviews_clean['is_double_day'] + reviews_clean['is_pre_double_day'] + reviews_clean['is_normal_day'])
    reviews_clean['is_double_day_pct'] = (reviews_clean['is_double_day'] / total_days * 100).round(2)
    reviews_clean['is_pre_double_day_pct'] = (reviews_clean['is_pre_double_day'] / total_days * 100).round(2)
    reviews_clean['is_normal_day_pct'] = (reviews_clean['is_normal_day'] / total_days * 100).round(2)
    
    # Display the result
    # st.write(marketplace_name)
    # st.dataframe(marketplace_reviews, hide_index=True)
    
    return reviews_clean

def plot_graph_stack(data):
    day_type_mapping = {
        'is_double_day_pct': 'Double Day',
        'is_pre_double_day_pct': 'Pre Double Day',
        'is_normal_day_pct': 'Normal Day'
    }

    df_melted = data.melt(id_vars='index', 
                    value_vars=['is_double_day_pct', 'is_pre_double_day_pct', 'is_normal_day_pct'],
                    var_name='day_type', 
                    value_name='percentage',)
    df_melted['day_type'] = df_melted['day_type'].map(day_type_mapping)

    
    fig = px.bar(df_melted, 
                x='index', 
                y='percentage', 
                color='day_type', 
                labels={'percentage':'Percent', 'day_type':'ประเภทวัน'},
                text='percentage', color_discrete_map=legend_mapping )
    
    fig.update_layout(barmode='stack',xaxis_title="",
        yaxis_title="",
        xaxis_tickfont_size=16,
        yaxis_tickfont_size=16,
        font=dict(
            size=18,
        ), width=2000,
        legend=dict(
            orientation="h",        # Set the legend orientation to horizontal
            yanchor="bottom",       # Anchor the legend at the bottom
            y=1,                    # Position the legend above the graph
            xanchor="center",       # Center the legend horizontally
            x=0.5                   # Set the legend to the center of the x-axis
        ),
        legend_title_text=''
    )
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='auto',
                      hovertemplate=(
            "เดือน: %{y}<br>" +
            "Percentage: %{x:.2f}%"  
        )
    )
    return fig


reviews = reviews[(reviews['year'] < 2024) & (reviews['year'] > 2021)]
shopee_clean = process_reviews(reviews, "shopee", thai_months, thai_month_order)
lazada_clean = process_reviews(reviews, "lazada", thai_months, thai_month_order)

st.markdown("**shopee**")
st.plotly_chart(plot_graph_stack(shopee_clean))

st.markdown("**lazada**")
st.plotly_chart(plot_graph_stack(lazada_clean))

# reviews_2023 = reviews[(reviews['year'] == 2023)]
# shopee_clean = process_reviews(reviews_2023, "shopee", thai_months, thai_month_order)
# lazada_clean = process_reviews(reviews_2023, "lazada", thai_months, thai_month_order)

# st.markdown("**Shopee 2023**")
# st.plotly_chart(plot_graph_stack(shopee_clean))

# st.markdown("**Lazada 2023**")
# st.plotly_chart(plot_graph_stack(lazada_clean))

desc_msg = '''
    **คำอธิบาย:**\n
    จากกราฟสองอันที่แสดงสัดส่วนของยอดขายในช่วง **Double Day, Pre Double Day**, และ **Normal Day** แบ่งตามเดือน:

    **การวิเคราะห์กราฟแรก:**

    **1. Normal Day:**
    - ยังคงมีสัดส่วนยอดขายที่สูงที่สุดในเดือนส่วนใหญ่ เช่น มีนาคม (**72.22%**), เมษายน (**75.00%**), และธันวาคม (**60.00%**)
    - การที่ยอดขายในวันปกติสูงกว่าช่วง Double Day แสดงให้เห็นว่าลูกค้าอาจยังคงมีกิจกรรมการซื้อขายประจำในช่วงเวลาที่ไม่ใช่ช่วงแคมเปญ

    **2. Pre Double Day:**
    - มีความโดดเด่นในเดือนตุลาคม (**48.84%**) และพฤศจิกายน (**44.83%**)

    **3. Double Day:**
    - สัดส่วนยอดขายในช่วง Double Day มีความน่าสนใจในบางเดือน เช่น มิถุนายน (**26.32%**) และพฤศจิกายน (**3.45%**)
    - Double Day เองอาจมีสัดส่วนที่ต่ำกว่าวันปกติ แต่ก็ยังคงมีบทบาทในการกระตุ้นยอดขายในบางช่วง

    **การวิเคราะห์กราฟสอง:**

    **1. Normal Day:**
    - เป็นช่วงที่มียอดขายสูงสุดในหลายเดือน เช่น มกราคม (**88.89%**), กุมภาพันธ์ (**81.82%**), มีนาคม (**90.00%**), และธันวาคม (**80.00%**)
    - แสดงให้เห็นว่าในวันปกติ ยอดขายมีสัดส่วนสูงที่สุดในทุกเดือน ซึ่งอาจเป็นเพราะลูกค้ามีการซื้อขายที่สม่ำเสมอในช่วงที่ไม่เกี่ยวข้องกับการจัดแคมเปญพิเศษ

    **2. Pre Double Day:**
    - มีสัดส่วนยอดขายสูงขึ้นในบางเดือน เช่น พฤษภาคม (**31.25%**), สิงหาคม (**41.94%**), และตุลาคม (**25.37%**)

    **3. Double Day:**
    - มีสัดส่วนยอดขายสูงสุดในพฤษภาคม (**31.25%**) และตุลาคม (**28.36%**)
    - Double Day เองแสดงให้เห็นถึงการกระตุ้นยอดขายในเดือนพฤษภาคมและตุลาคม ซึ่งเป็นช่วงแคมเปญใหญ่เช่น 5/5 และ 10/10
'''
summary_msg = '''
    **สรุปจากกราฟทั้งสอง:** 
    - **Normal Day** ยังคงเป็นช่วงที่มียอดขายสูงสุดในทุกเดือน โดยมีสัดส่วนมากกว่า 50% แสดงให้เห็นว่าลูกค้ามีกิจกรรมการซื้อขายสม่ำเสมอตลอดทั้งปี
    - **Pre Double Day** มียอดขายสูงขึ้นในเดือนตุลาคมและพฤศจิกายน ซึ่งเป็นช่วงก่อนแคมเปญ Double Day ขนาดใหญ่ (10/10 และ 11/11) แสดงว่าลูกค้าเตรียมตัวซื้อสินค้าล่วงหน้าก่อนถึงวันจริง
    - **Double Day** แม้จะมีสัดส่วนยอดขายต่ำกว่า แต่ก็ยังคงมียอดขายที่สำคัญในบางเดือน เช่น พฤษภาคม, มิถุนายน, และตุลาคม
'''
st.markdown(desc_msg)
st.markdown(summary_msg)