"""
LegalLens - Vector Store & Retrieval Module
Persistent ChromaDB instance seeded with Legal Risk Benchmarks from risk_playbook.json.
Uses Sentence-Transformers ("all-MiniLM-L6-v2") for semantic similarity search.
"""

# [Summary]: Local ChromaDB vector store + sentence-transformers for legal RAG search.

import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("LegalLens.VectorStore")

DEFAULT_DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_legal_db"))
DEFAULT_PLAYBOOK_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "risk_playbook.json"))
COLLECTION_NAME = "legal_risk_playbook"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


class LegalVectorStore:
    """Manages persistent ChromaDB vector storage and semantic search."""

    def __init__(self, db_path: str = DEFAULT_DB_DIR, playbook_path: str = DEFAULT_PLAYBOOK_PATH):
        self.db_path = db_path
        self.playbook_path = playbook_path
        self.client = None
        self.embedding_fn = None
        self.collection = None

        self._initialize_chroma()

    def _initialize_chroma(self):
        """Inits persistent storage in chroma_legal_db/ and loads all-MiniLM-L6-v2 embeddings."""
        import chromadb
        from chromadb.utils import embedding_functions

        logger.info(f"Initializing ChromaDB storage at: {self.db_path}")
        os.makedirs(self.db_path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.db_path)

        try:
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=EMBEDDING_MODEL_NAME
            )
        except Exception as e:
            logger.warning(f"Embedding error: {e}. Using default.")
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"description": "Legal benchmark clauses with risk tiers and citations"}
        )

        self.seed_from_playbook(force=False)

    def seed_from_playbook(self, force: bool = False) -> int:
        """Seeds ChromaDB with 20 Indian statutory benchmarks from risk_playbook.json."""
        if self.collection is None:
            raise RuntimeError("ChromaDB collection is not initialized.")

        existing_count = self.collection.count()
        if existing_count > 0 and not force:
            logger.info(f"Playbook already seeded with {existing_count} benchmark clauses.")
            return existing_count

        if not os.path.exists(self.playbook_path):
            logger.warning(f"Playbook file not found at {self.playbook_path}. Skipping seed.")
            return 0

        logger.info(f"Seeding ChromaDB collection from {self.playbook_path} (force={force})...")
        with open(self.playbook_path, "r", encoding="utf-8") as f:
            benchmarks: List[Dict[str, Any]] = json.load(f)

        ids = []
        documents = []
        metadatas = []

        for item in benchmarks:
            clause_id = item["id"]
            clause_text = item["clause_text"]
            indicators_str = "; ".join(item.get("predatory_indicators", []))

            metadata = {
                "clause_id": clause_id,
                "title": item.get("title", ""),
                "category": item.get("category", "General"),
                "risk_tier": item.get("risk_tier", "Moderate Risk"),
                "risk_score": int(item.get("risk_score", 5)),
                "explanation": item.get("explanation", ""),
                "recommended_countermeasure": item.get("recommended_countermeasure", ""),
                "grounded_legal_standard": item.get("grounded_legal_standard", ""),
                "predatory_indicators": indicators_str
            }

            ids.append(clause_id)
            documents.append(clause_text)
            metadatas.append(metadata)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        new_count = self.collection.count()
        logger.info(f"Successfully seeded ChromaDB with {new_count} benchmark clauses.")
        return new_count

    def query_similar_benchmarks(self, query_text: str, n_results: int = 2) -> List[Dict[str, Any]]:
        """Computes semantic similarity between a contract clause and legal benchmarks."""
        if self.collection is None:
            return []

        if not query_text or len(query_text.strip()) < 10:
            return []

        try:
            total_items = self.collection.count()
            k = min(n_results, total_items) if total_items > 0 else 0
            if k == 0:
                return []

            results = self.collection.query(
                query_texts=[query_text],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )

            matches = []
            if results and results.get("ids") and len(results["ids"]) > 0:
                doc_ids = results["ids"][0]
                docs = results["documents"][0]
                metas = results["metadatas"][0]
                distances = results["distances"][0] if results.get("distances") else [0.0] * len(doc_ids)

                for cid, doc, meta, dist in zip(doc_ids, docs, metas, distances):
                    similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                    matches.append({
                        "id": cid,
                        "benchmark_text": doc,
                        "title": meta.get("title", ""),
                        "category": meta.get("category", ""),
                        "risk_tier": meta.get("risk_tier", ""),
                        "risk_score": meta.get("risk_score", 0),
                        "explanation": meta.get("explanation", ""),
                        "recommended_countermeasure": meta.get("recommended_countermeasure", ""),
                        "grounded_legal_standard": meta.get("grounded_legal_standard", ""),
                        "predatory_indicators": meta.get("predatory_indicators", "").split("; ") if meta.get("predatory_indicators") else [],
                        "distance": round(float(dist), 4),
                        "similarity_score": round(float(similarity), 4)
                    })

            return matches
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []

    def batch_query_benchmarks(self, query_texts: List[str], n_results: int = 1) -> List[List[Dict[str, Any]]]:
        """Parallel batch search: retrieves closest benchmark for all clauses in ~30ms."""
        if self.collection is None or not query_texts:
            return [[] for _ in query_texts]

        try:
            total_items = self.collection.count()
            k = min(n_results, total_items) if total_items > 0 else 0
            if k == 0:
                return [[] for _ in query_texts]

            # Filter out empty strings for safety
            safe_queries = [q if q and len(q.strip()) > 5 else "commercial contract clause" for q in query_texts]

            results = self.collection.query(
                query_texts=safe_queries,
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )

            all_batch_matches = []
            if results and results.get("ids"):
                for i in range(len(query_texts)):
                    doc_ids = results["ids"][i]
                    docs = results["documents"][i]
                    metas = results["metadatas"][i]
                    distances = results["distances"][i] if results.get("distances") else [0.0] * len(doc_ids)

                    chunk_matches = []
                    for cid, doc, meta, dist in zip(doc_ids, docs, metas, distances):
                        similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                        chunk_matches.append({
                            "id": cid,
                            "benchmark_text": doc,
                            "title": meta.get("title", ""),
                            "category": meta.get("category", ""),
                            "risk_tier": meta.get("risk_tier", ""),
                            "risk_score": meta.get("risk_score", 0),
                            "explanation": meta.get("explanation", ""),
                            "recommended_countermeasure": meta.get("recommended_countermeasure", ""),
                            "grounded_legal_standard": meta.get("grounded_legal_standard", ""),
                            "predatory_indicators": meta.get("predatory_indicators", "").split("; ") if meta.get("predatory_indicators") else [],
                            "distance": round(float(dist), 4),
                            "similarity_score": round(float(similarity), 4)
                        })
                    all_batch_matches.append(chunk_matches)
            else:
                all_batch_matches = [[] for _ in query_texts]

            return all_batch_matches
        except Exception as e:
            logger.error(f"Error in batch query ChromaDB: {e}")
            return [self.query_similar_benchmarks(q, n_results=n_results) for q in query_texts]

    def get_all_benchmarks(self) -> List[Dict[str, Any]]:
        """
        Retrieves all benchmark clauses currently stored in the vector collection.
        Useful for dashboard inspection and playbook maintenance.
        """
        if self.collection is None:
            return []

        try:
            all_records = self.collection.get(include=["documents", "metadatas"])
            results = []
            if all_records and all_records.get("ids"):
                for cid, doc, meta in zip(all_records["ids"], all_records["documents"], all_records["metadatas"]):
                    results.append({
                        "id": cid,
                        "clause_text": doc,
                        "title": meta.get("title", ""),
                        "category": meta.get("category", ""),
                        "risk_tier": meta.get("risk_tier", ""),
                        "risk_score": meta.get("risk_score", 0),
                        "explanation": meta.get("explanation", ""),
                        "recommended_countermeasure": meta.get("recommended_countermeasure", ""),
                        "grounded_legal_standard": meta.get("grounded_legal_standard", ""),
                        "predatory_indicators": meta.get("predatory_indicators", "").split("; ") if meta.get("predatory_indicators") else []
                    })
            return sorted(results, key=lambda x: x["risk_score"], reverse=True)
        except Exception as e:
            logger.error(f"Error fetching all benchmarks: {e}")
            return []
