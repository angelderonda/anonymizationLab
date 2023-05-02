

import pandas as pd
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import Hash, SHA256
from cryptography.hazmat.primitives.hmac import HMAC
import os

#df = pd.read_csv("database/datos.csv")
def encrypt_column(data: pd.DataFrame, identifier_columns: 'list[str]'):
    key = Fernet.generate_key()
    f = Fernet(key)
    data = data.copy()
    for col in identifier_columns:
        series = data[col]
        to_replace = series.unique()
        replace_dict = {data: f.encrypt(str(data).encode("utf-8")).hex() for data in to_replace}
        series.replace(replace_dict, inplace=True)
    return data, key

def reverse_encryption(data: pd.DataFrame,  identifier_columns: 'list[str]', key: bytes):
    f = Fernet(key)
    data = data.copy()
    for col in identifier_columns:
        series = data[col]
        to_replace = series.unique()
        replace_dict = {data: f.decrypt(bytes.fromhex(data)).decode("utf-8") for data in to_replace}
        series.replace(replace_dict, inplace=True)
    return data


def hash(val: str, h: HMAC):
    h = h.copy()
    h.update(val.encode("utf-8"))
    return h.finalize().hex()

def deident_single_email(email: bytes, h: HMAC):
    user = email.split("@")[0]
    host = email.split("@")[1]
    return f"{hash(user, h)}@{hash(host, h)}"

def deident_email(data: pd.DataFrame, identifier_columns: 'list[str]'):
    data = data.copy()
    key = os.urandom(32)
    h = HMAC(key, SHA256())
    for col in identifier_columns:
        series = data[col]
        to_replace = series.unique()
        replace_dict = {data: deident_single_email(data, h) for data in to_replace}
        series.replace(replace_dict, inplace=True)
    return data, key
                        

    
# hash(df, ["nombre"])



