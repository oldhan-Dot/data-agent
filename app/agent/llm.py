from langchain.chat_models import init_chat_model

from app.conf.app_config import app_config

llm = init_chat_model(
    model=app_config.llm.model_name,
    api_key = app_config.llm.api_key,
    temperature = 0
)

if __name__ == '__main__':
    result = llm.invoke("你是什么模型")
    print(result)

