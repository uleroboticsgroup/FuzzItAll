"""
Declaration of database session object and definition of base models.
"""

from flask_sqlalchemy import SQLAlchemy

# --------------------------------------------------------------------
#   DATABASE SESSION OBJECT
# --------------------------------------------------------------------

db = SQLAlchemy()

# --------------------------------------------------------------------
#   BASE MODELS
# --------------------------------------------------------------------


class BaseModelMixin(object):
    """
    Mixin class for defining the base functionality of any database model
    used in FuzzItAll.

    Methods
    -------
    save():
        Saves the state of the object in the database.
    delete():
        Removes the object from the database.
    get_by_id(id):
        Gets an object from its unique identifier.
    get_all(id):
        Gets all objects available in the database.
    """

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def __repr__(cls):
        return cls.__str__()

    @classmethod
    def get_by_id(cls, id: int):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all(cls):
        return cls.query.all()


class PaginatedAPIMixin(object):
    # class based on src: https://github.com/miguelgrinberg/microblog/blob/v0.23/app/models.py
    """
    Mixin class for defining a mechanism to obtain all the instances of
    a class in a paginated format.

    Methods
    -------
    to_dict():
        Transform the attributes of the class to a dictionary.
    to_collection_dict(sqlalchemy.orm.Query, int, int, dict):
        Transform the attributes of the class to a dictionary but in a\
        paginated way.
    get_sorted_query(sqlalchemy.orm.Query, str, str) -> sqlalchemy.orm.Query:
        Returns a given query but sorted by a given column and direction.
    """

    def to_dict(self):
        # (interface method)
        pass

    @staticmethod
    def to_collection_dict(query, page: int, per_page: int, **kwargs):
        # perform the query
        resources = query.paginate(page, per_page, False)
        # and create the paginated dictionary
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total,
                'has_next': resources.has_next,
                'has_prev': resources.has_prev,
                'params': kwargs
            },
        }
        return data

    @classmethod
    def get_sorted_query(cls, query: db.Query, column: str, direction: str) -> db.Query:
        sorting_col = getattr(cls, column)
        sorting_dir = getattr(sorting_col, direction)
        return query.order_by(sorting_dir())
