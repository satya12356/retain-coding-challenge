from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB = "users.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn
@app.route('/')
def health():
    return jsonify({"status": "OK"}), 200

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db()
    users = conn.execute("SELECT id, name, email FROM users").fetchall()
    return jsonify([dict(u) for u in users]), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT id, name, email FROM users WHERE id=?", (user_id,)).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(dict(user)), 200

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name, email, password = data['name'], data['email'], data['password']
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        return jsonify({"message": "User created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name, email = data.get('name'), data.get('email')
    conn = get_db()
    conn.execute("UPDATE users SET name=?, email=? WHERE id=?", (name, email, user_id))
    conn.commit()
    return jsonify({"message": "User updated"}), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    return jsonify({"message": "User deleted"}), 200

@app.route('/search', methods=['GET'])
def search_user():
    name = request.args.get('name')
    conn = get_db()
    users = conn.execute("SELECT id, name, email FROM users WHERE name LIKE ?", ('%' + name + '%',)).fetchall()
    return jsonify([dict(u) for u in users]), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email, password = data['email'], data['password']
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()
    if user:
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(debug=True)
