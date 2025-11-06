from django.utils.functional import SimpleLazyObject
from django.http import JsonResponse
from firebase_admin import auth

class FirebaseAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.firebase_user = None
        
        # Ignorar autenticação para rotas de admin ou health check
        if request.path.startswith('/admin/') or request.path.endswith('/health/'):
            return self.get_response(request)

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1]
            user_data = verify_firebase_token(token)
            
            if user_data:
                request.firebase_user = user_data
            else:
                # Opcional: Retornar 401 se o token for inválido, mas estiver presente
                # Se você usar a classe de permissão, ela cuidará disso.
                pass 

        response = self.get_response(request)
        return response