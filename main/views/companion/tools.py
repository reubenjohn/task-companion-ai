from django.http import HttpResponse
from main.models.utils import UserId
from main.utils import tools


def get_items(request) -> str:
    place = request.GET.get("place", "")
    return HttpResponse(tools.get_items_impl(place), content_type="text/plain")


def where_cat_is_hiding(request) -> str:
    return HttpResponse(tools.where_cat_is_hiding_impl(), content_type="text/plain")


def query_tasks(request, user_id: UserId) -> str:
    query = request.GET.get("query", None)
    state = request.GET.get("state", None)
    return HttpResponse(
        tools.query_tasks_impl(user_id, query=query, state=state),
        content_type="text/plain",
    )
