# 负责定义过滤表格信息的节点
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def filter_table(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    #自定义数据输出
    runtime.stream_writer("过滤表格信息")


    try:
        #处理
        return {}
    except Exception as e:
        logger.error("过滤表格信息失败")
        raise
