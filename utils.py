from datetime import datetime as dt

def string_date(date_str: str) -> dt.date:
    """
    Converting Date from string to date object
    :date_str: String containing date
    :return:
    """
    date_object = dt.strptime(date_str, '%m/%d/%Y').date()
    return date_object
