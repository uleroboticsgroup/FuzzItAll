"""
Definition of helper functions for the main module.
"""

from werkzeug.datastructures import MultiDict as WSGIMultiDict
import flask as f


def get_pagination_params(url_params: WSGIMultiDict[str, str],
                          sorting_col: str) -> tuple:
    '''
    Extracts URL parameters related to result pagination.

        Parameters:
            url_params (WSGIMultiDict[str, str]):
                URL parameters obtained from a request.
            sorting_col (str):
                Name of the sorting column to extract its value.

        Return:
            page, per_page, column, direction (tuple):
                Pagination URL parameters.
    '''
    page = url_params.get('page', 1, type=int)
    per_page = url_params.get(
        'per_page', f.current_app.config['ITEMS_PER_PAGE'], type=int)
    column = url_params.get('col', sorting_col, type=str)
    direction = url_params.get('dir', 'desc', type=str)

    return page, per_page, column, direction
