
"""
用来操作qdrant库中字段数据的持久层模块
"""
from qdrant_client import AsyncQdrantClient, models

from app.conf.app_config import app_config
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant


class ColumnQdrantRepository:
    collection_name = "data-agent-column_collection2"

    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def _create_collection(self):
        client = self.client
        collection_name = self.collection_name

        # 创建集合  如果存在先删除 =》开发测试
        if await client.collection_exists(collection_name=collection_name):
            await client.delete_collection(collection_name=collection_name)
        await client.create_collection(
            collection_name=collection_name,  # 集合的名称
            # 向量配置
            vectors_config=models.VectorParams(
                size=app_config.qdrant.embedding_size,  # 向量维度
                distance=models.Distance.COSINE  # 余弦相似度
            ),
        )

    # 批量插入多个字段信息的向量列表
    async def insert_column_vectors(self, ids: list[str], payloads: list[ColumnInfoQdrant], vectors: list[list[float]]):
        # 创建集合  如果存在先删除 =》开发测试
        await self._create_collection()

        # 分批处理
        batch_size = 20
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_payloads = payloads[i:i + batch_size]
            batch_vectors = vectors[i:i + batch_size]

            # 批量插入多个向量
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=batch_ids[i],
                        payload=batch_payloads[i],
                        vector=batch_vectors[i],
                    )
                    for i in range(len(batch_ids))
                ],
            )
    #搜索
    async def search(self, keyword_vector):
        result = await self.client.query_points(
            collection_name=self.collection_name,
            query=keyword_vector,
            score_threshold=0.6# 相似度得分的最小值  (需要反复测试来确定这个值)
        )
        #读取payload数据列表返回
        return [ColumnInfoQdrant(**point.payload) for point in result.points]


