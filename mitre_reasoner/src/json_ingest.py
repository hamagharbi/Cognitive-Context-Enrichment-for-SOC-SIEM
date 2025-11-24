import json
import os
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from .embeddings import get_embedding_function


def safe_value(v):
    """Ensure metadata values are Chroma-compatible."""
    if isinstance(v, (list, dict)):
        return json.dumps(v)        # convert complex types → string
    return v


def ingest_mitre_json(json_path: str, persist_dir: str = "./chroma_db"):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Could not find {json_path}")

    print(f"Loading MITRE ATT&CK JSON from {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    objects = data.get("objects", [])
    print(f"Found {len(objects)} STIX objects")

    documents = []
    embedding_fn = get_embedding_function()

    for obj in objects:
        if obj.get("type") != "attack-pattern":
            continue

        # -------------------------------
        # Extract technique ID + URL
        # -------------------------------
        technique_id = None
        url = None

        for ref in obj.get("external_references", []):
            if ref.get("source_name") == "mitre-attack":
                technique_id = ref.get("external_id")
                url = ref.get("url")

        if not technique_id:
            continue

        # -------------------------------
        # Extract tactic & kill chain phase(s)
        # -------------------------------
        kill_chain_phases = obj.get("kill_chain_phases", [])
        tactics = list({phase.get("phase_name") for phase in kill_chain_phases})

        # -------------------------------
        # Extract technique name
        # -------------------------------
        name = obj.get("name", "Unknown Technique")

        # -------------------------------
        # Subtechnique detection (e.g., T1059.001 → parent T1059)
        # -------------------------------
        subtechnique_of = None
        if "." in technique_id:
            subtechnique_of = technique_id.split(".")[0]

        # -------------------------------
        # Description becomes the embedding text
        # -------------------------------
        description = obj.get("description", "No description available.")

        # -------------------------------
        # Safe metadata for Chroma
        # -------------------------------
        metadata = {
            "id": technique_id,
            "name": name,
            "url": url,
            "source": "MITRE_ATT&CK",
            "tactic": safe_value(tactics),
            "kill_chain_phase": safe_value([p.get("phase_name") for p in kill_chain_phases]),
            "subtechnique_of": safe_value(subtechnique_of)
        }

        documents.append(
            Document(page_content=description, metadata=metadata)
        )

    print(f"Preparing to ingest {len(documents)} techniques into ChromaDB...")

    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embedding_fn,
        persist_directory=persist_dir
    )

    print("Ingestion complete. Vector store updated.")
