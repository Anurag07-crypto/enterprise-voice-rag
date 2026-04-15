from langchain_community.document_loaders import TextLoader, DirectoryLoader
from pathlib import Path
from .logger import get_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = get_logger(__name__)
DirectoryPath = Path(__file__).parent.parent / "data" / "company_files"

def file_loader(DirectoryPath = DirectoryPath):
    Dir_loader = DirectoryLoader(
    path=DirectoryPath,
    glob="**/*.txt",
    loader_cls=TextLoader
)
    """
    File Loader to Load Directory Files using the File Path

    Raises:
        RuntimeError: File not Loaded SuccessFully
        RuntimeError: Unexpected Error Found

    Returns:
        _type_: File_loader
    """
    try:
        load = Dir_loader.load()
        logger.info("File Loaded successfully")
        return load 
    
    except FileNotFoundError as e:
        logger.error(f"File not loaded successfully: {e}")
        raise RuntimeError(f"File not found: {e}") from e
    
    except Exception as e:
        logger.critical(f"Unexpected error found: {e}")
        raise RuntimeError(f"Unexpected error found: {e}") from e
    
def splitter(document=file_loader(),
             chunk_size:int = 1000,
             chunk_overlap:int = 200):
    
    """
    A Document Splitter for Splitting Documents into Chunks
    Args:
        document (Text_format):  Defaults to file_loader().
        chunk_size (int):  Defaults to 1000.
        chunk_overlap (int):  Defaults to 200.

    Returns:
        Splitted Docs: Chunks of Provided Docs
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function = len,
        separators=["\n\n","\n",""]
    )
    
    split_docs = text_splitter.split_documents(document)
    logger.info("File Splitted successfully")
    return split_docs
