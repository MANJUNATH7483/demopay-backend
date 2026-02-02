import json
import os
import time
# Added 'send_from_directory' to serve HTML files
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Configure Flask to serve files from the current folder ('.')
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

DB_FILE = 'database.json'

# --- HELPER FUNCTIONS ---
def get_db():
    if not os.path.exists(DB_FILE):
        initial_data = {
            "user": {
                "name": "User Name",
                "mobile": "9876543210",
                "pin": "1234",
                "walletBalance": 50000,
                "walletBalance_HDFC": 50000
            },
            "transactions": []
        }
        with open(DB_FILE, 'w') as f:
            json.dump(initial_data, f, indent=2)
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# --- SERVE HTML FILES (Frontend) ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# --- API ROUTES (Backend) ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    db = get_db()
    if data.get('pin') == db['user']['pin']:
        return jsonify({"success": True, "message": "Login Successful"})
    else:
        return jsonify({"success": False, "message": "Invalid PIN"}), 401

@app.route('/api/user', methods=['GET'])
def get_user():
    db = get_db()
    return jsonify(db['user'])

@app.route('/api/add-money', methods=['POST'])
def add_money():
    data = request.json
    db = get_db()
    bank = data.get('bank')
    if bank == 'HDFC':
        db['user']['walletBalance_HDFC'] = 50000
    else:
        db['user']['walletBalance'] = 50000
    save_db(db)
    return jsonify({"success": True, "message": "Money Added", "newBalance": 50000})

@app.route('/api/pay', methods=['POST'])
def pay():
    data = request.json
    amount = float(data.get('amount'))
    bank = data.get('bank')
    recipient = data.get('recipient')
    description = data.get('description', 'Money Transfer')
    db = get_db()
    
    if bank == 'HDFC':
        current_bal = db['user']['walletBalance_HDFC']
    else:
        current_bal = db['user']['walletBalance']
        
    if amount > current_bal:
        return jsonify({"success": False, "message": "Insufficient Balance"})
    
    if bank == 'HDFC':
        db['user']['walletBalance_HDFC'] -= amount
    else:
        db['user']['walletBalance'] -= amount
        
    new_txn = {
        "id": f"T{int(time.time())}",
        "name": recipient,
        "amount": amount,
        "bank": bank,
        "time": time.strftime("%d/%m/%Y, %I:%M %p"),
        "status": "Paid",
        "description": description
    }
    db['transactions'].insert(0, new_txn)
    save_db(db)
    return jsonify({"success": True, "newBalance": current_bal - amount})

@app.route('/api/history', methods=['GET'])
def get_history():
    db = get_db()
    return jsonify(db['transactions'])

if __name__ == '__main__':
    # host='0.0.0.0' makes it accessible to the whole Wi-Fi network
    print("DemoPay Server Running! Access via http://YOUR-PC-IP:3000")
    app.run(host='0.0.0.0', port=3000, debug=True)