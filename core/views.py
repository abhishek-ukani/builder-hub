from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

class DualSerializerViewSet(viewsets.ModelViewSet):
    """
    A viewset that uses different serializers for read and write operations,
    and automatically configures drf-spectacular schema.
    """
    request_serializer_class = None
    response_serializer_class = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        req = getattr(cls, 'request_serializer_class', None)
        res = getattr(cls, 'response_serializer_class', None)
        if req and res:
            extend_schema_view(
                create=extend_schema(request=req, responses={201: res}),
                update=extend_schema(request=req, responses={200: res}),
                partial_update=extend_schema(request=req, responses={200: res}),
            )(cls)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return self.request_serializer_class or self.serializer_class
        return self.response_serializer_class or self.serializer_class

    def get_response_serializer_class(self):
        return self.response_serializer_class or self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        response_serializer = self.get_response_serializer_class()(
            serializer.instance, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        response_serializer = self.get_response_serializer_class()(
            instance, context=self.get_serializer_context()
        )
        return Response(response_serializer.data)
