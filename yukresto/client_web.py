from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/")
def login():
    return render_template("client/login.html")

@app.route("/login", methods=["POST"])
def do_login():
    username = request.form["username"]
    password = request.form["password"]
    if username == "user1" and password == "pass123":
        session["username"] = username
        return redirect(url_for("order"))
    return redirect(url_for("login"))

@app.route("/order")
def order():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    return render_template("client/order.html", username=username)

@app.route("/chat")
def chat():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    return render_template("client/chat.html", username=username)

@app.route("/register")
def register():
    if "username" in session:
        return redirect(url_for("order"))
    return render_template("client/register.html")

@app.route("/register", methods=["POST"])
def do_register():
    username = request.form["username"]
    password = request.form["password"]
    # Simpan ke database atau validasi sederhana (contoh)
    if username and password:
        session["username"] = username
        return redirect(url_for("order"))
    return redirect(url_for("register"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/place_order", methods=["POST"])
def place_order():
    port = request.form.get("port", "5000")
    username = session["username"]
    menu = request.form["menu"]
    quantity = int(request.form["quantity"])
    try:
        response = requests.post(f"http://localhost:{port}/place_order", json={
            "username": username, "menu": menu, "quantity": quantity
        })
        return jsonify(response.json())
    except:
        return jsonify({"error": "Server error"}), 500

@app.route("/send_message", methods=["POST"])
def send_message():
    port = request.form.get("port", "5000")
    username = session["username"]
    message = request.form["message"]
    try:
        response = requests.post(f"http://localhost:{port}/send_message", json={
            "username": username, "message": message, "sender": "You"
        })
        return jsonify(response.json())
    except:
        return jsonify({"error": "Server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)