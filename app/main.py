"""
Main Streamlit Application for Legal AI Assistant
"""
import streamlit as st
import logging
import asyncio
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.simple_config import settings
from core.database.sqlite import db_manager
from core.database.vector_store import vector_store
from workflows.nodes.retrieval import create_retrieval_workflow, RetrievalState
from workflows.nodes.analysis import create_analysis_workflow, AnalysisState
from core.llm.openai_client import OpenAIClient
from core.llm.clova_client import ClovaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=settings.app_title,
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f4e79;
        margin-bottom: 1rem;
    }
    .result-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'selected_document' not in st.session_state:
        st.session_state.selected_document = None

def display_header():
    """Display main header"""
    st.markdown('<h1 class="main-header">⚖️ Legal AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown("---")

def display_sidebar():
    """Display sidebar with navigation and settings"""
    with st.sidebar:
        st.title("🔧 설정")
        
        # LLM Provider selection
        llm_provider = st.selectbox(
            "LLM 제공자",
            options=["OpenAI GPT-4o", "HyperClova-X"],
            index=0
        )
        
        # Search settings
        st.subheader("🔍 검색 설정")
        max_results = st.slider("최대 결과 수", 5, 20, 10)
        
        # Analysis settings
        st.subheader("📊 분석 설정")
        analysis_type = st.selectbox(
            "분석 유형",
            options=["전체 분석", "요약만", "핵심 사항", "법적 쟁점", "개체명"],
            index=0
        )
        
        # Database stats
        st.subheader("📈 데이터베이스 현황")
        try:
            vector_stats = vector_store.get_collection_stats()
            st.metric("벡터 DB 문서 수", vector_stats.get("total_documents", 0))
        except Exception as e:
            st.error(f"DB 연결 오류: {str(e)}")
        
        return {
            "llm_provider": "openai" if "OpenAI" in llm_provider else "clova",
            "max_results": max_results,
            "analysis_type": {
                "전체 분석": "full",
                "요약만": "summary", 
                "핵심 사항": "key_points",
                "법적 쟁점": "legal_issues",
                "개체명": "entities"
            }[analysis_type]
        }

async def search_documents(query: str, settings_dict: dict):
    """Search documents using LangGraph workflow"""
    try:
        retrieval_workflow = create_retrieval_workflow()
        
        initial_state: RetrievalState = {
            "query": query,
            "document_types": None,
            "categories": None,
            "limit": settings_dict["max_results"],
            "postgres_results": [],
            "vector_results": [],
            "hybrid_results": [],
            "reranked_results": [],
            "final_results": [],
            "error": None
        }
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("PostgreSQL 검색 중...")
        progress_bar.progress(20)
        
        # Run the workflow
        result = await retrieval_workflow.ainvoke(initial_state)
        
        progress_bar.progress(100)
        status_text.text("검색 완료!")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if result.get("error"):
            st.error(f"검색 중 오류가 발생했습니다: {result['error']}")
            return []
        
        return result.get("final_results", [])
        
    except Exception as e:
        logger.error(f"Error in document search: {e}")
        st.error(f"검색 중 오류가 발생했습니다: {str(e)}")
        return []

async def analyze_document(content: str, settings_dict: dict):
    """Analyze document using LangGraph workflow"""
    try:
        analysis_workflow = create_analysis_workflow()
        
        initial_state: AnalysisState = {
            "document_content": content,
            "document_metadata": None,
            "analysis_type": settings_dict["analysis_type"],
            "llm_provider": settings_dict["llm_provider"],
            "summary": None,
            "key_points": None,
            "legal_issues": None,
            "entities": None,
            "recommendations": None,
            "risk_assessment": None,
            "analysis_result": None,
            "error": None
        }
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("문서 분석 중...")
        progress_bar.progress(50)
        
        # Run the workflow
        result = await analysis_workflow.ainvoke(initial_state)
        
        progress_bar.progress(100)
        status_text.text("분석 완료!")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if result.get("error"):
            st.error(f"분석 중 오류가 발생했습니다: {result['error']}")
            return None
        
        return result.get("analysis_result", {})
        
    except Exception as e:
        logger.error(f"Error in document analysis: {e}")
        st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
        return None

def display_search_results(results: list):
    """Display search results"""
    if not results:
        st.info("검색 결과가 없습니다.")
        return
    
    st.subheader(f"🔍 검색 결과 ({len(results)}건)")
    
    for i, result in enumerate(results):
        with st.container():
            st.markdown(f"""
            <div class="result-card">
                <h4>{result['rank']}. {result['title']}</h4>
                <p><strong>유형:</strong> {result['document_type']} | 
                   <strong>카테고리:</strong> {result['category']} | 
                   <strong>관련도:</strong> {result['relevance_score']:.3f}</p>
                <p>{result['content_preview']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"전체 내용 보기", key=f"view_{i}"):
                    st.session_state.selected_document = result
            with col2:
                if st.button(f"문서 분석", key=f"analyze_{i}"):
                    with st.spinner("문서 분석 중..."):
                        settings_dict = display_sidebar()
                        analysis_result = asyncio.run(
                            analyze_document(result['full_content'], settings_dict)
                        )
                        if analysis_result:
                            st.session_state.analysis_result = analysis_result

def display_analysis_results(analysis_result: dict):
    """Display document analysis results"""
    if not analysis_result:
        return
    
    st.subheader("📋 문서 분석 결과")
    
    # Summary
    if analysis_result.get("summary"):
        st.markdown("### 📝 요약")
        st.markdown(f"<div class='result-card'>{analysis_result['summary']}</div>", 
                   unsafe_allow_html=True)
    
    # Key Points
    if analysis_result.get("key_points"):
        st.markdown("### 🔍 핵심 사항")
        for i, point in enumerate(analysis_result["key_points"], 1):
            st.markdown(f"{i}. {point}")
    
    # Legal Issues
    if analysis_result.get("legal_issues"):
        st.markdown("### ⚖️ 법적 쟁점")
        for i, issue in enumerate(analysis_result["legal_issues"], 1):
            st.markdown(f"{i}. {issue}")
    
    # Recommendations
    if analysis_result.get("recommendations"):
        st.markdown("### 💡 권고사항")
        for i, rec in enumerate(analysis_result["recommendations"], 1):
            st.markdown(f"{i}. {rec}")
    
    # Risk Assessment
    if analysis_result.get("risk_assessment"):
        st.markdown("### 🚨 위험도 평가")
        st.markdown(f"<div class='result-card'>{analysis_result['risk_assessment']}</div>", 
                   unsafe_allow_html=True)

def document_search_tab():
    """Document search functionality"""
    st.header("🔍 문서 검색")
    
    search_query = st.text_input(
        "검색어를 입력하세요:",
        placeholder="예: 계약서, 민법, 판례 등"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("검색", type="primary")
    
    if search_button and search_query:
        settings_dict = display_sidebar()
        with st.spinner("문서 검색 중..."):
            results = asyncio.run(search_documents(search_query, settings_dict))
            st.session_state.search_results = results
    
    # Display results
    if st.session_state.search_results:
        display_search_results(st.session_state.search_results)

def document_analysis_tab():
    """Document analysis functionality"""
    st.header("📊 문서 분석")
    
    analysis_method = st.radio(
        "분석 방법 선택:",
        options=["텍스트 직접 입력", "파일 업로드"],
        horizontal=True
    )
    
    document_content = ""
    
    if analysis_method == "텍스트 직접 입력":
        document_content = st.text_area(
            "분석할 문서 내용을 입력하세요:",
            height=300,
            placeholder="법률 문서 내용을 여기에 붙여넣으세요..."
        )
    else:
        uploaded_file = st.file_uploader(
            "파일을 업로드하세요:",
            type=['txt', 'pdf', 'docx'],
            help="지원 형식: TXT, PDF, DOCX"
        )
        
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                document_content = str(uploaded_file.read(), "utf-8")
            else:
                st.warning("PDF 및 DOCX 파일 처리는 추가 패키지가 필요합니다.")
    
    if st.button("문서 분석", type="primary") and document_content:
        settings_dict = display_sidebar()
        with st.spinner("문서 분석 중..."):
            analysis_result = asyncio.run(
                analyze_document(document_content, settings_dict)
            )
            if analysis_result:
                st.session_state.analysis_result = analysis_result
    
    # Display analysis results
    if st.session_state.analysis_result:
        display_analysis_results(st.session_state.analysis_result)

def legal_qa_tab():
    """Legal Q&A functionality"""
    st.header("❓ 법률 Q&A")
    
    question = st.text_area(
        "법률 관련 질문을 입력하세요:",
        height=150,
        placeholder="예: 계약서에서 주의해야 할 조항은 무엇인가요?"
    )
    
    if st.button("질문하기", type="primary") and question:
        settings_dict = display_sidebar()
        
        try:
            # Initialize LLM client
            if settings_dict["llm_provider"] == "openai":
                llm_client = OpenAIClient()
            else:
                llm_client = ClovaClient()
            
            with st.spinner("답변 생성 중..."):
                # Search for relevant documents first
                search_results = asyncio.run(
                    search_documents(question, {"max_results": 3})
                )
                
                # Use search results as context
                context = ""
                if search_results:
                    context = "\n".join([
                        f"관련 문서: {result['title']}\n{result['content_preview']}"
                        for result in search_results[:2]
                    ])
                
                # Generate answer
                answer = llm_client.answer_legal_question(question, context)
                
                # Display answer
                st.markdown("### 💬 답변")
                st.markdown(f"<div class='result-card'>{answer}</div>", 
                           unsafe_allow_html=True)
                
                # Display related documents
                if search_results:
                    st.markdown("### 📚 관련 문서")
                    display_search_results(search_results[:3])
                    
        except Exception as e:
            logger.error(f"Error in Q&A: {e}")
            st.error(f"질문 처리 중 오류가 발생했습니다: {str(e)}")

def system_status_tab():
    """System status and configuration"""
    st.header("🔧 시스템 상태")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 데이터베이스 상태")
        try:
            # Vector database stats
            vector_stats = vector_store.get_collection_stats()
            st.metric("벡터 DB 문서 수", vector_stats.get("total_documents", 0))
            st.metric("컬렉션 이름", vector_stats.get("collection_name", "N/A"))
            
            # PostgreSQL stats
            try:
                doc_types = db_manager.get_document_types()
                categories = db_manager.get_categories()
                st.metric("문서 유형 수", len(doc_types))
                st.metric("카테고리 수", len(categories))
            except Exception as e:
                st.error(f"PostgreSQL 연결 오류: {str(e)}")
                
        except Exception as e:
            st.error(f"데이터베이스 연결 오류: {str(e)}")
    
    with col2:
        st.subheader("🤖 모델 상태")
        
        # Test OpenAI connection
        try:
            openai_client = OpenAIClient()
            openai_info = openai_client.get_model_info()
            st.success(f"✅ OpenAI 연결 성공: {openai_info['model']}")
        except Exception as e:
            st.error(f"❌ OpenAI 연결 실패: {str(e)}")
        
        # Test HyperClova-X connection
        try:
            clova_client = ClovaClient()
            clova_info = clova_client.get_model_info()
            if clova_info["available"]:
                st.success(f"✅ HyperClova-X 연결 성공: {clova_info['model']}")
            else:
                st.warning("⚠️ HyperClova-X 설정 필요")
        except Exception as e:
            st.error(f"❌ HyperClova-X 연결 실패: {str(e)}")

def main():
    """Main application function"""
    init_session_state()
    display_header()
    
    # Sidebar settings
    settings_dict = display_sidebar()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 문서 검색", 
        "📊 문서 분석", 
        "❓ 법률 Q&A", 
        "🔧 시스템 상태"
    ])
    
    with tab1:
        document_search_tab()
    
    with tab2:
        document_analysis_tab()
    
    with tab3:
        legal_qa_tab()
    
    with tab4:
        system_status_tab()
    
    # Display selected document details
    if st.session_state.selected_document:
        st.markdown("---")
        st.subheader("📄 문서 상세 내용")
        doc = st.session_state.selected_document
        st.markdown(f"**제목:** {doc['title']}")
        st.markdown(f"**유형:** {doc['document_type']} | **카테고리:** {doc['category']}")
        st.markdown("**전체 내용:**")
        st.text_area("", value=doc['full_content'], height=400, disabled=True)

if __name__ == "__main__":
    main() 