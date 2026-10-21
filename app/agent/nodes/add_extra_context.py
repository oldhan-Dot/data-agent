# 负责定义添加额外上下文信息的节点


from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def add_extra_context(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    #自定义数据输出
    runtime.stream_writer("添加额外上下文信息")


    try:
        #处理
        return {}
    except Exception as e:
        logger.error("添加额外上下文信息失败")
        raise

