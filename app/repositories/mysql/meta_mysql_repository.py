



"""
用于操作数据库meta的持久层模块
"""
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL


class MetaMysqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session
    #向table_info中添加多条数据
    def save_table_infos(self,table_infos:list[TableInfoMySQL]):
        self.session.add_all(table_infos)
    #向metric_info中添加多条数据
    def save_metric_infos(self,metric_infos:list[MetricInfoMySQL]):
        self.session.add_all(metric_infos)
    #向column_info中添加多条数据
    def save_column_infos(self,column_infos:list[ColumnInfoMySQL]):
        self.session.add_all(column_infos)
    #向column_metric中添加多条数据
    def save_column_metric_infos(self,column_metric:list[ColumnMetricMySQL]):
        self.session.add_all(column_metric)

    # 查询指定字段id对应的字段信息
    async def get_column_info_bv_id(self, column_id:str)->ColumnInfoMySQL:
        return await self.session.get(ColumnInfoMySQL, column_id)

    # 查询指定表的主键和外键字段信息列表
    async def get_key_column_infos(self, table_id:str)->list[ColumnInfoMySQL]:
        result = await self.session.execute(
            Select(ColumnInfoMySQL)
            .where(ColumnInfoMySQL.table_id == table_id)
            .where(ColumnInfoMySQL.role.in_(["primary_key", "foreign_key"]))
        )
        return result.scalars().all()

        # 根据表id查询meta得到表信息

    async def get_table_info_by_id(self, table_id: str) -> TableInfoMySQL:
        return await self.session.get(TableInfoMySQL, table_id)

