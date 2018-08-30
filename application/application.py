import os

from flask import Flask, session, render_template, request
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
    
    user_id = session.get('user_id')
        if user_id:
            user = db.execute("SELECT name FROM users WHERE user_id = :id", {"id": user_id}).fetchone()
            if user:
                # Success!
                return render_template("index.html", books=books, user=user)
            else:
                return render_template("index.html", books=books)
        

    #return render_template("index.html", books=books, user=user)

@app.route("/register", methods=["GET", "POST"])
def register():
      
    if request.method == "POST":

        """User registration"""

        # Get form information.
        name = request.form.get("name")
        login = request.form.get("login")
        password = request.form.get("password")
        pass_confirm = request.form.get("pass_confirm")

        #Check passwords match
        if password != pass_confirm:
            return render_template("error.html", message="Passwords not match!  Please try again.")

        #Check is login already exists 
        if db.execute("SELECT * FROM users WHERE login = :login", {"login":     login}).rowcount == 1:
            return render_template("error.html", message="Login already     exists!")
        db.execute("INSERT INTO users (name, login, password) VALUES (:name,    :login,:password)",
                    {"name": name, "login": login, "password":password})
        db.commit()
        return render_template("success.html", message="Registration    successfuly!")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
        
    if request.method == "POST":
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
    
    return render_template("login.html")

@app.route("/book/<int:book_id>")
def book(book_id):
    """Lists details about a single book."""

    # Make sure flight exists.
    book = db.execute("SELECT * FROM books WHERE book_id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")

    # Get all info.
    reviews = db.execute("SELECT review FROM reviews WHERE book_id = :book_id",{"book_id": book_id}).fetchall()
    return render_template("book.html", book=book, reviews=reviews)




