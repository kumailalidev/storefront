from django.urls import include, path

from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers

from . import views

from pprint import pprint

# router = SimpleRouter()

# Parent router
router = (
    routers.DefaultRouter()
)  # provides two additional features, Api Root and <endpoint>.json
router.register(
    "products", views.ProductViewSet, basename="products"
)  # products/ endpoints should be managed by ProductViewSet
router.register(
    "collections", views.CollectionViewSet
)  # collections/ endpoints should be managed by CollectionViewSet
router.register("carts", views.CartViewSet, basename="carts")
router.register("customers", views.CustomerViewSet)


# Child router
products_routers = routers.NestedDefaultRouter(router, "products", lookup="product")
products_routers.register("reviews", views.ReviewViewSet, basename="product-reviews")
carts_routers = routers.NestedDefaultRouter(router, "carts", lookup="cart")
carts_routers.register("items", views.CartItemViewSet, basename="cart-items")

# URLConf
# urlpatterns = [
#     # function-based views
#     # path("products/", views.product_list),
#     # path("products/<int:id>/", views.product_detail),
#     # path("collections/", views.collection_list),
#     # path(
#     #     "collections/<int:pk>/", views.collection_detail, name="collection-detail"
#     # ),  # NOTE: use pk instead of id, Django will use 'pk' to look-up a collection.
#     # class-based views
#     # path("products/", views.ProductList.as_view()),
#     # path(
#     #     "products/<int:pk>/", views.ProductDetail.as_view()
#     # ),  # generic views expect URL keyword argument named 'pk' DO NOT USE id
#     # path("collections/", views.CollectionList.as_view()),
#     # path(
#     #     "collections/<int:pk>/",
#     #     views.CollectionDetail.as_view(),
#     #     name="collection-detail",
#     # ),  # 'collection-detail' view name is used by HyperlinkRelatedField inside ProductSerializer
#     # ViewSets
#     # path("", include(router.urls))
# ]

# ViewSets
urlpatterns = router.urls + products_routers.urls + carts_routers.urls
