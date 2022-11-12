from django.core.paginator import Paginator


def pagination(request, post_list):
    paginator = Paginator(post_list, 10)
    return paginator.get_page(request.GET.get('page'))
