# Placeholder for any specific preprocessing if needed outside of the standard scaler
import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # Fill missing values or drop
    return df.dropna()
