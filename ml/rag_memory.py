from langchain_community.vectorstores import FAISS
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain.docstore.document import Document

class VectorMemory:
    def __init__(self):
        self.embeddings = NVIDIAEmbeddings(model="nvidia/nv-embed-v1", api_key=os.getenv("NVIDIA_API_KEY"))
        self.store = FAISS.from_texts([], self.embeddings)

    def add_entry(self, sensor, score, values, timestamp):
        doc = Document(
            page_content=f"{sensor} at {timestamp}: avg={sum(values)/len(values):.2f}, anomaly={score:.4f}",
            metadata={"sensor": sensor, "timestamp": str(timestamp), "score": score}
        )
        self.store.add_documents([doc])

    def query(self, query_text):
        return self.store.similarity_search(query_text, k=3)

