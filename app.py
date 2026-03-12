from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "SHHH ITS A SECRET"

def get_db_connection():
    conn = sqlite3.connect('db.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists('db.db'):
        conn = get_db_connection()
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        
        # Seed default venues
        default_venues = [
            ('Main Auditorium', True),
            ('Conference Hall A', True),
            ('CS Lab 1', False),
            ('Seminar Hall', True),
            ('Discussion Room 1', False)
        ]
        
        conn.executemany('INSERT INTO venues (name, isHall) VALUES (?, ?)', default_venues)
        conn.commit()
        conn.close()
        print("Database initialized with default schema and venues.")

# Initialize database on startup
with app.app_context():
    init_db()

@app.route("/")
def root():
    if "user" in session:
        print("IN HERE")
        return redirect("/" + session.get('user_type') + "/dashboard")
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form['user_type']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html")
        
        # Hash the password securely
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        
        try:
            if user_type == 'student':
                # Check if username already exists
                existing_user = conn.execute('SELECT * FROM CCs WHERE name = ?', (username,)).fetchone()
                if existing_user:
                    conn.close()
                    flash("Username already exists", "error")
                    return render_template("register.html")
                
                # Insert new student
                conn.execute('INSERT INTO CCs (name, password) VALUES (?, ?)', (username, hashed_password))
                
            elif user_type == 'faculty':
                # Check if username already exists
                existing_user = conn.execute('SELECT * FROM Faculty WHERE name = ?', (username,)).fetchone()
                if existing_user:
                    conn.close()
                    flash("Username already exists", "error")
                    return render_template("register.html")
                
                # Insert new faculty
                conn.execute('INSERT INTO Faculty (name, password) VALUES (?, ?)', (username, hashed_password))
            else:
                conn.close()
                flash("Invalid user type", "error")
                return render_template("register.html")
            
            conn.commit()
            conn.close()
            
            # Redirect to login after successful registration
            flash("Registration successful! Please log in.", "success")
            return redirect('/login')
            
        except Exception as e:
            conn.close()
            flash("Registration failed. Please try again.", "error")
            return render_template("register.html")
        
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if "user" in session:
        print("IN HERE")
        return redirect("/" + session.get('user_type') + "/dashboard")
    if request.method == 'POST':
        user_type = request.form['user_type']
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if user_type == 'student':
            user = conn.execute('SELECT * FROM CCs WHERE name = ?', (username,)).fetchone()
        elif user_type == 'faculty':
            user = conn.execute('SELECT * FROM Faculty WHERE name = ?', (username,)).fetchone()
        else:
            conn.close()
            flash("Invalid user type", "error")
            return render_template("login.html")
        
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            session['user_type'] = user_type
            if user_type == 'student':
                return redirect('/student/dashboard')
            elif user_type == 'faculty':
                return redirect('/faculty/dashboard')
        else:
            flash("Invalid credentials", "error")
            return render_template("login.html")
        
    return render_template("login.html")

@app.route('/student/dashboard')
def student_dashboard():
    if 'user' not in session or session.get('user_type') != 'student':
        return redirect('/login')
    
    conn = get_db_connection()
    approved_events = conn.execute('SELECT * FROM Bookings WHERE Name = ? AND Status = ?', (session['user'], 'approved')).fetchall()
    pending_events = conn.execute('SELECT * FROM Bookings WHERE Name = ? AND Status = ?', (session['user'], 'pending')).fetchall()
    conn.close()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('student_dashboard_content.html', approved_events=approved_events, pending_events=pending_events)
    
    return render_template('student_dashboard.html', approved_events=approved_events, pending_events=pending_events)

@app.route('/faculty/dashboard')
def faculty_dashboard():
    if 'user' not in session or session.get('user_type') != 'faculty':
        return redirect('/login')
    
    conn = get_db_connection()
    approved_events = conn.execute('SELECT * FROM Bookings WHERE Status = ?', ('approved',)).fetchall()
    pending_events = conn.execute('SELECT * FROM Bookings WHERE Status = ?', ('pending',)).fetchall()
    conn.close()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('faculty_dashboard_content.html', approved_events=approved_events, pending_events=pending_events)
    
    return render_template('faculty_dashboard.html', approved_events=approved_events, pending_events=pending_events)

@app.route('/faculty/add_venue', methods=['GET', 'POST'])
def add_venue():
    if 'user' not in session or session.get('user_type') != 'faculty':
        return redirect('/login')
        
    if request.method == 'POST':
        venue_name = request.form.get('venue_name')
        is_hall = request.form.get('is_hall') == 'true'
        
        if not venue_name:
            flash("Venue name is required.", "error")
            return render_template('add_venue.html')
            
        conn = get_db_connection()
        try:
            # Check if venue already exists
            existing = conn.execute('SELECT * FROM venues WHERE name = ?', (venue_name,)).fetchone()
            if existing:
                flash("A venue with this name already exists.", "error")
            else:
                conn.execute('INSERT INTO venues (name, isHall) VALUES (?, ?)', (venue_name, is_hall))
                conn.commit()
                flash(f"Venue '{venue_name}' added successfully!", "success")
                
                # If AJAX, we might want to return just the form again or a success message piece
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return render_template('add_venue_content.html', success=True)
                return redirect('/faculty/dashboard')
                
        except Exception as e:
            flash("Failed to add venue.", "error")
        finally:
            conn.close()
            
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('add_venue_content.html')
        
    return render_template('add_venue.html')

@app.route('/venue_availability', methods=['GET', 'POST'])
def venue_availability():
    if 'user' not in session:
        return redirect('/login')
    
    conn = get_db_connection()
    all_venues = conn.execute('SELECT name FROM venues').fetchall()
    
    form_data = {}
    if request.method == 'POST':
        # Store form data for persistence
        form_data = {
            'start_date': request.form.get('start_date', ''),
            'end_date': request.form.get('end_date', ''),
            'start_time': request.form.get('start_time', ''),
            'end_time': request.form.get('end_time', ''),
            'venue': request.form.get('venue', 'all')
        }
        
        start_date = form_data['start_date']
        end_date = form_data['end_date']
        start_time = form_data['start_time']
        end_time = form_data['end_time']
        venue = form_data['venue']

        # FIXED: Added Status != 'rejected' to ignore rejected bookings in availability check
        query = '''
            SELECT * FROM venues 
            WHERE name NOT IN (
                SELECT Venue FROM Bookings 
                WHERE Status != 'rejected' AND (
                    (Start_Date < ? AND End_Date > ?) OR
                    (Start_Date = ? AND Start_Time < ?) OR
                    (End_Date = ? AND End_Time > ?)
                )
            )
        '''

        params = [end_date, start_date, start_date, end_time, end_date, start_time]

        if venue != 'all':
            query += ' AND name = ?'
            params.append(venue)
            
        available_venues = conn.execute(query, tuple(params)).fetchall()
        conn.close()
        
        # Check if it's an AJAX request - return only the content
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('venue_availability_content.html', 
                                 venues=available_venues, 
                                 all_venues=all_venues,
                                 form_data=form_data)
        
        return render_template('venue_availability.html', 
                             venues=available_venues, 
                             all_venues=all_venues,
                             form_data=form_data)
    
    conn.close()
    
    # Check if it's an AJAX request - return only the content
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('venue_availability_content.html', 
                             venues=None, 
                             all_venues=all_venues,
                             form_data=form_data)
    
    return render_template('venue_availability.html', 
                         venues=None, 
                         all_venues=all_venues,
                         form_data=form_data)
@app.route('/book_venue', methods=['GET', 'POST'])
def book_venue():
    if 'user' not in session or session.get('user_type') != 'student':
        return redirect('/login')
        
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        venue = request.form['venue']
        event_name = request.form['event_name']
        
        conn = get_db_connection()
        
        # FIXED: Use the same availability check logic as venue_availability
        query = '''
            SELECT * FROM venues 
            WHERE name NOT IN (
                SELECT Venue FROM Bookings 
                WHERE Status != 'rejected' AND (
                    (Start_Date < ? AND End_Date > ?) OR
                    (Start_Date = ? AND Start_Time < ?) OR
                    (End_Date = ? AND End_Time > ?)
                )
            ) AND name = ?
        '''
        
        params = [end_date, start_date, start_date, end_time, end_date, start_time, venue]
        
        available_venues = conn.execute(query, tuple(params)).fetchall()
        
        # FIXED: Check if the venue IS available (not when it's NOT available)
        if len(available_venues) > 0:
            # Venue is available - proceed with booking
            conn.execute('INSERT INTO Bookings (Venue, Start_Time, Start_Date, End_Time, End_Date, Name, Status, Event_Name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                         (venue, start_time, start_date, end_time, end_date, session['user'], 'pending', event_name))
            conn.commit()
            conn.close()
            
            # AJAX response - return only content
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                conn = get_db_connection()
                venues = conn.execute('SELECT name FROM venues').fetchall()
                previous_bookings = conn.execute('SELECT * FROM Bookings WHERE Name = ?', (session['user'],)).fetchall()
                conn.close()
                flash("Venue booked successfully! Waiting for faculty approval.", "success")
                return render_template('book_venue_content.html', 
                                     venues=venues, 
                                     previous_bookings=previous_bookings)
            
            flash("Venue booked successfully! Waiting for faculty approval.", "success")
            return redirect('/student/dashboard')
        else:
            # Venue is NOT available - show error
            conn.close()
            
            # AJAX response for error - return only content
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                conn = get_db_connection()
                venues = conn.execute('SELECT name FROM venues').fetchall()
                previous_bookings = conn.execute('SELECT * FROM Bookings WHERE Name = ?', (session['user'],)).fetchall()
                conn.close()
                flash("Venue is not available for the selected time slot.", "error")
                return render_template('book_venue_content.html', 
                                     venues=venues, 
                                     previous_bookings=previous_bookings)
            
            flash("Venue is not available for the selected time slot.", "error")
            return render_template('book_venue.html')

    conn = get_db_connection()
    venues = conn.execute('SELECT name FROM venues').fetchall()
    previous_bookings = conn.execute('SELECT * FROM Bookings WHERE Name = ?', (session['user'],)).fetchall()
    conn.close()

    # Check if it's an AJAX request - return only content
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('book_venue_content.html', 
                             venues=venues, 
                             previous_bookings=previous_bookings)

    return render_template('book_venue.html', 
                         venues=venues, 
                         previous_bookings=previous_bookings)

@app.route('/approve_booking/<int:booking_id>', methods=['POST'])
def approve_booking(booking_id):
    if 'user' not in session or session.get('user_type') != 'faculty':
        return redirect('/login')
        
    conn = get_db_connection()
    conn.execute('UPDATE Bookings SET Status = ? WHERE Booking_ID = ?', ('approved', booking_id))
    conn.commit()
    conn.close()
    
    flash("Booking request approved successfully.", "success")
    return redirect('/faculty/dashboard')

@app.route('/reject_booking/<int:booking_id>', methods=['POST'])
def reject_booking(booking_id):
    if 'user' not in session or session.get('user_type') != 'faculty':
        return redirect('/login')
        
    conn = get_db_connection()
    conn.execute('UPDATE Bookings SET Status = ? WHERE Booking_ID = ?', ('rejected', booking_id))
    conn.commit()
    conn.close()
    
    flash("Booking request rejected.", "success")
    return redirect('/faculty/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
