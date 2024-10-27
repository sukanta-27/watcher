from sqlalchemy import Column, String, DateTime, JSON
from server.db.base import Base
from datetime import datetime
from server.constants.status import TaskStatus


class APIRequest(Base):
    __tablename__ = "api_requests"

    id = Column(String, primary_key=True)
    status = Column(String, nullable=False, default=TaskStatus.PENDING)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    error_code = Column(String, nullable=True)


    def __repr__(self):
        return f"<APIRequest id={self.id} status={self.status} created_at={self.created_at} completed_at={self.completed_at} result={self.result} error_code={self.error_code}>"