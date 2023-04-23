import enum

from ..schemas import BaseModel


class HealthStatus(enum.StrEnum):
    success = "i am alive"
    failure = "i am dead"


class HealthStatusSchema(BaseModel):
    status: HealthStatus
