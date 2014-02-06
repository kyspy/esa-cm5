from flask import render_template, redirect, url_for, flash
from cm5_app import app, db, login_manager
from forms import TrackingForm, LoginForm
from models import Track, Area, Shift, Material, User
from datetime import datetime
from flask.ext.login import login_user, login_required, logout_user
from sqlalchemy.orm.exc import NoResultFound

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
            ))

def add_users_db():
    """
    Add users here to control access
    """

    first_names = [
        'Kyla', 'Oleg', 'David', 'Test'
    ]
    last_names = [
        'Farrell', 'Moskovich', 'Deisadze', 'Tester'
    ]
    email = [
        'kfarrell@mtacc-esa.info', 'omoshkov@mtacc-esa.info', 'ddeisadze@mtacc-esa.info', 'test@gmail.com'
    ]
    password = [
        'Esalirovc123', 'Esalirovc1', 'Esalirovc12', 'testtesttest'
    ]

    for i in range(len(first_names)):
        try:
            User.query.filter(User.email == email[i]).one()
        except NoResultFound:
            user = User()
            user.firstname = first_names[i]
            user.lastname = last_names[i]
            user.email = email[i]
            user.password = password[i]
            db.session.add(user)

    db.session.commit()
    return

@login_manager.user_loader
def load_user(email):
    return User.get(email)

@app.route('/', methods=('GET', 'POST'))
@app.route("/index", methods=["GET", "POST"])
def index():
    add_users_db()
    users = User.query.order_by(User.id)
    return render_template('index.html', users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
    add_users_db()
    form = LoginForm()
    if form.validate_on_submit():
        user = form.get_user()
        login_user(user)
        flash("Logged in successfully.")
        return redirect(url_for("dashboard"))
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/track_waterproofing', methods=('GET', 'POST'))
def track_waterproofing():
    form = TrackingForm()
    if form.validate_on_submit():
        t = Track(timestamp = datetime.utcnow(),
        date = form.date.data,
        station_start = form.station_start.data,
        station_end = form.station_end.data,
        quantity = form.quantity.data,
        laborer = form.laborer.data,
        foreman = form.foreman.data,
        supervisor = form.supervisor.data)

        a = Area.query.filter_by(area = form.area.data).first()
        if a == None:
            a = Area(area = form.area.data, location = form.location.data)
            a.tracks.append(t)
            db.session.add(a)
            db.session.commit()
        else:
            a.tracks.append(t)
            db.session.commit()

        s = Shift.query.filter_by(shift = form.shift.data).first()
        if s == None:
            s = Shift(shift = form.shift.data, start = form.start.data, end = form.end.data)
            s.tracks.append(t)
            db.session.add(s)
            db.session.commit()
        else:
            s.tracks.append(t)
            db.session.commit()

        m = Material.query.filter_by(material = form.material.data).first()
        if m == None:
            m = Material(material = form.material.data, unit = form.unit.data)
            m.tracks.append(t)
            db.session.add(m)
            db.session.commit()
        else:
            m.tracks.append(t)
            db.session.commit()

        db.session.add(t)
        db.session.commit()
        return redirect(url_for('track_waterproofing'))

    tracks = Track.query.order_by(Track.id.desc()).slice(0,5)
    areas = Area.query.order_by(Area.id)
    shifts = Shift.query.order_by(Shift.id)
    materials = Material.query.order_by(Material.id)
    return render_template('track_waterproofing.html', form=form, tracks=tracks, areas=areas, shifts=shifts, materials=materials)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')
