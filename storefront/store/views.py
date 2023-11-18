from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.db.models import Count

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import ProductFilter
from .models import OrderItem, Product, Collection, Review
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer

from django_filters.rest_framework import DjangoFilterBackend

# P02-02-Building RESTful APIs with Django REST Framework


@api_view(["GET", "POST"])  # HTTP methods supported, GET is supported by default
def product_list(
    request,
):  # with api_view  decorator applied, the request is instance of Request object comes with Django REST framework
    # handle GET request
    if request.method == "GET":
        queryset = Product.objects.select_related(
            "collection"
        ).all()  # select_related will solve lazy loading issue
        serializer = ProductSerializer(
            queryset,
            many=True,
            context={
                "request": request
            },  # context variable used by HyperlinkRelatedField
        )  # converts QuerySet object into dictionary
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ProductSerializer(
            data=request.data
        )  # deserializing the data into dictionary OrderedDict

        # if serializer.is_valid():
        #     print(type(serializer.validated_data))
        #     return Response("OK")
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # automatically raise exception
        serializer.is_valid(
            raise_exception=True
        )  # validation rules comes from Model fields.

        # print(serializer.validated_data, " type: ", type(serializer.validated_data))

        serializer.save()  # save to database

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def product_detail(request: Request, id):
    # try:
    #     product = Product.objects.get(pk=id)
    #     serializer = ProductSerializer(
    #         product
    #     )  # convert the product object into a dictionary
    #     return Response(serializer.data)
    # except Product.DoesNotExist:
    #     return Response(status=status.HTTP_404_NOT_FOUND)

    # Using get_object_or_404
    product = get_object_or_404(Product, pk=id)

    if request.method == "GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = ProductSerializer(
            instance=product, data=request.data
        )  # when instance is provided update method of serializer will be executed while saving
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == "DELETE":
        # if product is present in order item
        if product.orderitems.count() > 0:
            return Response(
                {
                    "error": "Product can not be deleted it is associated with an order item."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def collection_list(request):
    # handle GET request
    if request.method == "GET":
        queryset = Collection.objects.prefetch_related(
            "product_set"
        ).all()  # fix lazy loading issue

        # OPTIONAL: Annotate queryset with extra column called products_count (requires related_name=products in collection field of Product model)
        # queryset = Collection.objects.annotate(products_counts=Count("products")).all()

        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = CollectionSerializer(data=request.data)  # get the data
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def collection_detail(request, pk):
    # get the collection object
    collection = get_object_or_404(Collection, pk=pk)

    # OPTIONAL: Annotate queryset with extra field called products_count (requires related_name=products in collection field of Product model)
    # collection = get_object_or_404(
    #     Collection.objects.annotate(products_counts=Count("products")), pk=pk
    # )

    # handle GET request
    if request.method == "GET":
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    # handle PUT request
    elif request.method == "PUT":
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    # handle DELETE request
    elif request.method == "DELETE":
        # if product is present in order item
        if collection.product_set.count() > 0:
            return Response(
                {
                    "error": "Collection can not be deleted because products are associated with it."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# P02-03-Advanced API Concepts


# class ProductList(APIView):  # help us write cleaner code
#     # handle GET request
#     def get(self, request):
#         queryset = Product.objects.select_related("collection").all()
#         serializer = ProductSerializer(
#             queryset, many=True, context={"request": request}
#         )
#         return Response(serializer.data)

#     # handle POST request
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# P02-03-04-Generic Views


class ProductList(ListCreateAPIView):
    # NOTE: Generic views also created form and raw data tabs for POST, PUT and PATCH requests.

    # either override queryset attribute of get_queryset method.
    # def get_queryset(self):
    #     return Product.objects.select_related("collection").all()

    # either override serializer_class attribute of get_serializer_class method.
    # def get_serializer_class(self):
    #     return ProductSerializer  # NOTE: return reference

    # overriding attribute instead of method
    # queryset = Product.objects.select_related("collection").all() # eager loading NO LONGER needed because we are only displaying collection id not the title (i.e. related model field)

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # get serializer context (used by HyperlinkRelatedField)
    def get_serializer_context(self):
        return {"request": self.request}

    # The below get and post methods are already implemented in inherited class ListCreateAPIView
    # # handle GET request
    # def get(self, request):
    #     queryset = Product.objects.select_related("collection").all()
    #     serializer = ProductSerializer(
    #         queryset, many=True, context={"request": request}
    #     )
    #     return Response(serializer.data)

    # # handle POST request
    # def post(self, request):
    #     serializer = ProductSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)


# class ProductDetail(APIView):
#     # handle the GET request
#     def get(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)

#     # handle the PUT request (fully update the object)
#     def put(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(instance=product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     # handle the DELETE request
#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response(
#                 {
#                     "error": "Product can not be deleted it is associated with an order item."
#                 },
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED,
#             )

#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# P02-03-05-Customizing Generic View


class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # lookup_field = "pk" # default

    # handle the DELETE request; Because of custom functionality we need to override inherited delete method
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response(
                {
                    "error": "Product can not be deleted it is associated with an order item."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionList(ListCreateAPIView):
    queryset = queryset = Collection.objects.prefetch_related(
        "product_set"
    ).all()  # avoids lazy loading condition
    serializer_class = CollectionSerializer


class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = queryset = Collection.objects.prefetch_related(
        "product_set"
    ).all()  # avoids lazy loading condition
    serializer_class = CollectionSerializer

    # OPTIONAL (visit function-based view implementation for details)
    # queryset = Collection.objects.annotate(products_count=Count("product"))

    # overriding delete method due to custom functionality
    def delete(self, request, pk):
        # collection = get_object_or_404(Collection, pk=pk)
        if self.queryset.product_set.count() > 0:  # if collection.products.count() > 0
            return Response(
                {
                    "error": "Collection can not be deleted it is associated with products",
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        self.queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# P03-03-06-ViewSets
class ProductViewSet(ModelViewSet):
    queryset = (
        Product.objects.all()
    )  # DRF uses queryset attribute to figure out the basename for router
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    # fields used for filtering
    # filterset_fields = ["collection_id", "unit_price"]
    # filtering using filter class
    filterset_class = ProductFilter

    # Filtering (Not required when using django_filter)
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     # collection_id = self.request.query_params["collection_id"] # assumes query_params dictionary have key 'collection_id'
    #     collection_id = self.request.query_params.get(
    #         "collection_id"
    #     )  # returns None if 'collection_id' key does not exists

    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)

    #     return queryset

    def get_serializer_context(self):
        return {"request": self.request}

    # handle the DELETE request; Because of custom functionality we need to override inherited destroy method from ModelViewSet
    def destroy(self, request, *args, **kwargs):
        if (
            OrderItem.objects.filter(product_id=kwargs["pk"]).count() > 0
        ):  # remember product_id is same as product__id in case of ForeignKey fields.
            return Response(
                {
                    "error": "Product can not be deleted it is associated with an order item."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.prefetch_related("product_set").all()
    serializer_class = CollectionSerializer

    # OPTIONAL (visit function-based view implementation for details)
    # queryset = Collection.objects.annotate(products_count=Count("product"))

    # overriding inherited destroy method from ModelViewSet
    def destroy(self, request, *args, **kwargs):
        if (
            Product.objects.filter(collection_id=kwargs["pk"]).count() > 0
        ):  # collection_id==collection__id
            return Response(
                {
                    "error": "Collection can not be deleted it is associated with products",
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    # overriding get_queryset method instead of attribute because we dont have access self to
    # access kwargs
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    # passing product_pk to serializer context
    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}
