from flask import render_template, redirect, url_for
from cm5_app import app, db
from forms import TrackingForm
from models import Track
from datetime import datetime

@app.route('/', methods=('GET', 'POST'))
@app.route('/index', methods=('GET', 'POST'))
def index():
    form = TrackingForm()
    if form.validate_on_submit():
        tracked = Track(timestamp = datetime.utcnow(),
            date = form.date.data,
            station_start = form.station_start.data,
            station_end = form.station_end.data,
            quantity = form.quantity.data)
        db.session.add(tracked)
        db.session.commit()
        return redirect(url_for('index'))
    tracks = Track.query.order_by(Track.station_start)
    return render_template('index.html', form=form, tracks=tracks)