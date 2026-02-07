"""
Filters for songs.
"""
from django_filters import rest_framework as filters
from .models import Song


class SongFilter(filters.FilterSet):
    """Filter for songs."""
    
    genre = filters.MultipleChoiceFilter(choices=Song.GENRE_CHOICES)
    mood = filters.MultipleChoiceFilter(choices=Song.MOOD_CHOICES)
    duration_min = filters.NumberFilter(field_name='duration', lookup_expr='gte')
    duration_max = filters.NumberFilter(field_name='duration', lookup_expr='lte')
    min_score = filters.NumberFilter(method='filter_min_score')
    
    class Meta:
        model = Song
        fields = ['genre', 'mood', 'duration_min', 'duration_max']
    
    def filter_min_score(self, queryset, name, value):
        """Filter by minimum score (upvotes - downvotes)."""
        from django.db.models import F
        return queryset.annotate(
            score=F('upvotes') - F('downvotes')
        ).filter(score__gte=value)
