# core/firebase_auth.py
import firebase_admin
from firebase_admin import auth, credentials
from functools import wraps
from django.http import JsonResponse
import os

# Caminho absoluto para o arquivo de credenciais
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cred_path = os.path.join(BASE_DIR, "firebase-service-account.json")

# Inicializa o Firebase apenas uma vez
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def verify_firebase_token(token):
    """
    Verifica o token JWT enviado pelo Firebase.
    Retorna o token decodificado se for válido, ou None se for inválido.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print("Erro ao verificar token:", e)
        return None


def firebase_auth_required(view_func):
    """
    Decorador que protege rotas Django com autenticação Firebase.
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header missing or invalid'}, status=401)

        token = auth_header.split('Bearer ')[1]
        decoded_token = verify_firebase_token(token)

        if not decoded_token:
            return JsonResponse({'error': 'Invalid or expired token'}, status=401)

        # Anexa o ID do usuário autenticado ao request
        request.user_id = decoded_token.get('uid')
        return view_func(self, request, *args, **kwargs)

    return wrapper
