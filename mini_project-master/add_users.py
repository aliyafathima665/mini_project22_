from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create users if they don't exist
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
            print(f"Created user: {user_data['username']}")
    
    db.session.commit()
    print("All users created successfully!")
    print("Login credentials:")
    print("Admin: admin / admin123")
    print("Faculty: faculty / faculty123")
    print("HOD: hod / hod123")