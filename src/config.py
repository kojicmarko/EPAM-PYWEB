import os

from dotenv import load_dotenv

load_dotenv()

test_db_url = os.environ["TEST_DATABASE_URL"]
db_url = os.environ["DATABASE_URL"]
