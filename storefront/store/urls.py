from django.urls import path
from . import views

urlpatterns = [
    # path("products/", views.product_list),
    # path("products/<int:id>/", views.product_detail),
    # path("collections/", views.collection_list),
    path(
        "collections/<int:pk>/", views.collection_detail, name="collection-detail"
    ),  # NOTE: use pk instead of id, Django will use 'pk' to look-up a collection.
    # class-based views
    path("products/", views.ProductList.as_view()),
    path("products/<int:pk>/", views.ProductDetail.as_view()),
    path("collections/", views.CollectionList.as_view()),
]
