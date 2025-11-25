from flask import Flask, send_file, jsonify

app = Flask(__name__, static_folder="../frontend", static_url_path="/static")

@app.route("/")
def index():
    return send_file("frontend/index.html")

@app.get("/api/hello")
def hello():
    return jsonify({"message": "Hello from backend"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
