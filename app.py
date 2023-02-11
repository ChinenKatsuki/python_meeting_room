import streamlit as st
import requests
import json
import datetime
import pandas as pd
import time


page = st.sidebar.selectbox('choose your page', ['users', 'rooms', 'bookings', 'user_detail', 'room_delete'])

if page == 'users':

    st.title('ユーザー登録画面')
    with st.form(key='user'):
        username: str = st.text_input('ユーザー名', max_chars=12)
        data = {
            'username': username
        }
        submit_button = st.form_submit_button(label='リクエスト送信')

        if submit_button:
            url = 'http://127.0.0.1:8000/users'
            res = requests.post(
                url,
                data=json.dumps(data)
            )
            if res.status_code == 200:
                st.success('登録成功')
    
elif page =='rooms':
    st.title('APIテスト画面（会議室）')

    with st.form(key='rooms'):
        room_name: str = st.text_input('会議室名', max_chars=12)
        capacity: int = st.number_input('定員', step=1)
        data = {
            'room_name': room_name,
            'capacity': capacity
        }
        submit_button = st.form_submit_button(label='リクエスト送信')

        if submit_button:
            url = 'http://127.0.0.1:8000/rooms'
            res = requests.post(
                url,
                data=json.dumps(data)
            )
            if res.status_code ==200:
                st.success('登録成功')
                st.json(res.json())
elif page == 'bookings':
    st.title('会議室予約画面')
    # ユーザー一覧取得
    url_users = 'http://127.0.0.1:8000/users'
    res = requests.get(url_users)
    users = res.json()
    users_name = {}
    for user in users:
        users_name[user['username']] = user['user_id']
    
    # 会議室一覧
    url_rooms = 'http://127.0.0.1:8000/rooms'
    res = requests.get(url_rooms)
    rooms = res.json()
    rooms_name = {}
    for room in rooms:
        rooms_name[room['room_name']] = {
            'capacity': room['capacity'],
            'room_id': room['room_id']
        }
    
    st.write('### 会議室一覧')
    df_rooms = pd.DataFrame(rooms)
    df_rooms.columns = ['会議室名', '定員', '会議室ID']
    st.table(df_rooms)
    
    url_bookings = 'http://127.0.0.1:8000/bookings'
    res = requests.get(url_bookings)
    bookings = res.json()
    df_bookings = pd.DataFrame(bookings)

    users_id = {}
    for user in users:
        users_id[user['user_id']] = user['username']

    rooms_id = {}
    for room in rooms:
        rooms_id[room['room_id']] = {
            'room_name': room['room_name'],
            'capacity': room['capacity']
        }

    # IDを各値に変更
    to_username = lambda x: users_id[x]
    to_room_name = lambda x: rooms_id[x]['room_name']
    to_datetime = lambda x: datetime.datetime.fromisoformat(x).strftime('%Y/%m/%d %H:%M')

    # 特定の列に適用
    df_bookings['user_id'] = df_bookings['user_id'].map(to_username)
    df_bookings['room_id'] = df_bookings['room_id'].map(to_room_name)
    df_bookings['start_datetime'] = df_bookings['start_datetime'].map(to_datetime)
    df_bookings['end_datetime'] = df_bookings['end_datetime'].map(to_datetime)

    df_bookings = df_bookings.rename(columns={
        'user_id': '予約者名',
        'room_id': '会議室名',
        'booked_num': '予約人数',
        'start_datetime': '開始時刻',
        'end_datetime': '終了時刻',
        'booking_id': '予約番号'
    })

    st.write('### 会議室予約一覧')
    st.table(df_bookings)


    with st.form(key='booking'):
        username: str = st.selectbox('予約者名', users_name.keys())
        room_name: str = st.selectbox('会議室名', rooms_name.keys())
        booked_num: int = st.number_input('予約人数', step=1, min_value=1)
        date = st.date_input('日付を入力:', min_value=datetime.date.today())
        start_time = st.time_input('開始時刻:', value=datetime.time(hour=9, minute=00))
        end_time = st.time_input('終了時刻:', value=datetime.time(hour=20, minute=00))

        submit_button = st.form_submit_button(label='予約登録')

        if submit_button:
            user_id: int = users_name[username]
            room_id: int = rooms_name[room_name]['room_id']
            capacity: int = rooms_name[room_name]['capacity']
            data = {
                'user_id': user_id,
                'room_id': room_id,
                'booked_num': booked_num,
                'start_datetime': datetime.datetime(
                    year=date.year,
                    month=date.month,
                    day=date.day,
                    hour=start_time.hour,
                    minute=start_time.minute
                ).isoformat(),
                'end_datetime': datetime.datetime(
                    year=date.year,
                    month=date.month,
                    day=date.day,
                    hour=end_time.hour,
                    minute=end_time.minute
                ).isoformat()
            }
            # 定員より多い予約人数の場合
            if booked_num > capacity:
                st.error(f'{room_name}の定員は、{capacity}名です。{capacity}名以下の予約人数のみ受け付けてます')
            # 開始時刻 >= 終了時刻
            elif start_time >= end_time:
                st.error('開始時刻が終了時刻を超えています。')
            elif start_time < datetime.time(9, 00) or end_time > datetime.time(20, 00):
                st.error('利用時間は9:00~20:00になります。')
            else:
                url = 'http://127.0.0.1:8000/bookings'
                res = requests.post(
                    url,
                    data=json.dumps(data)
                )
                # st.write(res.json())
                if res.status_code == 200:
                    st.success('予約完了')
                elif res.status_code == 404 and res.json()['detail'] == 'Already booked':
                    st.error('指定の時間はすでに予約済みです')

elif page == 'user_detail':
    # ユーザー一覧取得
    url_users = 'http://127.0.0.1:8000/users'
    res = requests.get(url_users)
    users = res.json()
    users_name = {}
    for user in users:
        users_name[user['username']] = user['user_id']

    users_id = {}
    for user in users:
        users_id[user['user_id']] = user['username']

    username: str = st.selectbox('ユーザー名', users_name.keys())
    if username:
        user_id = users_name[username]
        url = 'http://127.0.0.1:8000/user/' + str(user_id)
        res = requests.get(url)
        if res.status_code == 200:
            with st.form(key='user_detail'):
                username = st.text_input('ユーザー名', res.json()['username'])
                url_user_update = 'http://127.0.0.1:8000/user/' + str(res.json()['user_id'])

                submit = st.form_submit_button(label='ユーザー名変更')
                if submit:
                    data = {
                        'username': username
                    }
                    res = requests.post(
                        url_user_update,
                        data=json.dumps(data)
                    )
                    if res.status_code == 200:
                        st.success('変更成功')
elif page == 'room_delete':
    st.title('会議室削除')
    url = 'http://127.0.0.1:8000/rooms'
    res = requests.get(url)
    rooms = res.json()
    df_rooms = pd.DataFrame(rooms)
    df_rooms.columns = ['会議室名', '定員', '会議室ID']
    st.table(df_rooms)

    rooms_name = {}
    for room in rooms:
        rooms_name[room['room_name']]  = room['room_id']
    rooms_id = {}
    for room in rooms:
        rooms_id[room['room_id']] = room['room_name']
    
    with st.form(key='room_delete'):
        room_name = st.selectbox('会議室名', rooms_name.keys())
        submit_button = st.form_submit_button(label='会議室削除')
        
        if submit_button:
            to_room_id = rooms_name[room_name]
            room_delete_url = 'http://127.0.0.1:8000/room/delete/' + str(to_room_id)
            res = requests.get(room_delete_url)
            if res.status_code == 200:
                st.json(res.json())
                st.success('削除成功')
           
            