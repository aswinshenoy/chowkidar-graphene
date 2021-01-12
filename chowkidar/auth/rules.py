
def check_if_user_is_allowed_to_login(user) -> bool:
    return True


def check_if_other_tokens_need_to_be_revoked(user) -> bool:
    return False


__all__ = [
    'check_if_user_is_allowed_to_login',
    'check_if_other_tokens_need_to_be_revoked'
]
