"""
操作管理数据库客户端的管理器模块
"""
import asyncio
from typing import Optional

from sqlalchemy import text, Select
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from app.conf.app_config import DBConfig, app_config
from app.models.mysql.table_info_mysql import TableInfoMySQL


class MysqlClientManager:
    def __init__(self,config:DBConfig):
        self.config = config
        self.client:Optional[AsyncEngine] = None
        self.session_factory:Optional[async_sessionmaker] = None
    #获取连接字符串
    def _get_url(self):
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}/{self.config.database}?charset=utf8mb4"

    #初始化客户端
    def init_client(self):
        self.client = create_async_engine(
            self._get_url(),
            pool_size = 10,#创建连接池中缓存的长久连接数
            max_overflow=5 #最大临时连接数，默认是10
            #首先返回常驻连接，如果用满了，创建临时连接返回，如果用满了，等待指定的时间
            #如果有常驻连接归还返回他，如果有临时连接释放，创建临时连接返回
            #否则超时报错
        )
        #创建会话工厂
        self.session_factory = async_sessionmaker(
            self.client, #客户端对象
            autobegin = True,#自动开启事务 注意：事务需要提交和回滚
            autoflush= False #是否将未提交的更新同步/刷新到暂存区(后面的查询是否可见)
        )
    #释放资源
    async def close(self):
        await self.client.dispose()


#创建操作dw库的客户端管理器
dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)
#创建操作meta库的客户端管理器
meta_mysql_client_manager  = MysqlClientManager(app_config.db_meta)



if __name__ == '__main__':
    #查询dw2库中的dim_customer表中的数据
    #不用orm，自己编写sql执行
    async def test():
        #初始化客户端
        dw_mysql_client_manager.init_client()

        #进行数据库表的查询
        #创建会话
        # async with AsyncSession(
        #     dw_mysql_client_manager.client,
        #     autobegin = True, #自动开启事务 注意：事务需要手动提交或回滚
        #     autoflush = False # 是否将未提交的更新同步/刷新到暂存区（后面的查询是否可见）
        # ) as session:
        assert dw_mysql_client_manager.session_factory
        async with dw_mysql_client_manager.session_factory() as session:
            #执行sql
            sql = "select customer_name from dim_customer limit 2"
            result = await session.execute(text(sql))

            #取出所有的数据
            # 注意：Result 是一次性游标，只能取一次，下面三选一，不要连着调用
            #rows = result.all()#返回[row,row]row对象包含当前行所有字段值数据的可遍历对象
            # rows = result.mappings().all()#返回[RowMapping,RowMapping],RowMapping对象是包含当前行所有字段名和字段值数据的可遍历的对象
            # rows = result.scalars().all()#返回[val,val]val是查询的第一个字段的值

            # rows = result.all()
            # print(rows,type(rows),type(rows[0]))
            # for row in rows:
            #     for val in row:
            #         print(val)
            # print(rows[0].customer_name)

            # rows = result.mappings().all()
            # print(rows,type(rows),type(rows[0]))
            # for row in rows:
            #     for key,val in row.items():
            #         print(key,val)
            #
            rows = result.scalars().all()
            print(rows,type(rows),type(rows[0]))
            for val in rows:
                print(val)

        #关闭客户端
        await dw_mysql_client_manager.close()

    # asyncio.run(test())


    async def test_orm():
        #初始化客户端
        meta_mysql_client_manager.init_client()
        assert meta_mysql_client_manager.session_factory
        async with meta_mysql_client_manager.session_factory() as session:

            #添加一条数据
            table_info1 = TableInfoMySQL(
                id = "dim_customer1",
                name = "dim",
                description="客户信息维度1"
            )
            session.add(table_info1)

            # 添加多条数据
            table_info2 = TableInfoMySQL(
                id="dim_customer2",
                name="dim_customer2",
                role="dim",
                description="客户信息维度表2"
            )
            table_info3 = TableInfoMySQL(
                id="dim_customer3",
                name="dim_customer3",
                role="dim",
                description="客户信息维度表3"
            )
            session.add_all([table_info2,table_info3])

            #提交事务
            await session.commit()
            #查询一条数据
            table_info = await session.get(TableInfoMySQL,"dim_customer1") #select语句
            print(table_info,table_info.description)
            #查询多条
            result = session.execute(
                Select(TableInfoMySQL).limit(2)
            )

            table_infos:list[TableInfoMySQL] = result.scalars().all() #[row,row]
            print(table_infos)

    async def test_orm2():
        meta_mysql_client_manager.init_client()
        #增删改查都是异步，增删改需要提交事务
        assert meta_mysql_client_manager.session_factory
        async with meta_mysql_client_manager.session_factory() as session:
            #更新
            table_info:TableInfoMySQL = session.get(TableInfoMySQL,"dim_customer")
            table_info.description = "aaa"

            #删除
            await session.delete(table_info)

            #提交事务
            await session.commit()
        await meta_mysql_client_manager.close()

    asyncio.run(test_orm2())