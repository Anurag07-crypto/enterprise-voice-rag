from .embedding_manager import EmbeddingManager
from .vector_db import VectorStore
from typing import List, Dict, Any
from .logger import get_logger


logger = get_logger(__name__)

class Retriever:
    
    
    def __init__(self,
                 Embedding_Manager:EmbeddingManager,
                 Vector_Store:VectorStore):
        
        self.Embedding_Manager = Embedding_Manager
        self.Vector_Store = Vector_Store
    
    def retrieve(self,
                 query:str,
                 top_k:int=5,
                 threshold:float=0.2) -> List[Dict[str, Any]]:
        try:
            query_embeddings = self.Embedding_Manager.generate_embeddings([query])[0]
            results = self.Vector_Store.collection.query(
                query_embeddings=query_embeddings,
                n_results=top_k,
                include = ["metadatas", "documents", "distances"]
            )

            retrieved_docs = []
            
            if results["documents"] and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]
                ids = results["ids"][0]
                
                for i, (doc_id, document, metadata, distance) in enumerate(
                    zip(ids, documents, metadatas, distances)
                ):
                    similarity_score = 1 - distance

                    if similarity_score < threshold:
                        continue

                    retrieved_docs.append(
                        {
                            "id": doc_id,
                            "content": document,
                            "metadata": metadata,
                            "similarity_score": similarity_score,
                            "distance": distance,
                            "rank": i + 1,
                        }
                    )

            if not retrieved_docs:
                logger.critical("No documents found")

            logger.info(
                f"Retrieved {len(retrieved_docs)} documents"
            )
            return retrieved_docs

        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return []
