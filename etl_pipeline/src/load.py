from database import get_db_session
from models import Employees
import pandas as pd
from sqlalchemy import exists


def load_data(df):
    """Loads cleaned data into the database while avoiding duplicates."""
    with get_db_session() as session:  # Using the context manager
        try:
            # Convert 'salary' column to numeric (float), forcing errors to NaN
            df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

            for _, row in df.iterrows():
                # Check if the employee already exists (same name & date_of_birth)
                exists_query = session.query(
                    exists().where(
                        (Employees.name == row["name"])
                        & (Employees.date_of_birth == row["date_of_birth"])
                    )
                ).scalar()

                if not exists_query:
                    record = Employees(
                        name=row["name"],
                        date_of_birth=row["date_of_birth"],
                        salary=row["salary"],  # Now 'salary' should be a numeric value
                    )
                    session.add(record)
                else:
                    print(
                        f"⚠️ Skipping duplicate: {row['name']} ({row['date_of_birth']})"
                    )

            session.commit()  # Commit changes after all records are added
            print("✅ Data successfully inserted into the database.")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            session.rollback()  # Rollback in case of error
