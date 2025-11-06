# core/firebase_auth.py

from functools import wraps
from django.http import JsonResponse
from firebase_admin import auth

def firebase_auth_required(view_func ):
    @wraps(view_func)
    # Adicione 'self' como o primeiro argumento
    def wrapper(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header missing or invalid'}, status=401)

        try:
            token = auth_header.split('Bearer ')[1]
            decoded_token = auth.verify_id_token(token)
            # Anexar o usuário ao request para uso posterior na view
            request.user_id = decoded_token['uid']
        except Exception as e:
            return JsonResponse({'error': f'Invalid token: {str(e)}'}, status=401)

        # Passe 'self' e 'request' para a função original da view
        return view_func(self, request, *args, **kwargs)
    return wrapper
