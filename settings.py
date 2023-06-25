"""File with settings and configs for the project"""

from envparse import Env

env = Env()

DATABASE_URL = env.str('DATABASE_URL')  # connect string for the database
