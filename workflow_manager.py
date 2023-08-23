import gi
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class WorkflowManager:

    def execute_sequence(self, sequence):
        results = {}
        for name, cmd in sequence.items():
            try:
                output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
                results[name] = output.decode('utf-8')
            except subprocess.CalledProcessError as e:
                results[name] = str(e.output)
        return results


class WorkflowSequenceGUI(Gtk.Box):

    def __init__(self):
        super().__init__(spacing=10)
        self.manager = WorkflowManager()
        self.init_components()

    def init_components(self):
        # Entry widgets for adding command sequences
        self.name_entry = Gtk.Entry()
        self.name_entry.set_placeholder_text("Step Name (e.g., 'Nmap Scan')")

        self.cmd_entry = Gtk.Entry()
        self.cmd_entry.set_placeholder_text("Command (e.g., 'nmap -A 10.0.0.1')")

        self.add_step_button = Gtk.Button(label="Add Step")
        self.add_step_button.connect("clicked", self.add_step)

        self.sequence_button = Gtk.Button(label="Execute Sequence")
        self.sequence_button.connect("clicked", self.execute_sequence)

        # Text view for displaying results
        self.result_textview = Gtk.TextView()
        self.result_textview.set_editable(False)
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.add(self.result_textview)

        # Pack everything
        widgets = [self.name_entry, self.cmd_entry, self.add_step_button, scroll, self.sequence_button]
        for widget in widgets:
            self.pack_start(widget, True, True, 0)

        self.sequence = {}

    def add_step(self, widget):
        step_name = self.name_entry.get_text()
        cmd = self.cmd_entry.get_text()

        if step_name and cmd:
            self.sequence[step_name] = cmd

    def execute_sequence(self, widget):
        results = self.manager.execute_sequence(self.sequence)
        display_text = ""
        for step, result in results.items():
            display_text += f"Step: {step}\nResult:\n{result}\n\n"
        
        buffer = self.result_textview.get_buffer()
        buffer.set_text(display_text)



if __name__ == '__main__':
    win = Gtk.Window(title="Automated Workflow Sequences")
    win.connect("destroy", Gtk.main_quit)
    workflow_gui = WorkflowSequenceGUI()
    win.add(workflow_gui)
    win.show_all()
    Gtk.main()

