import pandas as pd

def read_csv_file(f, e='utf_8', s=';') -> pd.DataFrame:
    return pd.read_csv(f, encoding=e, sep=s)