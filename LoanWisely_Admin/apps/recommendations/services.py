from . import client


def fetch_recommendation_detail(request, recommendation_id):
    return client.get_recommendation_detail(request, recommendation_id)


def fetch_event_logs(request, product_id):
    return client.get_event_logs(request, product_id)


def fetch_reject_logs(request, request_id):
    return client.get_reject_logs(request, request_id)


def fetch_exclusion_reasons(request, result_id):
    return client.get_exclusion_reasons(request, result_id)
