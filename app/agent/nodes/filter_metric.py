# 负责定义过滤指标信息的节点
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def filter_metric(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    #自定义数据输出
    runtime.stream_writer("过滤指标信息")


    try:
        #处理
        return {}
    except Exception as e:
        logger.error("过滤指标信息失败")
        raise
