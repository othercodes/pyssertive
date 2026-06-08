# Database Assertions

!!! note
    Requires the Django adapter (`pip install pyssertive[django]`).

```python
from pyssertive.adapters.django.db import (
    assert_model_exists,
    assert_model_count,
    assert_num_queries,
)

assert_model_exists(User, username="john")
assert_model_count(User, 5)

with assert_num_queries(2):
    list(User.objects.all())
```
