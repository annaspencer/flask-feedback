from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, RegisterForm, FeedbackForm, DeleteForm
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///feedback"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"]= "105-919-298"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False 

toolbar = DebugToolbarExtension(app)
connect_db(app)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """creates a user"""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data 
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        flash('Welcome! Registration Successful.')
        return redirect('/users/{user.username}')
    return render_template('register.html', form=form)

@app.route('/users/<username>', methods=["GET", "POST"])
def show_secret(username):
    """secret page for users only"""
    if "username" not in session or username != session['username']:
        flash("Please login to view this page.")
        return redirect('/')
    else:
        user = User.query.get(username)
        form = FeedbackForm()
        return render_template("secret.html", user =user, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.first_name}!")
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors =["Invalid username or password."]
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """deletes user and content"""
    if "username" not in session or username != session['username']:
        flash("Please login to view this page.")
        return redirect('/')

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def show_feedbackform(username):
    """shows feedback form for logged in user"""
    form= FeedbackForm()
    if "username" not in session or username != session['username']:
        flash("Please login to view this page.")
        return redirect('/')
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content=content,
            username=username,
        )

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("feedback.html", form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show update-feedback form and process it."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        flash("Please login to view this page.")
        return redirect('/')

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("edit.html", form=form, feedback=feedback)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        flash("Please login to view this page.")
        return redirect('/')

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")
