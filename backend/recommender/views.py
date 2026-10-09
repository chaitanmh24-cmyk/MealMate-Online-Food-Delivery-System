from django.shortcuts import render
from django.http import JsonResponse
from .engine import get_recommendations


def recommendations_view(request):
    """
    Renders dedicated 'Recommended For You' page based on user signals.
    """
    user = request.user if request.user.is_authenticated else None
    recommendations = get_recommendations(user=user, limit=12)

    context = {
        'recommendations': recommendations,
        'title': 'Recommended For You — MealMate',
    }
    return render(request, 'recommender/recommendations.html', context)


def recommendations_api(request):
    """
    JSON API endpoint returning personalized recommendations for fetch API integrations.
    """
    user = request.user if request.user.is_authenticated else None
    limit = int(request.GET.get('limit', 8))
    recommendations = get_recommendations(user=user, limit=min(limit, 20))

    data = [
        {
            'id': item.id,
            'name': item.name,
            'price': str(item.price),
            'food_type': item.food_type,
            'image': item.image,
            'restaurant_name': item.restaurant.name,
            'restaurant_id': item.restaurant.id,
            'cuisine': item.cuisine.name if item.cuisine else None,
            'category': item.category.name if item.category else None,
        }
        for item in recommendations
    ]
    return JsonResponse({'ok': True, 'count': len(data), 'results': data})
