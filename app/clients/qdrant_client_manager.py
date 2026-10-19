import asyncio
import random
import uuid
from typing import Optional

from qdrant_client import AsyncQdrantClient, models

from app.conf.app_config import QdrantConfig, app_config

"""
用来操作Qdrant库的客户端管理器模块
"""
class QdrantClientManager:
    def __init__(self,config:QdrantConfig):
        self.config = config
        self.client:Optional[AsyncQdrantClient] = None


    def init_client(self):
        self.client = AsyncQdrantClient(
            f"http://{self.config.host}:{self.config.port}"
        )

    async def close(self):
        await self.client.close()
qdrant_client_manager = QdrantClientManager(app_config.qdrant)


if __name__ == '__main__':

    async def test():
        #初始化客户端
        qdrant_client_manager.init_client()
        client = qdrant_client_manager.client
        collection_name = "my_collection"

        #创建集合如果不存在则创建==》正式执行
        # if not await client.collection_exists(collection_name=collection_name):
        #     await client.create_collection(
        #         collection_name= collection_name, #集合的名称
        #         #向量配置
        #         vectors_config=models.VectorParams(
        #             size = app_config.qdrant.embedding_size, #向量维度
        #             distance=models.Distance.COSINE #余弦相似度
        #         )
        #     )
        #创建集合如果存在的时候删除集合并创建==》测试执行
        if await client.collection_exists(collection_name=collection_name):
            await client.delete_collection(collection_name=collection_name)
        await client.create_collection(
            collection_name= collection_name,
            vectors_config=models.VectorParams(
                size=app_config.qdrant.embedding_size,
                distance=models.Distance.COSINE
            )

        )

        #批量插入多个向量
        await client.upsert(
            collection_name=collection_name,
            points=[
                    models.PointStruct(
                        #id=uuid.uuid4()
                        id = i,
                        payload={
                            "color":"red" if i %2==0 else "blue"
                        },
                        vector=[random.random() for i in range(1024)]
                    ) for i in range(10)
            ]
        )
        #搜索
        result = await client.query_points(
            collection_name=collection_name,
            query = [random.random() for i in range(1024)],
            limit=5,#限制5条
            score_threshold=0.6,#相似度得分最小的值
            query_filter=models.Filter(
                #根据payload进行过滤
                must=[
                    models.FieldCondition(
                        key="color",match=models.MatchValue(value="blue")
                    )
                ]
            )
        )
        points = result.points
        print(points)
        for point in points:
            print(point.payload)

        await qdrant_client_manager.close()
    asyncio.run(test())