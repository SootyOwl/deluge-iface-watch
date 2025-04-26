import pytest
from unittest.mock import MagicMock, patch
from ifacewatch.gtk3ui.gtkui import GtkUI

@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    # 1) Mock deluge.component.get for Preferences and PluginManager
    fake_prefs = MagicMock()
    fake_pm = MagicMock()
    monkeypatch.setattr(
        "deluge.component.get",
        lambda name: {"Preferences": fake_prefs, "PluginManager": fake_pm}[name],
    )

    # 2) Mock client.ifacewatch
    fake_ifacewatch = MagicMock()
    fake_client = MagicMock(ifacewatch=fake_ifacewatch)
    monkeypatch.setattr("ifacewatch.gtk3ui.gtkui.client", fake_client)

    # 3) Stub out get_resource to point at some dummy file
    monkeypatch.setattr(
        "ifacewatch.gtk3ui.gtkui.get_resource",
        lambda x: __file__,  # just any existing path
    )

    # 4) Patch Gtk.Builder.new_from_file to return a fake builder
    fake_builder = MagicMock()
    fake_builder.get_object.side_effect = lambda name: MagicMock(name=name)
    class FakeBuilderClass:
        @staticmethod
        def new_from_file(path):
            return fake_builder

    monkeypatch.setattr("ifacewatch.gtk3ui.gtkui.Gtk.Builder", FakeBuilderClass)

    # 5) Clear component registry to avoid ComponentAlreadyRegistered errors
    # Import locally to avoid polluting the global namespace if not needed
    from deluge.component import _ComponentRegistry
    _ComponentRegistry.components.clear()


    return fake_prefs, fake_pm, fake_ifacewatch, fake_builder

def test_create_ui_registers_hooks(mock_dependencies):
    fake_prefs, fake_pm, _, fake_builder = mock_dependencies
    plugin = GtkUI("ifacewatch")
    plugin.create_ui()

    # Ensure we loaded some widget
    assert fake_builder.get_object.called

    # Preferences.add_page called once
    fake_prefs.add_page.assert_called_once()
    # PluginManager hooks registered
    fake_pm.register_hook.assert_any_call("on_apply_prefs", plugin.on_apply_prefs)
    fake_pm.register_hook.assert_any_call("on_show_prefs", plugin.on_show_prefs)

def test_on_checkbutton_active_toggled_saves_config(mock_dependencies):
    _, _, fake_ifacewatch, fake_builder = mock_dependencies
    plugin = GtkUI("ifacewatch")
    plugin.builder = fake_builder

    # Prepare the checkbutton_active widget
    cb = MagicMock()
    cb.get_active.return_value = True
    fake_builder.get_object.side_effect = lambda name: cb if name == "checkbutton_active" else MagicMock()

    plugin.on_checkbutton_active_toggled(None)
    fake_ifacewatch.save_config.assert_called_once_with({"active": True})

def test_set_iface_value(mock_dependencies):
    _, _, _, fake_builder = mock_dependencies
    plugin = GtkUI("ifacewatch")
    plugin.builder = fake_builder

    # Mock combobox and its model
    combobox = MagicMock(name="interface_combobox")
    model = MagicMock(name="model")

    # Simulate model content and behavior
    interfaces = ["eth0", "wlan0"]
    def model_get_iter(i):
        if 0 <= i < len(interfaces):
            # Return a simple object representing the iter, e.g., the index itself
            return i
        raise IndexError # Or return Gtk.TreePath(i) if more realism needed

    def model_get_value(it, column):
        # Assuming column 0 holds the interface name
        if column == 0 and 0 <= it < len(interfaces):
            return interfaces[it]
        return None # Or raise error

    model.__len__.return_value = len(interfaces)
    model.get_iter.side_effect = model_get_iter
    model.get_value.side_effect = model_get_value

    combobox.get_model.return_value = model
    # Mock get_object to return this specific combobox
    fake_builder.get_object.side_effect = lambda name: combobox if name == "interface_combobox" else MagicMock()

    # Test set_iface_value with existing interface
    plugin.set_iface_value("eth0")
    # Check set_active was called with the correct index (0 for "eth0")
    combobox.set_active.assert_called_once_with(0)
    combobox.set_active.reset_mock()

    # Test set_iface_value with another existing interface
    plugin.set_iface_value("wlan0")
    # Check set_active was called with the correct index (1 for "wlan0")
    combobox.set_active.assert_called_once_with(1)
    combobox.set_active.reset_mock()

    # Test set_iface_value with non-existing interface
    plugin.set_iface_value("new0")
    # Check set_active was called with iface 0 (default)
    combobox.set_active.assert_called_once_with(0)
    combobox.append_text.assert_called_once_with("new0")


def test_on_apply_prefs_saves_only_on_change(mock_dependencies):
    _, _, fake_ifacewatch, fake_builder = mock_dependencies
    plugin = GtkUI("ifacewatch")
    plugin.builder = fake_builder

    # Widgets returning specific values
    fake_builder.get_object.side_effect = lambda name: {
        "interface_combobox": MagicMock(get_active_text=lambda: "eth1"),
        "spinbutton_update_interval": MagicMock(get_value=lambda: 10),
        "checkbutton_active": MagicMock(get_active=lambda: False),
    }[name]

    # Case 1: last_config is None → always save
    plugin.last_config = None
    plugin.on_apply_prefs()
    fake_ifacewatch.save_config.assert_called_once_with({
        "interface": "eth1",
        "update_interval": 10,
        "active": False,
    })
    fake_ifacewatch.save_config.reset_mock()

    # Case 2: same config → no save
    plugin.last_config = {"interface": "eth1", "update_interval": 10, "active": False}
    plugin.on_apply_prefs()
    fake_ifacewatch.save_config.assert_not_called()

    # Case 3: changed interface → save
    plugin.last_config["interface"] = "eth0"
    plugin.on_apply_prefs()
    fake_ifacewatch.save_config.assert_called_once()