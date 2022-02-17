from django.core.paginator import Paginator
from yatube.settings import POSTS_PER_PAGE


def get_paginator_page(request, query_set):
    paginator = Paginator(query_set, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
