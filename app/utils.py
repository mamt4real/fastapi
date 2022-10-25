from passlib.context import CryptContext

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_pass: str, hashed_pass: str):
    return pwd_context.verify(plain_pass, hashed_pass)
