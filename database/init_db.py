import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from database.db import engine, Base
from database.models import MaritimeRecord


Base.metadata.create_all(bind=engine)

print("DATABASE CREATED SUCCESSFULLY")