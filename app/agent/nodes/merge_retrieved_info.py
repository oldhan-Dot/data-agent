# 负责定义合并召回信息的节点
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, TableInfoState, ColumnInfoState, MetricInfoState
from app.core.log import logger
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant

"""
1.收集一个最完整的字段信息列表 去重合并dict[column_id,ColumnInfoQdrant]
1.1收集召回的字段信息列表
1.2收集召回的指标信息列表关联的字段信息列表
1.3收集召回的字段值信息列表对应的字段信息列表=》将字段值保存到字段的值的样例列表中
1.4收集相关表的主键和外键字段信息列表
2.根据收集所有的字段信息列表生成：带字段信息列表的表信息列表
2.1对收集的字段信息列表进行按表id进行分组：dict[table_id,list[ColumnInfoQdrant]]
2.2生成带字段信息列表的表信息列表-》table_infos:list[TableInfoState]
    根据表id查询meta的到表信息
    根据当前字段信息列表-生成ColumnInfoState类型的字段状态信息列表
"""


async def merge_retrieved_info(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    #自定义数据输出
    runtime.stream_writer("合并召回信息")


    try:
        recall_columns = state["recall_columns"]
        recall_metrics = state["recall_metrics"]
        recall_values = state["recall_values"]
        meta_mysql_repo = runtime.context["meta_mysql_repo"]

        #1.收集一个完整的字段信息列表 去重合并dict[Column_id,ColumnInfoQdrant]
        #1.1收集召回的字段信息列表
        column_infos_dict:dict[str,ColumnInfoQdrant] = {recall_column["id"]:recall_column for recall_column in recall_columns}
        #1.2收集召回的指标信息列表关联的字段信息列表
        for recall_metric in recall_metrics:
            for column_id in recall_metric["relevant_columns"]:
                #查询当前字段id对应的字段信息
                column_info_mysql:ColumnInfoMySQL = await meta_mysql_repo.get_column_info_bv_id(column_id)
                column_infos_dict[column_id] = _convert_column_info_mysql_to_qdrant(column_info_mysql)

        #1.3收集召回的字段值信息列表对应的字段信息列表=》将字段值保存到字段的值样例中
        for recall_value in recall_values:
            column_id = recall_value["column_id"]
            #查询当前字段id对应的字段信息
            column_info_mysql:ColumnInfoMySQL = await meta_mysql_repo.get_column_info_bv_id(column_id)
            column_infos_dict[column_id] = _convert_column_info_mysql_to_qdrant(column_info_mysql)
            #将字段值保存到字段的值样例列表中
            value = recall_value["value"]
            examples = column_infos_dict[column_id]["examples"]
            if value not in examples:
                examples.append(value)

        #2.根据收集所有字段信息列表生成：带字段信息列表的表信息列表
        #2.1对收集的字段信息列表进行按表id分组：dict[table_id,list[ColumnInfoQdrant]]
        table_column_infos_dict:dict[str,list[ColumnInfoQdrant]] ={}
        for column_info in column_infos_dict.values():
            table_id = column_info['table_id']
            if table_id not in table_column_infos_dict:#只有表的第一个字段才需要创建数组
                table_column_infos_dict[table_id] = []
            table_column_infos_dict[table_id].append(column_info)
        #2.2生成带字段信息列表的表信息列表-》table_info:list[TableInfoState]
        table_infos:list[TableInfoState]=[]
        for table_id,column_infos in table_column_infos_dict.items():
            #查询当前表的主键和外键信息列表
            key_column_infos: list[ColumnInfoMySQL] = await meta_mysql_repo.get_key_column_infos(table_id)
            for key_column_info in key_column_infos:
                #只有当前字段在三路召回中都没有才添加
                if key_column_info.id not in column_infos_dict:
                    column_infos.append(_convert_column_info_mysql_to_qdrant(key_column_info))
            #根据表id查询meta得到表信息
            table_info_mysql: TableInfoMySQL = await meta_mysql_repo.get_table_info_by_id(table_id)
            #     根据当前字段信息列表·生成ColumnlnfoState类型的字段状态信息列表
            columns: list[ColumnInfoState] = [
                _convert_column_info_qdrant_to_state(item)
                for item in column_infos
            ]
            # 创建带字段信息列表的表信息对象并添加到总列表中
            table_infos.append(TableInfoState(
                name=table_info_mysql.name,
                role=table_info_mysql.name,
                description=table_info_mysql.description,
                columns=columns
            ))
        #整理指标信息
        metric_infos = [_convert_metric_info_qdrant_to_state(recall_metric)
                        for recall_metric in recall_metrics]
        logger.info(f"合并召回完成：{table_infos}")
        logger.info(f"合并召回完成：{metric_infos}")

        return {}
    except Exception as e:
        logger.error("合并召回信息失败")
        raise


# 将qdrant格式的指标信息列表转换为state格式
def _convert_metric_info_qdrant_to_state(recall_metric:MetricInfoQdrant):
    return MetricInfoState(
        name=recall_metric['name'],
        description=recall_metric["description"],
        relevant_columns=recall_metric["relevant_columns"],
        alias=recall_metric["alias"]
    )

# 将qcrant格式的字段信息转换为state格式
def _convert_column_info_qdrant_to_state(column:ColumnInfoQdrant)->ColumnInfoState:
    return ColumnInfoState(
        name=column['name'],
        type=column['type'],
        role=column["role"],
        examples=column["examples"],
        description=column["description"],
        alias=column["alias"]
    )

# 将mysql格式的字段信息转换为qdrant格式
def _convert_column_info_mysql_to_qdrant(column_info_mysql:ColumnInfoMySQL)->ColumnInfoQdrant:
    return ColumnInfoQdrant(
        id = column_info_mysql.id,
        name=column_info_mysql.name,
        description=column_info_mysql.description,
        role = column_info_mysql.role,
        type = column_info_mysql.type,
        examples = column_info_mysql.examples,
        table_id=column_info_mysql.table_id,
        alias=column_info_mysql.alias
    )