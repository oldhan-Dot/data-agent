# 负责定义合并召回信息的节点
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def merge_retrieved_info(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    #自定义数据输出
    runtime.stream_writer("合并召回信息")


    try:
        #处理
        return {}
    except Exception as e:
        logger.error("合并召回信息失败")
        raise
