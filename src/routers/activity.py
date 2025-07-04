from typing import List
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..dependencies import get_db_session
from ..domain.activity import service, schemas, models
from ..domain.asset import service as assetService, schemas as assetSchemas, models as assetModels
from .util_functions import UserQueryRequest, LoginQueryRequest, generate_uuid, string_hash, success_message_response, get_order_by_conditions, get_filter_conditions, get_select_fields
from resources.strings import ASSET_DOES_NOT_EXIST_ERROR, ACTIVITY_DOES_NOT_EXIST_ERROR
from starlette.config import Config
from fastapi.responses import StreamingResponse
import mimetypes

config = Config(".env")  # Automatically loads variables from .env file

router = APIRouter(tags=["activities"])

ASSET_FILES_PATH = os.path.join(config("UPLOAD_FOLDER", default="/"), "assets")
os.makedirs(ASSET_FILES_PATH, exist_ok=True)

ALLOWED_TYPES = {
    "image": assetModels.AssetTypeEnum.IMAGE,
    "application": assetModels.AssetTypeEnum.DOCUMENT,  # like PDF, DOCX
    "video": assetModels.AssetTypeEnum.VIDEO,
}

@router.post("/activity/", response_model=schemas.ActivityResponse)
async def create_block(activity: schemas.ActivityBase, db: Session = Depends(get_db_session)):
    # db_block = await service.get_block_by_name(db, name=activity.name)
    # if db_block:
    #     raise HTTPException(status_code=400, detail=BLOCK_ALREADY_EXISTS_ERROR)
    unique_id = str(generate_uuid())    
    updated_activity = activity.model_copy(update={"id": unique_id})   
    return await service.create_activity(db=db, activity=updated_activity)

@router.get("/activity/", response_model=List[schemas.ActivityResponse])
async def read_activities(page_no: int = 1, page_size: int = 100, db: Session = Depends(get_db_session)):
    limit = page_size
    skip = (page_no - 1) * page_size  # Offset calculation        
    activities = await service.get_activities(db, skip=skip, limit=limit)  # ✅ Await the async function
    return activities

@router.get("/activity/{activity_id}", response_model=schemas.ActivityResponse)
async def read_activity(activity_id: str, db: Session = Depends(get_db_session)):
    db_activity = await service.get_activity(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(status_code=404, detail=ACTIVITY_DOES_NOT_EXIST_ERROR)
    return db_activity

@router.get("/activity-academic-years", response_model=List[str])
async def get_academic_years(db: Session = Depends(get_db_session)):
    db_data = await service.get_activities_year(db)
    if db_data is None:
        raise HTTPException(status_code=404, detail=ASSET_DOES_NOT_EXIST_ERROR)
    return db_data

@router.post("/getActivitiesByParams/", response_model=List[schemas.ActivityResponse])
async def read_activities_by_params(
        request: UserQueryRequest, 
        db: Session = Depends(get_db_session)):

    # Get all valid columns from the activity model
    table_fields = models.Activity.get_valid_fields()    
  
    selected_fields = get_select_fields(request.fields, table_fields)

    filter_cond = get_filter_conditions(request.filters, table_fields)

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_activities = await service.get_activities_by_params(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)    
    return db_activities

@router.put("/activity/{activity_id}", response_model=success_message_response)
async def update_activity(activity_id: str, activity: schemas.ActivityUpdate, db: Session = Depends(get_db_session)):
    db_activity = await service.get_activity(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(status_code=404, detail=ACTIVITY_DOES_NOT_EXIST_ERROR)
    return await service.update_activity(db=db, activity_id=activity_id, activity=activity)

@router.delete("/activity/{activity_id}", response_model=success_message_response)
async def delete_activity(activity_id: str, db: Session = Depends(get_db_session)):
    db_activity = await service.get_activity(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(status_code=404, detail=ACTIVITY_DOES_NOT_EXIST_ERROR)
    return await service.delete_activity(db=db, activity_id=activity_id)


@router.post("/asset/", response_model=assetSchemas.AssetResponse)
async def create_block(asset: assetSchemas.AssetBase, db: Session = Depends(get_db_session)):
    # db_block = await service.get_block_by_name(db, name=activity.name)
    # if db_block:
    #     raise HTTPException(status_code=400, detail=BLOCK_ALREADY_EXISTS_ERROR)
    unique_id = str(generate_uuid())    
    updated_asset = asset.model_copy(update={"id": unique_id})   
    return await assetService.create_asset(db=db, asset=updated_asset)

@router.get("/asset/", response_model=List[assetSchemas.AssetResponse])
async def read_activities(page_no: int = 1, page_size: int = 100, db: Session = Depends(get_db_session)):
    limit = page_size
    skip = (page_no - 1) * page_size  # Offset calculation        
    activities = await assetService.get_assets(db, skip=skip, limit=limit)  # ✅ Await the async function
    return activities

@router.get("/asset/{asset_id}", response_model=assetSchemas.AssetResponse)
async def read_asset(asset_id: str, db: Session = Depends(get_db_session)):
    db_asset = await assetService.get_asset(db, asset_id=asset_id)
    if db_asset is None:
        raise HTTPException(status_code=404, detail=ASSET_DOES_NOT_EXIST_ERROR)
    return db_asset

@router.delete("/asset/{asset_id}", response_model=success_message_response)
async def delete_asset(asset_id: str, db: Session = Depends(get_db_session)):
    db_asset = await assetService.get_asset(db, asset_id=asset_id)
    if db_asset is None:
        raise HTTPException(status_code=404, detail=ASSET_DOES_NOT_EXIST_ERROR)
    return await assetService.delete_asset(db=db, asset_id=asset_id)
    # # delete activity asset association
    # return await assetService.delete_asset_activity_association(db=db, asset_id=asset_id)

@router.post("/allActivityAssets", response_model=List[schemas.ActivityWithAssetsResponse])
async def read_asset_with_filters(
    filters: schemas.ActivityFilter,
    page_no: int = 1, page_size: int = 100, db: Session = Depends(get_db_session)
):
    limit = page_size
    skip = (page_no - 1) * page_size  # Offset calculation 
    db_asset = await service.get_activities_with_assets(
        db,
        filters=filters,
        skip=skip, limit=limit
    )
    return db_asset

@router.get("/activityAssets/{activity_id}", response_model=List[assetSchemas.AssetResponse])
async def read_asset(activity_id: str, db: Session = Depends(get_db_session)):
    db_data = await assetService.get_assets_by_activity(db, activity_id=activity_id)
    if db_data is None:
        raise HTTPException(status_code=404, detail=ASSET_DOES_NOT_EXIST_ERROR)
    return db_data

@router.post("/uploadAsset")
async def upload_assets(
    activity_id: str = Form(...),
    files: List[UploadFile] = File(...),
    descriptions: List[str] = Form([]),  # Optional: one description per file
    db: Session = Depends(get_db_session),
):
    if not activity_id:
        raise HTTPException(status_code=400, detail="Activity ID is required")

    uploaded_assets = []
    activityAssetsAssociation = []

    for idx, file in enumerate(files):
        if not file:
            continue

        file_location = os.path.join(ASSET_FILES_PATH, file.filename)
        mime_type = file.content_type
        main_type = mime_type.split("/")[0]

        if main_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {mime_type}")

        asset_type = ALLOWED_TYPES[main_type]

        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)

        asset = assetSchemas.AssetBase(
            id=str(generate_uuid()),
            name=file.filename,
            description=descriptions[idx] if idx < len(descriptions) else "",
            type=asset_type,
            url=file_location,
            size=os.path.getsize(file_location),
            mime_type=mime_type
        )

        created_asset = await assetService.create_asset(db=db, asset=asset)
        uploaded_assets.append(created_asset)

        activityAssetsAssociation.append(
            assetSchemas.ActivityAssetBaseCreate(
                id=str(generate_uuid()),
                activity_id=activity_id,
                asset_id=created_asset.id
            ))

        # Optionally link to the activity
    await assetService.link_assets_to_activity(db=db, activityAssetsAssociation=activityAssetsAssociation)    

    return uploaded_assets

@router.get("/downloadAsset/{asset_id}")
async def download_asset(asset_id: str, db: Session = Depends(get_db_session)):
    # Fetch from DB
    asset = await assetService.get_asset(db=db, asset_id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    file_path = asset.url
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    # Open file as binary stream
    file_stream = open(file_path, mode="rb")

    # Guess mime type if not stored
    media_type = asset.mime_type or mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    # Force download with Content-Disposition
    headers = {
        "Content-Disposition": f'attachment; filename="{asset.name}"'
    }

    return StreamingResponse(file_stream, media_type=media_type, headers=headers)
