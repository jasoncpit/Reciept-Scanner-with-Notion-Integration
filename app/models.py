from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
from datetime import datetime

class ReceiptCategory(Enum):
    HAPPY_HAPPY = "Happy Happy" 
    GROCERY = "Grocery" 
    EATING_OUT = "Eating out"
    MISCELLANEOUS = "Miscellaneous"
    
class Receipt(BaseModel):
    date: datetime = Field(description="The date of the receipt in the format of YYYY-MM-DD")
    total: float = Field(description="The total amount of the receipt")
    items: List[str] = Field(description="The items on the receipt")
    items_price: List[float] = Field(description="The price of each item")
    items_quantity: List[int] = Field(description="The quantity of each item")
    reciept_category: ReceiptCategory = Field(description="The category of the receipt - Happy Happy, Grocery, Eating out, Miscellaneous. Happy Happy is the category for any purchases for leisure, shopping, etc. Grocery is the category for any purchases for groceries. Eating out is the category for any purchases for eating out. Miscellaneous is the category for any purchases that don't fit into the other categories.")
    store_name: str = Field(description="The name of the store")
    store_first_line: Optional[str] = Field(description="The first line of the address of the store")
    store_second_line: Optional[str] = Field(description="The second line of the address of the store")
    store_postcode: Optional[str] = Field(description="The postcode of the store") 
    discount: Optional[float] = Field(description="The discount amount of the receipt")


    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, '%Y-%m-%d') 
        return v
