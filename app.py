# registratie website voor activiteiten
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

db = SQL("sqlite:///registratie.db")

ACTIVITIES = ["Londen-Eye", "Madame Tussauds", "Tower of London", "St. Paul's Cathedral", "British Museum", "Natural History Museum", "Science Museum", "Victoria & Albert Museum"]
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
    "Victoria & Albert Museum": 0,
}

DETAILS = {
    "Londen-Eye": {
        "description": "Europe's tallest cantilevered observation wheel offering breathtaking panoramic views of London.",
        "image": "London_Eye.jpg"
    },
    "Madame Tussauds": {
        "description": "World-famous wax museum featuring incredibly lifelike figures of celebrities and historical icons.",
        "image": "MadameTussauds.jpg"
    },
    "Tower of London": {
        "description": "A historic castle and fortress on the River Thames, home to the Crown Jewels since 1303.",
        "image": "Tower_of_London.jpg"
    },
    "St. Paul's Cathedral": {
        "description": "Sir Christopher Wren's baroque masterpiece with a magnificent dome dominating London's skyline.",
        "image": "St_Paul's_Cathedral.jpg"
    },
    "British Museum": {
        "description": "One of the world's greatest museums, housing over 8 million works spanning 2 million years of history. Free entry.",
        "image": "British_Museum.jpg"
    },
    "Natural History Museum": {
        "description": "A breathtaking Victorian building home to 80 million specimens, including dinosaur skeletons. Free entry.",
        "image": "Natural_History_Museum.jpg"
    },
    "Science Museum": {
        "description": "An inspiring museum tracing humanity's greatest achievements in science and technology. Free entry.",
        "image": "Science_Museum.jpg"
    },
    "Victoria & Albert Museum": {
        "description": "The world's leading museum of art and design, with 2.3 million objects across 5,000 years. Free entry.",
        "image": "Victoria&Albert_Museum.jpg"
    },
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
    return render_template("activities.html", activities=ACTIVITIES, time=TIME, amount=AMOUNT, prices=PRICES, details=DETAILS)

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