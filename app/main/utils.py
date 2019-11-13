from datetime import datetime

from hashlib import md5
from base64 import b64decode
from base64 import b64encode

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def getDateTime():
    return str(datetime.now())


def getFileName(s):
    result = s
    result = result.replace(" ", "")
    result = result.replace("-", "")
    result = result.replace(":", "")
    result = result.replace(".", "")
    return result


def decrypt(data):
    part = data.split(":")
    raw = b64decode(part[0])
    cipher = AES.new(b'11d61bf42bc9bdfce40bcd73458b373f',
                     AES.MODE_CBC, b64decode(part[1]))
    return unpad(cipher.decrypt(raw), AES.block_size).decode('utf-8')


def encrypt(data):
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(b'11d61bf42bc9bdfce40bcd73458b373f', AES.MODE_CBC, iv)
    return b64encode(iv).decode("utf-8") + ":" + b64encode(cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))).decode("utf-8")
