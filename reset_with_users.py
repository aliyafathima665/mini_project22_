from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Drop and recreate all tables
    db.drop_all()
    db.create_all()
    
    # Create all users
    users = [
        {'username': 'admin', 'password': 'admin123'},
        {'username': 'faculty', 'password': 'faculty123'},
        {'username': 'hod', 'password': 'hod123'}
    ]
    
    for user_data in users:
        hashed_password = generate_password_hash(user_data['password'], method='pbkdf2:sha256')
        new_user = User(username=user_data['username'], password=hashed_password)
        db.session.add(new_user)
    
    db.session.commit()
    
    print("✅ Database reset with all users!")
    print("👤 Admin: admin / admin123")
    print("👨‍🏫 Faculty: faculty / faculty123")
    print("👨‍💼 HOD: hod / hod123")