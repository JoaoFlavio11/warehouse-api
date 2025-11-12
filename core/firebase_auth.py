# core/firebase_auth.py
import os
import logging
from typing import Optional
from functools import wraps
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# ==============================================================
# Inicialização e verificação de token Firebase
# ==============================================================

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth
    from firebase_admin import credentials

    _FIREBASE_INITIALIZED = False
    FIREBASE_CRED_PATH = os.getenv("FIREBASE_CREDENTIALS_JSON")  # caminho do JSON de credenciais

    def _init_firebase_app():
        """Inicializa o app Firebase uma única vez."""
        global _FIREBASE_INITIALIZED
        if _FIREBASE_INITIALIZED:
            return

        try:
            if FIREBASE_CRED_PATH and os.path.exists(FIREBASE_CRED_PATH):
                cred = credentials.Certificate(FIREBASE_CRED_PATH)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()
            _FIREBASE_INITIALIZED = True
            logger.info("Firebase app inicializado com sucesso.")
        except Exception as e:
            logger.warning("Não foi possível inicializar firebase_admin: %s", e)
            _FIREBASE_INITIALIZED = False

    def verify_firebase_token(id_token: str) -> Optional[dict]:
        """
        Verifica um ID token do Firebase e retorna o token decodificado (dict) se for válido.
        Retorna None se o token for inválido ou se o Firebase não estiver configurado.
        """
        if not id_token:
            return None

        _init_firebase_app()
        if not _FIREBASE_INITIALIZED:
            logger.debug("Firebase não inicializado — retornando None (modo dev).")
            return None

        try:
            decoded = firebase_auth.verify_id_token(id_token)
            return decoded
        except Exception as e:
            logger.info("Token inválido ou erro ao verificar token firebase: %s", e)
            return None

except Exception as import_exc:
    # Fallback caso o firebase_admin não esteja disponível (modo dev)
    logging.getLogger(__name__).warning("firebase_admin não disponível: %s", import_exc)

    def verify_firebase_token(id_token: str):
        """Stub: em ambiente sem firebase, retorna None (não autenticado)."""
        return None


# ==============================================================
# Decorador para proteger views com autenticação Firebase
# ==============================================================

def firebase_auth_required(view_func):
    """
    Decorador para proteger views (APIView ou function-based).
    Verifica o header Authorization: Bearer <token> e injeta
    `request.user` e `request.user_id` se o token for válido.
    """
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Token ausente ou inválido"}, status=401)

        token = auth_header.split("Bearer ")[1].strip()
        try:
            decoded_token = verify_firebase_token(token)
            if not decoded_token:
                return JsonResponse({"error": "Token inválido ou expirado"}, status=401)

            # ✅ adiciona informações do usuário autenticado no request
            request.user = decoded_token
            request.user_id = decoded_token.get("uid")

            logger.debug("Usuário autenticado via Firebase: %s", request.user_id)
        except Exception as e:
            logger.warning("Erro ao verificar token Firebase: %s", e)
            return JsonResponse({"error": f"Erro de autenticação: {str(e)}"}, status=401)

        return view_func(self, request, *args, **kwargs)

    return _wrapped_view
