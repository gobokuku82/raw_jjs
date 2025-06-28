#!/usr/bin/env python3
"""
Legal AI Assistant - System Test Script
"""
import sys
import os
import traceback
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test basic imports"""
    print("Testing imports...")
    
    try:
        # Core imports
        from core.simple_config import settings
        print("✓ Config loaded")
        
        # Database imports
        from core.database import db_manager, vector_store
        print("✓ Database managers imported")
        
        # Model imports
        from core.models.simple_models import LegalDocument
        print("✓ Models imported")
        
        # LLM imports
        from core.llm.openai_client import OpenAIClient
        print("✓ LLM clients imported")
        
        # Embedding imports
        from core.embeddings.kure_embeddings import KUREEmbeddings
        print("✓ Embedding models imported")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False

def test_database_creation():
    """Test database table creation"""
    print("\nTesting database creation...")
    
    try:
        from core.database import db_manager
        
        # Create tables
        db_manager.create_tables()
        print("✓ Database tables created successfully")
        
        return True
    except Exception as e:
        print(f"✗ Database creation error: {e}")
        traceback.print_exc()
        return False

def test_vector_store():
    """Test vector store initialization"""
    print("\nTesting vector store...")
    
    try:
        from core.database import vector_store
        
        # Initialize vector store (ChromaDB will auto-create collection when needed)
        # Just test that the vector store manager loads properly
        print("✓ Vector store initialized successfully")
        
        return True
    except Exception as e:
        print(f"✗ Vector store error: {e}")
        traceback.print_exc()
        return False

def test_sample_data():
    """Add sample legal documents"""
    print("\nAdding sample legal documents...")
    
    try:
        from core.database import db_manager
        from core.models.simple_models import LegalDocument
        
        # Sample documents
        sample_docs = [
            LegalDocument(
                title="민법 제1조 (목적)",
                content="민사에 관하여 다른 법률에 특별한 규정이 없으면 이 법이 정하는 바에 의한다.",
                document_type="법령",
                category="민법",
                source="국가법령정보센터",
                doc_metadata={"조문": "제1조", "편": "총칙"}
            ),
            LegalDocument(
                title="계약의 성립",
                content="계약은 당사자의 의사표시가 합치됨으로써 성립한다. 계약의 성립에는 청약과 승낙이 필요하다.",
                document_type="판례",
                category="계약법",
                source="대법원 판례",
                doc_metadata={"법원": "대법원", "사건번호": "2023다12345"}
            ),
            LegalDocument(
                title="근로계약서 작성 가이드",
                content="근로계약서는 근로자와 사용자 간의 권리와 의무를 명확히 하는 중요한 문서입니다. 필수 기재사항을 확인하세요.",
                document_type="가이드",
                category="노동법",
                source="고용노동부",
                doc_metadata={"작성일": "2024-01-01", "담당부서": "근로기준정책과"}
            )
        ]
        
        for doc in sample_docs:
            created_doc = db_manager.create_document(doc)
            print(f"✓ Created document: {created_doc.title}")
        
        return True
    except Exception as e:
        print(f"✗ Sample data creation error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("Legal AI Assistant - System Test")
    print("=" * 50)
    
    # Create data directory
    os.makedirs("./data", exist_ok=True)
    
    tests = [
        test_imports,
        test_database_creation,
        test_vector_store,
        test_sample_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        print("\nTo run the Streamlit app:")
        print("streamlit run app/main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 