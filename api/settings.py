import os


class Config:
    DATABASE_URI = os.getenv("DATABASE_URI")
    TESTING = False


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
