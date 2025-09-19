"""
Setup Guest User for Memory System
"""
from models import *
from controllers import engine
from sqlmodel import Session, select

def ensure_guest_user():
    """Ensure guest user exists in database"""
    with Session(engine) as session:
        # Check if guest user exists
        guest_user = session.exec(select(User).where(User.id == 0)).first()
        
        if not guest_user:
            # Create guest user
            guest_user = User(
                id=0,
                name="Guest",
                email="guest@autocare.com",
                number="0000000000",
                password="guest_password_hash"
            )
            session.add(guest_user)
            session.commit()
            print("✅ Guest user created successfully")
        else:
            print("✅ Guest user already exists")

if __name__ == "__main__":
    # Create tables first
    SQLModel.metadata.create_all(engine)
    ensure_guest_user()