# 负责定义执行SQL的节点
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def execute_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    #自定义数据输出
    runtime.stream_writer("执行SQL")


    try:
        #处理
        return {}
    except Exception as e:
        logger.error("执行SQL失败")
        raise
