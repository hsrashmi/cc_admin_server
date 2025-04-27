from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import or_, cast, String
from sqlalchemy.orm import Session
import pandas as pd
from .converter import ilpuser_converter
from ..dependencies import get_db_session
from ..domain.ilpuser import service, schemas, models
from ..domain.role import service as roleService, schemas as roleSchemas, models as roleModels
from ..domain.role_assignment import service as userRoleService, schemas as userRoleSchemas, models as userRoleModels
from ..domain.school import service as schoolService
from .util_functions import UserQueryRequest, LoginQueryRequest, generate_uuid, string_hash, success_message_response, get_order_by_conditions, get_filter_conditions, get_select_fields
from resources.strings import USER_DOES_NOT_EXIST_ERROR, EMAIL_ALREADY_EXISTS_ERROR, AUTHENTICATION_FAILED_ERROR, PROFILE_PIC_DOESNT_EXIST
import math

router = APIRouter(tags=["ilpuser"])
COMMON_PASSWORD = "common_password!123"

@router.post("/login/", response_model=schemas.ILPUserResponse)
async def login_user(request: LoginQueryRequest,db: Session = Depends(get_db_session)):
    db_user = await service.get_user_by_email(db, email=request.email)
    if not db_user:
        raise HTTPException(status_code=401, detail=AUTHENTICATION_FAILED_ERROR)
    return await service.login_user(db=db, email=request.email, password=request.password)


@router.post("/ilpuser/", response_model=schemas.ILPUserResponse)
async def create_user(user: schemas.ILPUserCreate, db: Session = Depends(get_db_session)):
    try:
        db_user = await service.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail=EMAIL_ALREADY_EXISTS_ERROR)
        unique_id = str(generate_uuid())
        hashed_password = string_hash(user.password)    
        updated_user = user.model_copy(update={"id": unique_id, "password": hashed_password})   
        print("updated_user ------------- ", updated_user)
        return await service.create_user(db=db, user=updated_user)
    except Exception as e:
        print("Error creating db entry for user -", str(e))
        return {}

@router.get("/ilpuser/", response_model=List[schemas.ILPUserResponse])
async def read_users(page_no: int = 1, page_size: int = 100, db: Session = Depends(get_db_session)):
    limit = page_size
    skip = (page_no - 1) * page_size  # Offset calculation    
    users = await service.get_users(db, skip=skip, limit=limit)  # ✅ Await the async function
    return users

@router.get("/ilpuser/{user_id}", response_model=schemas.ILPUserResponse)
async def read_user(user_id: str, db: Session = Depends(get_db_session)):
    db_user = await service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=USER_DOES_NOT_EXIST_ERROR)
    return db_user

@router.post("/allIlpusersWithRoles", response_model=list)
async def read_user(request: UserQueryRequest, db: Session = Depends(get_db_session)):
     # Get all valid columns from the User model
    table_fields = models.ILPUser.get_valid_fields()  
    
    selected_fields = get_select_fields(request.fields, table_fields)
    
    # filter_cond = get_filter_conditions(request.filters, table_fields)
    filter_cond = get_user_details_filter_conditions(request.filters)

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_user = await service.get_users_with_roles_by_params(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)
    return db_user

@router.post("/allIlpusersWithRolesCount")
async def read_user(request: UserQueryRequest, db: Session = Depends(get_db_session)):
     # Get all valid columns from the User model
    filters = get_user_details_filter_conditions(request.filters)  # helper to convert filter JSON to SQLAlchemy filters
    count = await service.get_users_with_roles_by_params_count(db, filters)
    return {"count": count}

@router.get("/ilpuser/{user_id}/profile-pic")
async def get_profile_pic(user_id: int, db: Session = Depends(get_db_session)):
    db_user = await service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=USER_DOES_NOT_EXIST_ERROR)
    if db_user.profile_pic is None:
        raise HTTPException(status_code=404, detail=PROFILE_PIC_DOESNT_EXIST)

    return FileResponse(db_user.profile_pic_url)

@router.post("/getIlpusersByParams/", response_model=list, response_model_exclude_none=True)
async def read_users(
        request: UserQueryRequest, 
        db: Session = Depends(get_db_session)):

    # Get all valid columns from the User model
    table_fields = models.ILPUser.get_valid_fields()    
  
    selected_fields = get_select_fields(request.fields, table_fields)

    filter_cond = get_filter_conditions(request.filters, table_fields)

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_users = await service.get_users_by_params(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)
    return [dict(zip(selected_fields, user)) for user in db_users]

@router.put("/ilpuser/{user_id}", response_model=success_message_response)
async def update_user(user_id: str, user: schemas.ILPUserUpdate, db: Session = Depends(get_db_session)):
    db_user = await service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=USER_DOES_NOT_EXIST_ERROR)
    return await service.update_user(db=db, user_id=user_id, user=user)

@router.delete("/ilpuser/{user_id}", response_model=success_message_response)
async def delete_user(user_id: str, db: Session = Depends(get_db_session)):
    db_user = await service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=USER_DOES_NOT_EXIST_ERROR)
    return await service.delete_user(db=db, user_id=user_id)

@router.get("/getTypesValues/{types}", response_model=dict)
async def get_types_values(types: str, db: Session = Depends(get_db_session)):  
    types_list = types.split(',')
    response = {}
    for type in types_list:
        values = await service.get_enum_values(db, enum_type_name=type) 
        response.update({
            type: values
        })
    return response
    
def get_user_details_filter_conditions(filters: dict):
    conditions = []
    for key, value in filters.items():
                # Combine first_name and last_name if filtering by 'name'
        if key == "name":
            conditions.append(
                or_(
                    models.ILPUser.first_name.ilike(f"%{value}%"),
                    models.ILPUser.last_name.ilike(f"%{value}%")
                )
            )
            
        elif key == "role_name":
            conditions.append(cast(roleModels.Role.name, String).ilike(f"%{value}%"))
        elif hasattr(models.ILPUser, key):
            conditions.append(getattr(models.ILPUser, key).ilike(f"%{value}%"))

    return conditions

@router.post("/bulkUploadUserData")
async def read_user(file: UploadFile = File(...), db: Session = Depends(get_db_session)):
    try:        
        # Read the uploaded file into a dataframe
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)

        validateFieldForNaN = lambda x: "" if isinstance(x, float) and math.isnan(x) else str(x).strip()

        validateIntField = lambda x: str(int(float(str(x).strip()))) if x and str(x).strip().lower() not in ["", "null"] else None
        
        print("df.columns ", df.columns)
       
        required_columns = {
            "First Name", "Last Name", "Email", "Username", 
            "Phone1", "Phone2", "Gender", "Address", "City", "State",
            "Country", "Pincode", "School Dise Code", "Role",         }
       
        if not required_columns.issubset(set(df.columns)):
            raise HTTPException(status_code=400, detail="Missing required columns")

        created = 0
        rejected = 0
        errors: List[str] = []

        # Convert the DataFrame to a list of dictionaries and validate them
        for index, row in df.iterrows():            
            first_name= validateFieldForNaN(row["First Name"])
            last_name= validateFieldForNaN(row["Last Name"])
            if first_name == "" or last_name == "":
                rejected += 1
                errors.append(f"Row {index + 2}: First Name or Last Name is missing")
                continue
            email = validateFieldForNaN(row["Email"])
            if email == "":
                rejected += 1
                errors.append(f"Row {index + 2}: Email is missing")
                continue                        
            username = validateFieldForNaN(row["Username"])
            if username == "":
                username = first_name.lower() + last_name.lower() # Default username if not provided
            role = validateFieldForNaN(row["Role"])                        
            if role not in roleModels.RoleEnum.__members__.values():
                rejected += 1
                errors.append(f"Row {index + 2}: Invalid role '{role}'")
                continue
            phone1 = validateFieldForNaN(row["Phone1"]).strip()
            phone2 = validateFieldForNaN(row["Phone2"]).strip()
            if phone1 == "" and phone2 == "":
                rejected += 1
                errors.append(f"Row {index + 2}: Both phone numbers missing")
                continue
            gender = validateFieldForNaN(row["Gender"])
            address = validateFieldForNaN(row["Address"])
            city = validateFieldForNaN(row["City"])
            state = validateFieldForNaN(row["State"])
            country = validateFieldForNaN(row["Country"])
            pincode = validateFieldForNaN(row["Pincode"])
            school_dise_code = validateIntField(row["School Dise Code"])
            if school_dise_code == "":
                rejected += 1
                errors.append(f"Row {index + 2}: School Dise Code is missing")
                continue
            
            db_user = await service.get_user_by_email(db, email=email)
            if db_user:
                print("row", 6)
                rejected += 1
                errors.append(f"Row {index + 2}: User with email '{email}' or username '{username}' already exists")
                continue
            new_user = schemas.ILPUserCreate(
                first_name=first_name,                
                last_name=last_name,                
                profile_pic_file=None,  # No file upload in bulk upload
                email=email,
                password= COMMON_PASSWORD, # Default password
                username=username,
                phone1=phone1,
                phone2=phone2,
                gender=gender,
                address=address,
                city=city,
                state=state,
                country=country,
                pincode=pincode
            )            
            
            unique_id = str(generate_uuid())
            hashed_password = string_hash(COMMON_PASSWORD)    
            updated_user = new_user.model_copy(update={"id": unique_id, "password": hashed_password})   
            response = await service.create_user(db=db, user=updated_user)                        
            created += 1
            user_id = response.id

            db_school = await schoolService.get_school_by_dise_code(db, dise_code=int(school_dise_code))
            if not db_school:
                rejected += 1
                errors.append(f"Row {index + 2}: A school with dise code, '{school_dise_code}' doesnt exist. So, role is not created for user '{first_name + ' ' + last_name}'")
                continue      
            print("db_school ", db_school)                  
            school_id = db_school.id
            db_role = await roleService.get_role_by_name(name=roleModels.RoleEnum(role), db=db)
            if not db_role:
                errors.append(f"Row {index + 2}: A role with name, '{role}' doesnt exist. So, role is not created for user '{first_name + ' ' + last_name}'")
                continue
            print("db_role  ", db_role)
            role_id = db_role.id

            # create user role assignment
            user_role_data = userRoleSchemas.UserRoleBase(user_id=user_id, role_id=role_id, access_type="WRITE", level="SCHOOL", level_id=school_id)
            unique_id = str(generate_uuid())
            updated_user_role = user_role_data.model_copy(update={"id": unique_id})
            response = await userRoleService.create_user_role(db=db, user_role=updated_user_role)
            if response:
                print("User role assignment created successfully")
            else:
                errors.append(f"Row {index + 2}: Failed to create user role assignment for '{first_name + ' ' + last_name}'")            

        return {
            "status": "completed",
            "total_rows": len(df),
            "created": created,
            "rejected": rejected,
            "errors": errors
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")    