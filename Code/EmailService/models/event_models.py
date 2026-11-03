from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator


class CreditCard(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    card_number: Optional[str] = Field(default=None, alias="cardNumber")
    expiration_month: Optional[int] = Field(default=None, alias="expirationMonth")
    expiration_year: Optional[int] = Field(default=None, alias="expirationYear")
    cvc: Optional[int] = Field(default=None)


class OrderCreatedEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    order_id: int = Field(default=0, alias="orderId")
    product_id: int = Field(default=0, alias="productId")
    merchant_id: int = Field(default=0, alias="merchantId")
    buyer_id: int = Field(default=0, alias="buyerId")
    product_name: str = Field(default="", alias="productName")
    buyer_email: str = Field(default="", alias="buyerEmail")
    merchant_email: str = Field(default="", alias="merchantEmail")
    total_price: float = Field(default=0.0, alias="totalPrice")
    discount: float = Field(default=0.0)
    creddit_card: Optional[CreditCard] = Field(default=None, alias="creditCard")

    @model_validator(mode="before")
    @classmethod
    def normalize_data(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        flattened = dict(data)

        # Handle nested 'order' dictionary if present (e.g. from OrderService event publisher)
        if "order" in flattened and isinstance(flattened["order"], dict):
            order_data = flattened.pop("order")
            for key, val in order_data.items():
                if key not in flattened or flattened[key] is None or flattened[key] == "":
                    flattened[key] = val
        # TODO Identify what this does
        # Handle field alias alternatives and typos
        if "orderId" in flattened and "order_id" not in flattened:
            flattened["order_id"] = flattened["orderId"]
        elif "order_id" in flattened and "orderId" not in flattened:
            flattened["orderId"] = flattened["order_id"]

        if "productId" in flattened and "product_id" not in flattened:
            flattened["product_id"] = flattened["productId"]
        if "merchantId" in flattened and "merchant_id" not in flattened:
            flattened["merchant_id"] = flattened["merchantId"]
        if "buyerId" in flattened and "buyer_id" not in flattened:
            flattened["buyer_id"] = flattened["buyerId"]

        if "productName" in flattened and "product_name" not in flattened:
            flattened["product_name"] = flattened["productName"]
        if "buyerEmail" in flattened and "buyer_email" not in flattened:
            flattened["buyer_email"] = flattened["buyerEmail"]
        if "merchantEmail" in flattened and "merchant_email" not in flattened:
            flattened["merchant_email"] = flattened["merchantEmail"]

        if "totalPrice" in flattened and "total_price" not in flattened:
            flattened["total_price"] = flattened["totalPrice"]

        # Support credit_card alias for creddit_card
        if "credit_card" in flattened and "creddit_card" not in flattened:
            flattened["creddit_card"] = flattened["credit_card"]
        elif "creditCard" in flattened and "creddit_card" not in flattened:
            flattened["creddit_card"] = flattened["creditCard"]

        return flattened


class PaymentEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    order_id: int = Field(default=0, alias="orderId")
    status: Optional[str] = None
    buyer_email: Optional[str] = Field(default=None, alias="buyerEmail")
    merchant_email: Optional[str] = Field(default=None, alias="merchantEmail")
    message: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_payment(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        flattened = dict(data)
        if "orderId" in flattened and "order_id" not in flattened:
            flattened["order_id"] = flattened["orderId"]
        if "buyerEmail" in flattened and "buyer_email" not in flattened:
            flattened["buyer_email"] = flattened["buyerEmail"]
        if "merchantEmail" in flattened and "merchant_email" not in flattened:
            flattened["merchant_email"] = flattened["merchantEmail"]
        return flattened
