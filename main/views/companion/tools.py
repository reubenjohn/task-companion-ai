from django.http import HttpResponse
from companion.db.utils import UserId
from companion import tools


def query_tasks(request, user_id: UserId) -> str:
    query = request.GET.get("query", None)
    state = request.GET.get("state", None)
    return HttpResponse(
        tools.query_tasks_impl(user_id, query, state),
        content_type="text/plain",
    )
