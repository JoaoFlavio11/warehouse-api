from django.utils.functional import SimpleLazyObject
from .firebase_auth import verify_firebase_token

class FirebaseAuthenticationMiddleware:
  def __init__(self, get_response):
    self.get.response = get_response

  def __call__(self, request):
    request.firebase_user = SimpleLazyObject(lambda: self._get_user(request))
    response = self.get_response(request)
    return response

    def _get_user(self, request):
      auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
      if auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1]          user_data = verify_firebase_token(token)
        return user_data
        
      return None