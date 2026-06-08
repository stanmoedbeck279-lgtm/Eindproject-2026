# registratie website voor activiteiten
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session

# Maak een Flask webapp aan en stel een geheime sleutel in voor sessiebeheer.
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


# Verbind met de lokale SQLite database.
db = SQL("sqlite:///registratie.db")

# Beschikbare activiteiten voor registratie.
ACTIVITIES = [
    "Londen-Eye",
    "Madame Tussauds",
    "Tower of London",
    "St. Paul's Cathedral",
    "British Museum",
    "Natural History Museum",
    "Science Museum",
    "Victoria & Albert Museum"
]

# Beschikbare tijdslots voor de activiteiten.
TIME = ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]

# Mogelijke aantallen personen voor registratie.
AMOUNT = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Prijs per persoon voor elke activiteit.
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

# Extra details zoals beschrijving en afbeelding voor elke activiteit.
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

# Route om het signup-formulier te tonen.
@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup_post():
    # Haal de formulierwaarden op.
    name = request.form.get("name")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # Controleer of de verplichte velden zijn ingevuld.
    if not name or not password:
        return render_template("signup.html", error="Please fill in all fields.")

    # Controleer of het wachtwoord en de bevestiging overeenkomen.
    if password != confirmation:
        return render_template("signup.html", error="Passwords do not match.")

    # Controleer of de naam al in gebruik is.
    existing = db.execute("SELECT * FROM registrants WHERE name = ?", name)
    if len(existing) > 0:
        return render_template("signup.html", error="Name already taken.")

    # Voeg de nieuwe gebruiker toe aan de database.
    db.execute("INSERT INTO registrants (name, password) VALUES (?, ?)", name, password)

    # Redirect naar de loginpagina na succesvolle registratie.
    return redirect("/login")

# Toon het loginformulier wanneer de gebruiker naar /login gaat.
@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    # Haal de inloggegevens op uit het formulier.
    name = request.form.get("name")
    password = request.form.get("password")

    # Controleer of de gebruiker bestaat met de opgegeven naam en wachtwoord.
    rows = db.execute("SELECT * FROM registrants WHERE name = ? AND password = ?", name, password)

    # Als er geen enkele rij overeenkomt, geef een foutmelding.
    if len(rows) != 1:
        return render_template("login.html", error="Invalid name or password")

    # Sla de ingelogde gebruiker op in de sessie.
    session["user"] = name

    # Leid de gebruiker door naar de startpagina.
    return redirect("/")

@app.route("/logout", methods=["GET"])
def logout():
    # Wissen van alle sessiegegevens om de gebruiker uit te loggen.
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    # Render de hoofdpagina van de applicatie.
    return render_template("index.html")

@app.route("/activities")
def activities():
    # Vereis dat de gebruiker is ingelogd om activiteiten te bekijken.
    if not session.get("user"):
        return redirect("/login")

    # Toon de activiteitenpagina met alle opties en details.
    return render_template(
        "activities.html",
        activities=ACTIVITIES,
        time=TIME,
        amount=AMOUNT,
        prices=PRICES,
        details=DETAILS
    )

@app.route("/register", methods=["POST"])
def register():
    # Lees de geselecteerde activiteit, tijd en aantal personen uit het formulier.
    activities = request.form.getlist("activity")
    time = request.form.get("time")
    amount = request.form.get("amount")

    # Controleer of er precies één activiteit is gekozen en dat tijd en aantal zijn ingevuld.
    if not len(activities) == 1 or not time or not amount:
        return render_template("error.html")

    # Haal de gekozen activiteit op.
    activity = activities[0]

    # Bepaal de prijs per persoon en bereken de totale prijs.
    price_per_person = PRICES.get(activity, 0)
    total_price = price_per_person * int(amount)

    # Werk de huidige registratierecord bij voor de ingelogde gebruiker.
    db.execute(
        "UPDATE registrants SET activity = ?, time = ?, amount = ?, total_price = ? WHERE name = ?",
        activity,
        time,
        amount,
        total_price,
        session.get("user")
    )

    # Stuur de gebruiker naar de registrantenpagina.
    return redirect("/registrants")

@app.route("/registrants")
def registrants():
    # Vereis dat de gebruiker is ingelogd.
    if not session.get("user"):
        return redirect("/login")

    # Haal de registraties op van de huidige gebruiker.
    registrants = db.execute("SELECT * FROM registrants WHERE name = ?", session["user"])

    # Toont een overzicht van de registraties.
    return render_template("registrants.html", registrants=registrants)

@app.route("/deregister", methods=["POST"])
def deregister():
    # Zorg dat alleen een ingelogde gebruiker een registratie kan verwijderen.
    if not session.get("user"):
        return redirect("/login")

    # Lees het id van de registratie die verwijderd moet worden.
    id = request.form.get("id")
    if id:
        # Controleer of de registratie echt bij de ingelogde gebruiker hoort.
        record = db.execute("SELECT * FROM registrants WHERE id = ? AND name = ?", id, session["user"])
        if len(record) == 0:
            return "Forbidden", 403

        # Verwijder de registratie uit de database.
        db.execute("DELETE FROM registrants WHERE id = ? AND name = ?", id, session["user"])

    # Keer terug naar het registrantenoverzicht.
    return redirect("/registrants")

if __name__ == "__main__":
    app.run(debug=True)