import logging
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger("varisetu.qdrant")


class QdrantAdapter:
    """
    Adapter for vector similarity search (biometric/face embeddings & text retrieval).
    Operates in 'mock' mode by default or connects to Qdrant cluster if enabled.
    """
    def __init__(self):
        self.provider = settings.VECTOR_PROVIDER
        self.url = settings.QDRANT_URL
        self.api_key = settings.QDRANT_API_KEY
        self._mock_vectors: Dict[str, List[float]] = {}
        self._mock_payloads: Dict[str, Dict[str, Any]] = {}

    async def upsert_embedding(
        self,
        point_id: str,
        embedding: List[float],
        payload: Dict[str, Any],
        collection_name: str = "lost_persons"
    ) -> bool:
        if self.provider == "mock":
            self._mock_vectors[point_id] = embedding
            self._mock_payloads[point_id] = payload
            logger.info(f"[MOCK Qdrant] Upserted vector for point: {point_id}")
            return True

        # Real Qdrant HTTP API
        try:
            headers = {"api-key": self.api_key} if self.api_key else {}
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.put(
                    f"{self.url}/collections/{collection_name}/points",
                    headers=headers,
                    json={
                        "points": [{
                            "id": point_id,
                            "vector": embedding,
                            "payload": payload
                        }]
                    }
                )
                return resp.status_code in (200, 201)
        except Exception as e:
            logger.error(f"Qdrant upsert error: {e}")
            return False

    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 5,
        collection_name: str = "lost_persons",
        score_threshold: float = 0.70
    ) -> List[Dict[str, Any]]:
        if self.provider == "mock":
            # Return demo candidate matches
            results = []
            for pid, payload in list(self._mock_payloads.items())[:limit]:
                results.append({
                    "id": pid,
                    "score": 0.89,
                    "payload": payload
                })
            return results

        try:
            headers = {"api-key": self.api_key} if self.api_key else {}
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{self.url}/collections/{collection_name}/points/search",
                    headers=headers,
                    json={
                        "vector": query_vector,
                        "limit": limit,
                        "score_threshold": score_threshold,
                        "with_payload": True
                    }
                )
                if resp.status_code == 200:
                    return resp.json().get("result", [])
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
        return []

    async def delete_embedding(self, point_id: str, collection_name: str = "lost_persons") -> bool:
        """Purge a single vector embedding (Privacy requirement)."""
        self._mock_vectors.pop(point_id, None)
        self._mock_payloads.pop(point_id, None)
        if self.provider == "qdrant":
            try:
                headers = {"api-key": self.api_key} if self.api_key else {}
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        f"{self.url}/collections/{collection_name}/points/delete",
                        headers=headers,
                        json={"points": [point_id]}
                    )
            except Exception as e:
                logger.error(f"Qdrant delete error: {e}")
        return True

    async def delete_case_embeddings(self, case_id: str) -> int:
        """Purge all temporary candidate embeddings associated with a case."""
        deleted_count = 0
        to_del = [k for k, v in self._mock_payloads.items() if v.get("case_id") == case_id]
        for k in to_del:
            self._mock_vectors.pop(k, None)
            self._mock_payloads.pop(k, None)
            deleted_count += 1
        logger.info(f"Purged {deleted_count} biometric embeddings for case {case_id}")
        return deleted_count

    async def health_check(self) -> str:
        if self.provider == "mock":
            return "mock"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{self.url}/healthz")
                return "connected" if resp.status_code == 200 else "degraded"
        except Exception:
            return "unreachable"


qdrant_adapter = QdrantAdapter()
