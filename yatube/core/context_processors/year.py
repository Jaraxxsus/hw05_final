from datetime import datetime

date = datetime.now()


def year(request):
    return {
        "year": date.year
    }
