from flask import Flask, render_template, request, redirect, url_for, flash,session,send_from_directory
from flaskext.mysql import MySQL
import secrets
from flask_mail import Message
from flask_mail import Mail
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from datetime import datetime
from flask_mail import Message
from flask_mail import Mail
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Change this to a secret key

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'compliant_system'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'  # Change this if your MySQL server is on a different host
app.config['MYSQL_DATABASE_AUTOCOMMIT'] = True

mysql = MySQL(app)


def get_user_complaint_count(username, status=None):
    try:
        # Create a cursor
        cursor = mysql.get_db().cursor()

        # Define the query
        if status:
            query = "SELECT COUNT(*) FROM compliant_tbl WHERE username = %s AND status = %s"
            cursor.execute(query, (username, status))
        else:
            query = "SELECT COUNT(*) FROM compliant_tbl WHERE username = %s"
            cursor.execute(query, (username,))

        # Fetch the count
        count = cursor.fetchone()[0]

        # Close the cursor
        cursor.close()

        return count
    except Exception as e:
        print(f"Error executing query: {e}")
        return 0


@app.route('/')
def home():
    return render_template('index.html')

users = [
    {'username': 'eb', 'password': generate_password_hash('eb'), 'role': 'eb'},
    {'username': 'water', 'password': generate_password_hash('water'), 'role': 'water'},
    {'username': 'road', 'password': generate_password_hash('road'), 'role': 'road'},
    {'username': 'drinage', 'password': generate_password_hash('drinage'), 'role': 'drinage'},
    {'username': 'other', 'password': generate_password_hash('other'), 'role': 'other'},
]


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = next((user for user in users if user['username'] == username), None)

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['role'] = user['role']
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password', 'error')

    return render_template('login.html')




@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user is trying to register
        if 'register' in request.form:
            name = request.form['name']
            email = request.form['email']
            contact_no = request.form['contact_no']

            try:
                cursor = mysql.get_db().cursor()
                cursor.execute("INSERT INTO usertbl (Name, Emailid, contactno, username, password) VALUES (%s, %s, %s, %s, %s)",
                               (name, email, contact_no, username, password))
                mysql.get_db().commit()
                flash('User registered successfully!', 'success')
            except Exception as e:
                print(f"Error inserting user: {e}")
            finally:
                if 'cursor' in locals():
                    cursor.close()

        # Otherwise, the user is trying to log in
        else:
            cursor = mysql.get_db().cursor()
            cursor.execute("SELECT * FROM usertbl WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()

            if user:
                user = {'id': user[0]} 
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid username or password', 'danger')

    return render_template('user_login.html')


@app.route('/user/dashboard')
def user_dashboard():
    if 'username' not in session:
        flash('Please log in to view this page', 'info')
        return redirect(url_for('user_login'))

    username = session['username']

    # Fetch the counts from your database
    submitted_count = get_user_complaint_count(username)
    resolved_count = get_user_complaint_count(username, status='COMPLETED')
    pending_count = get_user_complaint_count(username, status='PENDING')

    # Pass the counts to the template
    return render_template('user_dashboard.html', username=username,
                           submitted_count=submitted_count,
                           resolved_count=resolved_count,
                           pending_count=pending_count)



@app.route('/feedback', methods=['POST'])
def feedback():
    # Get form data
    feedback = request.form['feedback']
    suggestion = request.form['suggestion']
    rating = request.form['rating']

    # Save feedback to database or handle it as needed...

    flash('Thank you for your feedback!', 'success')
    return redirect(url_for('user_dashboard'))


# Set the upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}  # Add this line
# Define a route to serve files from the 'uploads' folder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/user/profile', methods=['GET', 'POST'])
def user_profile():
    if 'username' not in session:
        return redirect(url_for('user_login'))

    username = session['username']

    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        contact_no = request.form['contact_no']

        try:
            cursor = mysql.get_db().cursor()
            cursor.execute("UPDATE usertbl SET Name = %s, Emailid = %s, contactno = %s WHERE username = %s",
                           (name, email, contact_no, username))
            mysql.get_db().commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            print(f"Error updating profile: {e}")
            flash('An error occurred while updating your profile.', 'danger')
        finally:
            if 'cursor' in locals():
                cursor.close()

    # Fetch user data from the database
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT * FROM usertbl WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    return render_template('user_profile.html', user=user)


@app.route('/user/addcompliant', methods=['GET', 'POST'])
def add_compliant():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file, browser may also submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        # Validate file extension
        if not allowed_file(file.filename):
            flash('Invalid file type. Allowed extensions are: png, jpg, jpeg', 'error')
            return redirect(request.url)

        try:
            filename = secure_filename(file.filename)
            print("Filename:", filename)

            # Save the file to the upload folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Your form data handling code...
            username = session.get('username')
            ctype = request.form['compliant_type']
            description = request.form['description']
            city = request.form['city']
            street = request.form['street']
            pincode = request.form['pincode']
            current_date = datetime.now().date()

            # Your database insertion code...
            cursor = mysql.get_db().cursor()
            cursor.execute("INSERT INTO compliant_tbl (compliant_type, description, City, Street, Pincode, filename, status, username, regdate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (ctype, description, city, street, pincode, filename, 'PENDING', username, current_date))
            mysql.get_db().commit()

            flash('User Complaint registered successfully!', 'success')
            return redirect(url_for('user_dashboard'))

        except Exception as e:
            print(f"Error handling file upload and inserting user: {e}")
            flash('Error handling file upload and inserting user', 'error')

        finally:
            if 'cursor' in locals():
                cursor.close()

    return render_template('Add_Compliant.html')

@app.route('/user/viewcompliant', methods=['GET'])
def view_compliant():
    try:
        username = session.get('username')
        print(username)
        with mysql.get_db().cursor() as cursor:
            cursor.execute("SELECT * FROM compliant_tbl WHERE username = %s", (username,))
            results = cursor.fetchall()

        formatted_results = [(result[0], result[1], result[2], result[3], result[4], result[5],result[6],result[7]) for result in results]
        print("compliant", formatted_results)
        return render_template('view_complaints.html', results=formatted_results)

    except Exception as e:
        print(f"Error executing query: {e}")
        flash('An error occurred while fetching data.', 'danger')
        return redirect(url_for('view_compliant'))


                           
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        role=session.get('role')
        # Retrieve counts from your database or data source
        total_count = get_total_complaint_count(role)
        processing_count = get_complaint_count_by_status('PROCESSING',role)
        completed_count = get_complaint_count_by_status('COMPLETED',role)
        pending_count = get_complaint_count_by_status('PENDING',role)
        return render_template('dashboard.html', username=session['username'], role=session['role'],
                           total_count=total_count,
                           processing_count=processing_count,
                           completed_count=completed_count,
                           pending_count=pending_count)
    return redirect(url_for('login'))


def get_total_complaint_count(role):
    if role=='water':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM compliant_tbl WHERE compliant_type = %s", ('Water'))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error executing query: {e}")
    elif role=='eb':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM compliant_tbl WHERE compliant_type = %s", ('EB'))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error executing query: {e}")
    elif role=='road':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM compliant_tbl WHERE compliant_type = %s", ('Road'))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error executing query: {e}")
    elif role=='drinage':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM compliant_tbl WHERE compliant_type = %s", ('Drinage'))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error executing query: {e}")

    elif role=='other':  # New code for 'other'
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM compliant_tbl WHERE compliant_type = %s", ('Other'))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error executing query: {e}")
       
def get_complaint_count_by_status(Status,role):
    if role=='water':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM compliant_tbl WHERE compliant_type = %s AND Status=%s", ('Water',Status))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error executing query: {e}")
    elif role=='eb':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM compliant_tbl WHERE compliant_type = %s AND Status=%s", ('EB',Status))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error executing query: {e}")
    elif role=='road':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM compliant_tbl WHERE compliant_type = %s AND Status=%s", ('Road',Status))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error executing query: {e}")
    elif role=='drinage':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM compliant_tbl WHERE compliant_type = %s AND Status=%s", ('Drinage',Status))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error executing query: {e}")

    elif role=='other':  # New code for 'other'
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM compliant_tbl WHERE compliant_type = %s AND Status=%s", ('Other',Status))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error executing query: {e}")



@app.route('/user/logout')
def user_logout():
    # Clear the session to log the user out
    session.clear()
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/admin_compliant', methods=['GET'])
def admin_compliant():
    role=session.get('role')

    if role=='water':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT * FROM compliant_tbl WHERE compliant_type = %s", ('Water'))
                results = cursor.fetchall()

            formatted_results = [(result[0], result[1], result[2], result[3], result[4], result[5],result[6],result[7]) for result in results]
            print("compliant", formatted_results)
            return render_template('admin_complaints.html', results=formatted_results,role=role)

        except Exception as e:
            print(f"Error executing query: {e}")
            flash('An error occurred while fetching data.', 'danger')
            return redirect(url_for('login'))
    elif role=='eb':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT * FROM compliant_tbl WHERE compliant_type = %s", ('EB'))
                results = cursor.fetchall()

            formatted_results = [(result[0], result[1], result[2], result[3], result[4], result[5],result[6],result[7]) for result in results]
            print("compliant", formatted_results)
            return render_template('admin_complaints.html', results=formatted_results,role=role)

        except Exception as e:
            print(f"Error executing query: {e}")
            flash('An error occurred while fetching data.', 'danger')
            return redirect(url_for('login'))
    elif role=='road':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT * FROM compliant_tbl WHERE compliant_type = %s", ('Road'))
                results = cursor.fetchall()

            formatted_results = [(result[0], result[1], result[2], result[3], result[4], result[5],result[6],result[7]) for result in results]
            print("compliant", formatted_results)
            return render_template('admin_complaints.html', results=formatted_results,role=role)

        except Exception as e:
            print(f"Error executing query: {e}")
            flash('An error occurred while fetching data.', 'danger')
            return redirect(url_for('login'))
        
    elif role=='drinage':
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT * FROM compliant_tbl WHERE compliant_type = %s", ('Drinage'))
                results = cursor.fetchall()

            formatted_results = [(result[0], result[1], result[2], result[3], result[4], result[5],result[6],result[7]) for result in results]
            print("compliant", formatted_results)
            return render_template('admin_complaints.html', results=formatted_results,role=role)

        except Exception as e:
            print(f"Error executing query: {e}")
            flash('An error occurred while fetching data.', 'danger')
            return redirect(url_for('login'))

    elif role=='other': 
        try:
            print(role)
            with mysql.get_db().cursor() as cursor:
                cursor.execute("SELECT * FROM compliant_tbl WHERE compliant_type = %s", ('Other'))
                results = cursor.fetchall()

            formatted_results = [(result[0], result[1], result[2], result[3], result[4], result[5],result[6],result[7]) for result in results]
            print("compliant", formatted_results)
            return render_template('admin_complaints.html', results=formatted_results,role=role)

        except Exception as e:
            print(f"Error executing query: {e}")
            flash('An error occurred while fetching data.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('User Name Password Mismatch', 'danger')
        return redirect(url_for('login'))

@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    if 'username' in session and 'role' in session and session['role'] in ['water', 'eb', 'road', 'drinage', 'other']:
        new_status = request.form.get('new_status')
        try:
            cursor = mysql.get_db().cursor()
            cursor.execute("UPDATE compliant_tbl SET Status = %s WHERE id = %s", (new_status, id))
            mysql.get_db().commit()
            flash('Status updated successfully!', 'success')

            cursor.execute("SELECT u.Emailid, u.Name FROM compliant_tbl c JOIN usertbl u ON c.username = u.username WHERE c.id = %s", (id,))
            email, name = cursor.fetchone()
            print(email)
            
            # Prepare the email body
            email_body = f"""
            Dear {name},

            We hope this message finds you well.

            We are writing to inform you that there has been an update to your complaint status on our platform. Here are the details:

            Complaint Type: {session['role']}
            New Status: {new_status}

            We appreciate your patience and understanding as we work to address your complaint. If you have any questions or need further assistance, please do not hesitate to contact us.

            Best Regards,
            Your Support Team
            """

            send_email(email, 'Compliant Status Update', email_body)

        except Exception as e:
            flash(f"Error updating status: {e}", 'danger')
        finally:
            cursor.close()
    else:
        flash('You do not have the necessary permissions.', 'danger')

    return redirect(url_for('admin_compliant'))
   

@app.route('/reply_complaint/<int:id>', methods=['POST'])
def reply_complaint(id):
    if 'username' in session and 'role' in session and session['role'] in ['water', 'eb', 'road', 'drinage', 'other']:
        reply = request.form.get('reply')
        try:
            cursor = mysql.get_db().cursor()
            cursor.execute("SELECT u.Emailid, u.Name FROM compliant_tbl c JOIN usertbl u ON c.username = u.username WHERE c.id = %s", (id,))
            email, name = cursor.fetchone()
            
            # Prepare the email body
            email_body = f"""
            Dear {name},

            We have received your complaint and our admin has replied to it. Here is the reply:

            {reply}

            If you have any questions or need further assistance, please do not hesitate to contact us.

            Best Regards,
            Your Support Team
            """

            send_email(email, 'Complaint Reply', email_body)

            flash('Reply sent successfully!', 'success')
        except Exception as e:
            flash(f"Error sending reply: {e}", 'danger')
        finally:
            cursor.close()
    else:
        flash('You do not have the necessary permissions.', 'danger')

    return redirect(url_for('admin_compliant'))



def send_email(recipient, subject, body):
    # Replace these values with your actual email configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'myprojectfinalbe@gmail.com'
    # smtp_password = 'zenqftljvficjxsx' 
    smtp_password = 'xhlatgqungfdcikk'
    sender_email = 'Project'

    # Create a MIMEText object with the email body
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Login to the SMTP server
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(sender_email, recipient, msg.as_string())

        # Close the connection
        server.quit()

        print(f"Email sent successfully to {recipient}")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == '__main__':
    app.run(debug=True)