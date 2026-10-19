#定制日志输出格式，控制日志输出级别
#自动将日志内容保存到日志文件
#指定日志文件的最大大小，一旦超过自动创建一个新的日志文件
#指定日志文件有效期，一旦超过就删除
#记录当前日志输出是哪个请求的，记录请求id
import asyncio
import sys
import uuid

from loguru import logger

from app.conf.app_config import app_config
from app.core.context import set_request_id, get_request_id, reset_request_id

#配置日志格式
log_format = (
    "<yellow>{time:YYYY-MM-DD HH:mm:ss.SSS}</yellow> | "  # 绿色显示日志时间（精确到毫秒）
    "<level>{level: <8}</level> | "  # 按级别颜色显示日志级别（左对齐，占8个字符）
    "<magenta>request_id - {extra[request_id]}</magenta> | "  # 品红色显示request_id（从日志extra中获取）
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "  # 青色显示日志所在文件、函数、行号
    "<level>{message}</level>"  # 按级别颜色显示日志正文
)
#移除loguru库默认配置
logger.remove()

#给日志打补丁
#补丁函数：在每次输出日志前自动执行(回调函数：不调用在一定条件下自动执行)
def inject_request_id(record):
    #读取请求id并保存到record中
    record["extra"]["request_id"] = get_request_id()

logger = logger.patch(inject_request_id)


#添加控制台配置
if app_config.logging.console.enable:
    logger.add(
        sys.stdout,#标准输出(控制台输出)
        level = app_config.logging.console.level, #指定输出显示级别
        format = log_format
    )
#添加日志文件输出配置
if app_config.logging.file.enable:
    logger.add(
        "logger/app.log",#标准输出(控制台输出),
        level=app_config.logging.file.level,
        format = log_format,
        rotation=app_config.logging.file.rotation,#文件的最大大小
        retention=app_config.logging.file.retention#文件的有效期
    )



if __name__ == '__main__':
    # set_request_id(str(uuid.uuid4()))
    # logger.trace("这是 TRACE 级别的调试信息")  # 不会输出到控制台（控制台是 INFO），但会输出到文件
    # logger.debug("这是 DEBUG 级别的调试信息")  # 同上
    # logger.info("服务启动成功")  # 控制台+文件都输出
    # logger.success("数据同步完成")  # Loguru 独有级别
    # logger.warning("内存使用率超过 80%")
    # logger.error("接口调用失败：超时")
    # logger.critical("数据库连接中断，服务停止")

    async def req1():
        logger.info(f"1--req1 req_id = {get_request_id()}")
        token = set_request_id(str(uuid.uuid4()))
        await asyncio.sleep(2)
        logger.info(f"2--req1 req_id = {get_request_id()}")
        reset_request_id(token)
        logger.info(f"3--req1 req_id = {get_request_id()}")


    async def req2():
        logger.info(f"1--req2 req_id = {get_request_id()}")
        token = set_request_id(str(uuid.uuid4()))
        await asyncio.sleep(2)
        logger.info(f"2--req2 req_id = {get_request_id()}")
        reset_request_id(token)
        logger.info(f"3--req2 req_id = {get_request_id()}")

    async def test():
        await asyncio.gather(req1(),req2())
    asyncio.run(test())

