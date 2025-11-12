from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# ---------------------------------------------------------------------
# APP SETUP
# ---------------------------------------------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'
db = SQLAlchemy(app)

# ---------------------------------------------------------------------
# DATABASE MODELS
# ---------------------------------------------------------------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    regno = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    passed_out = db.Column(db.Boolean, default=False)
    skills = db.Column(db.Text)  # Skills stored at student level
    ptm_records = db.Column(db.Text)  # PTM records stored at student level

class StudentSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    marks = db.Column(db.String(10))
    grade = db.Column(db.String(5))
    performance = db.Column(db.String(50))
    
    student = db.relationship('Student', backref=db.backref('subjects', lazy=True))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ---------------------------------------------------------------------
# LOGIN REQUIRED DECORATOR
# ---------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------------------
# AUTHENTICATION ROUTES
# ---------------------------------------------------------------------
@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('semester_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['logged_in'] = True
            session['role'] = role
            flash(f'Login successful as {role}!', 'success')
            return redirect(url_for('semester_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))

# ---------------------------------------------------------------------
# PROTECTED ROUTES
# ---------------------------------------------------------------------
@app.route("/")
@login_required
def home():
    return redirect(url_for('semester_dashboard'))

@app.route("/semester_dashboard")
@login_required
def semester_dashboard():
    return render_template("semesters.html")

@app.route("/semester<int:semester_id>")
@login_required
def semester_page(semester_id):
    students = Student.query.filter_by(semester=semester_id, passed_out=False).all()
    return render_template(f"semester{semester_id}.html", students=students)

# ---------------------------------------------------------------------
# ADD STUDENT (Basic Info Only)
# ---------------------------------------------------------------------
@app.route("/add_student/<int:semester_id>", methods=["POST"])
@login_required
def add_student(semester_id):
    name = request.form.get("name")
    regno = request.form.get("regno")
    department = request.form.get("department")

    existing_student = Student.query.filter_by(regno=regno).first()
    if existing_student:
        flash('Student with this registration number already exists!', 'error')
        return redirect(f"/semester{semester_id}")

    new_student = Student(
        name=name,
        regno=regno,
        department=department,
        semester=semester_id
    )
    db.session.add(new_student)
    db.session.commit()

    flash('Student added successfully!', 'success')
    return redirect(f"/semester{semester_id}")

# ---------------------------------------------------------------------
# EDIT STUDENT - Show Edit Form
# ---------------------------------------------------------------------
@app.route("/edit_student/<int:semester_id>/<int:student_id>")
@login_required
def edit_student(semester_id, student_id):
    student = Student.query.get_or_404(student_id)
    return render_template("edit_student.html", student=student, semester_id=semester_id)

# ---------------------------------------------------------------------
# ADD SUBJECT TO STUDENT (Only subject data - no skills/PTM)
# ---------------------------------------------------------------------
@app.route("/add_subject/<int:semester_id>/<int:student_id>", methods=["POST"])
@login_required
def add_subject(semester_id, student_id):
    subject_name = request.form.get("subject_name")
    marks = request.form.get("marks")
    grade = request.form.get("grade")
    performance = request.form.get("performance")

    new_subject = StudentSubject(
        student_id=student_id,
        subject_name=subject_name,
        marks=marks,
        grade=grade,
        performance=performance
    )
    db.session.add(new_subject)
    db.session.commit()

    flash('Subject added successfully!', 'success')
    return redirect(f"/edit_student/{semester_id}/{student_id}")

# ---------------------------------------------------------------------
# UPDATE SUBJECT (Only subject data)
# ---------------------------------------------------------------------
@app.route("/update_subject/<int:semester_id>/<int:subject_id>", methods=["POST"])
@login_required
def update_subject(semester_id, subject_id):
    subject = StudentSubject.query.get_or_404(subject_id)
    
    subject.subject_name = request.form.get("subject_name")
    subject.marks = request.form.get("marks")
    subject.grade = request.form.get("grade")
    subject.performance = request.form.get("performance")
    
    db.session.commit()
    flash('Subject updated successfully!', 'success')
    return redirect(f"/edit_student/{semester_id}/{subject.student_id}")

# ---------------------------------------------------------------------
# DELETE SUBJECT
# ---------------------------------------------------------------------
@app.route("/delete_subject/<int:semester_id>/<int:subject_id>")
@login_required
def delete_subject(semester_id, subject_id):
    subject = StudentSubject.query.get_or_404(subject_id)
    student_id = subject.student_id
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(f"/edit_student/{semester_id}/{student_id}")

# ---------------------------------------------------------------------
# UPDATE STUDENT SKILLS & PTM RECORDS
# ---------------------------------------------------------------------
@app.route("/update_student_details/<int:semester_id>/<int:student_id>", methods=["POST"])
@login_required
def update_student_details(semester_id, student_id):
    student = Student.query.get_or_404(student_id)
    
    student.skills = request.form.get("skills")
    student.ptm_records = request.form.get("ptm_records")
    
    db.session.commit()
    flash('Student details updated successfully!', 'success')
    return redirect(f"/edit_student/{semester_id}/{student_id}")

# ---------------------------------------------------------------------
# UPDATE STUDENT BASIC INFO
# ---------------------------------------------------------------------
@app.route("/update_student_basic/<int:semester_id>/<int:student_id>", methods=["POST"])
@login_required
def update_student_basic(semester_id, student_id):
    student = Student.query.get_or_404(student_id)
    
    student.name = request.form.get("name")
    student.regno = request.form.get("regno")
    student.department = request.form.get("department")
    
    db.session.commit()
    flash('Student information updated successfully!', 'success')
    return redirect(f"/edit_student/{semester_id}/{student_id}")

# ---------------------------------------------------------------------
# DELETE STUDENT
# ---------------------------------------------------------------------
@app.route("/delete_student/<int:semester_id>/<int:student_id>")
@login_required
def delete_student(semester_id, student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(f"/semester{semester_id}")

# ---------------------------------------------------------------------
# MOVE STUDENT TO PASSED OUT
# ---------------------------------------------------------------------
@app.route("/move_to_passed_out/<int:semester_id>/<int:student_id>")
@login_required
def move_to_passed_out(semester_id, student_id):
    student = Student.query.get_or_404(student_id)
    student.passed_out = True
    db.session.commit()
    flash('Student moved to passed out list!', 'success')
    return redirect(url_for('passed_out_students'))

# ---------------------------------------------------------------------
# PASSED OUT PAGE
# ---------------------------------------------------------------------
@app.route("/passed_out_students")
@login_required
def passed_out_students():
    students = Student.query.filter_by(passed_out=True).all()
    return render_template("passedout.html", students=students)

# ---------------------------------------------------------------------
# CREATE DEFAULT USERS
# ---------------------------------------------------------------------
def create_admin_user():
    with app.app_context():
        users = [
            {'username': 'admin', 'password': 'admin123'},
            {'username': 'faculty', 'password': 'faculty123'},
            {'username': 'hod', 'password': 'hod123'}
        ]
        
        for user_data in users:
            user = User.query.filter_by(username=user_data['username']).first()
            if not user:
                hashed_password = generate_password_hash(user_data['password'], method='pbkdf2:sha256')
                new_user = User(username=user_data['username'], password=hashed_password)
                db.session.add(new_user)
        
        db.session.commit()
        print("Default users created!")

# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_admin_user()
    app.run(debug=True)