import streamlit as st
from menu import menu_with_redirect
import pandas as pd
from wordcloud import WordCloud
import plotly.express as px
import matplotlib.pyplot as plt
from collections import Counter
from pythainlp import word_tokenize
from pythainlp.corpus import thai_stopwords 
from pythainlp.util import normalize
from utils.load_data import get_data, get_reviews
from utils.text_editor import generate, get_color_template
from pythainlp import Tokenizer
import re

menu_with_redirect()

def preprocess_text(text):
    if not isinstance(text, str):
        text = ''
    tokens = word_tokenize(text, engine='newmm', keep_whitespace=False)
    stop_words = set(thai_stopwords())
    stop_words.add("คีโต")
    stop_words.add("เส้นคีโต")
    stop_words.add("ไร้ไขมัน")
    stop_words.add("อร่อยไม่คาว")
    stop_words.add("ไม่คาว")
    stop_words.add("ข้าว")
    stop_words.add("ข้าวไข่ขาว")
    stop_words.add("น้ำหนัก")
    stop_words.add("พร้อมทาน")
    stop_words.add("ส่งไว")
    stop_words.add("100 g")
    stop_words.add("100 g.")
    stop_words.add("100 กรัม")
    stop_words.add("รับประทาน")
    custom_tokenizer = Tokenizer(stop_words, keep_whitespace=False)

    # text = ' '.join(normalize(word) for word in custom_tokenizer.word_tokenize(text) if word not in stop_words)
    text = ' '.join(custom_tokenizer.word_tokenize(text))
    return text

def generate_wordcloud_and_count(text):
    # text = text.replace(" ", "")
    stop_words = set(thai_stopwords())
    stop_words.add("คีโต")
    stop_words.add("เส้นคีโต")
    stop_words.add("ไร้ไขมัน")
    stop_words.add("อร่อยไม่คาว")
    stop_words.add("ไม่คาว")
    stop_words.add("ข้าว")
    stop_words.add("ข้าวไข่ขาว")
    stop_words.add("น้ำหนัก")
    stop_words.add("ส่งไว")
    stop_words.add("พร้อมทาน")
    stop_words.add("100 g")
    stop_words.add("100 g.")
    stop_words.add("100 กรัม")
    stop_words.add("รับประทาน")
    custom_tokenizer = Tokenizer(stop_words, keep_whitespace=False)

    # words = word_tokenize(text, engine='newmm', keep_whitespace=False)
    words = custom_tokenizer.word_tokenize(text)
    wordcloud = WordCloud(
                      font_path='data/thsarabunnew-webfont.ttf', 
                      stopwords=thai_stopwords(),
                      relative_scaling=0.3,
                      min_font_size=1,
                      background_color = "white",
                      max_words=50, # จำนวนคำที่เราต้องการจะแสดงใน Word Cloud
                      colormap='plasma', 
                      scale=3,
                      font_step=4,
                      collocations=True,
                      regexp=r"[ก-๙a-zA-Z']+", # Regular expression to split the input text into token
                      margin=2
                      ).generate(' '.join(words))
    
    # Calculate word count
    word_count = Counter(words)
    most_common_words = word_count.most_common(20)
    return wordcloud, most_common_words

def classify_sold_amount(sold_amount):
    if sold_amount > 1000:
        return 'High ยอดขายมากกว่า 1000'
    elif sold_amount >= 500 and sold_amount <= 1000:
        return 'Normal ยอดขาย 501-1000'
    else:
        return 'Low ยอดขายน้อยกว่า 500'
    
def gen_word(data):
    text = ' '.join(data['product_name_clean'].dropna().astype(str))
    text = re.sub(r'[^ก-๙a-zA-Z\s]', '', text)
    wordcloud, word_count = generate_wordcloud_and_count(text)

    # Display word cloud using Plotly
    fig = px.imshow(wordcloud.to_array())
    fig.update_layout(xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False))
    st.plotly_chart(fig)

    # Display word count
    st.subheader("Word Count")
    word_count_df = pd.DataFrame(word_count, columns=['Word', 'Count']).sort_values(by='Count', ascending=False)
    st.dataframe(word_count_df, hide_index=True)

st.header(":blue[การวิเคราะห์ที่ 4]", divider=True)
st.subheader("คำใดควรเป็นชื่อผลิตภัณฑ์ที่โฆษณา")

data = get_data()
data = data[data['amount_sold_format'] > 0]
data['level'] = data['amount_sold_format'].apply(classify_sold_amount)

data = data[['marketplace', 'store', 'amount_sold_format', 'level', 'product_name']]
data['product_name_clean'] = data['product_name'].apply(preprocess_text)

data_display = data[['product_name', 'amount_sold_format']]
data_display.rename(columns={'product_name': 'ชื่อสินค้า', 'amount_sold_format': 'จำนวนที่ขายแล้ว'}, inplace=True)
data_display = data_display.sort_values(by='จำนวนที่ขายแล้ว', ascending=False)
st.dataframe(data_display, hide_index=True)
gen_word(data)

# data_filter_h = data[data['level'] == "High ยอดขายมากกว่า 1000"]
# st.write(data_filter_h)
# st.write("Word high sold")
# gen_word(data_filter_h)

# data_filter_n = data[data['level'] == "Normal ยอดขาย 501-1000"]
# st.write(data_filter_n)
# st.write("Word normal sold")
# gen_word(data_filter_n)

desc_msg = '''
    **คำอธิบาย:**\n
    การวิเคราะห์ชื่อสินค้าที่ขายดีบน Shopee และ Lazada พบว่าคำที่เกี่ยวข้องกับสุขภาพและคุณสมบัติพิเศษ เช่น "เส้นไข่ขาว", "ไรแป้ง", "Keto", และ "โปรตีน" มักปรากฏบ่อยในชื่อสินค้าที่มียอดขายสูง คำเหล่านี้แสดงถึงความเป็นเอกลักษณ์ของสินค้าที่มีคุณสมบัติพิเศษ เช่น สินค้าเพื่อสุขภาพหรือการรับประทานอาหารที่ปลอดภัย ดังนั้น การใช้คำเหล่านี้ในการตั้งชื่อผลิตภัณฑ์จะช่วยให้ชื่อสินค้าดูโดดเด่น ดึงดูดความสนใจจากกลุ่มลูกค้าที่มองหาสินค้าที่มีคุณสมบัติเฉพาะเจาะจง
'''
summary_msg = '''
    **สรุป:** คำที่เกี่ยวข้องกับสุขภาพ เช่น "เส้นไข่ขาว", "ไรแป้ง", "Keto", และ "โปรตีน" ควรใช้ในการตั้งชื่อผลิตภัณฑ์เพื่อดึงดูดความสนใจของลูกค้าที่ให้ความสำคัญกับสุขภาพและคุณภาพสินค้า
'''
st.markdown(desc_msg)
st.markdown(summary_msg)
