import json
import os


class PaymentRepository:
    DB_FILE: str = "data/paymentData.json"
    INDENT: int = 4


    def save_payment(self, orderId: int, status: str):

        format_message: dict = {
            "orderId": orderId,
            "status": status
        }

        self._get_jsonList()
        self.data_list.append(format_message)

        with open(self.DB_FILE, "w", encoding="utf-8") as file:
            json.dump(self.data_list, file, indent=self.INDENT)




    def get_payment(self, orderId) -> dict:

        if os.path.exists(self.DB_FILE) and os.path.getsize(self.DB_FILE) > 0:
            with open(self.DB_FILE, "r", encoding="utf-8") as file:
                data_list: dict = json.load(file)
                for entry_dict in data_list:
                    if entry_dict.get("orderId") == orderId:
                        return entry_dict
        return {}




    def _get_jsonList(self):
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

