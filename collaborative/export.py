from django.db.models.query import QuerySet
from import_export.resources import (
    ModelResource, ModelDeclarativeMetaclass
)
import tablib


class CollaborativeModelResource(ModelResource):
    def get_fk_fields(self):
        """
        Return information about reverse FK fields for a given
        base model. We use this to consistently add the FK headers
        and values to a given export.
        """
        for field in self._meta.model._meta.get_fields():
            if field.name.endswith("contactmetadata"):
                continue
            related_model = field.related_model
            if not related_model:
                continue
            for rel_field in related_model._meta.get_fields():
                if rel_field.name == "tagged_items":
                    continue
                if rel_field.name == field.name and field.name == "metadata":
                    continue
                yield field, rel_field, related_model

    def add_reverse_fk_headers(self, headers):
        for field, rel_field, related_model in self.get_fk_fields():
            header_value = "%s__%s" % (field.name, rel_field.name)
            if header_value in headers:
                continue
            headers.append(header_value)

    def add_reverse_fk_values(self, export_resource, obj):
        for field, rel_field, related_model in self.get_fk_fields():

            if not hasattr(obj, field.name):
                export_resource.append("")
                continue

            related_manager = getattr(obj, field.name)

            if not hasattr(related_manager, "first"):
                export_resource.append("")
                continue

            related_obj = related_manager.first()

            if rel_field.name == "tags":
                tags = ", ".join([t.name for t in related_obj.tags.all()])
                export_resource.append(tags)
                continue

            if not hasattr(related_obj, rel_field.name):
                export_resource.append("")
                continue

            rel_value = getattr(related_obj, rel_field.name)

            choices = getattr(
                related_obj, "%s_CHOICES" % rel_field.name.upper(), []
            )
            for pk, txt in choices:
                if pk == rel_value:
                    rel_value = txt
                    break

            export_resource.append(rel_value)

    def export(self, queryset=None, *args, **kwargs):
        """
        Exports a resource and handles reverse FK relationships.
        """

        self.before_export(queryset, *args, **kwargs)

        if queryset is None:
            queryset = self.get_queryset()
        headers = self.get_export_headers()
        self.add_reverse_fk_headers(headers)
        data = tablib.Dataset(headers=headers)

        if isinstance(queryset, QuerySet):
            # Iterate without the queryset cache, to avoid wasting memory when
            # exporting large datasets.
            iterable = queryset.iterator()
        else:
            iterable = queryset
        for obj in iterable:
            export_resource = self.export_resource(obj)
            self.add_reverse_fk_values(export_resource, obj)
            data.append(export_resource)

        self.after_export(queryset, data, *args, **kwargs)

        return data


def collaborative_modelresource_factory(
    model, resource_class=CollaborativeModelResource, meta_attrs=None
):
    """
    Factory for creating ``ModelResource`` class for given Django model.
    """
    attrs = {'model': model}

    if meta_attrs:
        attrs.update(meta_attrs)

    Meta = type(str('Meta'), (object,), attrs)

    class_name = model.__name__ + str('Resource')

    class_attrs = {
        'Meta': Meta,
    }

    metaclass = ModelDeclarativeMetaclass
    return metaclass(class_name, (resource_class,), class_attrs)



