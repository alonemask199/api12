from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_URL = "https://api.garibookadmin.com/api/v4/user/login"

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://garibook.com",
    "Referer": "https://garibook.com/",
    "User-Agent": "Mozilla/5.0"
}

@app.route("/send", methods=["GET"])
def send():
    phone = request.args.get("phone")

    if not phone:
        return jsonify({
            "success": False,
            "message": "phone parameter is required"
        }), 400

    # +880 ফরম্যাটে রূপান্তর
    if phone.startswith("0"):
        mobile = "+88" + phone
    elif phone.startswith("880"):
        mobile = "+" + phone
    elif phone.startswith("+880"):
        mobile = phone
    else:
        mobile = "+880" + phone

    payload = {
        "mobile": mobile,
        "recaptcha_token": "garibookcaptcha",
        "channel": "web"
    }

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=15
        )

        try:
            data = response.json()
        except:
            data = response.text

        return jsonify({
            "status_code": response.status_code,
            "response": data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
