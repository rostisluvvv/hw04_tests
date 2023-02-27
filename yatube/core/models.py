from django.db import models


class PubDateModels(models.Model):
    """Abstract model. Adds the creation date."""
    pub_date = models.DateTimeField('publication date', auto_now_add=True)

    class Meta:
        abstract = True