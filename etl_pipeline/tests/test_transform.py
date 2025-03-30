import pandas as pd
from src.transform import clean_data

def test_clean_data():
    df = pd.DataFrame({
        "name": ["John", "Jane", None, "Alice"],
        "date_of_birth": ["12/31/1990", "1992-06-15", "07-15-1985", "1988/03/20"],
        "salary": ["50000", "55000", "NaN", "NotANumber"]
    })
    
    df_clean = clean_data(df)
    
    assert df_clean.shape[0] == 2  # Only valid rows should remain
    assert df_clean["salary"].dtype == "float64"  # Salary should be numeric
