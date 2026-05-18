from flask import Flask, request, jsonify, send_from_directory
from chatbot import get_traffic_data, ask_chatbot

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Pitanje je prazno"}), 400

    kamere = get_traffic_data()
    odgovor = ask_chatbot(question, kamere)

    return jsonify({"answer": odgovor})

if __name__ == "__main__":
    app.run(debug=True, port=5000)