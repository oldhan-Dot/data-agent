#context_var代理
import asyncio
from _contextvars import ContextVar,Token

#创建一个存取请求id的context_var对象
_req_context_var = ContextVar("req_id",default = "1111")

#保存请求id
def set_request_id(request_id:str)->Token:
    return _req_context_var.set(request_id)
#获取请求id
def get_request_id():
    return _req_context_var.get()
#重置请求id
def reset_request_id(token:Token):
    _req_context_var.reset(token)

if __name__ == '__main__':
    async def req1():
        print(f"1---req1---req_id:{get_request_id()}")
        token = set_request_id("22222")
        print(f"2---req1---req_id:{get_request_id()}")
        await asyncio.sleep(1)
        print(f"3---eq1---req_id:{get_request_id()}")
        reset_request_id(token)
        print(f"4----req1---req_id:{get_request_id()}")


    async def req2():
        print(f"1---req2---req_id:{get_request_id()}")
        token = set_request_id("22222")
        print(f"2---req2---req_id:{get_request_id()}")
        await asyncio.sleep(1)
        print(f"3---req2---req_id:{get_request_id()}")
        reset_request_id(token)
        print(f"4----req2---req_id:{get_request_id()}")
    async def test():
            await asyncio.gather(req1(),req2())


    asyncio.run(test())
