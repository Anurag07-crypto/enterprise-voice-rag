from chromadb import PersistentClient
from typing import List, Any
from pathlib import Path
import os
import numpy as np 
import uuid
from .logger import get_logger


logger = get_logger(__name__)
persistant_path = Path(__file__).parent.parent / "data" / "vector_database"

class VectorStore:
    def __init__(self,
                 persistant_dir= persistant_path,
                 collection_name:str = "Text_files"):
        self.persistant_dir = persistant_dir
        self.collection_name = collection_name
        self.client = None
        self._initialize_store()
    
    def _initialize_store(self):
        try:
            os.makedirs(self.persistant_dir, exist_ok=True)
            self.client = PersistentClient(self.persistant_dir)
            self.collection = self.client.get_or_create_collection(
                name = self.collection_name,
                metadata = {"description": "Text files embedding for voice RAG"}
            )
            logger.info(f"VectorStore Initialized: collection_name - {self.collection_name}")
            
        except Exception as e:
            logger.error("Store Not Initialized: ", e)
            raise RuntimeError("Store Not Initialized: ", e) from e
    
    def add_documents(self,
                      documents:List[Any],
                      embeddings:np.ndarray):
        if len(documents)!=len(embeddings):
            logger.critical("Length of documents and embeddings should be same")
            
        ids = []
        metadatas = []
        document_texts = []
        embeddings_list = []
        
        for i, (document, embedding) in enumerate(zip(documents, embeddings)):
            doc_id = f"doc_{uuid.uuid4().hex[:50]}_{i}"
            metadata = dict(document.metadata)
            ids.append(doc_id)
            metadata["index"] = i
            metadata["context_length"] = len(document.page_content)
            metadatas.append(metadata)
            document_texts.append(document.page_content)
            embeddings_list.append(embedding.tolist())
        
        try:
            self.collection.add(
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=document_texts,
                ids=ids
            )
            logger.info(f"{len(ids)} documents added to ChromaDB")
        
        except Exception as e:
            logger.critical(f"Documents not loaded in ChromaDB: {e}")
            raise RuntimeError(f"Documents not loaded in ChromaDB: {e}") from e