import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.exception import AppwriteException
from appwrite.services.databases import Databases

from plugins.helpers.logger import logger

try:
    load_dotenv()
except FileNotFoundError:
    logger.info("No .env file found. ignore if you are using a production bot [database]")

client = Client()

endpoint = os.environ.get("ENDPOINT", "")
client.set_endpoint(endpoint)

client.set_project(os.environ.get("PROJECT", ""))
client.set_key(os.environ.get("API_KEY", ""))

databases = Databases(client)

collection_id = os.environ.get("COLLECTION_ID", "")
database_id = os.environ.get("DATABASE_ID", "")


class DATABASE:
    @staticmethod
    async def create_doc(update):
        username = str(update.effective_user.username)
        user_id = str(update.effective_user.id)
        name = str(update.effective_user.full_name)

        data = {
            "user_id": user_id,
            "name": name,
            "username": username,
            "language": "en",
        }

        databases.create_document(database_id=database_id, collection_id=collection_id,
                                  document_id=str(user_id), data=data)

    @staticmethod
    async def update_doc(update):
        username = str(update.effective_user.username)
        user_id = update.effective_user.id

        data = {"username": username}

        databases.update_document(database_id=database_id, collection_id=collection_id,
                                  document_id=str(user_id), data=data)

    @staticmethod
    async def doc_exists(user_id):
        try:
            # Attempt to get the document
            databases.get_document(database_id=database_id, collection_id=collection_id,
                                   document_id=str(user_id))

            # Document exists
            return True
        except AppwriteException as e:
            # Document not found, handle the exception or return False
            logger.info(f"{e}")
            return False

    @staticmethod
    async def check_document_id(update):
        user_id = update.effective_user.id
        doc_exists = await DATABASE.doc_exists(user_id)

        if doc_exists:
            # Document exists, update doc
            await DATABASE.update_doc(update)
        else:
            # Document does not exist, Create New doc
            await DATABASE.create_doc(update)
