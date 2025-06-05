from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def index():
    print("Worker 3: Rendering index page")
    return render_template("worker3/index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    port = request.form.get("port", "5000")
    username = request.form["username"]
    message = request.form["message"]
    print(f"Worker 3: Sending message for {username} on port {port}")
    try:
        response = requests.post(f"http://localhost:{port}/send_message", json={
            "username": username, "message": message, "sender": "CS"
        })
        print(f"Worker 3: Send message response: {response.json()}")
        return jsonify(response.json())
    except Exception as e:
        print(f"Worker 3: Error sending message: {str(e)}")
        return jsonify({"error": "Server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007, debug=True)