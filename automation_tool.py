import gi
import json
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

class AutomationWindow(Gtk.Window):
    def __init__(self, main_window):
        Gtk.Window.__init__(self, title="Automation Tool")
        self.set_default_size(400, 300)
        self.set_border_width(10)

        self.main_window = main_window  # Store a reference to the main window

        self.command_chains = []
        self.modes = []  # Initialize the modes list
        self.current_command_chain_index = None
        self.current_command_index = None

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        mode_label = Gtk.Label("Select Mode:")
        vbox.pack_start(mode_label, False, False, 0)

        self.mode_combo = Gtk.ComboBoxText()
        vbox.pack_start(self.mode_combo, False, False, 0)

        self.commands_list = Gtk.ListBox()
        vbox.pack_start(self.commands_list, True, True, 0)

        start_button = Gtk.Button(label="Start Selected Automation")
        start_button.connect("clicked", self.on_start_button_clicked)
        vbox.pack_start(start_button, False, False, 0)

        create_button = Gtk.Button(label="Create Command Chain")
        create_button.connect("clicked", self.on_create_button_clicked)
        vbox.pack_start(create_button, False, False, 0)
        
        self.json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "command_chains.json")
        self.modes_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modes.json")

        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, "r") as file:
                self.command_chains = json.load(file)
        else:
            self.command_chains = []

        if os.path.exists(self.modes_file_path):
            with open(self.modes_file_path, "r") as file:
                self.modes = json.load(file)
        else:
            self.modes = []

        self.load_modes()
        self.load_command_chains()

    def on_start_button_clicked(self, widget):
        selected_row = self.commands_list.get_selected_row()
        if selected_row:
            self.current_command_chain_index = selected_row.get_index()
            self.current_command_index = 0
            self.execute_next_command()

    def on_create_button_clicked(self, widget):
        dialog = Gtk.Dialog(
            title="Create Command Chain",
            parent=self,
            buttons=(
                "Save",
                Gtk.ResponseType.OK,
                "Cancel",
                Gtk.ResponseType.CANCEL,
            ),
        )
        dialog.set_default_response(Gtk.ResponseType.OK)

        name_entry = Gtk.Entry()
        name_entry.set_placeholder_text("Enter command chain name")
        dialog.vbox.pack_start(name_entry, False, False, 0)

        mode_label = Gtk.Label("Select Mode:")
        dialog.vbox.pack_start(mode_label, False, False, 0)

        mode_combo = Gtk.ComboBoxText()
        dialog.vbox.pack_start(mode_combo, False, False, 0)

        for mode in self.get_available_modes():
            mode_combo.append_text(mode)

        mode_entry = Gtk.Entry()
        mode_entry.set_placeholder_text("Enter mode name")
        dialog.vbox.pack_start(mode_entry, False, False, 0)

        entry = Gtk.Entry()
        entry.set_placeholder_text("Enter commands separated by ';'")
        dialog.vbox.pack_start(entry, True, True, 0)

        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name = name_entry.get_text()
            mode = mode_combo.get_active_text() or mode_entry.get_text()
            command_chain = entry.get_text()
            self.add_command_chain(name, mode, command_chain)
                
            # Add the new mode to the list of modes
            if mode and mode not in self.get_available_modes():
                self.modes.append({"name": mode})
            
            self.save_command_chains()

        dialog.destroy()


    def get_available_modes(self):
        modes = [mode['name'] for mode in self.modes]
        return modes

    def execute_next_command(self):
        if (
            self.current_command_chain_index is not None
            and self.current_command_chain_index < len(self.command_chains)
        ):
            if self.current_command_index is None:
                self.current_command_index = 0

            if (
                self.current_command_index < len(self.command_chains[self.current_command_chain_index]['commands'])
            ):
                command = self.command_chains[self.current_command_chain_index]['commands'][self.current_command_index]
                self.current_command_index += 1

                pid, _ = self.main_window.main_terminal.spawn_async(
                    GLib.PRIORITY_DEFAULT,
                    None,
                    ["/bin/bash", "-c", command],
                    [],
                    GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                    None,
                    None,
                )

                GLib.child_watch_add(pid, self.on_command_exit)
            else:
                self.current_command_chain_index = None
                self.current_command_index = None

    def on_command_exit(self, pid, status):
        self.execute_next_command()

    def add_command_chain(self, name, mode, command_chain):
        commands = command_chain.split(";")
        self.command_chains.append({"name": name, "mode": mode, "commands": commands})


    def load_modes(self):
        try:
            with open(self.modes_file_path, "r") as file:
                self.modes = json.load(file)
        except FileNotFoundError:
            self.modes = []

    def load_command_chains(self):
        try:
            with open(self.json_file_path, "r") as file:
                self.command_chains = json.load(file)
        except FileNotFoundError:
            self.command_chains = []

        for chain in self.command_chains:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=f"{chain['name']}: {', '.join(chain['commands'])}")
            row.add(label)
            self.commands_list.add(row)

    def save_modes(self):
        with open(self.modes_file_path, "w") as file:
            json.dump(self.modes, file, indent=4)

    def save_command_chains(self):
        self.save_modes()
        with open(self.json_file_path, "w") as file:
            json.dump(self.command_chains, file, indent=4)

