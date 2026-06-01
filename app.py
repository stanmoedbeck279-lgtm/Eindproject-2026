# registratie website voor activiteiten
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

db = SQL("sqlite:///registratie.db")

ACTIVITIES = ["Londen-Eye", "Madame Tussauds", "Tower of London", "St. Paul's Cathedral", "British Museum", "Natural History Museum", "Science Museum", "Victoria and Albert Museum"]
TIME = ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
AMOUNT = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Price per person (in GBP) for each activity
PRICES = {
    "Londen-Eye": 32,
    "Madame Tussauds": 35,
    "Tower of London": 30,
    "St. Paul's Cathedral": 22,
    "British Museum": 0,
    "Natural History Museum": 0,
    "Science Museum": 0,
    "Victoria and Albert Museum": 0,
}

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup_post():
    name = request.form.get("name")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if not name or not password:
        return render_template("signup.html", error="Please fill in all fields.")
    if password != confirmation:
        return render_template("signup.html", error="Passwords do not match.")

    existing = db.execute("SELECT * FROM registrants WHERE name = ?", name)
    if len(existing) > 0:
        return render_template("signup.html", error="Name already taken.")

    db.execute("INSERT INTO registrants (name, password) VALUES (?, ?)", name, password)
    return redirect("/login")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    name = request.form.get("name")
    password = request.form.get("password")

    rows = db.execute("SELECT * FROM registrants WHERE name = ? AND password = ?", name, password)

    if len(rows) != 1:
        return render_template("login.html", error="Invalid name or password")

    session["user"] = name
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/activities")
def activities():
    if not session.get("user"):
        return redirect("/login")
    return render_template("activities.html", activities=ACTIVITIES, time=TIME, amount=AMOUNT, prices=PRICES)

@app.route("/register", methods=["POST"])
def register():
    activities = request.form.getlist("activity")
    time = request.form.get("time")
    amount = request.form.get("amount")

    if not len(activities) == 1 or not time or not amount:
        return render_template("error.html")

    activity = activities[0]
    price_per_person = PRICES.get(activity, 0)
    total_price = price_per_person * int(amount)

    db.execute(
        "UPDATE registrants SET activity = ?, time = ?, amount = ?, total_price = ? WHERE name = ?",
        activity, time, amount, total_price, session.get("user")
    )
    return redirect("/registrants")

@app.route("/registrants")
def registrants():
    if not session.get("user"):
        return redirect("/login")
    registrants = db.execute("SELECT * FROM registrants WHERE name = ?", session["user"])
    return render_template("registrants.html", registrants=registrants)

@app.route("/deregister", methods=["POST"])
def deregister():
    if not session.get("user"):
        return redirect("/login")

    id = request.form.get("id")
    if id:
        record = db.execute("SELECT * FROM registrants WHERE id = ? AND name = ?", id, session["user"])
        if len(record) == 0:
            return "Forbidden", 403
        db.execute("DELETE FROM registrants WHERE id = ? AND name = ?", id, session["user"])

    return redirect("/registrants")

if __name__ == "__main__":
    app.run(debug=True)