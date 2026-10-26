import pytest

from wagtail_tag_manager.decorators import get_variables
from wagtail_tag_manager.widgets import VariableSelect


@pytest.mark.django_db
def test_widget():
    vs = VariableSelect()
    assert len(vs.choices) == len(get_variables())
