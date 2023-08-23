import subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def scan_ports(target: str) -> dict:
    # Placeholder using Nmap as an example; adjust as necessary
    command = ["nmap", "-sV", "-T4", target]  
    try:
        result = subprocess.check_output(command, text=True)
        
        # Here we are simply returning the raw result. In reality, you'd parse this for port and service details.
        # The dictionary structure can be {port: service}. This can be further enhanced to capture more info.
        return {'raw_output': result}
    except subprocess.CalledProcessError as e:
        print(f"Error during port scan: {e}")
        return {}


class PortScanGUI(Gtk.Box):

    def __init__(self, subdomains: list):
        super().__init__(spacing=10)

        # Dropdown to select subdomain/IP
        self.subdomain_selector = Gtk.ComboBoxText()
        for subdomain in subdomains:
            self.subdomain_selector.append_text(subdomain)
        self.subdomain_selector.set_active(0)
        self.pack_start(self.subdomain_selector, True, True, 0)

        # Button
        self.button = Gtk.Button(label="Start Port Scan")
        self.button.connect("clicked", self.on_button_clicked)
        self.pack_start(self.button, True, True, 0)

        # Display
        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.pack_start(self.text_view, True, True, 0)

    def on_button_clicked(self, widget):
        target = self.subdomain_selector.get_active_text()
        if target:
            result = scan_ports(target)
            
            # Display raw output in the text view. You can further parse the result to show structured data.
            text_buffer = self.text_view.get_buffer()
            text_buffer.set_text(result.get('raw_output', ''))
