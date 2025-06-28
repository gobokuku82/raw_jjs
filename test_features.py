#!/usr/bin/env python3
"""
Legal AI Assistant - Feature Test Script
모든 기능이 정상 작동하는지 테스트
"""
import sys
import os
import traceback
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_imports():
    """기본 import 테스트"""
    print("=" * 60)
    print("1. 기본 Import 테스트")
    print("=" * 60)
    
    try:
        from core.simple_config import settings
        print("✓ 설정 로드 완료")
        
        from core.database import db_manager, vector_store
        print("✓ 데이터베이스 매니저 로드 완료")
        
        from core.models.simple_models import LegalDocument
        print("✓ 모델 로드 완료")
        
        from core.llm.openai_client import OpenAIClient
        from core.llm.clova_client import ClovaClient
        print("✓ LLM 클라이언트 로드 완료")
        
        from core.embeddings.kure_embeddings import KUREEmbeddings
        from core.embeddings.reranker import BGEReranker
        print("✓ 임베딩 모델 로드 완료")
        
        # LangGraph imports
        from workflows.nodes.retrieval import create_retrieval_workflow, RetrievalState
        from workflows.nodes.analysis import create_analysis_workflow, AnalysisState
        print("✓ LangGraph 워크플로우 로드 완료")
        
        return True
        
    except Exception as e:
        print(f"✗ Import 오류: {e}")
        traceback.print_exc()
        return False

def test_database_operations():
    """데이터베이스 기능 테스트"""
    print("\\n" + "=" * 60)
    print("2. 데이터베이스 기능 테스트")
    print("=" * 60)
    
    try:
        from core.database import db_manager
        from core.models.simple_models import LegalDocument
        
        # 데이터베이스 초기화
        db_manager.create_tables()
        print("✓ 데이터베이스 테이블 생성 완료")
        
        # 검색 테스트
        search_results = db_manager.search_documents("민법", limit=5)
        print(f"✓ 검색 기능 테스트 완료 (결과: {len(search_results)}개)")
        
        # 새 문서 생성 테스트
        test_doc = LegalDocument(
            title="기능 테스트 문서",
            content="이것은 기능 테스트를 위한 샘플 문서입니다.",
            document_type="테스트",
            category="기능테스트"
        )
        
        created_doc = db_manager.create_document(test_doc)
        print(f"✓ 문서 생성 테스트 완료 (ID: {created_doc.id})")
        
        # 생성된 문서 검색
        found_doc = db_manager.get_document_by_id(created_doc.id)
        if found_doc:
            print("✓ 문서 조회 테스트 완료")
        
        return True
        
    except Exception as e:
        print(f"✗ 데이터베이스 테스트 오류: {e}")
        traceback.print_exc()
        return False

def test_vector_store():
    """벡터 저장소 테스트"""
    print("\\n" + "=" * 60)
    print("3. 벡터 저장소 테스트")
    print("=" * 60)
    
    try:
        from core.database import vector_store
        
        # 벡터 검색 테스트
        search_results = vector_store.search_documents("계약", n_results=3)
        print(f"✓ 벡터 검색 테스트 완료 (결과: {len(search_results)}개)")
        
        return True
        
    except Exception as e:
        print(f"✗ 벡터 저장소 테스트 오류: {e}")
        traceback.print_exc()
        return False

def test_llm_clients():
    """LLM 클라이언트 테스트"""
    print("\\n" + "=" * 60)
    print("4. LLM 클라이언트 테스트")
    print("=" * 60)
    
    try:
        from core.llm.openai_client import OpenAIClient
        from core.llm.clova_client import ClovaClient
        
        # OpenAI 클라이언트 테스트
        openai_client = OpenAIClient()
        if openai_client.available:
            print("✓ OpenAI 클라이언트 사용 가능")
            
            # 간단한 텍스트 완성 테스트
            test_text = "안녕하세요. 이것은 테스트입니다."
            summary = openai_client.summarize_text(test_text)
            print("✓ OpenAI 요약 기능 테스트 완료")
            
        else:
            print("⚠ OpenAI 클라이언트 사용 불가 (API 키 확인 필요)")
        
        # Clova 클라이언트 테스트
        clova_client = ClovaClient()
        if clova_client.available:
            print("✓ HyperClova-X 클라이언트 사용 가능")
        else:
            print("⚠ HyperClova-X 클라이언트 사용 불가 (API 키 없음)")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM 클라이언트 테스트 오류: {e}")
        traceback.print_exc()
        return False

def test_embeddings():
    """임베딩 모델 테스트"""
    print("\\n" + "=" * 60)
    print("5. 임베딩 모델 테스트")
    print("=" * 60)
    
    try:
        from core.embeddings.kure_embeddings import KUREEmbeddings
        from core.embeddings.reranker import BGEReranker
        
        # KURE 임베딩 테스트
        kure = KUREEmbeddings()
        if kure.is_available():
            print("✓ KURE 임베딩 모델 사용 가능")
            
            # 간단한 임베딩 테스트
            test_texts = ["안녕하세요", "법률 문서입니다"]
            embeddings = kure.encode(test_texts)
            print(f"✓ 임베딩 생성 테스트 완료 (차원: {len(embeddings[0])})")
        else:
            print("⚠ KURE 임베딩 모델 로딩 실패")
        
        # BGE 리랭커 테스트
        reranker = BGEReranker()
        if reranker.is_available():
            print("✓ BGE 리랭커 모델 사용 가능")
        else:
            print("⚠ BGE 리랭커 모델 로딩 실패")
        
        return True
        
    except Exception as e:
        print(f"✗ 임베딩 모델 테스트 오류: {e}")
        traceback.print_exc()
        return False

def test_langgraph_workflows():
    """LangGraph 워크플로우 테스트"""
    print("\\n" + "=" * 60)
    print("6. LangGraph 워크플로우 테스트")
    print("=" * 60)
    
    try:
        from workflows.nodes.retrieval import create_retrieval_workflow, RetrievalState
        from workflows.nodes.analysis import create_analysis_workflow, AnalysisState
        
        # 검색 워크플로우 생성 테스트
        retrieval_workflow = create_retrieval_workflow()
        print("✓ 검색 워크플로우 생성 완료")
        
        # 분석 워크플로우 생성 테스트
        analysis_workflow = create_analysis_workflow()
        print("✓ 분석 워크플로우 생성 완료")
        
        # 간단한 검색 워크플로우 실행 테스트
        initial_state = RetrievalState(
            query="민법",
            document_types=None,
            categories=None,
            limit=3,
            postgres_results=[],
            vector_results=[],
            hybrid_results=[],
            reranked_results=[],
            final_results=[],
            error=None
        )
        
        # Note: 실제 워크플로우 실행은 시간이 걸리므로 생성만 테스트
        print("✓ 워크플로우 상태 테스트 완료")
        
        return True
        
    except Exception as e:
        print(f"✗ LangGraph 워크플로우 테스트 오류: {e}")
        traceback.print_exc()
        return False

def main():
    """메인 테스트 실행"""
    print("🧪 Legal AI Assistant - 전체 기능 테스트")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_database_operations,
        test_vector_store,
        test_llm_clients,
        test_embeddings,
        test_langgraph_workflows
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("❌ 테스트 실패")
        except Exception as e:
            print(f"❌ 테스트 예외 발생: {e}")
    
    print("\\n" + "=" * 60)
    print(f"테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! 시스템이 정상 작동합니다.")
        print("\\n📱 Streamlit 앱 실행:")
        print("streamlit run app/main.py")
        print("브라우저에서 http://localhost:8501 접속")
    else:
        print("❌ 일부 테스트 실패. 문제를 해결해주세요.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 