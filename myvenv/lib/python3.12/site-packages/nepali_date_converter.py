import nepali_datetime
import datetime

english_today = datetime.datetime.now()
english_start_dt = datetime.datetime(english_today.year, english_today.month, english_today.day)

nepali_today = nepali_datetime.datetime.now()
nepali_start_dt = nepali_datetime.datetime(nepali_today.year, nepali_today.month, nepali_today.day)

def english_to_nepali_converter(year, month, day):
    english_end_dt = datetime.datetime(year, month, day)
    english_time_difference = english_end_dt - english_start_dt
    total_seconds = english_time_difference.total_seconds()
    total_days = total_seconds / (24 * 60 * 60)
    result = nepali_start_dt + datetime.timedelta(days = total_days)
    return result.strftime("%Y-%m-%d")


def nepali_to_english_converter(year, month, day):
    nepali_end_dt = nepali_datetime.datetime(year, month, day)
    nepali_time_difference = nepali_end_dt - nepali_start_dt
    total_seconds = nepali_time_difference.total_seconds()
    total_days = total_seconds / (24 * 60 * 60)
    result = english_start_dt + datetime.timedelta(days = total_days)
    return result.strftime("%Y-%m-%d")


if __name__ == "__main__":
    english_to_nepali_converter(2020,2,12)
    nepali_to_english_converter(2075,9,25)






