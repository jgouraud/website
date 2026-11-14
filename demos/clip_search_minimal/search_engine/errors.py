"""Controlled visitor messages and allowlisted failure diagnostics."""
import logging
from uuid import uuid4

from search_engine.validation import InputError

LOGGER = logging.getLogger('partfinder')


class SearchBusyError(RuntimeError):
    pass


class SearchTimeoutError(RuntimeError):
    pass


def visitor_error(error: Exception, operation: str) -> str:
    if isinstance(error, InputError):
        return str(error)
    if isinstance(error, SearchBusyError):
        return 'Search is busy. Try again shortly.'
    if isinstance(error, SearchTimeoutError):
        return 'Search took too long. Try a simpler query shortly.'
    reference = uuid4().hex[:12]
    LOGGER.error('operation_failed operation=%s error_type=%s reference=%s',
                 operation, type(error).__name__, reference)
    return f'{operation.capitalize()} could not complete. Please try again. Reference: {reference}'
