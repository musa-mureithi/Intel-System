import faiss
import numpy as np
import json
from ..models import Person

# Global index
dimension = 128  
index = faiss.IndexFlatL2(dimension)

person_ids = []


def build_index():
    embeddings = []
    person_ids = []

    for person in Person.objects.all():
        if not person.face_embeddings:
            # Skip persons with no embeddings
            continue

        try:
            emb = np.array(json.loads(person.face_embeddings)).astype("float32")
        except (json.JSONDecodeError, TypeError) as e:
            # Skip invalid embeddings
            continue

        embeddings.append(emb)
        person_ids.append(person.id)

    if embeddings:
        # build your FAISS index here
        pass
    else:
        print("No valid embeddings found to build FAISS index.")

def search_face(query_embedding, k=1):
    if index.ntotal == 0:
        return None, None

    query = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query, k)

    idx = indices[0][0]
    distance = distances[0][0]

    if idx == -1:
        return None, None

    person_id = person_ids[idx]
    person = Person.objects.get(id=person_id)

    return person, float(distance)