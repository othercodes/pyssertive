from clean_pkg.domain import User


def get_user(user_id: int) -> User:
    return User(id=user_id)
