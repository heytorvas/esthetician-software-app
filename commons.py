def paginate(items, page: int, limit: int):
    start = (page - 1) * limit
    end = start + limit
    return items[start:end]