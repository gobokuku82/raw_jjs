"""
OpenAI GPT-4o client implementation
"""
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import openai
from openai import OpenAI
import asyncio

from core.simple_config import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI GPT-4o client wrapper"""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.client = OpenAI(api_key=self.api_key) if self.api_key != "demo_key" else None
        self.model = "gpt-4o"
        self.max_tokens = 4096
        self.temperature = 0.1  # Lower temperature for legal work
        self.available = self.api_key != "demo_key" and self.client is not None
        
        logger.info(f"OpenAI client initialized with model: {self.model}, available: {self.available}")
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate chat completion"""
        if not self.available:
            return "OpenAI API 키가 설정되지 않았습니다. 데모 모드에서는 실제 AI 응답을 받을 수 없습니다."
            
        try:
            # Add system prompt if provided
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return f"죄송합니다. 오류가 발생했습니다: {str(e)}"
    
    def analyze_legal_document(self, document_content: str, analysis_type: str = "summary") -> str:
        """Analyze legal document"""
        system_prompt = """당신은 전문 법률 AI 어시스턴트입니다. 
        법률 문서를 정확하고 체계적으로 분석하여 다음과 같은 정보를 제공해주세요:
        1. 문서의 핵심 요약
        2. 주요 법적 쟁점
        3. 관련 법령 및 판례
        4. 주의사항 및 권고사항
        
        분석은 객관적이고 정확해야 하며, 법적 근거를 명확히 제시해주세요."""
        
        user_message = f"""다음 법률 문서를 분석해주세요:

문서 내용:
{document_content}

분석 유형: {analysis_type}"""
        
        messages = [{"role": "user", "content": user_message}]
        
        return self.chat_completion(messages, system_prompt=system_prompt)
    
    def answer_legal_question(self, question: str, context: Optional[str] = None) -> str:
        """Answer legal question"""
        system_prompt = """당신은 전문 법률 AI 어시스턴트입니다.
        사용자의 법률 질문에 대해 정확하고 유용한 답변을 제공해주세요.
        답변 시 다음을 포함해주세요:
        1. 직접적인 답변
        2. 관련 법령 및 조항
        3. 참고할 만한 판례 (있다면)
        4. 추가 주의사항
        
        단, 구체적인 법률 자문은 변호사와 상담하도록 안내해주세요."""
        
        user_content = f"질문: {question}"
        if context:
            user_content += f"\n\n관련 자료:\n{context}"
        
        messages = [{"role": "user", "content": user_content}]
        
        return self.chat_completion(messages, system_prompt=system_prompt)
    
    def summarize_text(self, text: str, summary_type: str = "brief") -> str:
        """Summarize text"""
        system_prompt = """당신은 법률 문서 요약 전문가입니다.
        주어진 텍스트를 명확하고 간결하게 요약해주세요.
        법적으로 중요한 내용은 반드시 포함시키고, 핵심 사항을 놓치지 않도록 주의해주세요."""
        
        length_instruction = {
            "brief": "간단히 3-4문장으로",
            "detailed": "상세하게 문단별로",
            "bullet": "불릿 포인트 형식으로"
        }.get(summary_type, "간단히")
        
        user_message = f"""다음 텍스트를 {length_instruction} 요약해주세요:

{text}"""
        
        messages = [{"role": "user", "content": user_message}]
        
        return self.chat_completion(messages, system_prompt=system_prompt)
    
    def extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text"""
        system_prompt = """당신은 법률 문서 분석 전문가입니다.
        주어진 텍스트에서 핵심 포인트들을 추출해주세요.
        각 포인트는 한 줄로 작성하고, 번호를 매겨서 나열해주세요."""
        
        user_message = f"""다음 텍스트에서 핵심 포인트들을 추출해주세요:

{text}"""
        
        messages = [{"role": "user", "content": user_message}]
        
        response = self.chat_completion(messages, system_prompt=system_prompt)
        
        # Extract numbered points
        points = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering and clean up
                clean_point = line.lstrip('0123456789.-• ').strip()
                if clean_point:
                    points.append(clean_point)
        
        return points if points else [response]
    
    async def stream_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion"""
        try:
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error in streaming completion: {e}")
            yield f"오류가 발생했습니다: {str(e)}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "provider": "OpenAI",
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "available": True
        } 