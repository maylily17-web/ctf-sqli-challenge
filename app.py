from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# 커스텀 에러 함수: 인자로 들어온 문자열(플래그)을 에러 메시지에 포함시켜 강제로 예외 발생
def sqlite_raise_error(val):
    raise sqlite3.OperationalError(f"Flag Revealed: {val}")

# DB 연결 생성 시 커스텀 함수를 등록하는 헬퍼 함수
def get_db_connection():
    conn = sqlite3.connect('database.db')
    # SQLite에 'RAISE_ERROR'라는 이름의 커스텀 SQL 함수 등록 (인자 1개)
    conn.create_function("RAISE_ERROR", 1, sqlite_raise_error)
    return conn

# DB 초기화 및 데이터 세팅
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 유저 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    
    # 플래그 저장용 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flags (
            flag TEXT
        )
    ''')
    
    # 기존 데이터 초기화
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM flags')
    
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'super_secret_p@ss')")
    cursor.execute("INSERT INTO flags (flag) VALUES ('FLAG{Fake_Error_Based_SQLi_Success!}')")
    
    conn.commit()
    conn.close()

# HTML 템플릿
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

    conn = get_db_connection()
    cursor = conn.cursor()

    # 취약한 SQL 쿼리문
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

    try:
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
            return render_template_string(HTML_TEMPLATE, message="로그인 성공!")
        else:
            return render_template_string(HTML_TEMPLATE, message="로그인 실패: 아이디나 비밀번호가 틀렸습니다.")

    except sqlite3.Error as e:
        # SQL 실행 중 발생한 에러 메시지를 화면에 노출
        conn.close()
        return render_template_string(HTML_TEMPLATE, error=str(e))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)