from django.shortcuts import render
from http import HTTPStatus


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию;
    # выводить её в шаблон пользовательской страницы 404 мы не станем
    return render(
        request, 'core/404.html',
        {'path': request.path}, status=HTTPStatus.NOT_FOUND
    )


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


def page_server_error(request):
    return render(
        request,
        'core/500server_error.html',
        {'path': request.path},
        status=HTTPStatus.INTERNAL_SERVER_ERROR
    )


def page_forbidden(request):
    return render(
        request,
        'core/403csrf.html',
        {'path': request.path},
        status=403
    )
