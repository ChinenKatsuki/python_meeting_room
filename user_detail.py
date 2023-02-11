# import streamlit as st
# import requests

# def index(res):
#     st.json(res.json())
#     # st.json(res.json()['username'])
#     with st.form(key='user_detail'):
#         username = st.text_input('ユーザー名', res.json()['username'])
#         # # url_user_update = 'http://127.0.0.1:8000/user' + int(res.json()['user_id'])
#         # res = requests.post()