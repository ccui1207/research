from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit


@csrf_exempt
@require_POST
@ratelimit(key="ip", rate="3/m", method="POST", block=False)
def login_view(request):
    if getattr(request, "limited", False):
        return JsonResponse(
            {"ok": False, "msg": "limited"},
            status=429
        )

    return JsonResponse(
        {"ok": True, "msg": "pass"},
        status=200
    )