from rest_framework_nested import routers

from . import views


router = routers.DefaultRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet)
router.register("carts", views.CartViewSet, basename="carts")
router.register("customers", views.CustomerViewSet)
router.register("orders", views.OrderViewSet, basename="orders")


products_routers = routers.NestedDefaultRouter(router, "products", lookup="product")
products_routers.register("reviews", views.ReviewViewSet, basename="product-reviews")
products_routers.register(
    "images", views.ProductImageViewSet, basename="product-images"
)
carts_routers = routers.NestedDefaultRouter(router, "carts", lookup="cart")
carts_routers.register("items", views.CartItemViewSet, basename="cart-items")


urlpatterns = router.urls + products_routers.urls + carts_routers.urls
