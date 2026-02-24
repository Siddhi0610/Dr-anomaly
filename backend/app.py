from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import sqlite3
import pandas as pd
from flask import request
from anomaly import detect_anomalies



app = Flask(__name__)
CORS(app)

DB_NAME = "users.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn










@app.route("/")
def home():
    return "Backend alive"







@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    username = data.get("username")
    password = generate_password_hash(data.get("password"))


    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409



@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401








@app.route("/upload", methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files allowed"}), 400

    try:
        df = pd.read_csv(file)
    except Exception as e:
        return jsonify({"error": f"CSV read failed: {str(e)}"}), 400

    # Explicitly expect time-series structure
    # Rule: first column = time, second column = value
    if df.shape[1] < 2:
        return jsonify({"error": "CSV must have at least 2 columns"}), 400

    time_col = df.columns[0]
    value_col = df.columns[1]

    try:
        values = df[value_col].astype(float).tolist()
    except Exception:
        return jsonify({"error": "Value column must be numeric"}), 400

    anomalies = detect_anomalies(values)

    return jsonify({
    "message": "CSV processed successfully",
    "time_column": time_col,
    "value_column": value_col,
    "timestamps": df[time_col].tolist(),
    "values": values,
    "anomalies": anomalies
})










if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
