"""Legal Workflow Definition using LangGraph"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from .legal_workflow_state import LegalWorkflowState
from ..nodes.retrieval import create_retrieval_workflow, RetrievalState
from ..nodes.analysis import create_analysis_workflow, AnalysisState


def create_legal_workflow() -> StateGraph:
    """법률 AI 워크플로우 생성"""
    
    # 상태 그래프 생성
    workflow = StateGraph(LegalWorkflowState)
    
    # 노드 추가 - 간단한 함수로 래핑
    workflow.add_node("retrieval", run_retrieval)
    workflow.add_node("analysis", run_analysis)
    
    # 시작점 설정
    workflow.set_entry_point("retrieval")
    
    # 엣지 추가
    workflow.add_edge("retrieval", "analysis")
    workflow.add_edge("analysis", END)
    
    return workflow.compile()


def run_retrieval(state: LegalWorkflowState) -> Dict[str, Any]:
    """검색 워크플로우 실행"""
    try:
        # 검색 상태 생성
        retrieval_state = RetrievalState(
            query=state["query"],
            document_types=None,
            categories=None,
            limit=10,
            postgres_results=[],
            vector_results=[],
            hybrid_results=[],
            reranked_results=[],
            final_results=[],
            error=None
        )
        
        # 검색 워크플로우 실행
        retrieval_workflow = create_retrieval_workflow()
        result = retrieval_workflow.invoke(retrieval_state)
        
        # 결과를 메인 상태에 반영
        return {
            "retrieved_docs": result.get("final_results", []),
            "current_step": "retrieval_complete",
            "messages": state["messages"] + [
                AIMessage(content=f"검색 완료: {len(result.get('final_results', []))}개 문서 발견")
            ]
        }
        
    except Exception as e:
        return {
            "error": f"검색 중 오류 발생: {str(e)}",
            "current_step": "retrieval_error"
        }


def run_analysis(state: LegalWorkflowState) -> Dict[str, Any]:
    """분석 워크플로우 실행"""
    try:
        retrieved_docs = state.get("retrieved_docs", [])
        
        if not retrieved_docs:
            return {
                "analysis_result": {"error": "분석할 문서가 없습니다."},
                "current_step": "analysis_complete"
            }
        
        # 첫 번째 문서를 분석 (실제로는 모든 문서를 분석할 수 있음)
        first_doc = retrieved_docs[0]
        
        # 분석 상태 생성
        analysis_state = AnalysisState(
            document_content=first_doc.get("full_content", ""),
            document_metadata={"title": first_doc.get("title", "")},
            analysis_type="full",
            llm_provider="openai",
            summary=None,
            key_points=None,
            legal_issues=None,
            entities=None,
            recommendations=None,
            risk_assessment=None,
            analysis_result=None,
            error=None
        )
        
        # 분석 워크플로우 실행
        analysis_workflow = create_analysis_workflow()
        result = analysis_workflow.invoke(analysis_state)
        
        # 결과를 메인 상태에 반영
        return {
            "analysis_result": result.get("analysis_result", {}),
            "current_step": "analysis_complete",
            "messages": state["messages"] + [
                AIMessage(content="문서 분석이 완료되었습니다.")
            ]
        }
        
    except Exception as e:
        return {
            "error": f"분석 중 오류 발생: {str(e)}",
            "current_step": "analysis_error"
        }


def should_continue(state: LegalWorkflowState) -> str:
    """워크플로우 계속 여부 결정"""
    if state.get("error"):
        return "error"
    
    current_step = state.get("current_step", "")
    
    if current_step == "retrieval_complete":
        return "analysis"
    elif current_step == "analysis_complete":
        return END
    else:
        return "retrieval"


def create_conditional_workflow() -> StateGraph:
    """조건부 법률 AI 워크플로우 생성"""
    
    # 상태 그래프 생성
    workflow = StateGraph(LegalWorkflowState)
    
    # 노드 추가
    workflow.add_node("retrieval", run_retrieval)
    workflow.add_node("analysis", run_analysis)
    workflow.add_node("error_handler", handle_error)
    
    # 시작점 설정
    workflow.set_entry_point("retrieval")
    
    # 조건부 엣지 추가
    workflow.add_conditional_edges(
        "retrieval",
        should_continue,
        {
            "analysis": "analysis",
            "error": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "analysis",
        should_continue,
        {
            END: END,
            "error": "error_handler"
        }
    )
    
    workflow.add_edge("error_handler", END)
    
    return workflow.compile()


def handle_error(state: LegalWorkflowState) -> Dict[str, Any]:
    """오류 처리"""
    error_msg = state.get("error", "Unknown error occurred")
    
    return {
        "messages": state["messages"] + [
            AIMessage(content=f"오류가 발생했습니다: {error_msg}")
        ],
        "current_step": "error_handled"
    } 