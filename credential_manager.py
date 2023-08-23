import gi
import base64
from cryptography.fernet import Fernet

from stegano_tools import SteganoGUI

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class CredentialManager:
    def __init__(self):
        # Generate a key for Fernet. Ideally, you'd store this securely or derive it from user input.
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.credentials = {}  # {service: encrypted_value}

    def add_credential(self, service, username, password):
        combined = f"{username}:{password}"
        encrypted = self.cipher.encrypt(combined.encode())
        self.credentials[service] = encrypted

    def get_credential(self, service):
        encrypted = self.credentials.get(service)
        if not encrypted:
            return None, None
        decrypted = self.cipher.decrypt(encrypted).decode()
        username, password = decrypted.split(':')
        return username, password
    

class CredentialGUI(Gtk.Box):

    def __init__(self):
        super().__init__(spacing=10)
        self.manager = CredentialManager()
        self.init_components()

    def init_components(self):
        # Components for adding credentials
        self.service_entry = Gtk.Entry()
        self.service_entry.set_placeholder_text("Service e.g. SSH")
        
        self.username_entry = Gtk.Entry()
        self.username_entry.set_placeholder_text("Username")
        
        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Password")
        self.password_entry.set_visibility(False)  # Mask password input
        
        self.add_button = Gtk.Button(label="Add Credential")
        self.add_button.connect("clicked", self.add_credential)

        # Components for retrieving credentials
        self.retrieve_service_entry = Gtk.Entry()
        self.retrieve_service_entry.set_placeholder_text("Service to Retrieve")
        
        self.retrieve_button = Gtk.Button(label="Retrieve Credential")
        self.retrieve_button.connect("clicked", self.retrieve_credential)
        
        self.result_label = Gtk.Label("")

        # Create a vertical Gtk Box to hold the widgets
        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        # Add margins to the widgets
        for widget in [self.service_entry, self.username_entry, self.password_entry, 
                    self.add_button, self.retrieve_service_entry, self.retrieve_button, 
                    self.result_label]:
            widget.set_margin_top(10)
            widget.set_margin_bottom(10)
            widget.set_margin_start(10)
            widget.set_margin_end(10)
            vertical_box.pack_start(widget, False, False, 0)
        
        self.pack_start(vertical_box, True, True, 0)  # Allow expansion


    def add_credential(self, widget):
        service = self.service_entry.get_text()
        username = self.username_entry.get_text()
        password = self.password_entry.get_text()
        if service and username and password:
            self.manager.add_credential(service, username, password)

    def retrieve_credential(self, widget):
        service = self.retrieve_service_entry.get_text()
        username, password = self.manager.get_credential(service)
        if username and password:
            self.result_label.set_text(f"Username: {username}, Password: {password}")
        else:
            self.result_label.set_text("No credentials found for this service.")


if __name__ == '__main__':
    # Add some custom styling
    style_provider = Gtk.CssProvider()
    css_str = """
    button.suggested-action {
        background-color: #4CAF50;
        border-radius: 5px;
        color: white;
    }
    button.suggested-action:hover {
        background-color: #45a049;
    }
    """
    style_provider.load_from_data(css_str.encode('utf-8'))

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    win = Gtk.Window(title="Credential Manager and Steganography Tools")
    win.connect("destroy", Gtk.main_quit)
    
    # Create a vertical Gtk Box to hold both the steganography and credential manager GUIs
    vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    

    credential_gui = CredentialGUI()

    vertical_box.pack_start(credential_gui, True, True, 0)
    
    win.add(vertical_box)
    
    # Set the transparent background with an alpha value of 0.8
    rgba = Gdk.RGBA()
    rgba.parse("rgba(0, 0, 0, 0.8)")
    win.override_background_color(Gtk.StateFlags.NORMAL, rgba)
    
    win.show_all()
    Gtk.main()
