from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError

"""
    Convert DjangoValidationError and IntegrityError to DRFValidationError (400 BAD REQUEST) 
"""
def django_to_drf_exception_handler(exc, context):     
    # 1. Django ValidationError (from model clean() methods) -> 400 Bad Request
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            detail = exc.message_dict
        elif hasattr(exc, 'messages'):
            detail = exc.messages
        else:
            detail = [str(exc)]
        exc = DRFValidationError(detail)
    
    # 2. Database constraint violations -> 400 Bad Request  
    elif isinstance(exc, IntegrityError):
        exc = DRFValidationError({'error': 'This data already exists or violates a database rule'})
    
    # Let DRF handle everything else (404s, permissions, etc.)
    return exception_handler(exc, context)
