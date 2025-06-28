"""
Document retrieval nodes for LangGraph
"""
import logging
from typing import Dict, List, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document

from core.database.sqlite import db_manager
from core.database.vector_store import vector_store
from core.embeddings.reranker import BGEReranker

logger = logging.getLogger(__name__)


class RetrievalState(TypedDict):
    """State for retrieval workflow"""
    query: str
    document_types: Optional[List[str]]
    categories: Optional[List[str]]
    limit: int
    postgres_results: List[Dict[str, Any]]
    vector_results: List[Dict[str, Any]]
    hybrid_results: List[Dict[str, Any]]
    reranked_results: List[Dict[str, Any]]
    final_results: List[Dict[str, Any]]
    error: Optional[str]


class RetrievalNode:
    """Node for document retrieval operations"""
    
    def __init__(self):
        self.reranker = BGEReranker()
    
    def search_postgres(self, state: RetrievalState) -> RetrievalState:
        """Search documents in PostgreSQL"""
        try:
            logger.info(f"Searching PostgreSQL for query: {state['query']}")
            
            # Search in PostgreSQL
            documents = db_manager.search_documents(
                query=state["query"],
                document_types=state.get("document_types"),
                categories=state.get("categories"),
                limit=state.get("limit", 20)
            )
            
            # Convert to dict format
            postgres_results = []
            for doc in documents:
                postgres_results.append({
                    "id": str(doc.id),
                    "title": doc.title,
                    "content": doc.content,
                    "document_type": doc.document_type,
                    "category": doc.category,
                    "source": doc.source,
                    "score": 1.0,  # Default score for SQL search
                    "search_type": "postgres"
                })
            
            state["postgres_results"] = postgres_results
            logger.info(f"Found {len(postgres_results)} documents in PostgreSQL")
            
        except Exception as e:
            logger.error(f"Error in PostgreSQL search: {e}")
            state["error"] = f"PostgreSQL search error: {str(e)}"
            state["postgres_results"] = []
        
        return state
    
    def search_vector_store(self, state: RetrievalState) -> RetrievalState:
        """Search documents in vector store"""
        try:
            logger.info(f"Searching vector store for query: {state['query']}")
            
            # Search in vector store
            vector_results = vector_store.search_documents(
                query=state["query"],
                n_results=state.get("limit", 20)
            )
            
            # Add search type
            for result in vector_results:
                result["search_type"] = "vector"
            
            state["vector_results"] = vector_results
            logger.info(f"Found {len(vector_results)} documents in vector store")
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            state["error"] = f"Vector search error: {str(e)}"
            state["vector_results"] = []
        
        return state
    
    def combine_results(self, state: RetrievalState) -> RetrievalState:
        """Combine PostgreSQL and vector search results"""
        try:
            postgres_results = state.get("postgres_results", [])
            vector_results = state.get("vector_results", [])
            
            # Create a map to track documents by ID
            combined_map = {}
            
            # Add PostgreSQL results
            for result in postgres_results:
                doc_id = result["id"]
                combined_map[doc_id] = result
            
            # Add vector results (merge if exists)
            for result in vector_results:
                doc_id = result["id"]
                if doc_id in combined_map:
                    # Merge results - combine scores
                    combined_map[doc_id]["vector_score"] = result["score"]
                    combined_map[doc_id]["combined_score"] = (
                        combined_map[doc_id]["score"] + result["score"]
                    ) / 2
                    combined_map[doc_id]["search_type"] = "hybrid"
                else:
                    # Add new result from vector search
                    result["combined_score"] = result["score"]
                    combined_map[doc_id] = result
            
            # Convert back to list and sort by combined score
            hybrid_results = list(combined_map.values())
            hybrid_results.sort(key=lambda x: x.get("combined_score", 0), reverse=True)
            
            # Limit results
            limit = state.get("limit", 10)
            hybrid_results = hybrid_results[:limit]
            
            state["hybrid_results"] = hybrid_results
            logger.info(f"Combined {len(hybrid_results)} unique documents")
            
        except Exception as e:
            logger.error(f"Error combining results: {e}")
            state["error"] = f"Result combination error: {str(e)}"
            state["hybrid_results"] = []
        
        return state
    
    def rerank_results(self, state: RetrievalState) -> RetrievalState:
        """Rerank results using BGE reranker"""
        try:
            hybrid_results = state.get("hybrid_results", [])
            
            if not hybrid_results:
                state["reranked_results"] = []
                return state
            
            if not self.reranker.is_available():
                logger.warning("Reranker not available, skipping reranking")
                state["reranked_results"] = hybrid_results
                return state
            
            logger.info(f"Reranking {len(hybrid_results)} documents")
            
            # Rerank using BGE reranker
            reranked = self.reranker.rerank_with_metadata(
                query=state["query"],
                documents=hybrid_results,
                content_key="content",
                top_k=state.get("limit", 10)
            )
            
            state["reranked_results"] = reranked
            logger.info(f"Reranked to {len(reranked)} documents")
            
        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            state["error"] = f"Reranking error: {str(e)}"
            state["reranked_results"] = state.get("hybrid_results", [])
        
        return state
    
    def finalize_results(self, state: RetrievalState) -> RetrievalState:
        """Finalize and format results"""
        try:
            reranked_results = state.get("reranked_results", [])
            
            # Format final results
            final_results = []
            for i, result in enumerate(reranked_results):
                final_result = {
                    "rank": i + 1,
                    "id": result["id"],
                    "title": result.get("title", ""),
                    "content_preview": result.get("content", "")[:500] + "..." if len(result.get("content", "")) > 500 else result.get("content", ""),
                    "full_content": result.get("content", ""),
                    "document_type": result.get("document_type", ""),
                    "category": result.get("category", ""),
                    "source": result.get("source", ""),
                    "relevance_score": result.get("rerank_score", result.get("combined_score", result.get("score", 0))),
                    "search_type": result.get("search_type", "unknown")
                }
                final_results.append(final_result)
            
            state["final_results"] = final_results
            logger.info(f"Finalized {len(final_results)} results")
            
        except Exception as e:
            logger.error(f"Error finalizing results: {e}")
            state["error"] = f"Result finalization error: {str(e)}"
            state["final_results"] = []
        
        return state


def create_retrieval_workflow() -> StateGraph:
    """Create the document retrieval workflow"""
    
    retrieval_node = RetrievalNode()
    
    # Create workflow
    workflow = StateGraph(RetrievalState)
    
    # Add nodes
    workflow.add_node("search_postgres", retrieval_node.search_postgres)
    workflow.add_node("search_vector", retrieval_node.search_vector_store)
    workflow.add_node("combine_results", retrieval_node.combine_results)
    workflow.add_node("rerank_results", retrieval_node.rerank_results)
    workflow.add_node("finalize_results", retrieval_node.finalize_results)
    
    # Set entry point
    workflow.set_entry_point("search_postgres")
    
    # Add edges
    workflow.add_edge("search_postgres", "search_vector")
    workflow.add_edge("search_vector", "combine_results")
    workflow.add_edge("combine_results", "rerank_results")
    workflow.add_edge("rerank_results", "finalize_results")
    workflow.add_edge("finalize_results", END)
    
    return workflow.compile() 