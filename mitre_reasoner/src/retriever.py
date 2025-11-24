from .knowledge_base import MitreKnowledgeBase
from .models import MitreTechnique
from .utils import extract_technique_id

class MitreRetriever:
    def __init__(self, knowledge_base: MitreKnowledgeBase):
        self.kb = knowledge_base

    def search(self, query: str, k: int = 5) -> list[MitreTechnique]:
        """
        Performs semantic similarity search.
        Adapted from ProductSearchWrapper.predict in MITREembed.ipynb
        """
        if not self.kb.vectordb:
            self.kb.load_existing()

        # Perform search
        # MITREembed uses similarity_search_with_score
        results = self.kb.vectordb.similarity_search_with_score(query, k=k)

        techniques = []
        for doc, score in results:
            # Extract metadata
            metadata = doc.metadata
            
            # Map to Pydantic model
            tech = MitreTechnique(
                name=metadata.get('Subject', 'Unknown'),
                description=doc.page_content,
                url=metadata.get('filepath', ''),
                technique_id=extract_technique_id(metadata.get('filepath', '')),
                source=metadata.get('Source', 'Unknown'),
                score=float(score),

                # NEW FIELDS
                tactic=metadata.get("tactic"),
                kill_chain_phase=metadata.get("kill_chain_phase"),
                subtechnique_of=metadata.get("subtechnique_of")
            )

            techniques.append(tech)
            
        return techniques
