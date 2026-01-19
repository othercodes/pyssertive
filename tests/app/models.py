from django.db import models


class SoftDeleteModel(models.Model):
    name = models.CharField(max_length=100)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "app"
