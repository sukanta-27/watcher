from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from server.db.session import get_db
from server.models.pydantic_models import (
    UploadRequest,
    TaskResponse,
    TaskStatusResponse,
)
from server.models.server_models import APIRequest
from server.constants.status import TaskStatus
from server.services.upload_service import process_csv_from_url

router = APIRouter()


async def process_csv_background(
        task_id: str,
        file_url: str,
        db: Session
):
    task = db.query(APIRequest).filter(APIRequest.id == task_id).first()
    if not task:
        return

    task.status = TaskStatus.PROCESSING
    db.commit()

    try:
        # Your existing process_csv_from_url logic here
        rows_processed_successfully, rows_could_not_be_processed, errors = await process_csv_from_url(file_url, db)

        result = {
            "rows_processed_successfully": rows_processed_successfully,
            "rows_could_not_be_processed": rows_could_not_be_processed,
            "errors": errors
        }

        if rows_processed_successfully == 0:
            task_status = TaskStatus.FAILED
            message = "CSV file could not be processed"
        elif rows_could_not_be_processed > 0:
            task_status = TaskStatus.PARTIALLY_COMPLETED
            message = "Not all rows could be processed successfully"
        else:
            task_status = TaskStatus.COMPLETED
            message = "CSV file processed successfully"

        task.status = task_status
        task.result = {
            "message": message,
            **result
        }
        task.completed_at = datetime.now()
        db.commit()

    except Exception as e:
        task.status = TaskStatus.FAILED
        task.error = str(e)
        task.completed_at = datetime.now()
        db.commit()


@router.post(
    "/upload_data_async",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload CSV Data (Async)",
    description="Upload and process CSV data from a publicly accessible URL"
)
async def upload_data_async(
        request: UploadRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    task_id = str(uuid.uuid4())

    # Create task record
    task = APIRequest(
        id=task_id,
        status=TaskStatus.PENDING
    )
    db.add(task)
    db.commit()

    # Add to background tasks
    background_tasks.add_task(
        process_csv_background,
        task_id=task_id,
        file_url=str(request.file_url),
        db=db
    )

    return TaskResponse(
        task_id=task_id,
        message="Added Request to Queue with ID: " + task_id
    )


@router.get(
    "/upload_data_async/status/",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Async Upload Status",
    description="Get the status of an async upload task"
)
async def get_task_status(
        task_id: str = Query(...),
        db: Session = Depends(get_db)
):
    task = db.query(APIRequest).filter(APIRequest.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskStatusResponse(
        task_id=task.id,
        status=task.status,
        message=task.result.get("message") if task.result else None,
        result=task.result,
        created_at=task.created_at,
        completed_at=task.completed_at
    )
