"""
Legal Database MCP Server
Provides access to legal documents and case data
"""
import asyncio
import logging
from typing import Any, Sequence, Dict, List, Optional
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    LoggingLevel, EmptyRequestArguments
)
import mcp.types as types
from pydantic import AnyUrl
import json

from core.database.postgres import db_manager
from core.database.vector_store import vector_store
from langgraph.nodes.retrieval import create_retrieval_workflow, RetrievalState
from langgraph.nodes.analysis import create_analysis_workflow, AnalysisState

logger = logging.getLogger(__name__)

# Create server instance
server = Server("legal-database")


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available legal database resources"""
    return [
        Resource(
            uri=AnyUrl("legal://documents"),
            name="Legal Documents",
            description="Access to legal documents database",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("legal://cases"),
            name="Legal Cases",
            description="Legal case database",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("legal://search"),
            name="Document Search",
            description="Search legal documents using hybrid retrieval",
            mimeType="application/json",
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read specific legal database resource"""
    if uri.scheme != "legal":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")
    
    try:
        if uri.path == "//documents":
            # Get document statistics
            stats = {
                "total_documents": 0,
                "document_types": [],
                "categories": []
            }
            
            try:
                stats["document_types"] = db_manager.get_document_types()
                stats["categories"] = db_manager.get_categories()
                vector_stats = vector_store.get_collection_stats()
                stats.update(vector_stats)
            except Exception as e:
                logger.error(f"Error getting document stats: {e}")
            
            return json.dumps(stats, ensure_ascii=False, indent=2)
            
        elif uri.path == "//cases":
            # Get case-related documents
            try:
                cases = db_manager.search_documents(
                    query="판례",
                    document_types=["판례", "판결문"],
                    limit=10
                )
                case_data = [
                    {
                        "id": case.id,
                        "title": case.title,
                        "category": case.category,
                        "source": case.source
                    }
                    for case in cases
                ]
                return json.dumps(case_data, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Error getting cases: {e}")
                return json.dumps({"error": str(e)}, ensure_ascii=False)
                
        elif uri.path == "//search":
            return json.dumps({
                "description": "Use the search_documents tool to search legal documents",
                "available_tools": ["search_documents", "analyze_document"]
            }, ensure_ascii=False, indent=2)
        
        else:
            raise ValueError(f"Unknown resource path: {uri.path}")
            
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available legal database tools"""
    return [
        Tool(
            name="search_documents",
            description="Search legal documents using hybrid retrieval (PostgreSQL + Vector DB + Reranking)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for legal documents"
                    },
                    "document_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by document types (optional)"
                    },
                    "categories": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "Filter by categories (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="analyze_document",
            description="Analyze a legal document for key insights, legal issues, and recommendations",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "ID of document to analyze"
                    },
                    "document_content": {
                        "type": "string", 
                        "description": "Document content to analyze (if no document_id provided)"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["summary", "key_points", "legal_issues", "entities", "full"],
                        "description": "Type of analysis to perform",
                        "default": "full"
                    },
                    "llm_provider": {
                        "type": "string",
                        "enum": ["openai", "clova"],
                        "description": "LLM provider to use",
                        "default": "openai"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_document",
            description="Retrieve a specific legal document by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "integer",
                        "description": "ID of the document to retrieve"
                    }
                },
                "required": ["document_id"]
            }
        ),
        Tool(
            name="add_document",
            description="Add a new legal document to the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title"},
                    "content": {"type": "string", "description": "Document content"},
                    "document_type": {"type": "string", "description": "Type of legal document"},
                    "category": {"type": "string", "description": "Document category"},
                    "source": {"type": "string", "description": "Document source"},
                    "author": {"type": "string", "description": "Document author"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Document tags"
                    }
                },
                "required": ["title", "content", "document_type"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for legal database operations"""
    try:
        if name == "search_documents":
            # Use LangGraph retrieval workflow
            retrieval_workflow = create_retrieval_workflow()
            
            initial_state: RetrievalState = {
                "query": arguments["query"],
                "document_types": arguments.get("document_types"),
                "categories": arguments.get("categories"),
                "limit": arguments.get("limit", 10),
                "postgres_results": [],
                "vector_results": [],
                "hybrid_results": [],
                "reranked_results": [],
                "final_results": [],
                "error": None
            }
            
            # Run the workflow
            result = await retrieval_workflow.ainvoke(initial_state)
            
            if result.get("error"):
                return [TextContent(type="text", text=f"검색 중 오류가 발생했습니다: {result['error']}")]
            
            final_results = result.get("final_results", [])
            
            if not final_results:
                return [TextContent(type="text", text="검색 결과가 없습니다.")]
            
            # Format search results
            response_text = f"검색 결과 ({len(final_results)}건):\n\n"
            
            for result_item in final_results:
                response_text += f"**{result_item['rank']}. {result_item['title']}**\n"
                response_text += f"유형: {result_item['document_type']}\n"
                response_text += f"카테고리: {result_item['category']}\n"
                response_text += f"관련도: {result_item['relevance_score']:.3f}\n"
                response_text += f"미리보기: {result_item['content_preview']}\n"
                response_text += f"---\n\n"
            
            return [TextContent(type="text", text=response_text)]
            
        elif name == "analyze_document":
            # Use LangGraph analysis workflow
            analysis_workflow = create_analysis_workflow()
            
            document_content = arguments.get("document_content")
            document_id = arguments.get("document_id")
            
            # Get document content if ID provided
            if document_id and not document_content:
                try:
                    doc_id = int(document_id)
                    document = db_manager.get_document(doc_id)
                    if document:
                        document_content = document.content
                    else:
                        return [TextContent(type="text", text=f"문서 ID {document_id}를 찾을 수 없습니다.")]
                except ValueError:
                    return [TextContent(type="text", text="잘못된 문서 ID 형식입니다.")]
            
            if not document_content:
                return [TextContent(type="text", text="분석할 문서 내용이 없습니다.")]
            
            initial_state: AnalysisState = {
                "document_content": document_content,
                "document_metadata": {"document_id": document_id} if document_id else None,
                "analysis_type": arguments.get("analysis_type", "full"),
                "llm_provider": arguments.get("llm_provider", "openai"),
                "summary": None,
                "key_points": None,
                "legal_issues": None,
                "entities": None,
                "recommendations": None,
                "risk_assessment": None,
                "analysis_result": None,
                "error": None
            }
            
            # Run the workflow
            result = await analysis_workflow.ainvoke(initial_state)
            
            if result.get("error"):
                return [TextContent(type="text", text=f"분석 중 오류가 발생했습니다: {result['error']}")]
            
            analysis_result = result.get("analysis_result", {})
            
            # Format analysis results
            response_text = "📋 **문서 분석 결과**\n\n"
            
            if analysis_result.get("summary"):
                response_text += f"**📝 요약**\n{analysis_result['summary']}\n\n"
            
            if analysis_result.get("key_points"):
                response_text += "**🔍 핵심 사항**\n"
                for i, point in enumerate(analysis_result["key_points"], 1):
                    response_text += f"{i}. {point}\n"
                response_text += "\n"
            
            if analysis_result.get("legal_issues"):
                response_text += "**⚖️ 법적 쟁점**\n"
                for i, issue in enumerate(analysis_result["legal_issues"], 1):
                    response_text += f"{i}. {issue}\n"
                response_text += "\n"
            
            if analysis_result.get("recommendations"):
                response_text += "**💡 권고사항**\n"
                for i, rec in enumerate(analysis_result["recommendations"], 1):
                    response_text += f"{i}. {rec}\n"
                response_text += "\n"
            
            if analysis_result.get("risk_assessment"):
                response_text += f"**🚨 위험도 평가**\n{analysis_result['risk_assessment']}\n\n"
            
            return [TextContent(type="text", text=response_text)]
            
        elif name == "get_document":
            document_id = arguments["document_id"]
            document = db_manager.get_document(document_id)
            
            if not document:
                return [TextContent(type="text", text=f"문서 ID {document_id}를 찾을 수 없습니다.")]
            
            response_text = f"**제목**: {document.title}\n"
            response_text += f"**유형**: {document.document_type}\n"
            response_text += f"**카테고리**: {document.category}\n"
            response_text += f"**출처**: {document.source}\n"
            response_text += f"**작성자**: {document.author}\n"
            response_text += f"**생성일**: {document.date_created}\n\n"
            response_text += f"**내용**:\n{document.content}\n"
            
            return [TextContent(type="text", text=response_text)]
            
        elif name == "add_document":
            from core.models.legal_document import LegalDocumentCreate
            
            # Create document
            document_data = LegalDocumentCreate(
                title=arguments["title"],
                content=arguments["content"],
                document_type=arguments["document_type"],
                category=arguments.get("category"),
                source=arguments.get("source"),
                author=arguments.get("author"),
                tags=arguments.get("tags")
            )
            
            # Add to PostgreSQL
            new_document = db_manager.create_document(document_data)
            
            # Add to vector store
            vector_store.add_document(
                document_id=str(new_document.id),
                content=new_document.content,
                metadata={
                    "title": new_document.title,
                    "document_type": new_document.document_type,
                    "category": new_document.category
                }
            )
            
            return [TextContent(type="text", text=f"문서가 성공적으로 추가되었습니다. ID: {new_document.id}")]
        
        else:
            return [TextContent(type="text", text=f"알 수 없는 도구: {name}")]
            
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        return [TextContent(type="text", text=f"도구 실행 중 오류가 발생했습니다: {str(e)}")]


async def main():
    """Run the Legal Database MCP server"""
    # Import here to avoid issues with event loop
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream, 
            InitializationOptions(
                server_name="legal-database",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main()) 