import typing
import fastapi

class QueryParams:
    def __init__(self, q: str = fastapi.Query(None, description="Filter query to be executed against database."), 
                       skip: int = 0,
                       limit: int = 100,
                       sort: str = None,
                       fields: str = fastapi.Query(None, description="Comma seperated list of fields to return.")):
        self.q = q
        self.skip = skip
        self.limit = limit
        self.sort = sort
        self.download = None
        self.fields = fields
