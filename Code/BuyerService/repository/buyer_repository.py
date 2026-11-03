import json
import os

class BuyerRepository:
    DB_FILE: str = "database/buyerData.json"
    INDENT: int = 4

    def save_buyer(self, buyer):
        next_id: int = self._get_next_id()

        format_message: dict = buyer.dict()
        format_message["buyerId"] = next_id

        self.data_list.append(format_message)
        with open(self.DB_FILE, "w", encoding="utf-8") as file:
            json.dump(self.data_list, file, indent=self.INDENT)

        return next_id



    def get_buyer(self, buyerId: int) -> dict:
        if os.path.exists(self.DB_FILE) and os.path.getsize(self.DB_FILE) > 0:
            with open(self.DB_FILE, "r", encoding="utf-8") as file:
                data_list: dict = json.load(file)
                for entry_dict in data_list:
                    if entry_dict.get("buyerId") == buyerId:
                        return entry_dict
        return {}





    def _get_next_id(self) -> int:
        """
        Gets next id for a new order, (id's go from 1 and up)

        :return: return the next orderId
        :rtype: int
        """

        # Load and check to see next id
        if os.path.exists(self.DB_FILE) and os.path.getsize(self.DB_FILE) > 0:
            with open(self.DB_FILE, "r", encoding="utf-8") as file:
                self.data_list = json.load(file)
        else:
            self.data_list = []

        if self.data_list:
            return self.data_list[-1]["buyerId"] + 1
        else:
            return 1