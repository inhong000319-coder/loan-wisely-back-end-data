from . import client


def fetch_recommendation_detail(request, recommendation_id):
    return client.get_recommendation_detail(request, recommendation_id)


def fetch_event_logs(request, product_id):
    return client.get_event_logs(request, product_id)


def fetch_reject_logs(request, request_id):
    return client.get_reject_logs(request, request_id)


def fetch_exclusion_reasons(request, result_id):
    return client.get_exclusion_reasons(request, result_id)


def fetch_recommendation_es_search(request, user_id, policy_version, keyword, date_from, date_to, page, size):
    return client.get_recommendation_es_search(
        request,
        user_id=user_id,
        policy_version=policy_version,
        keyword=keyword,
        date_from=date_from,
        date_to=date_to,
        page=page,
        size=size,
    )


def fetch_recommendation_es_reindex(request):
    return client.post_recommendation_es_reindex(request)
