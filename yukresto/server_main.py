from flask import Flask, jsonify, request
import requests
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")  # Izinkan semua asal untuk pengujian lokal

# Data server utama
stock_data = {
    "cabang_a": [
        {"name": "Pizza", "stock": 20, "price": 50000, "image": "pizza.jpg"},
        {"name": "Burger", "stock": 3, "price": 30000, "image": "burger.jpg"}
    ],
    "cabang_b": [
        {"name": "Pizza", "stock": 20, "price": 50000, "image": "pizza.jpg"},
        {"name": "Soda", "stock": 1, "price": 10000, "image": "soda.jpg"}
    ]
}
orders = {}
chat_messages = {"user1": []}
users = ["user1"]

@app.route("/health")
def health_check():
    print("Health check requested on server_main")
    return jsonify({"status": "alive"})

@app.route("/stock")
def get_stock():
    print("Stock requested on server_main:", stock_data)
    all_stock = stock_data["cabang_a"] + stock_data["cabang_b"]
    return jsonify(all_stock)

@app.route("/stock/<cabang>")
def get_stock_cabang(cabang):
    print(f"Stock for {cabang} requested on server_main")
    return jsonify(stock_data.get(cabang, []))

@app.route("/orders")
def get_orders():
    print("Orders requested on server_main:", orders)
    return jsonify(orders)

@app.route("/orders/<username>")
def get_user_orders(username):
    print(f"Orders for {username} requested on server_main")
    user_orders = {k: v for k, v in orders.items() if k.startswith(username)}
    return jsonify(user_orders)

@app.route("/place_order", methods=["POST"])
def place_order():
    data = request.json
    username = data["username"]
    menu = data["menu"]
    quantity = data["quantity"]
    order_id = f"{username}_{int(time.time())}"
    orders[order_id] = {"menu": menu, "quantity": quantity, "status": "Pesanan Akan Di-Proses", "cabang": "cabang_a"}
    for cabang in stock_data:
        for item in stock_data[cabang]:
            if item["name"] == menu:
                item["stock"] -= quantity if item["stock"] >= quantity else 0
    try:
        requests.post("http://localhost:5003/place_order", json=data)
    except:
        pass
    return jsonify({"status": "success", "order_id": order_id})

@app.route("/set_estimation", methods=["POST"])
def set_estimation():
    data = request.json
    order_id = data["order_id"]
    estimation = data["estimation"]
    if order_id in orders:
        orders[order_id]["status"] = f"Processing - Selesai pada: {estimation}"
    try:
        requests.post("http://localhost:5003/set_estimation", json=data)
    except:
        pass
    return jsonify({"status": "success"})

@app.route("/users")
def get_users():
    return jsonify(users)

@app.route("/messages/<username>")
def get_messages(username):
    print(f"Messages for {username} requested on server_main")
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
    try:
        requests.post("http://localhost:5003/send_message", json=data)
    except:
        pass
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)