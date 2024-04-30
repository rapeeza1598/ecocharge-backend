from pydantic import BaseModel


class DeleteLogs(BaseModel):
    start_date: str
    end_date: str