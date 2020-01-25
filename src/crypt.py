"""
crypt: simple password encryption / decryption

Created: Sun Jan  5 2020
"""
__version__ = '0.1.0'
__author__ = 'Torbjørn Pettersen <torbjorn.pettersen@outlook.com>'

import ucryptolib
import ubinascii


def _to16(seed):
    """Convert a seed to a nx16 byte string."""
    return seed + " " * (16 - len(seed) % 16)


class Crypt:
    """Simple encryption/decryption of tekst.

    Usage:
    ------
    cipher = Crypt("secret seed")
    coded = cipher.encode("Message")
    decoded = cipher.decrypt(coded)
    """
    def __init__(self, seed):
        """Initsialise based on seed."""
        self.seed = _to16(seed.encode())
        self.en = ucryptolib.aes(self.seed, 1)
        self.de = ucryptolib.aes(self.seed, 1)

    def encrypt(self, password):
        """Encrypt password."""
        en_pwd = self.en.encrypt(_to16(password))
        ascii_pwd = ubinascii.hexlify(en_pwd)
        return ascii_pwd.decode()

    def decrypt(self, ascii_pwd):
        """Decrypt password."""
        en_pwd = ubinascii.unhexlify(ascii_pwd.encode())
        pwd = self.de.decrypt(en_pwd).decode()
        return pwd.strip()
