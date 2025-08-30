"""
AI Services Router
AI服务路由 - 处理自然语言查询、智能分析等
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from typing import Dict, Any, List, Optional
import structlog

from ..middleware.auth import get_current_user
from ..services.proxy import get_service_proxy

logger = structlog.get_logger()
router = APIRouter()


@router.post("/chat")
async def ai_chat(
    request: Request,
    chat_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    AI对话接口
    处理自然语言查询和分析请求
    """
    try:
        proxy = get_service_proxy(request)
        
        # 添加用户上下文
        chat_request.update({
            "user_id": current_user["user_id"],
            "user_email": current_user.get("email"),
            "request_id": getattr(request.state, 'request_id', 'unknown')
        })
        
        response = await proxy.forward_request(
            service="ai_service",
            path="chat",
            request=request,
            json_data=chat_request
        )
        
        logger.info(
            "AI chat request forwarded",
            user_id=current_user["user_id"],
            message_length=len(chat_request.get("message", "")),
            session_id=chat_request.get("session_id")
        )
        
        return response
        
    except Exception as e:
        logger.error("AI chat forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service unavailable"
        )


@router.post("/query")
async def natural_language_query(
    request: Request,
    query_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    自然语言数据查询
    将自然语言转换为数据查询和分析
    """
    try:
        proxy = get_service_proxy(request)
        
        query_request.update({
            "user_id": current_user["user_id"],
            "request_id": getattr(request.state, 'request_id', 'unknown')
        })
        
        response = await proxy.forward_request(
            service="ai_service",
            path="query",
            request=request,
            json_data=query_request
        )
        
        logger.info(
            "Natural language query request forwarded",
            user_id=current_user["user_id"],
            dataset_id=query_request.get("dataset_id"),
            query=query_request.get("query", "")[:100]  # Log first 100 chars
        )
        
        return response
        
    except Exception as e:
        logger.error("Natural language query forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service unavailable"
        )


@router.post("/insights")
async def generate_insights(
    request: Request,
    insights_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    生成数据洞察
    基于数据自动生成分析洞察和建议
    """
    try:
        proxy = get_service_proxy(request)
        
        insights_request.update({
            "user_id": current_user["user_id"],
            "request_id": getattr(request.state, 'request_id', 'unknown')
        })
        
        response = await proxy.forward_request(
            service="ai_service",
            path="insights",
            request=request,
            json_data=insights_request
        )
        
        logger.info(
            "Insights generation request forwarded",
            user_id=current_user["user_id"],
            dataset_id=insights_request.get("dataset_id")
        )
        
        return response
        
    except Exception as e:
        logger.error("Insights generation forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service unavailable"
        )


@router.post("/recommendations")
async def get_recommendations(
    request: Request,
    recommendation_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取分析建议
    基于数据特征推荐合适的分析方法
    """
    try:
        proxy = get_service_proxy(request)
        
        recommendation_request.update({
            "user_id": current_user["user_id"],
            "request_id": getattr(request.state, 'request_id', 'unknown')
        })
        
        response = await proxy.forward_request(
            service="ai_service",
            path="recommendations",
            request=request,
            json_data=recommendation_request
        )
        
        logger.info(
            "Recommendations request forwarded",
            user_id=current_user["user_id"],
            dataset_id=recommendation_request.get("dataset_id")
        )
        
        return response
        
    except Exception as e:
        logger.error("Recommendations forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service unavailable"
        )


@router.get("/sessions")
async def list_chat_sessions(
    request: Request,
    page: int = 1,
    limit: int = 20,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取对话会话列表
    列出用户的AI对话历史
    """
    try:
        proxy = get_service_proxy(request)
        
        params = {
            "user_id": current_user["user_id"],
            "page": page,
            "limit": limit
        }
        
        response = await proxy.forward_request(
            service="ai_service",
            path="sessions",
            request=request,
            params=params
        )
        
        logger.debug(
            "Chat sessions list request forwarded",
            user_id=current_user["user_id"],
            page=page,
            limit=limit
        )
        
        return response
        
    except Exception as e:
        logger.error("Chat sessions list forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service unavailable"
        )


@router.get("/sessions/{session_id}")
async def get_chat_session(
    request: Request,
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取对话会话详情
    包含完整的对话历史
    """
    try:
        proxy = get_service_proxy(request)
        
        response = await proxy.forward_request(
            service="ai_service",
            path=f"sessions/{session_id}",
            request=request,
            params={"user_id": current_user["user_id"]}
        )
        
        logger.debug(
            "Chat session detail request forwarded",
            user_id=current_user["user_id"],
            session_id=session_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Chat session detail forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service unavailable"
        )


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    request: Request,
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    删除对话会话
    清除对话历史记录
    """
    try:
        proxy = get_service_proxy(request)
        
        response = await proxy.forward_request(
            service="ai_service",
            path=f"sessions/{session_id}",
            request=request,
            params={"user_id": current_user["user_id"]}
        )
        
        logger.info(
            "Chat session delete request forwarded",
            user_id=current_user["user_id"],
            session_id=session_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Chat session delete forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service unavailable"
        )


@router.post("/explain")
async def explain_analysis(
    request: Request,
    explain_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    解释分析结果
    用自然语言解释复杂的分析结果
    """
    try:
        proxy = get_service_proxy(request)
        
        explain_request.update({
            "user_id": current_user["user_id"],
            "request_id": getattr(request.state, 'request_id', 'unknown')
        })
        
        response = await proxy.forward_request(
            service="ai_service",
            path="explain",
            request=request,
            json_data=explain_request
        )
        
        logger.info(
            "Analysis explanation request forwarded",
            user_id=current_user["user_id"],
            analysis_id=explain_request.get("analysis_id")
        )
        
        return response
        
    except Exception as e:
        logger.error("Analysis explanation forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service unavailable"
        )