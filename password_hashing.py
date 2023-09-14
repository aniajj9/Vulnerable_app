import hashlib

class PasswordHash:

    def __init__(self, hash_algorithm) -> None:
        self.__hash_algorithm = hash_algorithm

    def hash_password(self, password):
        # Hash the password using the specified algorithm
        hash_obj = hashlib.new(self.__hash_algorithm)
        hash_obj.update(password.encode('utf-8'))
        return hash_obj.hexdigest()

    def verify_password(self, hashed_password, password):
        # Verify a password against its hashed version using the specified algorithm
        return hashed_password == self.hash_password(password)
