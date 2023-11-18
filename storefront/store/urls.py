from django.urls import path
from . import views

urlpatterns = [
    # function-based views
    # path("products/", views.product_list),
    # path("products/<int:id>/", views.product_detail),
    # path("collections/", views.collection_list),
    # path(
    #     "collections/<int:pk>/", views.collection_detail, name="collection-detail"
    # ),  # NOTE: use pk instead of id, Django will use 'pk' to look-up a collection.
    # class-based views
    path("products/", views.ProductList.as_view()),
    path(
        "products/<int:pk>/", views.ProductDetail.as_view()
    ),  # generic views expect URL keyword argument named 'pk' DO NOT USE id
    path("collections/", views.CollectionList.as_view()),
    path(
        "collections/<int:pk>/",
        views.CollectionDetail.as_view(),
        name="collection-detail",
    ),  # 'collection-detail' view name is used by HyperlinkRelatedField inside ProductSerializer
]
