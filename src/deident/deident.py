

import pandas as pd
from cryptography.fernet import Fernet

#df = pd.read_csv("database/datos.csv")
def encrypt_column(data: pd.DataFrame, identifier_columns: list[str]):
    key = Fernet.generate_key()
    f = Fernet(key)
    data = data.copy()
    for col in identifier_columns:
        series = data[col]
        to_replace = series.unique()
        replace_dict = {data: f.encrypt(str(data).encode("utf-8")) for data in to_replace}
        series.replace(replace_dict, inplace=True)
    return data, key

def reverse_encryption(data: pd.DataFrame,  identifier_columns: list[str], key: bytes):
    f = Fernet(key)
    data = data.copy()
    for col in identifier_columns:
        series = data[col]
        to_replace = series.unique()
        replace_dict = {data: f.decrypt(data).decode("utf-8") for data in to_replace}
        series.replace(replace_dict, inplace=True)
    return key, data

# hash(df, ["nombre"])



