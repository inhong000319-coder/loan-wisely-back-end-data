from django.core.paginator import Paginator


def paginate(request, items, per_page=20, page_param="page"):
    if items is None:
        items = []
    paginator = Paginator(items, per_page)
    page_number = request.GET.get(page_param, 1)
    page_obj = paginator.get_page(page_number)

    query = request.GET.copy()
    if page_param in query:
        query.pop(page_param, None)
    query_params = query.urlencode()

    return {
        "items": page_obj.object_list,
        "page_obj": page_obj,
        "page_param": page_param,
        "query_params": query_params,
    }
