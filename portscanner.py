import gi
import subprocess
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

# Define the functions to create target folder and save output to file
def create_target_folder(path, name):
    target_folder = os.path.join(path, name)
    
    try:
        os.makedirs(target_folder)
        return target_folder
    except OSError:
        return None

def save_output_to_file(folder, filename, content):
    file_path = os.path.join(folder, filename)
    
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return True
    except OSError:
        return False

class PortScannerGUI(Gtk.Box):

    def __init__(self):
        super().__init__(spacing=10)
        self.init_components()

    def init_components(self):
        self.target_entry = Gtk.Entry()
        self.target_entry.set_placeholder_text("Target IP or Hostname")

        self.params_entry = Gtk.Entry()
        self.params_entry.set_placeholder_text("Nmap Parameters")

        

        self.folder_entry = Gtk.Entry()
        self.folder_entry.set_placeholder_text("Target Folder")

        self.create_folder_button = Gtk.Button(label="Create Folder")
        self.create_folder_button.connect("clicked", self.create_target_folder)
        
        self.scan_button = Gtk.Button(label="Scan Ports")
        self.scan_button.connect("clicked", self.scan_ports)

        self.result_label = Gtk.Label("")

        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        for widget in [self.target_entry, self.params_entry, self.scan_button,
                       self.folder_entry, self.create_folder_button, self.result_label]:
            widget.set_margin_top(10)
            widget.set_margin_bottom(10)
            widget.set_margin_start(10)
            widget.set_margin_end(10)
            vertical_box.pack_start(widget, False, False, 0)

        self.pack_start(vertical_box, True, True, 0)  # Allow expansion

    def create_target_folder(self, widget):
        folder_name = self.folder_entry.get_text()

        if folder_name:
            target_folder = create_target_folder("", folder_name)

            if target_folder:
                self.target_folder = target_folder
                self.result_label.set_text(f"Target folder created: {self.target_folder}")
            else:
                self.result_label.set_text("Error creating target folder.")

    def scan_ports(self, widget):
        target = self.target_entry.get_text()
        params = self.params_entry.get_text()

        if not target or not params:
            self.result_label.set_text("Please enter target and params.")
            return

        if not hasattr(self, 'target_folder') or not self.target_folder:
            self.result_label.set_text("Please create a target folder first.")
            return

        # Perform the scanning logic
        nmap_command = ["nmap", target, *params.split()]
        try:
            nmap_output = subprocess.check_output(nmap_command, text=True)
            self.result_label.set_text("Scanning completed. Saving output...")

            # Save the output to the nmap_output.txt file in the target folder
            save_success = save_output_to_file(self.target_folder, "nmap_output.txt", nmap_output)

            if save_success:
                self.result_label.set_text("Scanning completed. Output saved.")
            else:
                self.result_label.set_text("Error saving output.")
        except subprocess.CalledProcessError as e:
            self.result_label.set_text("Error while scanning: " + str(e))

if __name__ == '__main__':
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

    win = Gtk.Window(title="Port Scanner and Credential Manager")
    win.connect("destroy", Gtk.main_quit)
    
    vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    
    port_scanner_gui = PortScannerGUI()

    vertical_box.pack_start(port_scanner_gui, True, True, 0)
    
    win.add(vertical_box)
    
    rgba = Gdk.RGBA()
    rgba.parse("rgba(0, 0, 0, 0.8)")
    win.override_background_color(Gtk.StateFlags.NORMAL, rgba)
    
    win.show_all()
    Gtk.main()
