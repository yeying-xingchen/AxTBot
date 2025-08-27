from fastapi import Request, status
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# 错误信息映射
ERROR_INFO = {
    404: {
        "title": "页面未找到",
        "description": "您正在寻找的页面可能已被移除、名称已更改或暂时不可用。请检查URL是否正确。",
    },
    500: {
        "title": "服务器内部错误",
        "description": "服务器遇到意外情况，无法完成您的请求。我们的技术团队已收到通知，将尽快解决此问题。",
    },
    403: {
        "title": "禁止访问",
        "description": "您没有权限访问此资源。如果您认为这是错误，请联系管理员。",
    },
    401: {
        "title": "未经授权",
        "description": "您需要登录才能访问此资源。请提供有效的凭证。",
    },
    400: {
        "title": "请求无效",
        "description": "服务器无法理解您的请求。请检查输入是否正确。",
    },
    405: {
        "title": "方法不允许",
        "description": "您所使用的请求方法不被允许，请检查请求方法。",
    },
}

# 默认错误信息
DEFAULT_ERROR = {
    "title": "发生错误",
    "description": "处理您的请求时出现问题。请稍后再试或联系支持团队。",
}

async def universal_exception_handler(request: Request, exc: Exception):
    # 对于未捕获的异常，返回500错误页面
    status_code = 500
    error_info = ERROR_INFO.get(status_code, DEFAULT_ERROR)

    return JSONResponse(
        {
            "code": status_code,
            "data": {
                "title": error_info["title"],
                "description": error_info["description"],}
        },
        status_code=status_code
    )


async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    status_code = exc.status_code
    error_info = ERROR_INFO.get(status_code, DEFAULT_ERROR)

    return JSONResponse(
        {
            "code": status_code,
            "data": {
                "title": error_info["title"],
                "description": error_info["description"]
            }
        },
        status_code=status_code
    )

async def custom_validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
):
    # 重构错误格式
    reformatted_errors = []
    for error in exc.errors():
        reformatted_errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "data": {
                "title": "请求验证失败",
                "description": "表单项不完整，请确保表单被正确地传递到后端"
            },
        },
    )