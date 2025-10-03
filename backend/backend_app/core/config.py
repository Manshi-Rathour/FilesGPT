import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.PROJECT_NAME = os.getenv("PROJECT_NAME", "pdfGpt")

        # MongoDB
        self.MONGO_URI = os.getenv("MONGO_URI")
        self.MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "pdfGpt")
        if not self.MONGO_URI:
            raise Exception("MONGO_URI not set in .env!")

        # JWT
        self.JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
        self.JWT_ALG = os.getenv("JWT_ALG", "HS256")
        self.JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "1440"))

        # Cloudinary
        self.CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
        self.CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
        self.CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

        # CORS
        self.CLIENT_URL = os.getenv("CLIENT_URL", "http://localhost:5173")

        # Pinecone
        self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        self.PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
        self.PINECONE_INDEX = os.getenv("PINECONE_INDEX", "pdfgpt")

        # OpenAI
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


settings = Settings()
