def send_verification_email(email):

    return {
        "success": True,
        "verification_code": "123456",
        "message": f"Dummy verification code sent to {email}"
    }


def send_reset_password(email):

    return {
        "success": True,
        "reset_code": "654321",
        "message": f"Dummy reset code sent to {email}"
    }