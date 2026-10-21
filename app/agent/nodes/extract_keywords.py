from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def extract_keywords(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    #自定义数据输出
    runtime.stream_writer("提取关键词")


    try:
        #处理
        return {}
    except Exception as e:
        logger.error("提取关键字失败")
        raise
