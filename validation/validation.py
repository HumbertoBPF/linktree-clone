import re

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,64}$"


def validate_email(value: str) -> str:
    if not re.fullmatch(EMAIL_REGEX, value):
        raise ValueError(f"Invalid email: {value}")
    return value


def validate_password(value: str) -> str:
    if not re.fullmatch(PASSWORD_REGEX, value):
        raise ValueError(f"Invalid password: {value}")
    return value
