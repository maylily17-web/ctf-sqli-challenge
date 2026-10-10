from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# Error-based SQLi 시 플래그 가로채기용 전역 변수
LAST_EXCEEDED_FLAG = None

def sqlite_raise_error(val):
    global LAST_EXCEEDED_FLAG
    LAST_EXCEEDED_FLAG = val  # SQL 구문 실행 중 전달받은 진짜 플래그 저장
    raise RuntimeError("TRIGGER_ERROR")

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.create_function("RAISE_ERROR", 1, sqlite_raise_error)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flags (
            flag TEXT
        )
    ''')
    
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM flags')
    
    # users 테이블 생성 (유저 정보)
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'super_secret_p@ss')")
    
    # 🚩 flags 테이블에 '진짜 플래그' 저장 (BUBU{} 형식 적용)
    cursor.execute("INSERT INTO flags (flag) VALUES ('BUBU{Real_Error_Based_SQLi_Master_2026!}')")
    
    conn.commit()
    conn.close()

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
    global LAST_EXCEEDED_FLAG
    LAST_EXCEEDED_FLAG = None  # 요청마다 초기화

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
            # 🎭 단순 로그인 성공 시 '가짜 플래그' 출력 (BUBU{} 형식 적용)
            fake_flag = "BUBU{Fake_Flag_Try_Error_Based_SQLi!}"
            return render_template_string(HTML_TEMPLATE, message=f"로그인 성공! Flag: {fake_flag}")
        else:
            return render_template_string(HTML_TEMPLATE, message="로그인 실패: 아이디나 비밀번호가 틀렸습니다.")

    except sqlite3.Error as e:
        conn.close()
        # 🚩 Error-based SQLi 우회 성공 시 진짜 플래그 출력
        if LAST_EXCEEDED_FLAG:
            err_msg = f"Flag Revealed -> {LAST_EXCEEDED_FLAG}"
        else:
            err_msg = str(e)
            
        return render_template_string(HTML_TEMPLATE, error=err_msg)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)