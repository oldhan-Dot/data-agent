from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.prompt.prompt_loader import load_prompt

"""
1.使用大模型对query进行语义关键字提取，与前面的jieba关键词进行去重合并=》keywords：list[str]
2.将所有的keywords进行向量化=》keywords:list[list[float]]
3.遍历每个关键词向量，去qdrant中匹配出一个字信息表，并进行去重合并=》recall_columns:list[ColumnInfoQdrant]
4.返回recall_columns
"""
async def recall_column(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    #自定义数据输出
    runtime.stream_writer("召回字段信息")

    try:
        query = state["query"]
        keywords = state["keywords"]
        embedding_client = runtime.context["embedding_client"]
        column_qdrant_repo = runtime.context["column_qdrant_repo"]
        #1.使用大模型对query进行语义关键字提取，与前面的jieba关键词进行去重合并=》keywords：list[str]
        prompt_template = PromptTemplate(
            template=load_prompt("extend_keywords_for_column_recall"),
            input_variables=["query"]
        )
        chain = prompt_template |  llm  | JsonOutputParser()
        result:list[str] = await chain.ainvoke({"query":query})
        logger.info(f"recall_column llm keywords = {result}")
        keywords = list(set(keywords+result))
        #2.将所有的keywords进行批量向量化=》keywords:list[list[float]]
        keyword_vectors:list[list[float]] = await embedding_client.aembed_documents(keywords)
        #3.遍历每个关键词向量，去qdrant中匹配出一个字段信息列表，并进行去重合并==> recall_columns:list[ColumnInfoQdrant]
        column_infos_dict:dict[str,ColumnInfoQdrant] = {}
        for keyword_vector in keyword_vectors:
            column_infos:list[ColumnInfoQdrant] = await column_qdrant_repo.search(keyword_vector)
            for column_info in column_infos:
                column_infos_dict[column_info["id"]] = column_info  # 如果重复就覆盖了
        #生成列表
        recall_columns = list(column_infos_dict.values())
        logger.info(f"召回字段完成：{recall_columns}")
        #4.返回recall_columns
        return {"recall_columns":recall_columns}

    except Exception as e:
        logger.error("召回字段信息失败")
        raise
