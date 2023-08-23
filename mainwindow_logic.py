import gi
import os
import json
import cairo
import subprocess
import xml.etree.ElementTree as ET
from gi.repository import Gtk, Vte, Gdk, GdkPixbuf, GLib
from automation_tool import AutomationWindow
from theme import load_themes_from_file, Theme



from terminal_tab import TerminalTab

class MainWindowLogic:
    def __init__(self, main_window):
        self.main_window = main_window
        self.command_chains = self.load_command_chains_from_file()
        self.main_window = main_window
        root_dir = os.path.dirname(os.path.abspath(__file__))  # get the directory of the current file
        self.themes = load_themes_from_file(root_dir)

    def load_modes_from_file(self):
        with open('modes.json', 'r') as file:
            modes = json.load(file)
        return modes
    
    def set_terminal_colors(self, terminal, theme):
        background_color = Gdk.RGBA(*theme.terminal_bg)
        foreground_color = Gdk.RGBA(*theme.terminal_text)
        terminal.set_color_background(background_color)
        terminal.set_color_foreground(foreground_color)
        # Apply other color settings as needed for the terminal


    def load_command_chains_from_file(self):
        file_path = 'command_chains.json'
        
        # Check if the file exists
        if not os.path.exists(file_path):
            # Create a default command_chains if the file doesn't exist
            default_command_chains = []  # You can define a default structure here
            with open(file_path, 'w') as file:
                json.dump(default_command_chains, file)

        # Now, open the file as it should exist
        with open(file_path, 'r') as file:
            command_chains = json.load(file)
            
        return command_chains


    def create_mode_combo(self):
        modes = self.load_modes_from_file()
        model = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mode.png')

        for mode in modes:
            mode_name = mode["name"]
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 16, 16)
            model.append([pixbuf, mode_name])

        combo = Gtk.ComboBox.new_with_model(model)
        combo.set_margin_top(0)
        combo.set_margin_bottom(0)
        combo.set_margin_start(2)
        combo.set_margin_end(2)

        cell_pixbuf = Gtk.CellRendererPixbuf()
        combo.pack_start(cell_pixbuf, False)
        combo.add_attribute(cell_pixbuf, "pixbuf", 0)

        cell_text = Gtk.CellRendererText()
        combo.pack_start(cell_text, False)
        combo.add_attribute(cell_text, "text", 1)

        combo.set_name('custom_image_button')

        return combo

    def on_mode_changed(self, combo):
        active_iter = combo.get_active_iter()
        model = combo.get_model()
        mode = model[active_iter][1]
        self.load_commands_for_mode(mode)

    def load_commands_for_mode(self, selected_mode):
        self.main_window.command_combo.get_model().clear()
        for command_chain in self.command_chains:
            if command_chain["mode"] == selected_mode:
                self.main_window.command_combo.append_text(command_chain["name"])


    def on_add_button_clicked(self, widget):
        dialog = Gtk.Dialog(
            title="Add Terminal Tab",
            parent=self.main_window,
            buttons=(
                "Add",
                Gtk.ResponseType.OK,
                "Cancel",
                Gtk.ResponseType.CANCEL,
            ),
        )
        dialog.set_default_response(Gtk.ResponseType.OK)

        entry = Gtk.Entry()
        entry.set_placeholder_text("Tab Name")
        dialog.vbox.pack_start(entry, True, True, 0)
        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            tab_name = entry.get_text()
            terminal_tab = TerminalTab(tab_name, self.main_window.notebook, self.themes, self.main_window)            
            GLib.idle_add(self.spawn_terminal, terminal_tab)

            self.main_window.notebook.append_page(terminal_tab, terminal_tab.create_tab_label())
            self.main_window.notebook.set_name("notebook-background")
            self.main_window.notebook.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 0.0, 0.8))
            self.load_modes()
            self.main_window.notebook.show_all()

        dialog.destroy()

    def spawn_terminal(self, terminal_tab):
        new_terminal = Vte.Terminal()
        shell = os.environ.get("SHELL", "/bin/sh")
        new_terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.environ["HOME"],
            [shell, "--login"],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )

        terminal_tab.set_terminal_colors(new_terminal, self.theme)  # Call set_terminal_colors

        return False



    def load_modes(self):
        modes = self.load_modes_from_file()
        self.main_window.mode_combo.get_model().clear()
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mode.png')

        for mode in modes:
            mode_name = mode["name"]
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 16, 16)
            self.main_window.mode_combo.get_model().append([pixbuf, mode_name])

    def on_settings_button_clicked(self, widget):
        print("Settings button clicked")

    def area_draw(self, widget, cr):
        cr.set_source_rgba(0.6, 0.0, 0.0, 0.8)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

    def on_sidebar_button_clicked(self, widget):
        if self.main_window.sidebar.get_visible():
            self.main_window.sidebar.hide()
        else:
            self.main_window.sidebar.show()



    def open_terminal_in_new_window(self, command_chain):
        print("Opening new terminal window with command chain:", command_chain)
        window = Gtk.Window(title="New Terminal")
        terminal = Vte.Terminal()

        terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            ["/bin/bash"],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )

        for command in command_chain.split('&&'):
            terminal.feed_child_binary(command.strip().encode() + b'\n')

        window.add(terminal)
        window.set_default_size(800, 600)
        window.show_all()

    def on_command_changed(self, combo):
        command_name = combo.get_active_text()
        if command_name is None:
            return

        command_chain = None
        for command in self.command_chains:
            if command["name"] == command_name:
                command_chain = command["commands"][0]  # Since commands is an array, take the first element
                break

        if command_chain:
            self.open_terminal_in_new_window(command_chain)

    def search_for_cves(self, user_input):
        try:
            result = subprocess.run(["searchsploit", user_input], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"An error occurred while searching for CVEs: {result.stderr}"
        except FileNotFoundError:
            return "searchsploit is not installed on this system."

    def on_search_button_clicked(self, button, search_entry):
        user_input = search_entry.get_text()
        # Use the user_input to search for CVEs, assuming results are a string
        results = self.search_for_cves(user_input)  # replace with actual search code
        text_buffer = self.main_window.result_text_view.get_buffer()
        text_buffer.set_text(results)

    def on_script_button_clicked(self, widget):
        script_path = "/home/eb/Desktop/Aurora-main/settings.sh"
        bashrc_path = "/home/eb/Desktop/Aurora-main/bashrc"  # Temporary location for the new .bashrc

        # Create the .bashrc file content
        bashrc_content = f'source {script_path}'

        # Write the content to the temporary .bashrc file
        with open(bashrc_path, 'w') as bashrc_file:
            bashrc_file.write(bashrc_content)

        # Make the temporary .bashrc file executable
        os.chmod(bashrc_path, 0o755)

        # Prepare the command to execute
        command = f"bash -c 'source {bashrc_path} && {script_path}'"

        # Open a VTE terminal and execute commands
        self.open_terminal_in_new_window(command)

        # Clean up the temporary .bashrc file (optional)
        os.remove(bashrc_path)

    def on_metasploit_button_clicked(self, widget):
        command_chain = "msfconsole"  # Command to execute 'msfconsole'
        self.open_terminal_in_new_window(command_chain)



    def on_main_window_destroy(self, widget):
        Gtk.main_quit()