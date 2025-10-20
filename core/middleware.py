from django.utils.functional import SimpleLazyObject
from django.http import JsonResponse
from firebase_admin import auth


def verify_firebase_token(token):
    """Verifica o token Firebase e retorna os dados decodificados do usuário."""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print("Erro ao verificar token Firebase:", e)
        return None


class FirebaseAuthenticationMiddleware:
    """Middleware para autenticação via Firebase."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lazy load do usuário autenticado
        request.firebase_user = SimpleLazyObject(lambda: self._get_user(request))
        response = self.get_response(request)
        return response

    def _get_user(self, request):
        """Obtém o usuário autenticado a partir do cabeçalho Authorization."""
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
            user_data = verify_firebase_token(token)
            if user_data:
                return user_data
            else:
                # Se quiser, pode retornar um JsonResponse, mas geralmente middleware só define o request
                print("Token inválido ou expirado.")
                return None

        return None
