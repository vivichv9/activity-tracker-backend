from email_validator import validate_email, EmailNotValidError

def validate_email_address(email):
    try:
        validate_email(email)
        return True

    except EmailNotValidError as e:
        print(f"Invalid email: {e}")
        return False