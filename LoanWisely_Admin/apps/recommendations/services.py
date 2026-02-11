from . import client


def fetch_recommendation_detail(request, recommendation_id):
    return client.get_recommendation_detail(request, recommendation_id)
