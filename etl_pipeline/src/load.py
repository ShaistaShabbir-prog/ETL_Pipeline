
from database import get_db_session
from models import Employees
import pandas as pd
from sqlalchemy import exists, Date
from datetime import datetime
from loguru import logger


def load_data(df):
    """Loads cleaned data into the database while avoiding duplicates."""
    with get_db_session() as session:  # Using the context manager
        try:
            # Convert 'salary' column to numeric (float), forcing errors to NaN
            df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

            # Ensure 'date_of_birth' is in the correct datetime format
            df["date_of_birth"] = pd.to_datetime(
                df["date_of_birth"], errors="coerce"
            ).dt.date

            # Drop rows where 'date_of_birth' is NaT (invalid or missing dates)
            df = df.dropna(subset=["date_of_birth"])

            for _, row in df.iterrows():
                # Check if the employee already exists (same name & date_of_birth)
                exists_query = session.query(
                    exists().where(
                        (Employees.name == row["name"])
                        & (
                            Employees.date_of_birth.cast(Date) == row["date_of_birth"]
                        )  # Cast to Date explicitly
                    )
                ).scalar()

                if not exists_query:
                    # Create a new employee record and add it to the session
                    record = Employees(
                        name=row["name"],
                        date_of_birth=row[
                            "date_of_birth"
                        ],  # Now it matches the Date type in DB
                        salary=row["salary"],  # Now 'salary' is a numeric value (float)
                    )
                    session.add(record)
                else:
                   logger.info(
                        f"⚠️ Skipping duplicate: {row['name']} ({row['date_of_birth']})"
                    )

            session.commit()  # Commit changes after all records are added
            logger.info("✅ Data successfully inserted into the database.")
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            session.rollback()  # Rollback in case of error
