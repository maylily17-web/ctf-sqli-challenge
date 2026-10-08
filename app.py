from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('ctf.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'SuperComplexPassword1234!@#$')")
    conn.commit()
    conn.close()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>CTF - Admin Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; text-align: center; }
        .login-box { display: inline-block; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }
        input { margin: 10px 0; padding: 8px; width: 80%; }
        button { padding: 8px 16px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Admin Login</h2>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password"><br>
            <button type="submit">Login</button>
        </form>
        {% if message %}
            <p style="color: red; font-weight: bold;">{{ message }}</p>
        {% endif %}
    </div>
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

    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

    try:
        conn = sqlite3.connect('ctf.db')
        cursor = conn.cursor()
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
            if user[1] == 'admin':
                return f"<h1>Welcome Admin!</h1><p>Flag: <code>FLAG{{SQLi_E4sy_Auth_Byp4ss_S2}}</code></p>"
            else:
                return "<h1>Login Success!</h1><p>But you are not admin.</p>"
        else:
            return render_template_string(HTML_TEMPLATE, message="Login Failed!")
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, message=f"SQL Error: {e}")

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)