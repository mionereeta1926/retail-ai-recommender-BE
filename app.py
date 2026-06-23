from flask import Flask
from flask_cors import CORS

from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.items import items_bp
from routes.checkout import checkout_bp

app = Flask(__name__)

app.secret_key = "mysecretkey"

CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(items_bp)
app.register_blueprint(checkout_bp)


@app.route("/")
def home():

    return {
        "success": True,
        "message": "Invoice API Running"
    }


if __name__ == "__main__":
    app.run(debug=True)