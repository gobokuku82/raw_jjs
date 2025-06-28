"""
Legal document data models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class LegalDocumentORM(Base):
    """Legal document ORM model for PostgreSQL"""
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
    
    # Relationships
    citations = relationship("CitationORM", back_populates="document")


class CitationORM(Base):
    """Citation ORM model"""
    __tablename__ = "citations"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("legal_documents.id"))
    cited_document_id = Column(Integer, ForeignKey("legal_documents.id"))
    citation_text = Column(Text)
    context = Column(Text)
    
    # Relationships
    document = relationship("LegalDocumentORM", foreign_keys=[document_id], back_populates="citations")
    cited_document = relationship("LegalDocumentORM", foreign_keys=[cited_document_id])


# Pydantic models for API
class LegalDocumentBase(BaseModel):
    """Base legal document model"""
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    document_type: str = Field(..., description="Type of legal document")
    category: Optional[str] = Field(None, description="Document category")
    source: Optional[str] = Field(None, description="Document source")
    author: Optional[str] = Field(None, description="Document author")
    date_published: Optional[datetime] = Field(None, description="Publication date")
    doc_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[List[str]] = Field(None, description="Document tags")


class LegalDocumentCreate(LegalDocumentBase):
    """Model for creating a legal document"""
    pass


class LegalDocumentUpdate(BaseModel):
    """Model for updating a legal document"""
    title: Optional[str] = None
    content: Optional[str] = None
    document_type: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    date_published: Optional[datetime] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class LegalDocument(LegalDocumentBase):
    """Complete legal document model"""
    id: int
    date_created: datetime
    date_updated: datetime
    
    class Config:
        from_attributes = True


class SearchQuery(BaseModel):
    """Search query model"""
    query: str = Field(..., description="Search query text")
    document_types: Optional[List[str]] = Field(None, description="Filter by document types")
    categories: Optional[List[str]] = Field(None, description="Filter by categories")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    limit: int = Field(10, description="Maximum number of results")
    offset: int = Field(0, description="Offset for pagination")


class SearchResult(BaseModel):
    """Search result model"""
    document: LegalDocument
    score: float = Field(..., description="Relevance score")
    highlighted_content: Optional[str] = Field(None, description="Highlighted content snippet")


class AnalysisResult(BaseModel):
    """Document analysis result"""
    document_id: int
    summary: str = Field(..., description="Document summary")
    key_points: List[str] = Field(..., description="Key points extracted")
    legal_concepts: List[str] = Field(..., description="Legal concepts identified")
    entities: Dict[str, List[str]] = Field(..., description="Named entities")
    sentiment: Optional[str] = Field(None, description="Sentiment analysis")
    complexity_score: Optional[float] = Field(None, description="Document complexity score")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)


class Citation(BaseModel):
    """Citation model"""
    id: int
    document_id: int
    cited_document_id: int
    citation_text: str
    context: Optional[str] = None
    
    class Config:
        from_attributes = True 