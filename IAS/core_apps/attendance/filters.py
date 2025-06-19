from datetime import date

import django_filters

from .models import Attendance


class AttendanceFilter(django_filters.FilterSet):
    date_range = django_filters.ChoiceFilter(
        choices=[
            ('today', 'Today'),
            ('this_month', 'This Month'),
            ('this_year', 'This Year'),
        ],
        method='filter_by_date_range',
        label="Date Range",
    )

    class Meta:
        model = Attendance
        fields = ['date_range']

    def filter_by_date_range(self, queryset, name, value):
        today = date.today()
        if value == 'today':
            return queryset.filter(a_date=today)
        elif value == 'this_month':
            return queryset.filter(a_date__month=today.month, a_date__year=today.year)
        elif value == 'this_year':
            return queryset.filter(a_date__year=today.year)
        return queryset
