import asyncio
from typing import Optional

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    def __init__(self,config:EmbeddingConfig):
        self.config = config
        self.client:Optional[HuggingFaceEndpointEmbeddings] = None

    def init_client(self):
        self.client = HuggingFaceEndpointEmbeddings(
            model = f"http://{self.config.host}:{self.config.port}"
        )

embedding_client_manager = EmbeddingClientManager(app_config.embedding)


if __name__ == '__main__':
    async def test():
        #初始化客户端
        embedding_client_manager.init_client()
         #生成一个向量
        vector:list[float] = await embedding_client_manager.client.aembed_query("hello")
        print(vector)
        print(len(vector)) #1024
        #生成多个向量
        vectors:list[list[float]] = await embedding_client_manager.client.aembed_documents(["hello","guigu"])
        print(vectors)
        print(len(vectors),len(vectors[0])) #2 1024  =>[[float]]

    asyncio.run(test())








