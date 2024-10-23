import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///todo.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    userId = session["user_id"]
    userName = session["username"]
    userDetails = db.execute("SELECT id, title, todo, state, time FROM todo WHERE user_id = ?",userId)
    if not userDetails:
        return render_template("index.html", userName=userName)
    return render_template("index.html",userDetails=userDetails, userName=userName)


@app.route("/add_todo", methods=["GET", "POST"])
@login_required
def addTodo():
    userId = session["user_id"]
    if request.method == "POST" and userId:
        title = request.form.get("title")
        todo = request.form.get("todo")

        if not title:
            title = "No title"
        if not todo :
            return apology("Some text is necesary")
        state = "todo"
        db.execute("INSERT INTO todo (user_id, title, todo, state) VALUES(?,?,?,?)", userId, title, todo, state)
        db.execute("INSERT INTO history (user_id, title, todo, state) VALUES(?,?,?,?)", userId, title, todo, "create")
        countTodo = db.execute("SELECT COUNT(*) AS todos FROM todo WHERE user_id = ?", userId)[0]["todos"]

        flash(f"You added a new todo, and you have {countTodo} ToDo's")

        return redirect("/")
    else:
        return render_template("add_todo.html")


@app.route("/delete_todo/<int:todo_id>", methods=["DELETE"])
@login_required
def delete_todo(todo_id):
    if request.method == "DELETE" and 'user_id' in session:
        todo = db.execute( "SELECT id, title, todo, state FROM todo WHERE id=?", todo_id)[0]
        if todo is not None:
            db.execute("DELETE FROM todo WHERE id = ?", todo_id)
            db.execute("INSERT INTO history (user_id, title, todo, state) VALUES(?,?,?,?)", session["user_id"], todo["title"],todo["todo"], "delete")
            flash(f'Deleted succesfully')
            return jsonify({'success': True})
        else:
            flash(f'Element not found')
            return jsonify({'success': False, 'message': 'Elemento no encontrado'})


@app.route("/update_todo/<int:todo_id>", methods=["PUT"])
@login_required
def update_todo(todo_id):
    if request.method == "PUT" and 'user_id' in session:
        todo = db.execute("SELECT state, title, todo FROM todo WHERE id = ?", todo_id)[0]
        if todo is not None:
            state = todo['state']
            if state == 'todo':
                db.execute("UPDATE todo SET state = 'done' WHERE id = ?", todo_id)
                db.execute("INSERT INTO history (user_id, title, todo, state) VALUES(?,?,?,?)", session["user_id"], todo["title"],todo["todo"], "done")
                return jsonify({'success': True})
            elif state == 'done':
                db.execute("UPDATE todo SET state = 'todo' WHERE id = ?", todo_id)
                db.execute("INSERT INTO history (user_id, title, todo, state) VALUES(?,?,?,?)", session["user_id"], todo["title"],todo["todo"], "todo")
                return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Elemento no encontrado'})
    return jsonify({'success': False, 'message': 'No autorizado'})


@app.route("/update_text/<int:todo_id>", methods=["PUT"])
@login_required
def update(todo_id):
      if request.method == "PUT" and 'user_id' in session:
        todo = db.execute("SELECT state, title, todo FROM todo WHERE id = ?", todo_id)[0]
        if todo is not None:
            if request.get_json() is not None:
                data = request.get_json()
                new_text = data.get("newText")
                db.execute("UPDATE todo SET todo = ? WHERE id = ?", new_text, todo_id)
                db.execute("INSERT INTO history (user_id, title, todo, state) VALUES(?,?,?,?)", session["user_id"], todo["title"], new_text, "update")
                flash(f'ToDo update sucesfully')
                return jsonify({'success': True})

@app.route("/history")
@login_required
def history():
    userId = session["user_id"]
    history = db.execute("SELECT id, title, todo, state, time FROM history WHERE user_id=? ORDER BY time DESC", userId)
    return render_template("history.html", history=history)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username or not password or not confirmation:
            return apology("Complete all the fields please")
        if password != confirmation:
            return apology("Passwords not match")
        hash = generate_password_hash(password)
        exist = db.execute(
            "SELECT EXISTS (SELECT 1 FROM users WHERE username=?) AS user", username
        )[0]["user"]
        if exist == 1:
            return apology("user already exists")
        db.execute("INSERT INTO users (username,hash) VALUES(?,?)", username, hash)
        rows = db.execute("SELECT * FROM users WHERE username=?", username)
        print (rows)
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        return redirect("/")
    else:
        return render_template("register.html")
