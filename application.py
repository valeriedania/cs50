import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL(os.getenv("postgres://nfmvuwscnxxgcm:ad670db8856629022398e96ba5248c0fd7192c07dbe9283238c0b2a9163d5562@ec2-3-231-48-230.compute-1.amazonaws.com:5432/d119o5sn47esvo"))

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    if request.method == "POST":
        db.execute("UPDATE users SET cash = cash + :amount WHERE id=:id", amount = request.form.get("cash"), id=session["user_id"])
        flash("Added Cash!")
        return redirect("/")

    else:
        return render_template("add_cash.html")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    #Select the stock owned by the user currently logged in
    rows = db.execute("SELECT symbol, SUM(shares) as TotalShares FROM portfolio WHERE id =:id GROUP BY symbol HAVING TotalShares > 0", id=session["user_id"])

    #Create a temporary variable to store TOTAL worth (cash + share)
    total_cash = 0

    #Create a dictionary and append
    holdings =[]

    #Update each symbol prices and total
    for row in rows:
        stock = lookup(row["symbol"])
        holdings.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "shares": row["TotalShares"],
            "price": usd(stock["price"]),
            "total": usd(stock["price"] * row["TotalShares"])
        })

    #Update user's cash in portfolio
    updated_cash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])

    #Update total cash (cash + share)
    total_cash += updated_cash[0]["cash"]

    #Print portfolio in index homepage
    updated_portfolio = db.execute("SELECT * from portfolio WHERE id=:id", id=session["user_id"])

    return render_template("index.html", holdings = holdings, cash=usd(updated_cash[0]["cash"]), total_cash=usd(total_cash))

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    #User reached route via POST
    if request.method == "POST":

        #Get user input for stock symbol
        symbol = request.form.get("symbol").upper()

        #Check if input is blank, if so, return apology
        if not symbol:
            return apology("Must provide symbol.")

        #Check for valid symbol
        symbol = lookup(request.form.get("symbol"))

        if not symbol:
            return apology("Symbol is not valid.")

        #Get user input for number of shares
        shares = int(request.form.get("shares"))

        #Check if input is a positive integer
        if not shares > 0:
            return apology("Please input a value greater than 0.")

        #Query database for cash the user currently has
        cash = db.execute("SELECT cash from users WHERE id= :id", id=session["user_id"])

        #Check if enough money to buy
        if not cash or float(cash[0]["cash"]) < symbol["price"] * shares:
            return apology("Not enough money")

        #Update user's cash
        db.execute("UPDATE users SET cash = cash - :purchase WHERE id=:id", id=session["user_id"], purchase=symbol["price"] * float(shares))

        #Insert updated values into portfolio
        db.execute("INSERT INTO portfolio (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)", user_id=session["user_id"], symbol = symbol["symbol"], shares=shares, price = symbol["price"])

        flash("Bought!")

        #Redirect user to portfolio page (index)
        return render_template("index.html")

    #User reached route via GET(as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    histories = db.execute("SELECT symbol, shares, price, transacted FROM portfolio WHERE id=:id", id=session["user_id"])
    for i in range(len(histories)):
        histories[i]["price"] = usd(histories[i]["price"])

    return render_template("history.html", histories=histories)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    #User reached route via POST
    if request.method == "POST":

        #Get user input for stock symbol
        symbol = request.form.get("symbol")

        #Check if input is blank, if so, return apology
        if not symbol:
            return apology("Must provide symbol.")

        #Check for valid symbol
        symbol = lookup(request.form.get("symbol"))

        if not symbol:
            return apology("Symbol is not valid.")

        #Render the second template (quoted.html)
        else:
            return render_template("quoted.html", stock=symbol)

    #User reached route via GET(as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    #Forget any user_id
    session.clear()

    #User reached route via POST (as by submitting a form via POST)
    if request.method =="POST":

        #Take input for username
        username = request.form.get("username")

        #Check if input is blank and if so return apology
        if not request.form.get("username"):
            return apology("You must provide a username.")

        #Take input for password
        password = request.form.get("password")

        #Check if input is blank and if so return apology
        if not request.form.get("password"):
            return apology("You must provide a password.")

        #Take input for conformation:
        conformation = request.form.get("conformation")

        #Check if input is blank and if so return apology
        if not request.form.get("conformation"):
            return apology("You must confirm password")

        #Check if password and confirmation match
        if password != conformation:
            return apology("Your password confirmation does not match the password")

        #Hash the password with generate_password_hash
        pwhash = generate_password_hash(request.form.get("password"))

         #Query database for username (which checks if username already exists)
        usernamecheck = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if usernamecheck:
            return apology("Username already exists")

        #Insert the username and hash into the users table
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=pwhash)

        #Redirect user to homepage
        return redirect('/')

    #User reached route via GET(as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        #Check for valid symbol
        stock = lookup(request.form.get("symbol"))
        if not stock:
            return apology("Invalid Symbol")

        #Get user input for number of shares
        shares = int(request.form.get("shares"))

        #Check if input is a positive integer
        if not shares > 0:
            return apology("Please input a value greater than 0.")

        #Select the symbol shares of that user
        user_shares = db.execute("SELECT symbol, SUM(shares) as TotalShares FROM portfolio WHERE id=:id AND symbol=:symbol", id=session["user_id"], symbol=stock["symbol"])

        #Check if user has enough shares to sell
        if not user_shares or int(user_shares[0]["TotalShares"]) < shares:
            return apology("You do not have enough shares")

        #Update user cash
        db.execute("UPDATE users SET cash = cash + :purchase WHERE id =:id", id=session["user_id"], purchase= stock["price"] * float(shares))

        #Decrement the shares count
        shares_total = user_shares[0]["TotalShares"] - shares

        #If no more shares, delete
        if shares_total == 0:
            db.execute("DELETE FROM portfolio WHERE id=:id AND symbol=:symbol", id=session["user_id"], symbol=stock["symbol"])

        #Update porfolio shares count
        else:
            db.execute("UPDATE portfolio SET shares=:shares WHERE id=:id AND symbol=:symbol", shares=shares_total, id=session["user_id"], symbol=stock["symbol"])


        flash("Sold!")

        #Return to index
        return render_template("index.html")

    #User reached route via GET(as by clicking a link or via redirect)
    else:
        rows =db.execute("SELECT symbol from portfolio WHERE user_id=:user_id GROUP BY symbol HAVING SUM(shares) >0", user_id=session["user_id"])
        return render_template("sell.html", symbols=[row["symbol"] for row in rows])


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
