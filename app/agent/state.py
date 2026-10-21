from typing import TypedDict


class DataAgentState(TypedDict):
    query :str #用户提问
    keywords:list[str] #分词列表
    sql:str #生成的sql
    error:str #检验失败的信息