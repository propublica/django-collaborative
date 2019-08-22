import logging

from django.contrib.contenttypes.models import ContentType
from taggit.models import Tag

from django_models_from_csv.utils.common import http_response


logger = logging.getLogger(__name__)


def user_has_access(content_type, requestor):
    Permission = ContentType.objects.get(
        app_label="auth", model="permission"
    ).model_class()
    logger.debug("Permission Model: %s" % str(Permission))
    logger.debug("Requestor ID: %s" % (requestor.pk))
    perms = Permission.objects.filter(
        content_type=content_type,
        codename__startswith="change_",
        user__pk=requestor.pk
    ).count()
    logger.debug("Matching permission groups: %s" % (perms))
    if perms:
        return True
    return False


def field_updater(request):
    """
    Update a field on an object, respecting object permissions.

    Example, where 2 is the content type ID and 11 is the object ID
    and we want to update the first_name field.

        POST /object-updater/
          {
            "model": 2,
            "object": 11,
            "field": "first_name",
            "value": "Brandon"
          }

    Example for a tag foreign key removal:

        POST /object-updater/
          {
            "model": 2,
            "object": 11,
            "field": "metadata__tags",
            "value": "Brandon",
            "fk_operation": "remove"
          }

    Upon success, this endpoint returns 200 with body:
      {
        "status": "OK",
        "message": "Saved!"
      }
    """
    model_pk = request.POST.get('model') # content-type
    model_ct = ContentType.objects.get(pk=model_pk)
    Model = model_ct.model_class()
    logger.debug("Updater model ID: %s, model: %s" % (
        model_pk, model_ct
    ))

    if not request.user.is_superuser and \
       not user_has_access(model_ct, request.user):
        return http_response({
            "status": "FAILURE",
            "message": "Access denied.",
        }, status=403)

    object_pk = request.POST.get('object')
    object = Model.objects.get(pk=object_pk)
    logger.debug("Object ID=%s, object=%s" % (object_pk, object))
    if not object:
        return http_response({
            "status": "FAILURE",
            "message": "Row %s not found." % (object_pk),
        }, status=400)

    field_name = request.POST.get('field')
    new_value = request.POST.get('value')
    logger.debug("field_name=%s, new_value=%s" % (field_name, new_value))

    if "__" not in field_name:
        setattr(object, field_name, new_value)
        object.save()
        return http_response({"status": "OK", "message": "Saved!"})

    # NOTE: we _do not_ support many-to-many here. we
    # assume ForeignKey (with single value) as the only
    # possible relation type. (that's the only relation
    # field supported by dynamic models)
    field_parts = field_name.split("__")
    last_part = field_parts.pop()
    path = object
    for rel in field_parts:
        logger.debug("Relation part: %s" % (rel))
        path = getattr(path, rel).first()
        logger.debug("New relation path: %s" % (path))

    logger.debug("Setting field=%s to value=%s" % (last_part, new_value))
    if last_part != "tags":
        setattr(path, last_part, new_value)
        path.save()
        return http_response({"status": "OK", "message": "Saved!"})

    # handle tags separately
    fk_operation = request.POST.get("fk_operation", "add")
    tagger = getattr(path, last_part)
    if tagger.filter(name=new_value).count():
        return http_response({
            "status": "OK", "message": "Tag already exists."
        })

    if fk_operation == "add":
        tag, _ = Tag.objects.get_or_create(name=new_value)
        tagger.add(tag)
        return http_response({
            "status": "OK",
            "object": object_pk,
            "message": "Tag added."
        })
    elif fk_operation == "remove":
        try:
            tag = Tag.objects.get(name=new_value)
        except Tag.DoesNotExist:
            return http_response({
                "status": "OK",
                "message": "Non-existant tag, ignoring remove"
            })
        tagger.remove(tag)
        return http_response({
            "status": "OK",
            "object": object_pk,
            "message": "Tag removed."
        })

    return http_response({
        "status": "Failure", "message": "Bad tag operation."
    }, status=400)
