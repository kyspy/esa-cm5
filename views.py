from flask import render_template, redirect, url_for
from cm5_app import app, db
from forms import TrackingForm
from models import Track, Area
from datetime import datetime

@app.route('/', methods=('GET', 'POST'))
@app.route('/index', methods=('GET', 'POST'))
def index():
    form = TrackingForm()
    if form.validate_on_submit():
        t = Track(timestamp = datetime.utcnow(),
            date = form.date.data,
            station_start = form.station_start.data,
            station_end = form.station_end.data,
            quantity = form.quantity.data)
        a = Area.query.filter_by(area = form.area.data).first()
        if a == None:
            a2 = Area(area = form.area.data, location = form.location.data)
            a2.tracks.append(t)
            db.session.add(a2)
            db.session.commit()
        else:
            a.tracks.append(t)
        db.session.add(t)
        db.session.commit()
        return redirect(url_for('index'))
    tracks = Track.query.order_by(Track.id)
    areas = Area.query.order_by(Area.id)
    return render_template('index.html', form=form, tracks=tracks, areas=areas)