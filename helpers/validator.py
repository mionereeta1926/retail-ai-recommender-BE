from email_validator import validate_email, EmailNotValidError


def validate_signup(data):

    errors = []

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone_number")

    if not username:
        errors.append("Username is required")

    if not email:
        errors.append("Email is required")
    else:

        try:
            validate_email(email)

        except EmailNotValidError:
            errors.append("Invalid email")

    if not password:
        errors.append("Password is required")

    if not phone:
        errors.append("Phone number is required")

    return errors


def validate_login(data):

    errors = []

    if not data.get("email"):
        errors.append("Email is required")

    if not data.get("password"):
        errors.append("Password is required")

    return errors