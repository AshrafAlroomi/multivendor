from rest_framework.exceptions import ValidationError
import datetime


def is_valid_date(date):
    try:
        valid_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        date_string = valid_date.strftime("%Y-%m-%d")
        return [valid_date, date_string, 'day']
    except ValueError:
        try:
            valid_date = datetime.datetime.strptime(date, "%Y-%m")
            date_string = valid_date.strftime("%Y-%m")
            return [valid_date, date_string, 'month']
        except ValueError:
            raise ValidationError(
                {'403': "Date is not valid."}
            )
    except TypeError:
        valid_date = datetime.datetime.now()
        date_string = valid_date.strftime("%Y-%m")
        return [valid_date, date_string, 'month']
