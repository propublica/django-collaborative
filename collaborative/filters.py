from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from taggit.models import Tag


class TagListFilter(admin.SimpleListFilter):
    """
    A custom filterable for tags. Restricts the displayed tags by the
    current data source, even though tags are global.
    """
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('tag')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        Model = model_admin.model
        meta_name = "%smetadata" % (Model._meta.object_name)
        ct = ContentType.objects.get(
            app_label="django_models_from_csv", model=meta_name
        )
        tags = Tag.objects.filter(
            taggit_taggeditem_items__content_type=ct
        ).values_list("name", "slug").distinct()
        return tags

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(metadata__tags__name=value)

