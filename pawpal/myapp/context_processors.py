# work/dsi202/pawpal/myapp/context_processors.py

from .models import UserFavorite

def favorite_count(request):
    """
    Adds the number of favorite pets for the logged-in user to the context.
    """
    if request.user.is_authenticated:
        count = UserFavorite.objects.filter(user=request.user).count()
        return {'favorite_count': count, 'has_favorites': count > 0}
    return {'favorite_count': 0, 'has_favorites': False}