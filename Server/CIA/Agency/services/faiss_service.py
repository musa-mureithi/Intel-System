
import faiss
import numpy as np
import json
from ..models import Person

# Global FAISS index
index = None
person_ids = []
dimension = None


def build_index():

    global index, person_ids, dimension

    embeddings = []
    new_person_ids = []

    print("BUILDING FACE INDEX...", flush=True)

    for person in Person.objects.all():

        if not person.face_embeddings:
            continue

        try:
            embedding = np.array(
                json.loads(person.face_embeddings),
                dtype="float32"
            ).reshape(-1)

            if not np.all(np.isfinite(embedding)):
                continue

            if len(embedding) == 0:
                continue

            embeddings.append(embedding)
            new_person_ids.append(person.id)

        except (ValueError, TypeError, json.JSONDecodeError) as e:
            print(
                f"Invalid embedding for person ID {person.id}: {e}",
                flush=True
            )
            continue

    if not embeddings:

        index = None
        person_ids = []
        dimension = None

        print("NO VALID FACE EMBEDDINGS FOUND.", flush=True)
        return

    # Determine dimension from stored embeddings
    dimension = len(embeddings[0])

    # Ensure every embedding has the same dimension
    valid_embeddings = []
    valid_person_ids = []

    for embedding, person_id in zip(embeddings, new_person_ids):

        if len(embedding) == dimension:

            valid_embeddings.append(embedding)
            valid_person_ids.append(person_id)

    if not valid_embeddings:
        index = None
        person_ids = []
        dimension = None
        return

    # Create FAISS index using actual embedding dimension
    new_index = faiss.IndexFlatL2(dimension)

    embedding_matrix = np.vstack(valid_embeddings).astype("float32")

    # Add embeddings to FAISS
    new_index.add(embedding_matrix)

    # Update global variables
    index = new_index
    person_ids = valid_person_ids

    print("FAISS INDEX BUILT SUCCESSFULLY", flush=True)
    print("EMBEDDING DIMENSION:", dimension, flush=True)
    print("TOTAL EMBEDDINGS:", index.ntotal, flush=True)


def search_face(query_embedding, k=1):

    global index, person_ids, dimension

    # Build index if it has not yet been initialized
    if index is None or index.ntotal == 0:
        build_index()

    if index is None or index.ntotal == 0:
        print("FAISS INDEX IS EMPTY", flush=True)
        return None, None

    query = np.asarray(
        query_embedding,
        dtype="float32"
    ).reshape(1, -1)

    # Check dimensions
    if query.shape[1] != dimension:

        print(
            f"EMBEDDING DIMENSION MISMATCH: "
            f"Query={query.shape[1]}, Index={dimension}",
            flush=True
        )

        return None, None

    # Search nearest face
    distances, indices = index.search(
        query,
        min(k, index.ntotal)
    )

    idx = int(indices[0][0])
    distance = float(distances[0][0])

    if idx == -1:
        return None, None

    person_id = person_ids[idx]

    person = Person.objects.filter(id=person_id).first()

    if not person:
        return None, distance

    print("CLOSEST PERSON ID:", person_id, flush=True)
    print("FACE DISTANCE:", distance, flush=True)

    return person, distance
