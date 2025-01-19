import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, 'data')

GRANTS_DATA_DIR = os.path.join(DATA_DIR, 'grants')
ENROLLMENT_DATA_DIR = os.path.join(DATA_DIR, 'enrollments')

DATABASE_PATH = os.path.join(DATA_DIR, 'naec.db')
SEED_DIR = os.path.join(DATA_DIR, 'seed')