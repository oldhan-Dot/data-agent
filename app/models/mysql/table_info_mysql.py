from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mysql.base import Base

class TableInfoMySQL(Base):
    __tablename__ = "table_info"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        comment="表编号"
    )
    name: Mapped[str] = mapped_column(
        String(128),
        comment="表名称"
    )
    role: Mapped[str] = mapped_column(
        String(32),
        comment="表类型(fact/dim)"
    )
    description: Mapped[str] = mapped_column(
        Text,  # 可变长度
        comment="表描述"
    )

    