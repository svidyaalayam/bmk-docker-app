def username_for_school_email(email, school):
    """Use the email itself as the username in a single-school deployment."""
    return (email or '').strip().lower()
