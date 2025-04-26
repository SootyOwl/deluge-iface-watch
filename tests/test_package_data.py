import pkg_resources
import pytest

def test_ui_resource_available():
    # This will raise if the resource isn't in the egg-info
    data = pkg_resources.resource_string("ifacewatch", "data/ifacewatch.ui")
    assert data.startswith(b"<?xml"), "UI file should start with XML header"