import bcrypt
from database import cursor, conn

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), bytes(hashed))

def register_user(email, password):

    hashed = hash_password(password)

    cursor.execute(
        "INSERT INTO users(email,password) VALUES (?,?)",
        (email, hashed)
    )

    conn.commit()

def login_user(email):

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    return cursor.fetchone()
