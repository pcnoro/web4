from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import logging
from datetime import datetime
import random 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)


# Initialize Flask-Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # Rate limit by IP address
    default_limits=["2000 per day", "500 per hour"]  # Global rate limits
)

# Hardcoded user data (for demonstration purposes)
USER_DATA = {
    "username": "admin",
    "password": "supersecurepassword&&&",
    "security_questions": {
        "color": "cerulean",  # Correct answer for "What color is your mother like?"
        "pet": "doggggggggggdoggggggg=)=)",     # Correct answer for "What is the name of your first pet?"
        "city": "parisssssssssssssspiiiop=)=)"   # Correct answer for "In which city were you born?"
    }
}

# Flag to be displayed after successful password reset
FLAG = "SECOPS{200_fl4g_f0und_succ3ssfully}"
FAKE_FLAGS = [
    "CTF{404_flag_not_found}",
    "CTF{403_forbidden_flag}",
    "CTF{500_internal_server_error}",
    "CTF{302_flag_redirected}",
    "CTF{401_unauthorized_flag}",
    "CTF{418_im_a_teapot}",
    "CTF{503_service_unavailable}",
    "CTF{408_request_timeout}",
    "CTF{400_bad_request_flag}",
    "CTF{429_too_many_requests}"
]

# Logging setup
logging.basicConfig(filename="security_attempts.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Track incorrect attempts
incorrect_attempts = 0


# Home page with password generator
@app.route("/")
def home():
    return render_template("home.html")


# Serve robots.txt
@app.route("/robots.txt")
def robots():
    return render_template("robots.txt")

# Fake routes to mislead participants
@app.route("/admin")
def admin():
    return "Nothing to see here. <a href='/'>Go back</a>"

@app.route("/secret")
def secret():
    return "This is not the secret you're looking for. <a href='/'>Go back</a>"

@app.route("/flag")
def fake_flag():
    return "Nope, the flag isn't here. <a href='/'>Go back</a>"

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per minute") 
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USER_DATA["username"] and password == USER_DATA["password"]:
            return redirect(url_for("reset_password"))
        else:
            return render_template("index.html", error="Invalid credentials. Please try again.")
    return render_template("index.html")

@app.route("/reset", methods=["GET", "POST"])
def reset_password():
    global incorrect_attempts

    if request.method == "POST":
        question = request.form.get("question")
        answer = request.form.get("answer")

        # Log the attempt
        logging.info(f"Attempt by {request.remote_addr}: Question='{question}', Answer='{answer}'")

        if answer.lower() == USER_DATA["security_questions"].get(question):
            return render_template("index.html", flag=FLAG)
        else:
            incorrect_attempts += 1
            if incorrect_attempts >= 3:  # Display fake flag after 3 incorrect attempts
                fake_flag = random.choice(FAKE_FLAGS)
                return render_template("index.html", reset=True, reset_error="Incorrect answer. Here's your flag: " + fake_flag)
            else:
                return render_template("index.html", reset=True, reset_error="Incorrect answer. Please try again.")
    return render_template("index.html", reset=True)

# Error handler for rate limit exceeded
@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("index.html", error="Too many login attempts. Please try again in 1 minute."), 429

if __name__ == "__main__":
    app.run(debug=True)