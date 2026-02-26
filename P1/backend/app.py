from flask import Flask
from controllers.patient_controller import patient_bp
from controllers.admin_controller import admin_bp

app = Flask(__name__)

app.register_blueprint(patient_bp, url_prefix="/api/patient")
app.register_blueprint(admin_bp, url_prefix="/api/admin")

if __name__ == "__main__":
    app.run(debug=True)