from flask import Flask, request, redirect, render_template
import json
import tf_encrypted as tfe
import numpy as np
import os
import tensorflow as tf

app = Flask(__name__)

DATA_FILE = 'data.json'


def encrypt_text(text):  

    text_bytes = [ord(c) for c in text]  

    config = tfe.LocalConfig([  
        ('alice', 'localhost:4000'),  
        ('bob', 'localhost:4001'),  
        ('crypto-producer', 'localhost:4002')  
    ])  

    tfe.set_config(config)  

    protocol = tfe.protocol.Pond()  
    tfe.set_protocol(protocol)  

    alice = tfe.get_config().get_player('alice')  

    session = tfe.Session()  

    with session:  
        private_input = tfe.define_private_input(alice, lambda: tf.constant(text_bytes, tf.int32))  
        result = session.run(private_input.reveal())  

    return result

def load_users():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_user(username, password):
    users = load_users()
    username_enc = encrypt_text(username).tolist()  # Mã hóa tên người dùng
    password_enc = encrypt_text(password).tolist()  # Mã hóa mật khẩu
    users.append({'username_enc': username_enc, 'password_enc': password_enc})
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f)

def check_login(username, password):
    users = load_users()
    username_enc = encrypt_text(username).tolist()
    password_enc = encrypt_text(password).tolist()
    for user in users:
        if 'username_enc' in user and 'password_enc' in user:
            if user['username_enc'] == username_enc and user['password_enc'] == password_enc:
                return user
    return None

@app.route('/')
def home():
    return render_template('login.html')  # mặc định đưa tới trang đăng nhập

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        save_user(username, password)
        return render_template('res_success.html', username_enc=encrypt_text(username).tolist(), password_enc=encrypt_text(password).tolist())
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = check_login(username, password)
        if user:
            return render_template('success.html', username_enc=user['username_enc'], password_enc=user['password_enc'])
        else:
            return render_template('not_success.html')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
