import streamlit as st

def authenticated_menu(initial_page=False):
    st.sidebar.page_link("pages/Home.py", label="🏚️ เส้นไข่ขาว")
    st.sidebar.page_link("pages/Page1.py", label="1️⃣ การวิเคราะห์ที่ 1")
    st.sidebar.page_link("pages/Page2.py", label="2️⃣ การวิเคราะห์ที่ 2")
    st.sidebar.page_link("pages/Page3.py", label="3️⃣ การวิเคราะห์ที่ 3")
    st.sidebar.page_link("pages/Page4.py", label="4️⃣ การวิเคราะห์ที่ 4")
    st.sidebar.page_link("pages/Page5.py", label="5️⃣ การวิเคราะห์ที่ 5")
    st.sidebar.page_link("pages/Page6.py", label="6️⃣ การวิเคราะห์ที่ 6")
    st.sidebar.page_link("pages/Page7.py", label="7️⃣ การวิเคราะห์ที่ 7")
    st.sidebar.page_link("pages/Page8.py", label="8️⃣ การวิเคราะห์ที่ 8")
    st.sidebar.markdown("---")
    st.session_state.authenticator.logout("Logout", "sidebar")


def unauthenticated_menu():
    st.sidebar.page_link("app.py", label="Log in")


def menu(initial_page):
    if "authentication_status" not in st.session_state or st.session_state.authentication_status is None:
        unauthenticated_menu()
        return
    authenticated_menu(initial_page)


def menu_with_redirect():
    if "authentication_status" not in st.session_state or st.session_state.authentication_status is None:
        st.switch_page("app.py")
    authenticated_menu()