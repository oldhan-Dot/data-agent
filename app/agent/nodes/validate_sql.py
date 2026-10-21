# 负责定义校验SQL的节点
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def validate_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    #自定义数据输出
    runtime.stream_writer("校验SQL")


    try:
        #处理
        return {}
    except Exception as e:
        logger.error("校验SQL失败")
        raise
