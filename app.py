# registratie website voor activiteiten
from cs50 import SQL # pip install cs50
from flask import Flask, render_template, request, redirect
app = Flask(__name__)

db = SQL("sqlite:///registratie.db")


ACTIVITIES = ["Londen-Eye", "Madame Tussauds", "Tower of London", "St. Paul's Cathedral", "British Museum", "Natural History Museum", "Science Museum", "Victoria and Albert Museum"]
TIME = ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]

@app.route("/")
def index():
    return render_template("index.html", activities=ACTIVITIES, time=TIME)


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    activities = request.form.getlist("activity")
    time = request.form.get("time")

    if not name or len(activities) != 1 or not time:
        return render_template("error.html")


    #Slaan nieuwe gebruikers op
    db.execute("INSERT INTO registrants (name, activity) VALUES (?, ?)", name, activities[0])

    #Bevestigen we registratie 
    return redirect("/registrants")
   
@app.route("/registrants")
def registrants():
    registrants = db.execute("SELECT * FROM registrants")
    return render_template("registrants.html", registrants = registrants)

@app.route("/deregister", methods=["POST"])
def deregister():
    id = request.form.get("id")
    if id:
        db.execute("DELETE FROM registrants WHERE id = ?", id)
    return redirect("/registrants")

if __name__ == "__main__":
    app.run(debug=True)