# server/api/upload.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from server.db.session import get_db
from server.services.upload_service import process_csv_from_url
from server.models.pydantic_models import (
    UploadRequest,
    UploadResponse,
    UploadErrorResponse,
    UploadProcessingErrorResponse
)

router = APIRouter()

@router.post(
    "/upload_data",
    response_model=UploadResponse,
    responses={
        200: {"model": UploadResponse, "description": "Successfully processed CSV file"},
        422: {"model": UploadProcessingErrorResponse, "description": "Could not process CSV file"},
        400: {"model": UploadErrorResponse, "description": "Invalid URL or file format"},
        500: {"model": UploadErrorResponse, "description": "Server error during processing"}
    },
    status_code=status.HTTP_200_OK,
    summary="Upload CSV Data",
    description="Upload and process CSV data from a publicly accessible URL"
)
async def upload_data(
    request: UploadRequest,
    db: Session = Depends(get_db)
):
    try:
        rows_processed_successfully, rows_could_not_be_processed, errors = await process_csv_from_url(str(request.file_url), db)
        print(f"Processed {rows_processed_successfully} rows successfully and {rows_could_not_be_processed} rows could not be processed")
        if rows_processed_successfully == 0:
            error_response = UploadProcessingErrorResponse(
                message="CSV file could not be processed",
                rows_processed_successfully=rows_processed_successfully,
                rows_could_not_be_processed=rows_could_not_be_processed,
                errors=errors,
                status="failure"
            )
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=error_response.__dict__
            )

        return UploadResponse(
            message="CSV file processed successfully",
            rows_processed_successfully=rows_processed_successfully,
            rows_could_not_be_processed=rows_could_not_be_processed,
            errors=errors,
            status="success"
        )
    except Exception as e:
        import traceback as tb
        print(tb.format_exc())
        raise HTTPException(status_code=500, detail=str(e))