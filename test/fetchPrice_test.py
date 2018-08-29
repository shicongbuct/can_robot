from robot_app.models import fetchPrice
from django.utils import timezone
import datetime

if __name__ == "__main__":
    price = fetchPrice('lsk', '/currencies/lisk/')
    #price = fetchPrice('can', '/currencies/can/')
    print(price)
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))