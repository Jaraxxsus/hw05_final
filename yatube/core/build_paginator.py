from django.core.paginator import Page, Paginator


class BuildPaginator:
    """Класс позволяет построить пагинатор"""
    @staticmethod
    def get_page_obj(page_number: int,
                     posts: any, count_pages: int) -> Page:
        """Вернуть page_obj"""
        paginator = Paginator(posts, count_pages)
        page_obj = paginator.get_page(page_number)
        return page_obj

    @staticmethod
    def get_paginator_count(posts: any, count_pages: int) -> int:
        """Вернуть количество постов в пагинаторе"""
        paginator = Paginator(posts, count_pages)
        return paginator.count
