# ETL Pipeline with Data Quality Controls

This project implements an ETL (Extract, Transform, Load) pipeline with data quality controls using Python. The pipeline extracts data from a CSV file, transforms it by cleaning and validating it, and loads it into a PostgreSQL database. Additionally, it includes logging and error handling to ensure data integrity.

## Project Structure

```
etl_pipeline/
│── data/                     # Sample input CSV files
│── logs/                     # Log files
│── config/                   # Configuration files
│   ├── config.yaml           # Database and ETL settings
│── src/                      # Main source code
│   ├── __init__.py           # Package initializer
│   ├── extract.py            # Extraction logic
│   ├── transform.py          # Data cleaning & transformation logic
│   ├── load.py               # Database loading logic
│   ├── database.py           # DB connection utilities
│   ├── logging_config.py     # Logging setup
│   ├── main.py               # Main ETL runner
│── tests/                    # Unit tests
│── Dockerfile                # Docker setup for the Python application
│── docker-compose.yml        # PostgreSQL container setup
│── requirements.txt          # Dependencies
│── README.md                 # Setup and usage instructions
│── .env                      # Environment variables (e.g., DB credentials)
```

## Features

- **Data Extraction**: Extracts data from a CSV file.
- **Data Transformation**:
  - Standardizes date formats.
  - Handles missing values.
  - Removes duplicate records.
  - Validates data types (e.g., ensures numeric fields contain only numbers).
- **Data Loading**: Loads the cleaned data into a PostgreSQL database.
- **Data Quality Controls**: Logs any inconsistencies or errors during the extraction, transformation, and loading processes.
- **Dockerized Setup**: Includes a `docker-compose.yml` file to spin up a PostgreSQL instance for testing.

## Requirements

- Python 3.x
- Docker (for running PostgreSQL container)
- PostgreSQL 12+ (used in Dockerized environment)

### Dependencies

The dependencies for this project are listed in `requirements.txt`. You can install them using:

```bash
pip install -r requirements.txt
```

### Docker Setup

This project uses Docker to spin up a PostgreSQL database container. Follow these steps to set it up:

1. **Build and Start the Docker Containers**:

   ```bash
   docker-compose up --build
   ```

   This will:
   - Build the Docker image for the Python application.
   - Start the PostgreSQL container with the appropriate environment variables.

2. **Verify the Database Connection**:

   ```bash
   docker exec -it etl_postgres psql -U admin -d etl_db
   ```

   This will open a `psql` session connected to the `etl_db` database.

## Configuration

You need to configure the database connection details in `config/config.yaml`:

```yaml
database:
  user: admin
  password: yourpassword
  host: localhost
  port: 5432
  db_name: etl_db

etl:
  data:
    sample_data.csv: "data/sample_data.csv"
```

Make sure the file `data/sample_data.csv` exists in the `data` directory and contains the sample data for testing.

## Running the ETL Pipeline

To run the ETL pipeline, execute the following command:

```bash
python src/main.py
```

### Logging

Logs for the ETL process are stored in the `logs/` directory. You can inspect the logs to monitor the process and check for any errors.

## Testing

Unit tests are located in the `tests/` directory. To run the tests, use:

```bash
pytest
```

## Assumptions

- The CSV file (`sample_data.csv`) is assumed to have columns that are validated in the ETL process.
- The PostgreSQL instance is set up with the credentials provided in `config/config.yaml`.

## Notes

- Make sure that you have the required Python version and Docker installed to run this project smoothly.
- Ensure that the `sample_data.csv` file is correctly formatted as expected by the script.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

