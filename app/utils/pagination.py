from math import ceil


def get_pagination_meta(
    total: int,
    page: int,
    limit: int
) -> dict:
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": ceil(total / limit),
        "has_next": page * limit < total,
        "has_previous": page > 1
    }
