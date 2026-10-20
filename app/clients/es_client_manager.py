


"""
es客户端的配置控制
"""
import asyncio
from typing import Optional

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class EsClientManager:
    def __init__(self,config:ESConfig):
        self.config = config
        self.client:Optional[AsyncElasticsearch] = None

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init_client(self):
        self.client=AsyncElasticsearch(
            self._get_url()
        )


    async def close(self):
        await self.client.close()

es_client_manager = EsClientManager(app_config.es)

if __name__ == '__main__':
    async def test():
        es_client_manager.init_client()
        client = es_client_manager.client
        index_name = "my-books"
        #创建索引
        #如果存在则先删除再创建
        if await client.indices.exists(index=index_name):
            await client.indices.delete(index=index_name)
        await client.indices.create(
                index=index_name,
                mappings={
                    "dynamic": False,
                    "properties": {
                        "name": {
                            "type": "text"
                        },
                        "author": {
                            "type": "text"
                        },
                        "release_date": {
                            "type": "date",
                            "format": "yyyy-MM-dd"
                        },
                        "page_count": {
                            "type": "integer"
                        }
                    }
                },
            )

        #添加数据(批量插入)
        await client.bulk(
            operations=[
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Revelation Space",
                    "author": "Alastair Reynolds",
                    "release_date": "2000-03-15",
                    "page_count": 585
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "1984",
                    "author": "George Orwell",
                    "release_date": "1985-06-01",
                    "page_count": 328
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Fahrenheit 451",
                    "author": "Ray Bradbury",
                    "release_date": "1953-10-15",
                    "page_count": 227
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Brave New World",
                    "author": "Aldous Huxley",
                    "release_date": "1932-06-01",
                    "page_count": 268
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "The Handmaids Tale",
                    "author": "Margaret Atwood",
                    "release_date": "1985-06-01",
                    "page_count": 311
                }
            ],
        )
        #立即刷新保存到数据库中(默认1秒才保存)
        await client.indices.refresh(index = index_name)

        #查询
        result = await client.search(
                    index=index_name,
                    query={#根据name属性分词查询
                        "match": {
                            "name": "brave"
                        }
                    },
                )
        #读取数据
        print(result)
        print(result["hits"]["hits"][0]["_source"])



        await es_client_manager.close()
    asyncio.run(test())
