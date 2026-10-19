from dataclasses import dataclass
from pathlib import Path

import yaml
from omegaconf import OmegaConf


def load_by_yaml():
    #yaml配置路径
    yaml_path = Path(__file__).parents[2]/"conf"/"test_config.yaml"
    #打开文件流
    with open(yaml_path,"r",encoding="utf-8") as file:
        #加载文件获取数据
        yaml_data = yaml.safe_load(file)
        print(yaml_data,type(yaml_data))

        #问题：读取属性时有补全提示，也没有错误的警察提示
        print(yaml_data["name"])


@dataclass
class PersonConfig:
    name:str
    age:int
    height:float

def load_by_omegaconf():
    #yaml配置路径
    yaml_path = Path(__file__).parent[2]/"conf"/"test_config.yaml"
    #加载数据
    yaml_data = OmegaConf.load(yaml_path)
    print(yaml_data,type(yaml_data))
    print(yaml_data["name"])
    #将得到数据封装成指定数据的对象
    person_config:PersonConfig = OmegaConf.to_object(OmegaConf.merge(PersonConfig,yaml_data))
    print(person_config.name)
