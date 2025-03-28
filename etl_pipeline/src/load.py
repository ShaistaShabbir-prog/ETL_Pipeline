from database import get_db_session
from models import MyTable  # Import your ORM model
import pandas as pd

def load_data(df):
    """Loads cleaned data into the database."""
    with get_db_session() as session:  # Using the context manager
        try:
            # Convert 'salary' column to numeric (float), forcing errors to NaN
            df['salary'] = pd.to_numeric(df['salary'], errors='coerce')

            # Insert data into the database
            for _, row in df.iterrows():
                record = MyTable(
                    name=row["name"],
                    date_of_birth=row["date_of_birth"],
                    salary=row["salary"]  # Now 'salary' should be a numeric value
                )
                session.add(record)

            session.commit()  # Commit changes after all records are added
            print("✅ Data successfully inserted into the database.")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            session.rollback()  # Rollback in case of error
