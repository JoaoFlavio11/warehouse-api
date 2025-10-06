from rest_framework import permissions

class IsFirebaseAuthenticated(permissions.BasePermission):
  """
  Permission para verificar se usuário está autenticado via Firebase
  """
  message = 'Autenticação Firebase obrigatória.'

  def has_permission(self, request, view):
    return request.firebase_user is not None
    