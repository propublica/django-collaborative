from django.contrib.contenttypes.models import ContentType
from django.shortcuts import HttpResponse


def user_has_access(content_type, requestor):
    Permission = ContentType.objects.get(
        app_label="auth", model="permission"
    ).model_class()
    perms = Permission.objects.filter(
        content_type=content_type,
        codename__startswith="change_",
        user__pk=requestor.pk
    ).count()
    if perms:
        return True
    return False


def field_updater(request):
    """
    Update a field on an object, respecting object permissions.

    Example, where 2 is the content type ID and 11 is the object ID
    and we want to update the first_name field.

        POST /updater/2/11
          {
            "field": "first_name",
            "value": "Brandon"
          }

        Returns 200 with:
          {
            "status": "OK"
          }
    """
    model_pk = request.GET.get('model') # content-type
    model_ct = ContentType.objects.get(pk=model_pk)
    Model = model_ct.model_class()

    if not request.user.is_superuser and \
       not user_has_access(model_ct, request.user):
        return HttpResponse(403, {
            "status": "FAILURE",
            "message": "Access denied.",
        })

    object_pk = request.GET.get('object')
    object = Model.objects.get(pk=object_pk)
    field_name = request.POST.get('field')
    new_value = request.POST.get('value')
    value = getattr(object, field_name)
    # TODO: handle relations
    setattr(object, field_name, value)
    object.save()

    return HttpResponse(200, {"status": "OK"})
