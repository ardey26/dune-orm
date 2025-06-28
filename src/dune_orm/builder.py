    
import copy
from functools import wraps

def chainable(method):
    """Decorator: clone self, apply method to clone, and return the clone."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        new = copy.copy(self)
        method(new, *args, **kwargs)
        return new
    return wrapper

def mutating_chain(method):
    """Decorator: run method on self, then return self."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        method(self, *args, **kwargs)
        return self
    return wrapper

class DuneQueryBuilder:
    """Chainable builder methods for DuneQuery."""
    @chainable
    def filter(self, **kwargs):
        """Add filters and return a new builder."""
        self.filters = kwargs

    @chainable
    def exclude(self, **kwargs):
        """Add exclude filters and return a new builder."""
        self.exclude_filters = kwargs

    @chainable
    def values(self, *args):
        """Select specific fields and return a new builder."""
        self.fields = args

    @chainable
    def order_by(self, field, ascending=True):
        """Set ordering and return a new builder."""
        self.sort_by = field
        self.sort_order = 'asc' if ascending else 'desc'

    @chainable
    def limit(self, n):
        """Set row limit and return a new builder."""
        self._limit = n

    @chainable
    def get(self, **kwargs):
        """Filter and limit to 1, returning a new builder."""
        self.filters = kwargs
        self._limit = 1

    @chainable
    def all(self):
        """Clear filters and fields, returning a new builder."""
        self.filters = {}
        self.fields = []