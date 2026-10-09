from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# DB 초기화 및 데이터 세팅
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 기존 유저 테이블 생성 및 데이터 삽입
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    
    # 🚩 [추가] 플래그 저장용 테이블 생성 및 가짜 플래그 삽입
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flags (
            flag TEXT
        )
    ''')
    
    # 기존 데이터 삭제 후 초기화
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM flags')
    
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'super_secret_p@ss')")
    # 🚩 가짜 플래그 설정 (원하는 문구로 바꾸셔도 됩니다)
    cursor.execute("INSERT INTO flags (flag) VALUES ('FLAG{Fake_Error_Based_SQLi_Success!}')")
    
    conn.commit()
    conn.close()

# HTML 템플릿 (로그인 폼 & 결과 출력)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SQLi Challenge - Error Based</title>
</head>
<body style="text-align: center; margin-top: 50px;">
    <h2>Login Page</h2>
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Username" required><br><br>
        <input type="password" name="password" placeholder="Password"><br><br>
        <button type="submit">Login</button>
    </form>

    {% if error %}
        <div style="color: red; margin-top: 20px;">
            <h3>⚠️ Database Error Occurred!</h3>
            <p><b>Error Message:</b> {{ error }}</p>
        </div>
    {% endif %}

    {% if message %}
        <div style="color: green; margin-top: 20px;">
            <h3>{{ message }}</h3>
        </div>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 취약한 SQL 쿼리문
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

    try:
        # 쿼리 실행
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
            return render_template_string(HTML_TEMPLATE, message="로그인 성공!")
        else:
            return render_template_string(HTML_TEMPLATE, message="로그인 실패: 아이디나 비밀번호가 틀렸습니다.")

    except sqlite3.Error as e:
        # 🚩 [핵심] SQL 에러가 발생하면 에러 내용을 그대로 화면에 전달합니다!
        conn.close()
        return render_template_string(HTML_TEMPLATE, error=str(e))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)