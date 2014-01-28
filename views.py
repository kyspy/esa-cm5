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
        areaed = Area(area = form.area.data, location = form.location.data)
        tracked = Track(timestamp = datetime.utcnow(),
            date = form.date.data,
            station_start = form.station_start.data,
            station_end = form.station_end.data,
            quantity = form.quantity.data,
            area = areaed)
        db.session.add(tracked)
        db.session.commit()
        db.session.merge(areaed)
        db.session.commit()
        return redirect(url_for('index'))
    tracks = Track.query.order_by(Track.station_start)
    areas = Area.query.filter_by(id='Track.area_id')
    return render_template('index.html', form=form, tracks=tracks, areas = areas)