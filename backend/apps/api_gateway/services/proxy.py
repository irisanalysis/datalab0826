"""
Service Proxy
服务代理 - 负责转发请求到微服务
"""
import asyncio
import time
from typing import Dict, Any, Optional, Union
import aiohttp
import structlog
from fastapi import Request, HTTPException, UploadFile
import json

from ..config import settings

logger = structlog.get_logger()


class ServiceProxy:
    """微服务代理"""
    
    def __init__(self, service_registry: Dict[str, str]):
        """
        初始化服务代理
        
        Args:
            service_registry: 服务注册表，映射服务名到URL
        """
        self.service_registry = service_registry
        self.session: Optional[aiohttp.ClientSession] = None
        self._health_status: Dict[str, Dict[str, Any]] = {}
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(
                total=settings.request_timeout,
                connect=10
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "User-Agent": f"{settings.app_name}/1.0"
                }
            )
        return self.session
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def forward_request(
        self,
        service: str,
        path: str,
        request: Request,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        转发HTTP请求到微服务
        
        Args:
            service: 目标服务名
            path: 请求路径
            request: 原始请求对象
            params: 查询参数
            json_data: JSON数据
            
        Returns:
            服务响应数据
        """
        if service not in self.service_registry:
            raise HTTPException(
                status_code=404,
                detail=f"Service '{service}' not found"
            )
        
        service_url = self.service_registry[service]
        full_url = f"{service_url.rstrip('/')}/{path.lstrip('/')}"
        
        try:
            session = await self._get_session()
            
            # 准备请求头
            headers = self._prepare_headers(request)
            
            # 准备请求体
            request_kwargs = {
                "headers": headers,
                "params": params or {},
            }
            
            if json_data:
                request_kwargs["json"] = json_data
            elif request.method in ["POST", "PUT", "PATCH"]:
                # 尝试读取原始请求体
                try:
                    body = await request.body()
                    if body:
                        request_kwargs["data"] = body
                        headers["Content-Type"] = request.headers.get("Content-Type", "application/json")
                except Exception as e:
                    logger.warning("Failed to read request body", error=str(e))
            
            # 发送请求
            start_time = time.time()
            async with session.request(
                method=request.method,
                url=full_url,
                **request_kwargs
            ) as response:
                response_time = time.time() - start_time
                
                # 记录请求日志
                logger.info(
                    "Service request completed",
                    service=service,
                    path=path,
                    method=request.method,
                    status_code=response.status,
                    response_time=f"{response_time:.3f}s",
                    request_id=getattr(request.state, 'request_id', 'unknown')
                )
                
                # 检查响应状态
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(
                        "Service request failed",
                        service=service,
                        path=path,
                        status_code=response.status,
                        error=error_text
                    )
                    
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Service '{service}' returned error: {error_text}"
                    )
                
                # 解析响应
                try:
                    if response.headers.get("Content-Type", "").startswith("application/json"):
                        return await response.json()
                    else:
                        text_content = await response.text()
                        return {"content": text_content, "content_type": response.headers.get("Content-Type")}
                except Exception as e:
                    logger.error("Failed to parse service response", error=str(e))
                    return {"error": "Failed to parse response", "raw_content": await response.text()}
        
        except aiohttp.ClientError as e:
            logger.error(
                "Service connection failed",
                service=service,
                url=full_url,
                error=str(e)
            )
            raise HTTPException(
                status_code=503,
                detail=f"Service '{service}' unavailable"
            )
        except Exception as e:
            logger.error(
                "Service request error",
                service=service,
                url=full_url,
                error=str(e)
            )
            raise HTTPException(
                status_code=500,
                detail="Internal service error"
            )
    
    async def forward_file_upload(
        self,
        service: str,
        path: str,
        request: Request,
        file: UploadFile,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        转发文件上传请求到微服务
        
        Args:
            service: 目标服务名
            path: 请求路径
            request: 原始请求对象
            file: 上传文件
            data: 附加数据
            
        Returns:
            服务响应数据
        """
        if service not in self.service_registry:
            raise HTTPException(
                status_code=404,
                detail=f"Service '{service}' not found"
            )
        
        service_url = self.service_registry[service]
        full_url = f"{service_url.rstrip('/')}/{path.lstrip('/')}"
        
        try:
            session = await self._get_session()
            headers = self._prepare_headers(request, exclude_content_type=True)
            
            # 准备multipart form data
            form_data = aiohttp.FormData()
            
            # 添加文件
            form_data.add_field(
                'file',
                file.file,
                filename=file.filename,
                content_type=file.content_type
            )
            
            # 添加其他数据
            if data:
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        form_data.add_field(key, json.dumps(value))
                    else:
                        form_data.add_field(key, str(value))
            
            # 发送请求
            start_time = time.time()
            async with session.post(
                url=full_url,
                headers=headers,
                data=form_data
            ) as response:
                response_time = time.time() - start_time
                
                logger.info(
                    "File upload request completed",
                    service=service,
                    path=path,
                    filename=file.filename,
                    size=file.size,
                    status_code=response.status,
                    response_time=f"{response_time:.3f}s"
                )
                
                if response.status >= 400:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"File upload to service '{service}' failed: {error_text}"
                    )
                
                return await response.json()
        
        except aiohttp.ClientError as e:
            logger.error("File upload connection failed", service=service, error=str(e))
            raise HTTPException(status_code=503, detail=f"Service '{service}' unavailable")
        except Exception as e:
            logger.error("File upload error", service=service, error=str(e))
            raise HTTPException(status_code=500, detail="File upload failed")
    
    def _prepare_headers(self, request: Request, exclude_content_type: bool = False) -> Dict[str, str]:
        """准备转发请求的头信息"""
        headers = {}
        
        # 转发认证头
        if "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]
        
        # 转发请求ID
        if hasattr(request.state, 'request_id'):
            headers["X-Request-ID"] = request.state.request_id
        
        # 转发客户端信息
        if "User-Agent" in request.headers:
            headers["X-Original-User-Agent"] = request.headers["User-Agent"]
        
        # 转发内容类型
        if not exclude_content_type and "Content-Type" in request.headers:
            headers["Content-Type"] = request.headers["Content-Type"]
        
        return headers
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """检查所有服务健康状态"""
        results = {}
        
        for service_name, service_url in self.service_registry.items():
            try:
                results[service_name] = await self.health_check_service(service_name)
            except Exception as e:
                logger.error(f"Health check failed for {service_name}", error=str(e))
                results[service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": time.time()
                }
        
        return results
    
    async def health_check_service(self, service: str) -> Dict[str, Any]:
        """检查单个服务健康状态"""
        if service not in self.service_registry:
            raise ValueError(f"Unknown service: {service}")
        
        service_url = self.service_registry[service]
        health_url = f"{service_url.rstrip('/')}/health"
        
        try:
            session = await self._get_session()
            start_time = time.time()
            
            async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = {
                        "status": "healthy",
                        "response_time": f"{response_time:.3f}s",
                        "timestamp": time.time()
                    }
                    
                    # 尝试解析健康检查详细信息
                    try:
                        health_data = await response.json()
                        result.update(health_data)
                    except:
                        pass
                    
                    self._health_status[service] = result
                    return result
                else:
                    result = {
                        "status": "unhealthy",
                        "http_status": response.status,
                        "response_time": f"{response_time:.3f}s",
                        "timestamp": time.time()
                    }
                    self._health_status[service] = result
                    return result
        
        except asyncio.TimeoutError:
            result = {
                "status": "timeout",
                "error": "Health check timeout",
                "timestamp": time.time()
            }
            self._health_status[service] = result
            return result
        except Exception as e:
            result = {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
            self._health_status[service] = result
            return result
    
    def get_cached_health_status(self, service: str) -> Optional[Dict[str, Any]]:
        """获取缓存的健康状态"""
        return self._health_status.get(service)


def get_service_proxy(request: Request) -> ServiceProxy:
    """从请求中获取服务代理实例"""
    if not hasattr(request.app.state, 'service_proxy'):
        raise HTTPException(status_code=500, detail="Service proxy not initialized")
    return request.app.state.service_proxy