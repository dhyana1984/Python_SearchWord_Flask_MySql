from datetime import datetime


def convert2ampm(time24 : str) -> str:
    return datetime.strptime(time24,'%H:%M').strftime('%I:%M%p')