from sentence_transformers import SentenceTransformer
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import faiss
import os
import pickle
from .config import Config


class WebRAG:
    def __init__(self):
        self.cfg = Config().load_config()
        self.index_path = self.cfg.get("rag", {}).get("index_path", "rag_index")
        self.model = SentenceTransformer(self.cfg.get("rag", {}).get("model_name", "all-MiniLM-L6-v2"))
        self.index = None
        self.chunks = []
        self.urls = []  # map chunks back to source URLs
        self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_path + ".faiss") and os.path.exists(self.index_path + ".pkl"):
            self.index = faiss.read_index(self.index_path + ".faiss")
            with open(self.index_path + ".pkl", "rb") as f:
                data = pickle.load(f)
                self.chunks = data.get("chunks", [])
                self.urls = data.get("urls", [])
                #self.chunks, self.urls = pickle.load(f)
        else:
            self.index = None
            self.chunks, self.urls = [], []

    def _save_index(self):
        faiss.write_index(self.index, self.index_path + ".faiss")
        data = {"chunks": self.chunks, "urls": self.urls}
        with open(self.index_path + ".pkl", "wb") as f:
            pickle.dump(data, f)

    def chunk_text(self, text, chunk_size=500, overlap=50):
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(len(words), start + chunk_size)
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    def add_document(self, text, url="local"):
        chunks = self.chunk_text(text)

        for chunk in chunks:
            embedding = self.model.encode([chunk], convert_to_numpy=True)

            if self.index is None:
                dim = embedding.shape[1]
                self.index = faiss.IndexFlatL2(dim)

            self.index.add(embedding)
            self.chunks.append(chunk)
            self.urls.append(url)

        self._save_index()

    def query(self, q, top_k=3, min_similarity=0.6):
        self._load_index()
        if self.index is None:
            return []
        embedding = self.model.encode([q], convert_to_numpy=True)
        distances, indices = self.index.search(embedding, top_k)
        results = []
        for dist, i in zip(distances[0], indices[0]):
            if i < len(self.chunks):
                # Convert FAISS L2 distance → cosine similarity approx
                similarity = 1 / (1 + dist)
                if similarity >= min_similarity:
                    results.append({"text": self.chunks[i], "url": self.urls[i]})
        return results


    def web_search_and_store(self, query, max_results=3):
        """Perform web search, fetch pages, and index them."""
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=max_results))
        for r in search_results:
            url = r.get("href")
            try:
                text = self.fetch_page(url)

                if text:
                    self.add_document(text, url)
            except Exception as e:
                print(f"⚠️ Failed to fetch {url}: {e}")
        return search_results

    def fetch_page(self, url: str) -> str:
        # Convert GitHub "blob" link → raw link
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        if "raw.githubusercontent.com" in url:
            # return raw file content directly
            return resp.text
        else:
            # fallback: parse with BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup.get_text(separator=" ", strip=True)
