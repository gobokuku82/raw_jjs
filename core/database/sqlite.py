"""
SQLite database connection and operations for MVP
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging
import os

from core.simple_config import settings
from core.models.simple_models import Base, LegalDocumentORM, LegalDocument

logger = logging.getLogger(__name__)


class SQLiteManager:
    """SQLite database manager for MVP"""
    
    def __init__(self):
        # Ensure data directory exists
        os.makedirs("./data", exist_ok=True)
        
        self.engine = create_engine(
            settings.database_url,
            echo=settings.debug,
            connect_args={"check_same_thread": False}  # SQLite specific
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def create_document(self, document: LegalDocument) -> LegalDocument:
        """Create a new legal document"""
        with self.get_session() as session:
            try:
                db_document = LegalDocumentORM(
                    title=document.title,
                    content=document.content,
                    document_type=document.document_type,
                    category=document.category,
                    source=document.source,
                    author=document.author,
                    date_published=document.date_published,
                    doc_metadata=document.doc_metadata,
                    tags=document.tags
                )
                session.add(db_document)
                session.commit()
                session.refresh(db_document)
                return LegalDocument.from_orm(db_document)
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error creating document: {e}")
                raise
    
    def get_document_by_id(self, document_id: int) -> Optional[LegalDocument]:
        """Get document by ID"""
        with self.get_session() as session:
            try:
                db_document = session.query(LegalDocumentORM).filter(
                    LegalDocumentORM.id == document_id
                ).first()
                
                if db_document:
                    return LegalDocument.from_orm(db_document)
                return None
            except SQLAlchemyError as e:
                logger.error(f"Error getting document {document_id}: {e}")
                raise
    
    def search_documents(
        self, 
        query: str, 
        document_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[LegalDocument]:
        """Search documents using full-text search"""
        with self.get_session() as session:
            try:
                db_query = session.query(LegalDocumentORM)
                
                # Add simple text search condition (SQLite compatible)
                if query:
                    search_condition = text(
                        "(title LIKE :query OR content LIKE :query)"
                    )
                    db_query = db_query.filter(search_condition).params(query=f"%{query}%")
                
                # Add filters
                if document_types:
                    db_query = db_query.filter(LegalDocumentORM.document_type.in_(document_types))
                
                if categories:
                    db_query = db_query.filter(LegalDocumentORM.category.in_(categories))
                
                # Apply pagination
                documents = db_query.offset(offset).limit(limit).all()
                
                return [LegalDocument.from_orm(doc) for doc in documents]
            except SQLAlchemyError as e:
                logger.error(f"Error searching documents: {e}")
                raise
    
    def get_document_types(self) -> List[str]:
        """Get all unique document types"""
        with self.get_session() as session:
            try:
                types = session.query(LegalDocumentORM.document_type).distinct().all()
                return [t[0] for t in types if t[0]]
            except SQLAlchemyError as e:
                logger.error(f"Error getting document types: {e}")
                raise
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        with self.get_session() as session:
            try:
                categories = session.query(LegalDocumentORM.category).distinct().all()
                return [c[0] for c in categories if c[0]]
            except SQLAlchemyError as e:
                logger.error(f"Error getting categories: {e}")
                raise
    
    def update_document(self, document_id: int, updates: Dict[str, Any]) -> Optional[LegalDocument]:
        """Update document"""
        with self.get_session() as session:
            try:
                db_document = session.query(LegalDocumentORM).filter(
                    LegalDocumentORM.id == document_id
                ).first()
                
                if not db_document:
                    return None
                
                for key, value in updates.items():
                    if hasattr(db_document, key):
                        setattr(db_document, key, value)
                
                session.commit()
                session.refresh(db_document)
                return LegalDocument.from_orm(db_document)
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error updating document {document_id}: {e}")
                raise
    
    def delete_document(self, document_id: int) -> bool:
        """Delete document"""
        with self.get_session() as session:
            try:
                db_document = session.query(LegalDocumentORM).filter(
                    LegalDocumentORM.id == document_id
                ).first()
                
                if not db_document:
                    return False
                
                session.delete(db_document)
                session.commit()
                return True
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error deleting document {document_id}: {e}")
                raise


# Global database manager instance
db_manager = SQLiteManager() 