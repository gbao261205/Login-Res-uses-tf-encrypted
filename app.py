from flask import Flask, render_template, request, redirect, url_for
import json
import os
import tf_encrypted as tfe

app = Flask(__name__)

DATA_FILE = 'data.json'

def encrypt_text(text):
    # Mã hóa chuỗi bằng tf-encrypted (biểu diễn đơn giản dưới dạng số)
    return [ord(c) for c in text]

def decrypt_text(encoded_list):
    return ''.join([chr(i) for i in encoded_list])

def load_users():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_user(username, password):
    users = load_users()
    users.append({
        'username_enc': encrypt_text(username),
        'password_enc': encrypt_text(password)
    })
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f)

def check_login(username, password):
    users = load_users()
    username_enc = encrypt_text(username)
    password_enc = encrypt_text(password)
    for user in users:
        if user['username_enc'] == username_enc and user['password_enc'] == password_enc:
            return user
    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    save_user(username, password)
    return "Đăng ký thành công! <a href='/'>Quay lại trang chủ</a>"

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = check_login(username, password)
    if user:
        return render_template('success.html',
                               username_enc=user['username_enc'],
                               password_enc=user['password_enc'])
    else:
        return "Sai tài khoản hoặc mật khẩu. <a href='/'>Thử lại</a>"

if __name__ == '__main__':
    app.run(debug=True)
