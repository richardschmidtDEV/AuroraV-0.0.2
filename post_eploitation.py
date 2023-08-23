import gi
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class PostExploitationManager:
    def execute_script(self, script_path, args=[]):
        cmd = [script_path] + args
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            return output.decode('utf-8')
        except subprocess.CalledProcessError as e:
            return str(e.output)


class PostExploitationGUI(Gtk.Box):
    def __init__(self):
        super().__init__(spacing=10)
        self.manager = PostExploitationManager()
        self.init_components()

    def init_components(self):
        # Dropdown for module/script selection
        self.module_dropdown = Gtk.ComboBoxText()
        modules = ["BeRoot", "CrackMapExec", "data_extractor"]
        for module in modules:
            self.module_dropdown.append_text(module)
        self.module_dropdown.set_active(0)

        # Entry box for arguments
        self.args_entry = Gtk.Entry()
        self.args_entry.set_placeholder_text("Arguments (if needed)")

        # Button to execute
        self.execute_button = Gtk.Button(label="Execute")
        self.execute_button.connect("clicked", self.execute_module)

        # Result display
        self.result_textview = Gtk.TextView()
        self.result_textview.set_editable(False)
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.add(self.result_textview)

        # Pack everything
        for widget in [self.module_dropdown, self.args_entry, self.execute_button, scroll]:
            self.pack_start(widget, True, True, 0)

    def execute_module(self, widget):
        module_name = self.module_dropdown.get_active_text()
        args = self.args_entry.get_text().split()

        # Map the module_name to actual script paths
        script_map = {
            "BeRoot": "/path/to/beroot",
            "CrackMapExec": "crackmapexec",
            "data_extractor": "./data_extractor.sh"
        }

        script_path = script_map.get(module_name)

        result = self.manager.execute_script(script_path, args)

        buffer = self.result_textview.get_buffer()
        buffer.set_text(result)


if __name__ == '__main__':
    win = Gtk.Window(title="Post-Exploitation Modules")
    win.connect("destroy", Gtk.main_quit)
    post_exploit_gui = PostExploitationGUI()
    win.add(post_exploit_gui)
    win.show_all()
    Gtk.main()
