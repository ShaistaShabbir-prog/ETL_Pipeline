from database import get_db_session
from models import MyTable  # Import your ORM model


def load_data(df):
    """Loads cleaned data into the database."""
    with get_db_session() as session:  # Using the context manager
        try:
            # Insert data into the database
            for _, row in df.iterrows():
                record = MyTable(
                    column1=row["col1"], column2=row["col2"]
                )  # Adjust columns
                session.add(record)

            print("✅ Data successfully inserted into the database.")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
