#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

#----------------------------------------------------------------------------#
# Initial Record Creation (temp)
#----------------------------------------------------------------------------#

# show1 = Show(start_time="2019-05-21T21:30:00.000Z")
# show2 = Show(start_time="2019-06-15T23:00:00.000Z")
# show3 = Show(start_time="2035-04-01T20:00:00.000Z")
# show4 = Show(start_time="2035-04-08T20:00:00.000Z")
# show5 = Show(start_time="2035-04-15T20:00:00.000Z")

# musicalHop = Venue(name="The Musical Hop",
#   genres=["Jazz", "Reggae", "Swing", "Classical", "Folk"],
#   address="1015 Folsom Street",
#   city="San Francisco",
#   state="CA",
#   phone="123-123-1234",
#   website="https://www.themusicalhop.com",
#   facebook_link="https://www.facebook.com/TheMusicalHop",
#   seeking_talent=True,
#   seeking_description="We are on the lookout for a local artist to play every two weeks. Please call us.",
#   image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
#   shows=[show1])

# duelingPianos = Venue(name="The Dueling Pianos Bar",
#   genres=["Classical", "R&B", "Hip-Hop"],
#   address="335 Delancey Street",
#   city="New York",
#   state="NY",
#   phone="914-003-1132",
#   website="https://www.theduelingpianos.com",
#   facebook_link="https://www.facebook.com/theduelingpianos",
#   seeking_talent=False,
#   image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
#   shows=[])

# parkSquare = Venue(name="Park Square Live Music & Coffee",
#   genres=["Rock n Roll", "Jazz", "Classical", "Folk"],
#   address="34 Whiskey Moore Ave",
#   city="San Francisco",
#   state="CA",
#   phone="415-000-1234",
#   website="https://www.parksquarelivemusicandcoffee.com",
#   facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
#   seeking_talent=False,
#   image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#   shows=[show2, show3,show4,show5])

# gunsNPetals = Artist(name="Guns N Petals",
#   genres=["Rock n Roll"],
#   city="San Francisco",
#   state="CA",
#   phone="326-123-5000",
#   website="https://www.gunsnpetalsband.com",
#   facebook_link="https://www.facebook.com/GunsNPetals",
#   seeking_venue=True,
#   seeking_description="Looking for shows to perform at in the San Francisco Bay Area!",
#   image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#   shows=[show1])

# mattQuevedo = Artist(name="Matt Quevedo",
#   genres=["Jazz"],
#   city="New York",
#   state="NY",
#   phone="300-400-5000",
#   website="https://www.gunsnpetalsband.com",
#   facebook_link="https://www.facebook.com/mattquevedo923251523",
#   seeking_venue=False,
#   image_link="https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#   shows=[show2])

# wildSaxBand = Artist(name="The Wild Sax Band",
#   genres=["Jazz", "Classical"],
#   city="San Francisco",
#   state="CA",
#   phone="432-325-5432",
#   website="https://www.gunsnpetalsband.com",
#   seeking_venue=False,
#   image_link="https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#   shows=[show3,show4,show5])

# db.session.add(musicalHop)
# db.session.add(duelingPianos)
# db.session.add(parkSquare)

# db.session.commit()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  all_areas = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

  for area in all_areas:
    area_venues = Venue.query.filter_by(city=area.city, state=area.state).all()
    venues_data = []
    for venue in area_venues:
      num_upcoming_shows = 0
      if venue.shows:
        for show in venue.shows:
          if show.start_time > datetime.now():
            num_upcoming_shows += 1 

      venues_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })

    data.append({
      "city": area.city,
      "state": area.state,
      "venues": venues_data
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []

  for venue in results:
    num_upcoming_shows = 0

    if venue.shows:
      for show in venue.shows:
        if show.start_time > datetime.now():
          num_upcoming_shows += 1 

    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    })

  response={
    "count": len(results),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []

  if venue.shows:
    for show in venue.shows:
      showArtist = Artist.query.get(show.artist_id)
      show_data = {
        "artist_id": showArtist.id,
        "artist_name": showArtist.name,
        "artist_image_link": showArtist.image_link,
        "start_time": str(show.start_time)
      }
      if show.start_time < datetime.now():
        past_shows.append(show_data)
      else:
        upcoming_shows.append(show_data)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    venue = Venue(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      address=request.form['address'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      facebook_link=request.form['facebook_link'],
      image_link=request.form['image_link'],
      website=request.form['website'],
      seeking_talent=True if 'seeking_talent' in request.form else False,
      seeking_description=request.form['seeking_description'] if 'seeking_description' in request.form else ''
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Venue ' + venue_id + ' could not be deleted.')
  else:
    flash('Venue ' + venue_id + ' was successfully deleted.')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = db.session.query(Artist.id, Artist.name).all()

  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []

  for artist in results:
    num_upcoming_shows = 0

    if artist.shows:
      for show in artist.shows:
        if show.start_time > datetime.now():
          num_upcoming_shows += 1

    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows
    })

  response = {
    "count": len(results),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []

  if artist.shows:
    for show in artist.shows:
      showVenue = Venue.query.get(show.venue_id)
      show_data = {
      "venue_id": showVenue.id,
      "venue_name": showVenue.name,
      "venue_image_link": showVenue.image_link,
      "start_time": str(show.start_time)
    }
    if show.start_time < datetime.now():
        past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)
  
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()

  if artist:
    form = ArtistForm(
      name=artist.name,
      city=artist.city,
      state=artist.state,
      phone=artist.phone,
      image_link=artist.image_link,
      genres=artist.genres,
      facebook_link=artist.facebook_link,
      website=artist.website,
      seeking_venue=artist.seeking_venue,
      seeking_description=artist.seeking_description
    )
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
    abort(404)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  artist = Artist.query.get(artist_id)

  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    artist.seeking_description=request.form['seeking_description'] if 'seeking_description' in request.form else ''
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be changed.')
  else:
    flash('Artist' + request.form['name'] + 'was successfully updated')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm()

  if venue:
    form = VenueForm(
      name=venue.name,
      city=venue.city,
      state=venue.state,
      address=venue.address,
      phone=venue.phone,
      image_link=venue.image_link,
      genres=venue.genres,
      facebook_link=venue.facebook_link,
      website=venue.website,
      seeking_talent=venue.seeking_talent,
      seeking_description=venue.seeking_description
    )
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
    abort(404)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description=request.form['seeking_description'] if 'seeking_description' in request.form else ''
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + 'could not be changed.')
  else:
    flash('Venue' + request.form['name'] + 'was successfully updated')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False

  try:
    artist = Artist(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      facebook_link=request.form['facebook_link'],
      image_link=request.form['image_link'],
      website=request.form['website'],
      seeking_venue=True if 'seeking_venue' in request.form else False,
      seeking_description=request.form['seeking_description'] if 'seeking_description' in request.form else ''
    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.all()

  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)

    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()

  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False

  try:
    show = Show(
      start_time=request.form['start_time'],
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id']
    )
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
