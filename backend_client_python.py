"""
VariSetu - backend client for the ML inference Hugging Face Space.

Install: pip install gradio_client

This replaces direct HTTP calls to a self-hosted API (Cloud Run version) with
calls through gradio_client, which speaks the Gradio Space API protocol.
Usage is otherwise the same shape as before.
"""

from gradio_client import Client, handle_file

SPACE_ID = "your-username/varisetu-ml-inference"   # replace with your actual Space repo id


class VariSetuMLClient:
    def __init__(self, space_id: str = SPACE_ID, hf_token: str = None):
        # hf_token is optional for a public Space, but including it gives you
        # better rate limits and is required if the Space is private.
        self.client = Client(space_id, hf_token=hf_token)

    def embed_query(self, image_path: str) -> dict:
        return self.client.predict(handle_file(image_path), api_name="/reid_embed_query")

    def rank_candidates(self, query_embedding: list, gallery: list, top_k: int = 10) -> list:
        return self.client.predict(query_embedding, gallery, top_k, api_name="/reid_rank_candidates")

    def verify_pair_reid(self, image_a_path: str, image_b_path: str) -> dict:
        return self.client.predict(handle_file(image_a_path), handle_file(image_b_path), api_name="/reid_verify_pair")

    def verify_pair_face(self, image_a_path: str, image_b_path: str) -> dict:
        return self.client.predict(handle_file(image_a_path), handle_file(image_b_path), api_name="/face_verify_pair")

    def lostfound_search(self, query_image_path: str, gallery: list, top_k: int = 10) -> list:
        import json
        return self.client.predict(
            handle_file(query_image_path), json.dumps(gallery), top_k,
            api_name="/lostfound_search",
        )

    def health(self) -> dict:
        return self.client.predict(api_name="/health")


if __name__ == "__main__":
    # quick manual smoke test
    ml = VariSetuMLClient()
    print(ml.health())
