from flask import Flask, jsonify, request
import threading
import time
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")  # Izinkan semua asal untuk pengujian lokal

# Data server cadangan
stock_data = {}
orders = {}
chat_messages = {}

def sync_with_main_server():
    while True:
        try:
            # Sinkronkan stok
            response = requests.get("http://localhost:5000/stock")
            if response.status_code == 200:
                all_stock = response.json()
                global stock_data
                stock_data["cabang_a"] = [item for item in all_stock if item in requests.get("http://localhost:5000/stock/cabang_a").json()]
                stock_data["cabang_b"] = [item for item in all_stock if item in requests.get("http://localhost:5000/stock/cabang_b").json()]
            
            # Sinkronkan pesanan
            response = requests.get("http://localhost:5000/orders")
            if response.status_code == 200:
                global orders
                orders.update(response.json())
            
            # Sinkronkan pesan chat
            for user in requests.get("http://localhost:5000/users").json():
                response = requests.get(f"http://localhost:5000/messages/{user}")
                if response.status_code == 200:
                    global chat_messages
                    chat_messages[user] = response.json()
        except:
            pass
        time.sleep(3)  # Sinkronkan setiap 3 detik

threading.Thread(target=sync_with_main_server, daemon=True).start()

@app.route("/health")
def health_check():
    print("Health check requested on server_backup")
    return jsonify({"status": "alive"})

@app.route("/stock")
def get_stock():
    print("Stock requested on server_backup:", stock_data)
    all_stock = stock_data.get("cabang_a", []) + stock_data.get("cabang_b", [])
    return jsonify(all_stock)

@app.route("/stock/<cabang>")
def get_stock_cabang(cabang):
    print(f"Stock for {cabang} requested on server_backup")
    return jsonify(stock_data.get(cabang, []))

@app.route("/orders")
def get_orders():
    print("Orders requested on server_backup:", orders)
    return jsonify(orders)

@app.route("/orders/<username>")
def get_user_orders(username):
    print(f"Orders for {username} requested on server_backup")
    user_orders = {k: v for k, v in orders.items() if k.startswith(username)}
    return jsonify(user_orders)

@app.route("/place_order", methods=["POST"])
def place_order():
    data = request.json
    username = data["username"]
    menu = data["menu"]
    quantity = data["quantity"]
    order_id = f"{username}_{int(time.time())}"
    orders[order_id] = {"menu": menu, "quantity": quantity, "status": "Pending", "cabang": "cabang_a"}
    for cabang in stock_data:
        for item in stock_data[cabang]:
            if item["name"] == menu:
                item["stock"] -= quantity if item["stock"] >= quantity else 0
    return jsonify({"status": "success"})

@app.route("/set_estimation", methods=["POST"])
def set_estimation():
    data = request.json
    order_id = data["order_id"]
    estimation = data["estimation"]
    if order_id in orders:
        orders[order_id]["status"] = f"Processing - Selesai pada: {estimation}"
    return jsonify({"status": "success"})

@app.route("/users")
def get_users():
    return jsonify(["user1"])  # Sementara hardcode

@app.route("/messages/<username>")
def get_messages(username):
    print(f"Messages for {username} requested on server_backup")
    return jsonify(chat_messages.get(username, []))

@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    username = data["username"]
    message = data["message"]
    sender = data["sender"]
    if username not in chat_messages:
        chat_messages[username] = []
    chat_messages[username].append({"sender": sender, "text": message, "time": time.strftime("%H:%M")})
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)