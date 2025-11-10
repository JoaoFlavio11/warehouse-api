# core/middleware.py
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class FirebaseAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware para autenticação via Firebase.
    - Verifica o header Authorization: Bearer <token>.
    - Anexa o usuário Firebase decodificado em request.firebase_user.
    - Ignora rotas /admin/ e /health/.
    - Usa import dinâmico de verify_firebase_token para evitar erros de import.
    """

    def _get_verifier(self):
        """Importa verify_firebase_token dinamicamente (evita erro em tempo de boot)."""
        try:
            from .firebase_auth import verify_firebase_token
            return verify_firebase_token
        except Exception as e:
            logger.warning("Não foi possível importar verify_firebase_token: %s", e)
            return None

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)

    def __call__(self, request):
        # Inicializa o atributo
        request.firebase_user = None

        # Ignorar autenticação para rotas específicas
        if request.path.startswith('/admin/') or request.path.endswith('/health/'):
            return self.get_response(request)

        # Obter a função verificador
        verifier = self._get_verifier()
        if verifier is None:
            # Firebase indisponível ou falha de import — segue sem autenticação
            logger.debug("Firebase verifier indisponível (modo dev).")
            return self.get_response(request)

        # Extrair token do cabeçalho Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = None
        if auth_header and auth_header.lower().startswith('bearer '):
            token = auth_header.split(' ', 1)[1].strip()

        if not token:
            # Nenhum token fornecido — segue sem autenticação
            return self.get_response(request)

        # Verificar token Firebase
        try:
            decoded = verifier(token)
            if decoded:
                request.firebase_user = decoded
                logger.debug("Usuário Firebase autenticado: %s", decoded.get('uid'))
            else:
                logger.info("Token Firebase inválido ou expirado.")
                # Opcional: Retornar 401 se quiser bloquear requisições com token inválido
                # return JsonResponse({'error': 'Invalid or expired token'}, status=401)
        except Exception as e:
            logger.warning("Erro ao verificar token Firebase: %s", e)
            # Também opcional retornar 401 aqui
            # return JsonResponse({'error': f'Invalid token: {str(e)}'}, status=401)

        # Continua o fluxo normalmente
        response = self.get_response(request)
        return response
