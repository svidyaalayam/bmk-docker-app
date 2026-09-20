import hashlib


def username_for_school_email(email, school):
    """Build the private, globally unique username for a school email address."""
    normalized_email = (email or '').strip().lower()
    local, separator, domain = normalized_email.partition('@')
    school_suffix = f'--{school.school_number}'
    if not separator:
        return f'{normalized_email[:150 - len(school_suffix)]}{school_suffix}'

    available_local_length = 150 - len(school_suffix) - len(separator) - len(domain)
    if available_local_length < len(local):
        # Keep a digest when shortening unusually long addresses to avoid collisions.
        digest = hashlib.sha256(normalized_email.encode()).hexdigest()[:10]
        available_local_length -= len(digest) + 1
        local = f'{local[:max(1, available_local_length)]}-{digest}'
    return f'{local}{school_suffix}{separator}{domain}'
