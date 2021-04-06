
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from blog.models.Community import Community

from blog.serializers.CommunitySerializer import CommunityCreateUpdateSerializer, CommunityModelSerializer


class CommunityCreateView(CreateAPIView):
    serializer_class = CommunityCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommunityDeleteView(DestroyAPIView):
    queryset = Community.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def perform_destroy(self, serializer):
        obj = self.get_object()

        if self.request.user != obj.owner:
            raise ValidationError({'detail': _('Only the community owner can perform this action.')})

        if obj.members.count() > 0:
            raise ValidationError({'detail': _('Only communities without members can be deleted.')})

        serializer.delete()


class CommunityListView(ListAPIView):
    serializer_class = CommunityModelSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = ['name']

    def get_queryset(self):
        queryset = Community.objects.select_related('owner').prefetch_related('members').all()

        query_params = self.request.query_params

        name = query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class CommunityReadView(RetrieveAPIView):
    queryset = Community.objects.select_related('owner').prefetch_related('members').all()
    serializer_class = CommunityModelSerializer
    lookup_field = 'uuid'


class CommunityUpdateView(UpdateAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunityCreateUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def perform_update(self, serializer):
        obj = self.get_object()

        if self.request.user != obj.owner:
            raise ValidationError({'detail': _('Only the community owner can perform this action.')})

        serializer.save()