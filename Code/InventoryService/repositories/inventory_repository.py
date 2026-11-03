import json
import os

from models.inventory_model import Inventory, build_inventory


class InventoryRepository:
    DB_FILE: str = "database/data_json.json"
    INDENT: int = 4
    ID: str = "productId"

    def __init__(self) -> None:
        self.latest_id: int = 0

    def save_product(self, product: Inventory) -> int:
        """
        Save message to json and return the productId

        :param message: the request body
        :type message: Inventory
        :return: the productId of the message
        :rtype: int
        """

        next_id: int = self._get_next_id()

        format_message: dict = product.model_dump()
        format_message[self.ID] = next_id

        self.data_list.append(format_message)
        with open(self.DB_FILE, "w", encoding="utf-8") as file:
            json.dump(self.data_list, file, indent=self.INDENT)

        self.latest_id = next_id
        return next_id

    def get_product(self, product_id: int) -> dict:
        """
        Get message with productId and return dictionary of it (from json)

        :param productId: assigned id to products
        :type productId: int
        :return: product in dictionary form from json
        :rtype: dict
        """
        if os.path.exists(self.DB_FILE) and os.path.getsize(self.DB_FILE) > 0:
            with open(self.DB_FILE, "r", encoding="utf-8") as file:
                data_list: dict = json.load(file)
                for entry_dict in data_list:
                    if entry_dict.get(self.ID) == product_id:
                        return entry_dict
        return {}

    def decrease_quantity(self, product_id: int, amount: int = 1) -> bool:
        # Get the product
        product = self.get_product(product_id)
        if not product:
            return False

        # Decrease the quantity
        product["quantity"] -= amount
        if product["quantity"] < 0:
            product["quantity"] = 0

        # Update the database
        updated_product = build_inventory(product)
        self.save_product(updated_product)
        return True

    def _get_next_id(self) -> int:
        """
        Gets next id for a new product, (id's go from 1 and up)

        :return: return the next productId
        :rtype: int
        """

        # Load and check to see next id
        if os.path.exists(self.DB_FILE) and os.path.getsize(self.DB_FILE) > 0:
            with open(self.DB_FILE, "r", encoding="utf-8") as file:
                self.data_list = json.load(file)
        else:
            self.data_list = []

        if self.data_list:
            return self.data_list[-1][self.ID] + 1
        else:
            return 1
