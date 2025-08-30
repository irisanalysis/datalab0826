"""
Analysis Router
数据分析路由 - 处理统计分析、机器学习等
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from typing import Dict, Any, List, Optional
import structlog

from ..middleware.auth import get_current_user
from ..services.proxy import get_service_proxy

logger = structlog.get_logger()
router = APIRouter()


@router.post("/statistical")
async def statistical_analysis(
    request: Request,
    analysis_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    执行统计分析
    支持描述性统计、相关性分析、假设检验等
    """
    try:
        proxy = get_service_proxy(request)
        
        # 添加用户ID到请求
        analysis_request["user_id"] = current_user["user_id"]
        
        response = await proxy.forward_request(
            service="compute_service",
            path="analysis/statistical",
            request=request,
            json_data=analysis_request
        )
        
        logger.info(
            "Statistical analysis request forwarded",
            user_id=current_user["user_id"],
            dataset_id=analysis_request.get("dataset_id"),
            analysis_type=analysis_request.get("type")
        )
        
        return response
        
    except Exception as e:
        logger.error("Statistical analysis forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compute service unavailable"
        )


@router.post("/regression")
async def regression_analysis(
    request: Request,
    regression_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    执行回归分析
    支持线性回归、逻辑回归、多项式回归等
    """
    try:
        proxy = get_service_proxy(request)
        
        regression_request["user_id"] = current_user["user_id"]
        
        response = await proxy.forward_request(
            service="compute_service",
            path="analysis/regression",
            request=request,
            json_data=regression_request
        )
        
        logger.info(
            "Regression analysis request forwarded",
            user_id=current_user["user_id"],
            dataset_id=regression_request.get("dataset_id"),
            model_type=regression_request.get("model_type")
        )
        
        return response
        
    except Exception as e:
        logger.error("Regression analysis forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compute service unavailable"
        )


@router.post("/clustering")
async def clustering_analysis(
    request: Request,
    clustering_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    执行聚类分析
    支持K-means、DBSCAN、层次聚类等
    """
    try:
        proxy = get_service_proxy(request)
        
        clustering_request["user_id"] = current_user["user_id"]
        
        response = await proxy.forward_request(
            service="compute_service",
            path="analysis/clustering",
            request=request,
            json_data=clustering_request
        )
        
        logger.info(
            "Clustering analysis request forwarded",
            user_id=current_user["user_id"],
            dataset_id=clustering_request.get("dataset_id"),
            algorithm=clustering_request.get("algorithm")
        )
        
        return response
        
    except Exception as e:
        logger.error("Clustering analysis forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compute service unavailable"
        )


@router.post("/classification")
async def classification_analysis(
    request: Request,
    classification_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    执行分类分析
    支持决策树、随机森林、SVM等
    """
    try:
        proxy = get_service_proxy(request)
        
        classification_request["user_id"] = current_user["user_id"]
        
        response = await proxy.forward_request(
            service="compute_service",
            path="analysis/classification",
            request=request,
            json_data=classification_request
        )
        
        logger.info(
            "Classification analysis request forwarded",
            user_id=current_user["user_id"],
            dataset_id=classification_request.get("dataset_id"),
            model_type=classification_request.get("model_type")
        )
        
        return response
        
    except Exception as e:
        logger.error("Classification analysis forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compute service unavailable"
        )


@router.get("/jobs")
async def list_analysis_jobs(
    request: Request,
    page: int = 1,
    limit: int = 20,
    status_filter: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取分析任务列表
    支持按状态筛选和分页
    """
    try:
        proxy = get_service_proxy(request)
        
        params = {
            "user_id": current_user["user_id"],
            "page": page,
            "limit": limit
        }
        if status_filter:
            params["status"] = status_filter
        
        response = await proxy.forward_request(
            service="compute_service",
            path="analysis/jobs",
            request=request,
            params=params
        )
        
        logger.debug(
            "Analysis jobs list request forwarded",
            user_id=current_user["user_id"],
            page=page,
            limit=limit,
            status_filter=status_filter
        )
        
        return response
        
    except Exception as e:
        logger.error("Analysis jobs list forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compute service unavailable"
        )


@router.get("/jobs/{job_id}")
async def get_analysis_job(
    request: Request,
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取分析任务详情
    包括状态、结果、日志等
    """
    try:
        proxy = get_service_proxy(request)
        
        response = await proxy.forward_request(
            service="compute_service",
            path=f"analysis/jobs/{job_id}",
            request=request,
            params={"user_id": current_user["user_id"]}
        )
        
        logger.debug(
            "Analysis job detail request forwarded",
            user_id=current_user["user_id"],
            job_id=job_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Analysis job detail forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compute service unavailable"
        )


@router.get("/jobs/{job_id}/results")
async def get_analysis_results(
    request: Request,
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取分析结果
    包括统计数据、图表数据等
    """
    try:
        proxy = get_service_proxy(request)
        
        response = await proxy.forward_request(
            service="compute_service",
            path=f"analysis/jobs/{job_id}/results",
            request=request,
            params={"user_id": current_user["user_id"]}
        )
        
        logger.debug(
            "Analysis results request forwarded",
            user_id=current_user["user_id"],
            job_id=job_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Analysis results forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compute service unavailable"
        )


@router.delete("/jobs/{job_id}")
async def cancel_analysis_job(
    request: Request,
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    取消分析任务
    停止正在运行的分析任务
    """
    try:
        proxy = get_service_proxy(request)
        
        response = await proxy.forward_request(
            service="compute_service",
            path=f"analysis/jobs/{job_id}/cancel",
            request=request,
            params={"user_id": current_user["user_id"]}
        )
        
        logger.info(
            "Analysis job cancel request forwarded",
            user_id=current_user["user_id"],
            job_id=job_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Analysis job cancel forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compute service unavailable"
        )


@router.post("/correlations")
async def correlation_analysis(
    request: Request,
    correlation_request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    执行相关性分析
    计算变量间的相关系数
    """
    try:
        proxy = get_service_proxy(request)
        
        correlation_request["user_id"] = current_user["user_id"]
        
        response = await proxy.forward_request(
            service="compute_service",
            path="analysis/correlations",
            request=request,
            json_data=correlation_request
        )
        
        logger.info(
            "Correlation analysis request forwarded",
            user_id=current_user["user_id"],
            dataset_id=correlation_request.get("dataset_id")
        )
        
        return response
        
    except Exception as e:
        logger.error("Correlation analysis forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compute service unavailable"
        )