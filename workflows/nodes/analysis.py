"""
Document analysis nodes for LangGraph
"""
import logging
from typing import Dict, List, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END

from core.llm.openai_client import OpenAIClient
from core.llm.clova_client import ClovaClient

logger = logging.getLogger(__name__)


class AnalysisState(TypedDict):
    """State for analysis workflow"""
    document_content: str
    document_metadata: Optional[Dict[str, Any]]
    analysis_type: str  # summary, key_points, legal_issues, entities
    llm_provider: str  # openai or clova
    
    # Analysis results
    summary: Optional[str]
    key_points: Optional[List[str]]
    legal_issues: Optional[List[str]]
    entities: Optional[Dict[str, List[str]]]
    recommendations: Optional[List[str]]
    risk_assessment: Optional[str]
    
    # Final output
    analysis_result: Optional[Dict[str, Any]]
    error: Optional[str]


class AnalysisNode:
    """Node for document analysis operations"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.clova_client = ClovaClient()
    
    def _get_llm_client(self, provider: str):
        """Get appropriate LLM client"""
        if provider.lower() == "clova" and self.clova_client.available:
            return self.clova_client
        else:
            return self.openai_client
    
    def extract_summary(self, state: AnalysisState) -> AnalysisState:
        """Extract document summary"""
        try:
            if state.get("analysis_type") not in ["summary", "full"]:
                return state
            
            logger.info("Extracting document summary")
            
            llm_client = self._get_llm_client(state.get("llm_provider", "openai"))
            
            summary = llm_client.summarize_text(
                text=state["document_content"],
                summary_type="detailed"
            )
            
            state["summary"] = summary
            logger.info("Document summary extracted")
            
        except Exception as e:
            logger.error(f"Error extracting summary: {e}")
            state["error"] = f"Summary extraction error: {str(e)}"
        
        return state
    
    def extract_key_points(self, state: AnalysisState) -> AnalysisState:
        """Extract key points from document"""
        try:
            if state.get("analysis_type") not in ["key_points", "full"]:
                return state
            
            logger.info("Extracting key points")
            
            llm_client = self._get_llm_client(state.get("llm_provider", "openai"))
            
            key_points = llm_client.extract_key_points(state["document_content"])
            
            state["key_points"] = key_points
            logger.info(f"Extracted {len(key_points)} key points")
            
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            state["error"] = f"Key points extraction error: {str(e)}"
        
        return state
    
    def identify_legal_issues(self, state: AnalysisState) -> AnalysisState:
        """Identify legal issues in document"""
        try:
            if state.get("analysis_type") not in ["legal_issues", "full"]:
                return state
            
            logger.info("Identifying legal issues")
            
            llm_client = self._get_llm_client(state.get("llm_provider", "openai"))
            
            system_prompt = """당신은 법률 문서 분석 전문가입니다.
            주어진 문서에서 다음과 같은 법적 쟁점들을 식별해주세요:
            1. 주요 법적 위험요소
            2. 규정 위반 가능성
            3. 계약상 분쟁 요소
            4. 권리 및 의무 관계
            5. 법적 절차상 주의사항
            
            각 쟁점은 명확하고 구체적으로 기술해주세요."""
            
            messages = [{"role": "user", "content": f"다음 문서의 법적 쟁점을 분석해주세요:\n\n{state['document_content']}"}]
            
            response = llm_client.chat_completion(messages, system_prompt=system_prompt)
            
            # Extract legal issues from response
            legal_issues = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    clean_issue = line.lstrip('0123456789.-• ').strip()
                    if clean_issue:
                        legal_issues.append(clean_issue)
            
            if not legal_issues:
                legal_issues = [response]
            
            state["legal_issues"] = legal_issues
            logger.info(f"Identified {len(legal_issues)} legal issues")
            
        except Exception as e:
            logger.error(f"Error identifying legal issues: {e}")
            state["error"] = f"Legal issues identification error: {str(e)}"
        
        return state
    
    def extract_entities(self, state: AnalysisState) -> AnalysisState:
        """Extract named entities from document"""
        try:
            if state.get("analysis_type") not in ["entities", "full"]:
                return state
            
            logger.info("Extracting named entities")
            
            llm_client = self._get_llm_client(state.get("llm_provider", "openai"))
            
            system_prompt = """당신은 법률 문서 개체명 인식 전문가입니다.
            주어진 문서에서 다음 카테고리별로 개체명을 추출해주세요:
            
            1. 인명 (당사자, 변호사, 판사 등)
            2. 기관명 (법원, 회사, 정부기관 등)
            3. 법령명 (법률, 시행령, 조례 등)
            4. 날짜 (계약일, 판결일, 기한 등)
            5. 금액 (손해액, 계약금액 등)
            6. 장소 (주소, 법원 등)
            
            각 카테고리별로 구분하여 나열해주세요."""
            
            messages = [{"role": "user", "content": f"다음 문서에서 개체명을 추출해주세요:\n\n{state['document_content']}"}]
            
            response = llm_client.chat_completion(messages, system_prompt=system_prompt)
            
            # Parse entities from response
            entities = {
                "인명": [],
                "기관명": [],
                "법령명": [],
                "날짜": [],
                "금액": [],
                "장소": []
            }
            
            current_category = None
            for line in response.split('\n'):
                line = line.strip()
                if any(cat in line for cat in entities.keys()):
                    for cat in entities.keys():
                        if cat in line:
                            current_category = cat
                            break
                elif line and current_category and (line.startswith('-') or line.startswith('•')):
                    entity = line.lstrip('-• ').strip()
                    if entity:
                        entities[current_category].append(entity)
            
            state["entities"] = entities
            logger.info("Named entities extracted")
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            state["error"] = f"Entity extraction error: {str(e)}"
        
        return state
    
    def generate_recommendations(self, state: AnalysisState) -> AnalysisState:
        """Generate recommendations based on analysis"""
        try:
            logger.info("Generating recommendations")
            
            llm_client = self._get_llm_client(state.get("llm_provider", "openai"))
            
            # Combine available analysis results
            analysis_context = []
            
            if state.get("summary"):
                analysis_context.append(f"문서 요약: {state['summary']}")
            
            if state.get("key_points"):
                analysis_context.append(f"핵심 사항: {', '.join(state['key_points'][:3])}")
            
            if state.get("legal_issues"):
                analysis_context.append(f"법적 쟁점: {', '.join(state['legal_issues'][:3])}")
            
            context = "\n".join(analysis_context)
            
            system_prompt = """당신은 법률 자문 전문가입니다.
            문서 분석 결과를 바탕으로 다음과 같은 권고사항을 제시해주세요:
            1. 즉시 조치가 필요한 사항
            2. 위험 방지를 위한 예방조치
            3. 추가 검토가 필요한 부분
            4. 전문가 상담이 권장되는 영역
            
            실무적이고 구체적인 조언을 제공해주세요."""
            
            messages = [{"role": "user", "content": f"다음 분석 결과를 바탕으로 권고사항을 제시해주세요:\n\n{context}"}]
            
            response = llm_client.chat_completion(messages, system_prompt=system_prompt)
            
            # Extract recommendations
            recommendations = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    clean_rec = line.lstrip('0123456789.-• ').strip()
                    if clean_rec:
                        recommendations.append(clean_rec)
            
            if not recommendations:
                recommendations = [response]
            
            state["recommendations"] = recommendations
            logger.info(f"Generated {len(recommendations)} recommendations")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            state["error"] = f"Recommendations generation error: {str(e)}"
        
        return state
    
    def assess_risk(self, state: AnalysisState) -> AnalysisState:
        """Assess legal risk level"""
        try:
            logger.info("Assessing risk level")
            
            llm_client = self._get_llm_client(state.get("llm_provider", "openai"))
            
            legal_issues = state.get("legal_issues", [])
            
            system_prompt = """당신은 법률 위험 평가 전문가입니다.
            식별된 법적 쟁점들을 바탕으로 전체적인 위험도를 평가해주세요.
            위험도는 다음 중 하나로 분류하고 그 이유를 설명해주세요:
            
            - 높음: 즉시 법적 조치나 전문가 상담이 필요
            - 중간: 주의 깊은 모니터링과 예방조치 필요
            - 낮음: 일반적인 주의사항 준수로 충분
            
            형식: "위험도: [높음/중간/낮음] - [이유]" """
            
            issues_text = "\n".join([f"- {issue}" for issue in legal_issues])
            
            messages = [{"role": "user", "content": f"다음 법적 쟁점들에 대한 위험도를 평가해주세요:\n\n{issues_text}"}]
            
            risk_assessment = llm_client.chat_completion(messages, system_prompt=system_prompt)
            
            state["risk_assessment"] = risk_assessment
            logger.info("Risk assessment completed")
            
        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            state["error"] = f"Risk assessment error: {str(e)}"
        
        return state
    
    def compile_analysis(self, state: AnalysisState) -> AnalysisState:
        """Compile final analysis result"""
        try:
            logger.info("Compiling final analysis")
            
            analysis_result = {
                "document_metadata": state.get("document_metadata", {}),
                "analysis_type": state.get("analysis_type", "unknown"),
                "llm_provider": state.get("llm_provider", "unknown"),
                "summary": state.get("summary"),
                "key_points": state.get("key_points", []),
                "legal_issues": state.get("legal_issues", []),
                "entities": state.get("entities", {}),
                "recommendations": state.get("recommendations", []),
                "risk_assessment": state.get("risk_assessment"),
                "analysis_complete": True
            }
            
            state["analysis_result"] = analysis_result
            logger.info("Analysis compilation completed")
            
        except Exception as e:
            logger.error(f"Error compiling analysis: {e}")
            state["error"] = f"Analysis compilation error: {str(e)}"
        
        return state


def create_analysis_workflow() -> StateGraph:
    """Create the document analysis workflow"""
    
    analysis_node = AnalysisNode()
    
    # Create workflow
    workflow = StateGraph(AnalysisState)
    
    # Add nodes
    workflow.add_node("extract_summary", analysis_node.extract_summary)
    workflow.add_node("extract_key_points", analysis_node.extract_key_points)
    workflow.add_node("identify_legal_issues", analysis_node.identify_legal_issues)
    workflow.add_node("extract_entities", analysis_node.extract_entities)
    workflow.add_node("generate_recommendations", analysis_node.generate_recommendations)
    workflow.add_node("assess_risk", analysis_node.assess_risk)
    workflow.add_node("compile_analysis", analysis_node.compile_analysis)
    
    # Set entry point
    workflow.set_entry_point("extract_summary")
    
    # Add edges
    workflow.add_edge("extract_summary", "extract_key_points")
    workflow.add_edge("extract_key_points", "identify_legal_issues")
    workflow.add_edge("identify_legal_issues", "extract_entities")
    workflow.add_edge("extract_entities", "generate_recommendations")
    workflow.add_edge("generate_recommendations", "assess_risk")
    workflow.add_edge("assess_risk", "compile_analysis")
    workflow.add_edge("compile_analysis", END)
    
    return workflow.compile() 