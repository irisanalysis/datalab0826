"""
Visualizations Router  
可视化路由 - 处理图表生成、导出等
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from typing import Dict, Any, List, Optional
import structlog

from ..middleware.auth import get_current_user
from ..services.proxy import get_service_proxy

logger = structlog.get_logger()
router = APIRouter()


@router.post("/generate")
async def generate_visualization(
    request: Request,
    viz_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    生成可视化图表
    支持多种图表类型和自定义配置
    """
    try:
        proxy = get_service_proxy(request)
        
        viz_request.update({
            "user_id": current_user["user_id"],
            "request_id": getattr(request.state, 'request_id', 'unknown')
        })
        
        response = await proxy.forward_request(
            service="viz_service",
            path="visualizations/generate",
            request=request,
            json_data=viz_request
        )
        
        logger.info(
            "Visualization generation request forwarded",
            user_id=current_user["user_id"],
            dataset_id=viz_request.get("dataset_id"),
            chart_type=viz_request.get("chart_type")
        )
        
        return response
        
    except Exception as e:
        logger.error("Visualization generation forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visualization service unavailable"
        )


@router.get("/")
async def list_visualizations(
    request: Request,
    page: int = 1,
    limit: int = 20,
    chart_type: Optional[str] = None,
    dataset_id: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取可视化图表列表
    支持按图表类型和数据集筛选
    """
    try:
        proxy = get_service_proxy(request)
        
        params = {
            "user_id": current_user["user_id"],
            "page": page,
            "limit": limit
        }
        
        if chart_type:
            params["chart_type"] = chart_type
        if dataset_id:
            params["dataset_id"] = dataset_id
        
        response = await proxy.forward_request(
            service="viz_service",
            path="visualizations",
            request=request,
            params=params
        )
        
        logger.debug(
            "Visualization list request forwarded",
            user_id=current_user["user_id"],
            page=page,
            limit=limit,
            chart_type=chart_type,
            dataset_id=dataset_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Visualization list forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visualization service unavailable"
        )


@router.get("/{viz_id}")
async def get_visualization(
    request: Request,
    viz_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取可视化图表详情
    包含图表配置和数据
    """
    try:
        proxy = get_service_proxy(request)
        
        response = await proxy.forward_request(
            service="viz_service",
            path=f"visualizations/{viz_id}",
            request=request,
            params={"user_id": current_user["user_id"]}
        )
        
        logger.debug(
            "Visualization detail request forwarded",
            user_id=current_user["user_id"],
            viz_id=viz_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Visualization detail forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visualization service unavailable"
        )


@router.put("/{viz_id}")
async def update_visualization(
    request: Request,
    viz_id: str,
    update_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    更新可视化图表
    修改图表配置、样式等
    """
    try:
        proxy = get_service_proxy(request)
        
        update_data["user_id"] = current_user["user_id"]
        
        response = await proxy.forward_request(
            service="viz_service",
            path=f"visualizations/{viz_id}",
            request=request,
            json_data=update_data
        )
        
        logger.info(
            "Visualization update request forwarded",
            user_id=current_user["user_id"],
            viz_id=viz_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Visualization update forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visualization service unavailable"
        )


@router.delete("/{viz_id}")
async def delete_visualization(
    request: Request,
    viz_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    删除可视化图表
    """
    try:
        proxy = get_service_proxy(request)
        
        response = await proxy.forward_request(
            service="viz_service",
            path=f"visualizations/{viz_id}",
            request=request,
            params={"user_id": current_user["user_id"]}
        )
        
        logger.info(
            "Visualization delete request forwarded",
            user_id=current_user["user_id"],
            viz_id=viz_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Visualization delete forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visualization service unavailable"
        )


@router.post("/{viz_id}/export")
async def export_visualization(
    request: Request,
    viz_id: str,
    export_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    导出可视化图表
    支持PNG、PDF、SVG等格式
    """
    try:
        proxy = get_service_proxy(request)
        
        export_request.update({
            "user_id": current_user["user_id"],
            "viz_id": viz_id
        })
        
        response = await proxy.forward_request(
            service="viz_service",
            path=f"visualizations/{viz_id}/export",
            request=request,
            json_data=export_request
        )
        
        logger.info(
            "Visualization export request forwarded",
            user_id=current_user["user_id"],
            viz_id=viz_id,
            format=export_request.get("format")
        )
        
        return response
        
    except Exception as e:
        logger.error("Visualization export forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visualization service unavailable"
        )


@router.get("/templates/list")
async def list_chart_templates(
    request: Request,
    category: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取图表模板列表
    按类别筛选可用模板
    """
    try:
        proxy = get_service_proxy(request)
        
        params = {"user_id": current_user["user_id"]}
        if category:
            params["category"] = category
        
        response = await proxy.forward_request(
            service="viz_service",
            path="visualizations/templates",
            request=request,
            params=params
        )
        
        logger.debug(
            "Chart templates list request forwarded",
            user_id=current_user["user_id"],
            category=category
        )
        
        return response
        
    except Exception as e:
        logger.error("Chart templates list forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visualization service unavailable"
        )


@router.post("/smart-suggest")
async def suggest_visualizations(
    request: Request,
    suggest_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    智能图表推荐
    基于数据特征推荐合适的可视化类型
    """
    try:
        proxy = get_service_proxy(request)
        
        suggest_request.update({
            "user_id": current_user["user_id"],
            "request_id": getattr(request.state, 'request_id', 'unknown')
        })
        
        response = await proxy.forward_request(
            service="viz_service",
            path="visualizations/smart-suggest",
            request=request,
            json_data=suggest_request
        )
        
        logger.info(
            "Smart visualization suggestion request forwarded",
            user_id=current_user["user_id"],
            dataset_id=suggest_request.get("dataset_id")
        )
        
        return response
        
    except Exception as e:
        logger.error("Smart visualization suggestion forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visualization service unavailable"
        )


@router.post("/dashboards")
async def create_dashboard(
    request: Request,
    dashboard_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    创建数据看板
    组合多个可视化图表
    """
    try:
        proxy = get_service_proxy(request)
        
        dashboard_request.update({
            "user_id": current_user["user_id"],
            "request_id": getattr(request.state, 'request_id', 'unknown')
        })
        
        response = await proxy.forward_request(
            service="viz_service",
            path="visualizations/dashboards",
            request=request,
            json_data=dashboard_request
        )
        
        logger.info(
            "Dashboard creation request forwarded",
            user_id=current_user["user_id"],
            dashboard_name=dashboard_request.get("name")
        )
        
        return response
        
    except Exception as e:
        logger.error("Dashboard creation forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visualization service unavailable"
        )