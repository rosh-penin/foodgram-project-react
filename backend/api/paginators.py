from rest_framework.pagination import PageNumberPagination

PAGE_LIMIT = 6


class PageLimitPagination(PageNumberPagination):
    """Paginator with custom page_size parameter."""
    page_size = PAGE_LIMIT
    page_size_query_param = 'limit'
