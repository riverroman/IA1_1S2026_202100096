from flask import Flask, jsonify

app = Flask(__name__)

@app.get('/')
def home():
    return "<p>Welcome to the Flask backend!</p>"
    
if __name__ == '__main__':
    app.run(debug=True)