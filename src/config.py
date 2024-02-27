import os

from dotenv import load_dotenv

load_dotenv()

db_url = os.environ["DATABASE_URL"]
secret_key = os.environ["SECRET_KEY"]
algorithm = os.environ["ALGORITHM"]
token_expire_time = os.environ["TOKEN_EXPIRE_TIME"]
