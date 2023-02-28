from django.db import models


class PubDateModels(models.Model):
    """Abstract model. Adds post creation date."""
    pub_date = models.DateTimeField(
        'publication date',
        auto_now_add=True,
        db_index=True)

    class Meta:
        abstract = True
