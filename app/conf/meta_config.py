from dataclasses import dataclass
from pathlib import Path
from omegaconf import OmegaConf

# ==================== 字段信息配置模型 ====================
@dataclass
class ColumnConfig:
    name: str
    role: str
    description: str
    alias: list[str]
    sync: bool

# ==================== 表信息配置模型 ====================
@dataclass
class TableConfig:
    name: str
    role: str
    description: str
    columns: list[ColumnConfig]

# ==================== 指标信息配置模型 ====================
@dataclass
class MetricConfig:
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]

# ==================== 元数据的总配置模型 ====================
@dataclass
class MetaConfig:
    tables: list[TableConfig]
    metrics: list[MetricConfig]

# 得到yaml配置文件的绝对路径
_yaml_path = Path(__file__).parents[2] / "conf" / "meta_config.yaml"

# 根据路径加载配置文件数据 =》DictConfig对象
_yaml_data = OmegaConf.load(_yaml_path)

# 将数据转换为MetaConfig类型的对象
meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(MetaConfig, _yaml_data))

if __name__ == "__main__":
    print(meta_config)
    print(meta_config.metrics[0].description)
