from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

#create a flask app
app = Flask(__name__)
#database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.sqlite3"
#create an instance of sqlalchemy
db = SQLAlchemy(app)

app.app_context().push()

class Venue(db.Model):
    venue_id = db.Column(db.Integer, primary_key = True)
    venue_name = db.Column(db.String, unique = True, nullable = False)
    location = db.Column(db.String)
    capacity = db.Column(db.Integer)
    shows = db.relationship("Show", backref = 'venue', secondary = 'association')

class Show(db.Model):
    show_id = db.Column(db.Integer, primary_key = True)
    show_name = db.Column(db.String, unique = True, nullable = False)
    rating = db.Column(db.Float)
    timing = db.Column(db.String)
    tags = db.Column(db.String)
    price = db.Column(db.Integer)

class Association(db.Model):
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.venue_id'), primary_key = True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.show_id'), primary_key = True)

class Booking(db.Model):
    booking_id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String)
    venue_name = db.Column(db.String)
    show_name = db.Column(db.String)
    number = db.Column(db.Integer)
    time = db.Column(db.String)

class Username(db.Model):
    user_id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String,unique=True)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def landing_page():
    return render_template('login_page.html')

@app.route('/admin_login', methods = ['GET','POST'])
def admin_login():
    if request.method == 'POST':
        name = request.form["username"]
        password = request.form["password"]
        if name == 'Sanjib' and password == '12345':
            session['username'] = name
            return redirect(url_for('admin_dashboard'))
        return 'invalid username or password'
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session:
        venues = Venue.query.all()
        return render_template('admin_dashboard.html', admin = session['username'], venues = venues)
    return redirect('/')

@app.route('/admin_logout')
def admin_logout():
    session.pop('username', None)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard/create_venue', methods = ['GET','POST'])
def venue_create():
    if request.method == 'POST':
        v = request.form["v_name"]
        l = request.form["loc"]
        c = request.form["cap"]
        
        ven = Venue(venue_name = v, location = l, capacity = c)
        
        db.session.add(ven)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_venue.html',admin = session['username'])


@app.route('/admin_dashboard/create_show', methods = ['GET','POST'])
def show_create():
    venues = Venue.query.all()
    if request.method == 'POST':
        s = request.form["s_name"]
        r = request.form["rate"]
        time = request.form["time"]
        tag = request.form["tag"]
        p = request.form["price"]
        id = request.form["v_id"]
        
        show = Show(show_name = s, rating = r, timing = time, tags = tag, price = p)
        db.session.add(show)
        v = Venue.query.get(id)
        show.venue.append(v)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_show.html',admin = session['username'], venues = venues)

@app.route('/admin_dashboard/edit_venue/<int:v_id>', methods=["GET", "POST"])
def edit_venue(v_id):
    ven = Venue.query.get(v_id)
    
    if request.method == 'POST':
        ven.venue_name = request.form["v_name"]
        ven.location = request.form["loc"]
        ven.capacity = request.form["cap"]
        db.session.commit()
        return(redirect(url_for('admin_dashboard')))

    return render_template("edit_venue.html", admin = session['username'], ven = ven)

@app.route('/admin_dashboard/edit_show/<int:s_id>', methods=["GET", "POST"])
def edit_show(s_id):
    show = Show.query.get(s_id)
    venues = Venue.query.all()
    if request.method == 'POST':
        show.show_name = request.form["s_name"]
        show.rating = request.form["rate"]
        show.timing = request.form["time"]
        show.tags = request.form["tag"]
        show.price = request.form["price"]
        id = request.form["v_id"]
        v = Venue.query.get(id)
        show.venue.append(v)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_show.html',admin = session['username'],venues=venues)

@app.route('/admin_dashboard/delete_venue/<int:v_id>', methods=['GET','POST'])
def delete_venue(v_id):
    ven = Venue.query.get(v_id)
    if request.method == 'POST':
        confirm = request.form['confirm']
        if confirm == 'ok':
            db.session.delete(ven)
            db.session.commit()
        return(redirect(url_for('admin_dashboard')))
    return render_template('venue_delete_confirm.html', venue = ven)

@app.route('/admin_dashboard/delete_show/<int:s_id>', methods=['GET','POST'])
def delete_show(s_id):
    show = Show.query.get(s_id)
    if request.method == 'POST':
        confirm = request.form['confirm']
        if confirm == 'ok':
            db.session.delete(show)
            db.session.commit()
        return(redirect(url_for('admin_dashboard')))
    return render_template('show_delete_confirm.html', show = show)

@app.route('/user_dashboard')
def index():
    if 'username' in session:
        venues = Venue.query.all()
        return render_template('user_dashboard.html', user = session["username"], venues = venues)
    return redirect(url_for('login'))

@app.route('/user_login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        q=Username.query.filter_by(username=name).first()
        if q == None:
            return 'You have to register'
        else:
            session['username'] = name
            return redirect(url_for('index'))
    return render_template('user_login.html')

@app.route('/user_registration',methods=['POST'])
def register():
    name = request.form['username']
    user=Username(username=name)
    db.session.add(user)
    db.session.commit()
    session['username'] = name
    return redirect(url_for('index'))

@app.route('/user_logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/user_dashboard/venue_search',methods=['GET','POST'])
def venue_search():
    if request.method == 'POST':
        l = request.form['location']
        venues = Venue.query.filter_by(location = l).all()
        return render_template('search_result.html', venues = venues)
    return render_template('search_venue.html',user = session["username"])

@app.route('/user_dashboard/show_search',methods=['GET','POST'])
def show_search():
    if request.method == 'POST':
        t = request.form['tags']
        r = request.form['rating']
        if t!='':
            shows = Show.query.filter_by(tags=t).all()
        if r!='':
            shows = Show.query.filter_by(rating=float(r)).all()
        return render_template('search_result.html', shows = shows)
    return render_template('search_show.html',user = session["username"])


@app.route('/user_dashboard/book_show/<int:v_id>/<int:s_id>',methods=['GET','POST'])
def show_booking(v_id,s_id):
    v=Venue.query.get(v_id)
    s=Show.query.get(s_id)
    q=Booking.query.filter_by(venue_name=v.venue_name).all()
    booked=0
    for obj in q:
        booked+=obj.number
    available_seat=v.capacity-booked
    if request.method == 'POST':
        number=request.form['no']
        book = Booking(username=session['username'],venue_name=v.venue_name,show_name=s.show_name,number=number,time=s.timing)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('booking_show.html',v=v,s=s,available_seat=available_seat,user=session['username'])

@app.route('/user_bookings/<string:name>')
def bookings(name):
    q = Booking.query.filter_by(username=name).all()
    return render_template('bookings.html',bookings=q, user=session['username'])

app.run(debug = True)