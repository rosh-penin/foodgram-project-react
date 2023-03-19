from rest_framework.pagination import PageNumberPagination

PAGE_LIMIT = 6


class PageLimitPagination(PageNumberPagination):
    page_size = PAGE_LIMIT
    page_size_query_param = 'limit'
