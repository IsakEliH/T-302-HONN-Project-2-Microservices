from models import CreditCard

def __validateCardNumber(cardNumber: str):
    total = 0
    length = len(cardNumber)

    for i in range(length):
        digit = int(cardNumber[i])
        offset_from_end = length - 1 - i

        if offset_from_end % 2 == 1:
            total += digit
        elif digit < 5:
            total += 2 * digit
        else:
            total += 2 * digit - 9

    return total % 10 == 0


def __ValidateExpirationMonth(expirationMonth):
    return 1 <= expirationMonth <= 12


def __validateExpirationYear(expirationYear):
    return len(str(expirationYear)) == 4


def __validateCvc(cvc):
    return len(str(cvc)) == 3


def validateCard(cardInfo: CreditCard):
    """
    Takes in a Card object
    Retrieves it's information and validates each indevidually
    Returns True if all are valid, else returns False
    """
    cardNumber = cardInfo.get("cardNumber")
    expirationMonth = cardInfo.get("expirationMonth")
    expirationYear = cardInfo.get("expirationYear")
    cvc = cardInfo.get("cvc")

    return (
        __validateCardNumber(cardNumber)
        and __ValidateExpirationMonth(expirationMonth)
        and __validateExpirationYear(expirationYear)
        and __validateCvc(cvc)
    )