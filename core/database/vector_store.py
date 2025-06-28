"""
Vector database operations using ChromaDB
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from core.simple_config import settings
from core.embeddings.kure_embeddings import KUREEmbeddings

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """ChromaDB vector store manager"""
    
    def __init__(self):
        # Ensure the persist directory exists
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize KURE embeddings
        self.embeddings = KUREEmbeddings()
        
        # Create or get collection
        self.collection_name = "legal_documents"
        try:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Legal documents vector store"}
            )
        except Exception:
            # Collection already exists
            self.collection = self.client.get_collection(name=self.collection_name)
        
        logger.info(f"Vector store initialized with collection: {self.collection_name}")
    
    def add_document(
        self, 
        document_id: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add document to vector store"""
        try:
            # Generate embedding
            embedding = self.embeddings.embed_text(content)
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata or {}],
                ids=[document_id]
            )
            
            logger.info(f"Document {document_id} added to vector store")
            return True
        except Exception as e:
            logger.error(f"Error adding document {document_id}: {e}")
            return False
    
    def add_documents_batch(
        self, 
        document_ids: List[str], 
        contents: List[str], 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Add multiple documents to vector store"""
        try:
            # Generate embeddings
            embeddings = self.embeddings.embed_texts(contents)
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas or [{}] * len(contents),
                ids=document_ids
            )
            
            logger.info(f"Added {len(document_ids)} documents to vector store")
            return True
        except Exception as e:
            logger.error(f"Error adding documents batch: {e}")
            return False
    
    def search_documents(
        self, 
        query: str, 
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search documents using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_text(query)
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1 - results["distances"][0][i]  # Convert distance to similarity score
                })
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def hybrid_search(
        self, 
        query: str, 
        document_ids: List[str],
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining vector similarity and document filtering"""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_text(query)
            
            # Create where clause for document filtering
            where_clause = {"id": {"$in": document_ids}} if document_ids else None
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1 - results["distances"][0][i]
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    def update_document(
        self, 
        document_id: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update document in vector store"""
        try:
            # Delete existing document
            self.delete_document(document_id)
            
            # Add updated document
            return self.add_document(document_id, content, metadata)
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document from vector store"""
        try:
            self.collection.delete(ids=[document_id])
            logger.info(f"Document {document_id} deleted from vector store")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "persist_directory": settings.chroma_persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def reset_collection(self) -> bool:
        """Reset (clear) the collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Legal documents vector store"}
            )
            logger.info("Vector store collection reset")
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False


# Global vector store manager instance
vector_store = VectorStoreManager() 