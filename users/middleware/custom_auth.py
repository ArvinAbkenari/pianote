from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from users.models import User  # Use your actual User model

class ManualLoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_id = request.session.get('user_id')
        if user_id:
            try:
                request.user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()