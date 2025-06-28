"""Legal Workflow State Definition"""

from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage


class LegalWorkflowState(TypedDict):
    """법률 AI 워크플로우 상태"""
    
    # 사용자 쿼리
    query: str
    
    # 원본 문서들
    documents: List[Dict[str, Any]]
    
    # 검색된 문서들
    retrieved_docs: List[Dict[str, Any]]
    
    # 분석 결과
    analysis_result: Dict[str, Any]
    
    # 메시지 기록
    messages: List[BaseMessage]
    
    # 현재 단계
    current_step: Optional[str]
    
    # 오류 정보
    error: Optional[str]
    
    # 메타데이터
    metadata: Optional[Dict[str, Any]] 