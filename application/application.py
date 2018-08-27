import os

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['DEBUG'] = True

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    books = db.execute("SELECT * FROM books LIMIT 10").fetchall()
    return render_template("index.html", books=books)

@app.route("/register", methods=["POST"])
def register():
    """User registration"""

    # Get form information.
    name = request.form.get("name")
    login = request.form.get("login")
    password = request.form.get("password")
    pass_confirm = request.form.get("pass_confirm")
    
    #Check passwords match
    if password != pass_confirm:
        return render_template("error.html", message="Passwords not match! Please try again.")
    
    #Check is login already exists 
    if db.execute("SELECT * FROM users WHERE login = :login", {"login": login}).rowcount == 1:
        return render_template("error.html", message="Login already exists!")
    db.execute("INSERT INTO users (name, login, password) VALUES (:name, :login,:password)",
            {"name": name, "login": login, "password":password})
    db.commit()
    return render_template("success.html", message="Registration successfuly!")

@app.route("/login", methods=["POST"])
def login():
    """User login"""

    # Get form information.

    login = request.form.get("login")
    password = request.form.get("password")
    
    # Check login and pass not null
    if len(login) == 0 and len(password) == 0:
        return render_template("error.html", message="Login or password could not be empty!")

    user = db.execute("SELECT login, password FROM users WHERE login = :login",
                        {"login": login}).fetchone()
    
    #Check is login exists
    if user is None:
        return render_template("error.html", message="User does not exist!")

    #Check password 
    if password != user.password:
        return render_template("error.html", message="Incorrect password!")
        
    
    return render_template("success.html", message="Welcome,")



@app.route("/book", methods=["POST"])
def book():
    """Book a flight."""

    # Get form information.
    name = request.form.get("name")
    try:
        flight_id = int(request.form.get("flight_id"))
    except ValueError:
        return render_template("error.html", message="Invalid flight number.")

    # Make sure flight exists.
    if db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).rowcount == 0:
        return render_template("error.html", message="No such flight with that id.")
    db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)",
            {"name": name, "flight_id": flight_id})
    db.commit()
    return render_template("success.html")

@app.route("/flights")
def flights():
    """Lists all flights."""
    flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("flights.html", flights=flights)

@app.route("/flights/<int:flight_id>")
def flight(flight_id):
    """Lists details about a single flight."""

    # Make sure flight exists.
    flight = db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).fetchone()
    if flight is None:
        return render_template("error.html", message="No such flight.")

    # Get all passengers.
    passengers = db.execute("SELECT name FROM passengers WHERE flight_id = :flight_id",
                            {"flight_id": flight_id}).fetchall()
    return render_template("flight.html", flight=flight, passengers=passengers)
