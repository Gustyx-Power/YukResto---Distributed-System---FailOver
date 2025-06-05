from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def index():
    print("Worker 2: Rendering index page")
    return render_template("worker2/index.html")

@app.route("/set_estimation", methods=["POST"])
def set_estimation():
    port = request.form.get("port", "5000")
    order_id = request.form["order_id"]
    estimation = request.form["estimation"]
    print(f"Worker 2: Setting estimation for order {order_id} on port {port}")
    try:
        response = requests.post(f"http://localhost:{port}/set_estimation", json={
            "order_id": order_id, "estimation": estimation
        })
        print(f"Worker 2: Set estimation response: {response.json()}")
        return jsonify(response.json())
    except Exception as e:
        print(f"Worker 2: Error setting estimation: {str(e)}")
        return jsonify({"error": "Server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)