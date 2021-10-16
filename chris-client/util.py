class PaginationNotImplementedException(Exception):
    pass


def collection_helper(obj: dict = None) -> dict:
    if not obj:
        obj = {}
    return {
        'template': {
            'data': [{'name': k, 'value': v} for k, v in obj.items()]
        }
    }
