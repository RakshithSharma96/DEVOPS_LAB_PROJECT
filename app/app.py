import re

from flask import Flask, render_template, request

app = Flask(__name__)
# Demonstration credentials only; this is not a production authentication system.
app.config.update(DEMO_EMAIL="admin@example.com", DEMO_PASSWORD="admin123")


def valid_email(value):
    # Basic format validation for this lab, not email address verification.
    return re.fullmatch(r"[^\s@]+@[^\s@.]+(?:\.[^\s@.]+)+", value) is not None


@app.route("/", methods=["GET", "POST"])
def login():
    message = ""
    success = False
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password.strip():
            message = "Email and password are required."
        elif not valid_email(email):
            message = "Enter a valid email address."
        elif (email == app.config["DEMO_EMAIL"]
              and password == app.config["DEMO_PASSWORD"]):
            message = "Login successful!"
            success = True
        else:
            message = "Invalid email or password."
    return render_template("login.html", message=message, success=success,
                           values=request.form)


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    success = False
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        phone = request.form.get("phone", "").strip()
        if not all([name, email, password.strip(), confirm.strip(), phone]):
            message = "All registration fields are required."
        elif not valid_email(email):
            message = "Enter a valid email address."
        elif len(password) < 8:
            message = "Password must contain at least 8 characters."
        elif password != confirm:
            message = "Passwords do not match."
        elif not re.fullmatch(r"[0-9]{10}", phone):
            message = "Phone number must contain exactly 10 digits."
        elif request.form.get("terms") != "on":
            message = "You must accept the terms and conditions."
        else:
            message = "Registration successful (demo only). No account was saved."
            success = True
    return render_template("register.html", message=message, success=success,
                           values=request.form)


@app.get("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
