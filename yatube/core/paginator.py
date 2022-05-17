from django.core.paginator import Paginator


class BuildPaginator:
    """Класс позволяет построить пагинатор"""
    @staticmethod
    def get_page_obj(request, posts, count_pages: int) -> Paginator:
        """Вернуть page_obj"""
        paginator = Paginator(posts, count_pages)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return page_obj

    @staticmethod
    def get_paginator_count(posts, count_pages: int) -> Paginator:
        """Вернуть количество постов в пагинаторе"""
        paginator = Paginator(posts, count_pages)
        return paginator.count
