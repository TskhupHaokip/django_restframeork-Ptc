import keyring

class TokenStore:
    @staticmethod
    def save( token):
        keyring.set_password("myapp", "refresh", token)

    @staticmethod
    def load():
        return keyring.get_password("myapp", "refresh")
    @staticmethod
    def delete():
        keyring.delete_password("myapp", "refresh")
