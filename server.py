from flask import Flask
from flask_cors import CORS  # ✅ Import CORS

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS

@app.route('/')
def home():
    return 'Hello, world!'

if __name__ == "__main__":
    app.run()
