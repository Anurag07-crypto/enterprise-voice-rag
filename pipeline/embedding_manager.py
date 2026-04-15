from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np 
from .logger import get_logger

logger = get_logger(__name__)

# Code cleaning and logging and docstring required
class EmbeddingManager:
    """Embedding Manager to Embed the Given Files """
    
    def __init__(self,
                 model_name:str="BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self.model = None
        self._load_model()
    def _load_model(self):
        """Load The BAAI/bge-small-en-v1.5 Model in the Embedding Manager

        Raises:
            RuntimeError: Model not Loaded
            RuntimeError: Unexpected Error Loading
        """
        
        try:
            self.model = SentenceTransformer(
                self.model_name
            )
            logger.info(f"Model loaded successfully: {self.model_name}")
            
        except OSError as e:
            logger.error(f"model not loaded: {self.model_name}")
            raise RuntimeError(f"model not loaded: {self.model_name}") from e
        
        except Exception as e:
            logger.error(f"uxpexted error loading: {e}")
            raise RuntimeError(f"uxpexted error loading: {e}") from e            
    
    def generate_embeddings(self,
                            texts:List[str])->np.ndarray:
        """Generating Embeddings for the List of Texts

        Args:
            texts (List[str]): np.ndarray

        Raises:
            RuntimeError: Embeddings not Generated

        Returns:
            np.ndarray: Embeddings
        """
        try:
            embeddings = self.model.encode(texts)
            logger.info("Embeddings generated successfully")
            return embeddings
        
        except Exception as e:
            logger.critical(f"Embeddings not generated: {e}")
            raise RuntimeError(f"Embeddings not generated: {e}") from e
            
        