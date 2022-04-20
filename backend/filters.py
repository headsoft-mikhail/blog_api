from django_filters import rest_framework as filters, DateTimeFilter
from backend.models import Post


class PostsFilter(filters.FilterSet):
    """Фильтры для постов."""
    created_at_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    nesting_gte = filters.NumberFilter(field_name='nesting_level', lookup_expr='gte')
    nesting_lte = filters.NumberFilter(field_name='nesting_level', lookup_expr='lte')

    class Meta:
        model = Post
        fields = ['owner', 'created_at_after', 'created_at_before', 'nesting_level']
