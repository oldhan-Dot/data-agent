# 负责定义召回字段取值的节点
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def recall_value(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    #自定义数据输出
    runtime.stream_writer("召回字段取值")


    try:
        #处理
        return {}
    except Exception as e:
        logger.error("召回字段取值失败")
        raise
