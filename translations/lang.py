import os
import yaml

from database.db import databases, database_id, collection_id


class Language:
    @staticmethod
    def load_translation(language_code):
        path = os.path.join('translations', f'{language_code}.yaml')
        with open(path, 'r') as f:
            return yaml.safe_load(f)


async def get_translation(translation_key, default_value, update):
    user_id = update.effective_user.id
    lang = databases.get_document(database_id=database_id, collection_id=collection_id,
                                  document_id=str(user_id))

    language = lang.get('language', 'en')

    translations = Language.load_translation(language)

    translated_text = translations.get(translation_key, default_value)

    return translated_text
