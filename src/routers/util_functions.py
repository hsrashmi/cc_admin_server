import uuid
import bcrypt
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import operator
from sqlalchemy.sql.expression import desc, asc

# Generate a random UUID
def generate_uuid() -> str:
    return uuid.uuid4()


def string_hash(string_to_hash: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(string_to_hash.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def get_filter_conditions(filters: dict, table_fields: list) -> list:
    filter_conditions = []
    if filters:
        ops = {
            ">": operator.gt, 
            "<": operator.lt, 
            ">=": operator.ge, 
            "<=": operator.le, 
            "==": operator.eq, 
            "!=": operator.ne,
            "like": lambda col, val: col.like("%"+val+"%"),
            "ilike": lambda col, val: col.ilike("%"+val+"%"),
            "in": lambda col, val: col.in_(val if isinstance(val, list) else val.split(",")),
            "not in": lambda col, val: ~col.in_(val if isinstance(val, list) else val.split(",")),
            "isnull": lambda col, _: col.is_(None),
            "notnull": lambda col, _: col.is_not(None),
        }
        
        for field, conditions in filters.items():
            if field in table_fields:
                column = table_fields[field]  # Get the SQLAlchemy column
                for op, value in conditions.items():
                    if op in ops:
                        filter_conditions.append(ops[op](column, value))
    
    return filter_conditions

def get_order_by_conditions(order_by: list, table_fields: list) -> tuple:
    ordering = []
    if not order_by:
        return ordering

    for field in order_by:
        is_desc = field.startswith("-")  # Check for descending order
        field_name = field.lstrip("-")  # Remove '-' if present
        if field_name in table_fields:
            column = table_fields[field_name]
            ordering.append(desc(column) if is_desc else asc(column))
    return ordering

def get_limit_offset(limit: int, offset: int) -> tuple[int]:
    limit = min(int(limit), 100) if limit is not None else 25
    offset = max(int(offset), 0) if offset is not None else 0
    return limit, offset

def get_select_fields(fields: list, table_fields: list) -> list:
    selected_fields = []
    print("------------------------")
    print(table_fields)
    if not fields:
        selected_fields = list(table_fields)
    else:
        selected_fields = [field for field in fields if field in table_fields]

    print("------------------------")
    print(table_fields)

    return selected_fields

def get_pagination_params(page_size: int, page_number: int) -> tuple[int]:
    page_size = min(max(int(page_size), 1), 100)
    page_number = max(int(page_number), 1)

class success_message_response(BaseModel):
    type: Optional[str] = "success"
    message: str

class error_message_response(BaseModel):  
    type: str = "error"  
    message: str
    status_code: int


class UserQueryRequest(BaseModel):
    fields: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    page_no: Optional[int] = Field(1, ge=1)  # Optional with default value
    page_size: Optional[int] = Field(100, ge=1, le=100)  # Optional with default value
    order_by: Optional[List[str]] = None


class LoginQueryRequest(BaseModel):
    email: str = None
    password: str = None