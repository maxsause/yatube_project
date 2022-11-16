from django.core.paginator import Paginator
from django.conf import settings


def pagination(request, post_list):
    paginator = Paginator(post_list, settings.PAGINATOR_POSTS_PER_PAGE)
    return paginator.get_page(request.GET.get('page'))
