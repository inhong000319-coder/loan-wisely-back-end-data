from . import client


def fetch_dashboard(request):
    return client.get_dashboard(request)
