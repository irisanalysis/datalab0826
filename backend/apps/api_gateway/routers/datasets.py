"""
Datasets Router
数据集路由 - 处理数据集的上传、管理、查询等
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends, File, UploadFile
from typing import Dict, Any, List, Optional
import structlog

from ..middleware.auth import get_current_user
from ..services.proxy import get_service_proxy

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def list_datasets(
    request: Request,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取数据集列表
    支持分页和搜索
    """
    try:
        proxy = get_service_proxy(request)
        
        # 构建查询参数
        params = {
            "page": page,
            "limit": limit,
            "user_id": current_user["user_id"]
        }
        if search:
            params["search"] = search
        
        response = await proxy.forward_request(
            service="data_service",
            path="datasets",
            request=request,
            params=params
        )
        
        logger.debug(
            "Dataset list request forwarded",
            user_id=current_user["user_id"],
            page=page,
            limit=limit,
            search=search
        )
        
        return response
        
    except Exception as e:
        logger.error("Dataset list forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data service unavailable"
        )


@router.post("/upload")
async def upload_dataset(
    request: Request,
    file: UploadFile = File(...),
    name: Optional[str] = None,
    description: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    上传数据集文件
    支持CSV、JSON、Excel等格式
    """
    try:
        proxy = get_service_proxy(request)
        
        # 准备上传数据
        upload_data = {
            "user_id": current_user["user_id"],
            "name": name or file.filename,
            "description": description,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size
        }
        
        response = await proxy.forward_file_upload(
            service="data_service",
            path="datasets/upload",
            request=request,
            file=file,
            data=upload_data
        )
        
        logger.info(
            "Dataset upload request forwarded",
            user_id=current_user["user_id"],
            filename=file.filename,
            size=file.size,
            content_type=file.content_type
        )
        
        return response
        
    except Exception as e:
        logger.error("Dataset upload forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data service unavailable"
        )


@router.get("/{dataset_id}")
async def get_dataset(
    request: Request,
    dataset_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取数据集详细信息
    包括元数据和预览数据
    """
    try:
        proxy = get_service_proxy(request)
        
        response = await proxy.forward_request(
            service="data_service",
            path=f"datasets/{dataset_id}",
            request=request,
            params={"user_id": current_user["user_id"]}
        )
        
        logger.debug(
            "Dataset detail request forwarded",
            user_id=current_user["user_id"],
            dataset_id=dataset_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Dataset detail forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data service unavailable"
        )


@router.get("/{dataset_id}/preview")
async def preview_dataset(
    request: Request,
    dataset_id: str,
    rows: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    预览数据集内容
    返回指定行数的数据预览
    """
    try:
        proxy = get_service_proxy(request)
        
        response = await proxy.forward_request(
            service="data_service",
            path=f"datasets/{dataset_id}/preview",
            request=request,
            params={
                "user_id": current_user["user_id"],
                "rows": rows
            }
        )
        
        logger.debug(
            "Dataset preview request forwarded",
            user_id=current_user["user_id"],
            dataset_id=dataset_id,
            rows=rows
        )
        
        return response
        
    except Exception as e:
        logger.error("Dataset preview forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data service unavailable"
        )


@router.get("/{dataset_id}/schema")
async def get_dataset_schema(
    request: Request,
    dataset_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取数据集模式信息
    包括列名、数据类型、统计信息等
    """
    try:
        proxy = get_service_proxy(request)
        
        response = await proxy.forward_request(
            service="data_service",
            path=f"datasets/{dataset_id}/schema",
            request=request,
            params={"user_id": current_user["user_id"]}
        )
        
        logger.debug(
            "Dataset schema request forwarded",
            user_id=current_user["user_id"],
            dataset_id=dataset_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Dataset schema forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data service unavailable"
        )


@router.put("/{dataset_id}")
async def update_dataset(
    request: Request,
    dataset_id: str,
    update_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    更新数据集信息
    如名称、描述等元数据
    """
    try:
        proxy = get_service_proxy(request)
        
        # 添加用户ID验证
        update_data["user_id"] = current_user["user_id"]
        
        response = await proxy.forward_request(
            service="data_service",
            path=f"datasets/{dataset_id}",
            request=request,
            json_data=update_data
        )
        
        logger.info(
            "Dataset update request forwarded",
            user_id=current_user["user_id"],
            dataset_id=dataset_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Dataset update forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data service unavailable"
        )


@router.delete("/{dataset_id}")
async def delete_dataset(
    request: Request,
    dataset_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    删除数据集
    包括文件和元数据
    """
    try:
        proxy = get_service_proxy(request)
        
        response = await proxy.forward_request(
            service="data_service",
            path=f"datasets/{dataset_id}",
            request=request,
            params={"user_id": current_user["user_id"]}
        )
        
        logger.info(
            "Dataset delete request forwarded",
            user_id=current_user["user_id"],
            dataset_id=dataset_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Dataset delete forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data service unavailable"
        )


@router.post("/{dataset_id}/validate")
async def validate_dataset(
    request: Request,
    dataset_id: str,
    validation_rules: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    验证数据集质量
    检查数据完整性、格式等
    """
    try:
        proxy = get_service_proxy(request)
        
        validation_data = {
            "user_id": current_user["user_id"],
            "rules": validation_rules
        }
        
        response = await proxy.forward_request(
            service="data_service",
            path=f"datasets/{dataset_id}/validate",
            request=request,
            json_data=validation_data
        )
        
        logger.info(
            "Dataset validation request forwarded",
            user_id=current_user["user_id"],
            dataset_id=dataset_id
        )
        
        return response
        
    except Exception as e:
        logger.error("Dataset validation forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data service unavailable"
        )