from products.models import Basket


def baskets(request):
    user = request.user
    if user.is_authenticated:
        return {"baskets": Basket.objects.filter(user=user)}
    return {"baskets": []}
