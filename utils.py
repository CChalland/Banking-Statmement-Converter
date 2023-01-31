def reduce(function, iterable, initializer=None):
    """
    Python program to  illustrate sum of two numbers.
    """
    it = iter(iterable)
    if initializer is None:
        value = next(it)
    else:
        value = initializer
    for element in it:
        value = function(value, element)
    return value


def check_float_format(text: str) -> bool:
    """
    Check that the text is a positive floating number
    :param text: Text entered by the user in a tk.Entry widget
    :return:
    """
    if text == "":
        return True

    if all(x in "0123456789." for x in text) and text.count(".") <= 1:
        try:
            float(text)
            return True
        except ValueError:
            return False
    else:
        return False
