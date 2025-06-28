"""
Simple data models for Streamlit MVP
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LegalDocumentORM(Base):
    """Legal document ORM model for SQLite"""
    __tablename__ = "legal_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    document_type = Column(String(100), nullable=False, index=True)
    category = Column(String(100), index=True)
    source = Column(String(200))
    author = Column(String(200))
    date_published = Column(DateTime)
    date_created = Column(DateTime, default=datetime.utcnow)
    date_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    doc_metadata = Column(JSON)
    tags = Column(JSON)


@dataclass
class LegalDocument:
    """Simple legal document data class"""
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    document_type: str = ""
    category: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    date_published: Optional[datetime] = None
    date_created: Optional[datetime] = None
    date_updated: Optional[datetime] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'document_type': self.document_type,
            'category': self.category,
            'source': self.source,
            'author': self.author,
            'date_published': self.date_published,
            'date_created': self.date_created,
            'date_updated': self.date_updated,
            'doc_metadata': self.doc_metadata,
            'tags': self.tags
        }
    
    @classmethod
    def from_orm(cls, orm_obj: LegalDocumentORM) -> 'LegalDocument':
        """Create from ORM object"""
        return cls(
            id=orm_obj.id,
            title=orm_obj.title,
            content=orm_obj.content,
            document_type=orm_obj.document_type,
            category=orm_obj.category,
            source=orm_obj.source,
            author=orm_obj.author,
            date_published=orm_obj.date_published,
            date_created=orm_obj.date_created,
            date_updated=orm_obj.date_updated,
            doc_metadata=orm_obj.doc_metadata,
            tags=orm_obj.tags
        )


@dataclass
class SearchResult:
    """Search result data class"""
    document: LegalDocument
    score: float = 0.0
    highlighted_content: Optional[str] = None


@dataclass
class AnalysisResult:
    """Document analysis result"""
    document_id: int
    summary: str = ""
    key_points: List[str] = field(default_factory=list)
    legal_concepts: List[str] = field(default_factory=list)
    entities: Dict[str, List[str]] = field(default_factory=dict)
    sentiment: Optional[str] = None
    complexity_score: Optional[float] = None
    analysis_date: datetime = field(default_factory=datetime.utcnow) 