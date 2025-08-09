from notion_client import Client
from dotenv import load_dotenv
from typing import Dict, Any, List
from app.models import ReceiptCategory
from datetime import datetime
import os 
import logging
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("NotionReceiptManager initialized")

class NotionReceiptManager:
    def __init__(self):
        self.client = Client(auth=os.environ["NOTION_TOKEN"])
        self.parent_page_id = os.getenv("PAGE_ID")
        self.transaction_db_id = os.getenv("NOTION_TRANSACTIONS_DATABASE_ID")

    def create_transaction_db(self, parent_page_id: str, database_name: str = "Transactions Database") -> Dict[str, Any]:
        """
        Create a Notion database for storing receipt data.
        
        Args:
            parent_page_id: The ID of the parent page where the database will be created
            database_name: The name of the database
        
        Returns:
            The created database object
        """
        properties = {
            "Total": {
                "number": {
                    "format": "number_with_commas"
                }
            },
            "Store Name": {
                "title": {}
            },
            "Store First Line": {
                "rich_text": {}
            },
            "Store Second Line": {
                "rich_text": {}
            },
            "Store Postcode": {
                "rich_text": {}
            },
            "Category": {
                "select": {
                    "options": [
                        {"name": category.value, "color": "default"} 
                        for category in ReceiptCategory
                    ]
                }
            },
            "Date": {
                "date": {}
            },
            "Discount": {
                "number": {
                    "format": "number_with_commas"
                }
            },
            "Created Time": {
                "created_time": {}
            }
        }
        
        database = self.client.databases.create(
            parent={"page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": database_name}}],
            properties=properties,
            is_inline=True
        )
        
        return database

    def create_page(self, database_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new page in the database with the given properties.
        """
        page_properties = {
            "Store Name": {
                "title": [{"text": {"content": properties.get("store_name", "Unknown")}}]
            },
            "Store First Line": {
                "rich_text": [{"text": {"content": properties.get("store_first_line", "Unknown")}}]
            },
            "Store Second Line": {
                "rich_text": [{"text": {"content": properties.get("store_second_line", "Unknown")}}]
            },
            "Store Postcode": {
                "rich_text": [{"text": {"content": properties.get("store_postcode", "Unknown")}}]
            },
            "Total": {
                "number": properties["total"]
            },
            "Category": {
                "select": {"name": properties["reciept_category"]}
            },
            "Date": {
                "date": {"start": properties["date"].strftime("%Y-%m-%d")}
            }
        }

        discount_value = properties.get("discount", None)
        if isinstance(discount_value, (int, float)):
            page_properties["Discount"] = {"number": float(discount_value)}

        page = self.client.pages.create(
            parent={"database_id": database_id},
            properties=page_properties
        )
        return page

    def create_item_db(self, parent_page_id: str, db_name: str = "Items Database") -> Dict[str, Any]:
        """
        Create a new database for items.
        
        Args:
            parent_page_id: The ID of the parent page where the database will be created
            db_name: The name of the database
            
        Returns:
            The created database object
        """
        properties = {
            "Item": {
                "title": {}  # Required property
            },
            "Price": {
                "number": {
                    "format": "pound"
                }
            },
            "Quantity": {
                "number": {
                    "format": "number"
                }
            }
        }
        
        title = [{"type": "text", "text": {"content": db_name}}]
        icon = {"type": "emoji", "emoji": "🧾"}
        parent = {"type": "page_id", "page_id": parent_page_id}
        
        return self.client.databases.create(
            parent=parent,
            title=title, 
            properties=properties,
            icon=icon,
            is_inline=True
        )

    def create_items_within_page(self, database_id: str, properties: Dict[str, Any]) -> bool:
        """
        Create items within a page.
        Items, Price, Quantity 
        """
        items = properties["items"]
        items_price = properties["items_price"]
        items_quantity = properties["items_quantity"]
        
        for item, price, quantity in zip(items, items_price, items_quantity):
            self.client.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Item": {"title": [{"text": {"content": item}}]},
                    "Price": {"number": price},
                    "Quantity": {"number": quantity}
                }
            )
        return True

    def search_db(self, database_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Search the database for pages that match the query.
        """
        results = self.client.databases.retrieve(
            database_id=database_id,
            filter={"property": "Name", "text": {"equals": query}}
        )
        return results

    def create_new_entry(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new entry in the database.
        """
        logger.info(f"Creating new entry with properties: {properties['store_name']}")
        page = self.create_page(self.transaction_db_id, properties)
        logger.info(f"Page created ")
        item_db = self.create_item_db(page['id'], "Items Database")
        logger.info(f"Item database created: with {len(properties['items'])} items")
        self.create_items_within_page(item_db['id'], properties) 
        logger.info("Items created within page")
        return page

if __name__ == "__main__":
    # Example usage
    mock_data = {
        "store_name": "Test Store 123",
        "store_first_line": "123 Main St",
        "store_second_line": "Anytown",
        "store_postcode": "12345",
        "total": 200.00,
        "reciept_category": ReceiptCategory.GROCERY.value,
        "date": datetime.now(),
        "discount": 20.00,
        "items": ["Item 1", "Item 2", "Item 3"],
        "items_price": [10.00, 20.00, 30.00],
        "items_quantity": [1, 2, 3]
    }

    
    notion_manager = NotionReceiptManager()
    database = notion_manager.create_transaction_db(notion_manager.parent_page_id, "Transactions Database")
    database_id = database['id']
    page = notion_manager.create_page(database_id, mock_data)
    item_db = notion_manager.create_item_db(page['id'], "Items Database")
    notion_manager.create_items_within_page(item_db['id'], mock_data)

