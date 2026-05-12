from argon2 import PasswordHasher
import re
from rest_framework.exceptions import ValidationError


ph = PasswordHasher()

# Hashing
def getHashPassword(user_password):
    hash = ph.hash(user_password)
    return hash

# Verifying
def matchPassword(stored_hash, input_password):

    try:
        ph.verify(stored_hash, input_password)
    except Exception:
       raise ValidationError(detail="Invalide credancials")
    

def validate_password(value):
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    if not re.search(r"[A-Z]", value):
        raise ValidationError("Password must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", value):
        raise ValidationError("Password must contain at least one lowercase letter.")

    if not re.search(r"[0-9]", value):
        raise ValidationError("Password must contain at least one number.")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-\\/]", value):
        raise ValidationError("Password must contain at least one special character.")

    return value