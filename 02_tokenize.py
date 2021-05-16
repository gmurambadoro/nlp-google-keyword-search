import datetime
import sys

import nltk
import spacy
from bson import ObjectId

from database import collection, database
from keywords import keywords

nlp = spacy.load("en_core_web_sm")

for keyword in keywords:
    # find docs that match this keyword
    docs = collection.find({'keyword': keyword})

    full_text_list = list()

    for doc in docs:
        text_clean = str(doc['full_text'] or '').strip().lower().replace('\n', '')
        doc['full_text_clean'] = text_clean
        collection.update_one({'_id': ObjectId(doc['_id'])}, {'$set': {'full_text_clean': text_clean}})
        full_text_list.append(text_clean)

    kw_collection = database.get_collection('keywords')

    document = kw_collection.find_one({'keyword': keyword})

    if not document:
        document = dict()
        document['keyword'] = keyword
        document['created_at'] = datetime.datetime.now()

        kw_collection.insert_one(document=document)

    text: str = " ".join(full_text_list)

    # process the document
    doc = nlp(text)
    print(doc)
    sys.exit(1)

    kw_collection.update_one({'_id': ObjectId(document['_id'])}, {'$set': {'full_text': text, 'updated_at': datetime.datetime.now()}})

