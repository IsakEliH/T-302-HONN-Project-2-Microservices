from PaymentService.models import CreditCard

def __validateCardNumber(cardNumber: str):
    sum = 0
    length = len(cardNumber)

    for i in range(length):
        digit = int(cardNumber[i])
        offset_from_end = length - i

        if offset_from_end % 2 == 1:
            sum += digit
        elif digit < 5:
            sum += 2 * digit
        else:
            sum += 2 * digit - 9

    return sum % 10 == 0

def __ValidateExpirationMonth(expirationMonth):
    return 1<= expirationMonth <=12

def __validateExpirationYear(expirationYear):
    return len(str(expirationYear)) == 4

def __validateCvc(cvc):
    len(str(cvc)) == 3

def validateCard(cardInfo: CreditCard):
    cardNumber: str = cardInfo.get("cardNumber")
    expirationMonth: int = cardInfo.get("expirationMonth")
    expirationYear: int = cardInfo.get("expirationYear")
    cvc: int = cardInfo.get("cvc")

    return __validateCardNumber(cardNumber) & __ValidateExpirationMonth(expirationMonth) & __validateExpirationYear(expirationYear) & __validateCvc(cvc) 