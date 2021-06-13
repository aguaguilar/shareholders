from typing import Dict, Any

from django.db import models


def prepare_data_for_read_only_db(instance: models.Model) -> Dict[str, Any]:
    """
    Transform the data from django ORM object to python dict in order to save it into read only db.
    """
    data = instance.__dict__.copy()
    del data["_state"]
    data["_id"] = instance.pk
    del data[instance._meta.pk.name]  # delete the original pk for write only database
    return data
