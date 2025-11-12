from app import app, db, User, Student
from werkzeug.security import generate_password_hash

with app.app_context():
    # Drop all tables and recreate
    db.drop_all()
    db.create_all()
    
    # Create default admin user
    hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
    admin_user = User(username='admin', password=hashed_password)
    db.session.add(admin_user)
    db.session.commit()
    
    print("Database reset successfully!")
    print("Default admin user created:")
    print("Username: admin")
    print("Password: admin123")