import gi
import string
import os

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gtk, Vte, GLib, Gdk



class MyNotebook(Gtk.Notebook):
    def __init__(self):
        Gtk.Notebook.__init__(self)

        css_provider = Gtk.CssProvider()
        css = """
            .notebook-background {
                background-color: rgba(0, 0, 0, 0.5); /* Adjust the color and alpha as needed */
            }
        """
        css_provider.load_from_data(css.encode())

        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.set_tab_pos(Gtk.PositionType.TOP)
        self.set_show_border(False)
        self.set_border_width(0)
        
        self.get_style_context().add_class("notebook-background") 


class TerminalTab(Gtk.Box):
    tab_counter = 0

    def __init__(self, tab_name, notebook, themes, main_window):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.main_window = main_window  # Store the main_window reference
        self.themes = themes
        self.current_theme = themes[0]  # Initialize with a default theme or another appropriate theme

        self.tab_name = tab_name
        self.notebook = notebook

        self.active_terminal = None  # Initialize the active terminal variable
        # Connect the button_press_event signal for all terminals
        
        self.grid = Gtk.Grid()  # Create the grid first
        self.pack_start(self.grid, True, True, 0)

        # Load and apply CSS for the buttons and tab labels
        css_provider = Gtk.CssProvider()
        css = """
            .button-custom {
                min-height: 10px;
                padding: 0px;
                margin: 0px;
            }
            .button-box {
                margin: 0px;
                padding: 0px;
            }
            .hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            .tab-label-background {
                background-color: rgba(0, 0, 0, 0.5);  /* Adjust the color and alpha as needed */
                padding: 0px;
                margin: 0px;
            }
        """
        css_provider.load_from_data(css.encode())

        # Apply the CSS provider to the window
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.set_border_width(0)

        self.terminals = []
        self.add_terminal_to_grid(self.grid, self.current_theme)


    def set_terminal_colors(self, theme):
        for terminal in self.terminals:
            self.main_window.set_terminal_colors(terminal, theme)

        # Update the background color of the MainWindow
        self.main_window.override_background_color(
            Gtk.StateType.NORMAL, Gdk.RGBA(*theme.background_color)
        )



    def on_theme_changed(self, theme):
        self.current_theme = theme  # Update the current theme
        for terminal in self.terminals:
            self.main_window.set_terminal_colors(terminal, theme)

        # Update the background color of the MainWindow
        self.main_window.override_background_color(
            Gtk.StateType.NORMAL, Gdk.RGBA(*theme.background_color)
        )   

    def add_terminal_to_grid(self, grid, current_theme):
        terminal = Vte.Terminal.new()
        shell = os.environ.get("SHELL", "/bin/sh")
        terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.environ["HOME"],
            [shell, "--login"],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )
        grid.attach(terminal, 0, 0, 1, 1)
        terminal.connect("key-press-event", self.on_terminal_key_press)

        self.main_window.set_terminal_colors(terminal, current_theme)
        self.terminals.append(terminal)
        # Set expand properties for the terminal
        terminal.set_hexpand(True)
        terminal.set_vexpand(True)
        terminal.set_halign(Gtk.Align.FILL)
        terminal.set_valign(Gtk.Align.FILL)




    def on_tab_close(self, widget, event=None):
        self.notebook.remove_page(self.notebook.page_num(self))

    def on_terminal_key_press(self, widget, event):
        active_terminal = self.get_focused_terminal()
        if not active_terminal:
            return

        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if event.keyval == Gdk.KEY_c:  # Ctrl+C
                active_terminal.copy_clipboard()
            elif event.keyval == Gdk.KEY_v:  # Ctrl+V
                clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
                clipboard.request_text(self.on_clipboard_text_received, active_terminal)

    def on_clipboard_text_received(self, clipboard, text, terminal):
        if terminal and text:
            terminal_text = text.encode()
            terminal.feed_child(terminal_text)



    def get_focused_terminal(self):
        terminal = self.terminals[0]  # assuming you have at least one terminal in the list
        toplevel_window = terminal.get_toplevel()

        if not isinstance(toplevel_window, Gtk.Window):
            return None

        focused_widget = toplevel_window.get_focus()
        if isinstance(focused_widget, Vte.Terminal):
            return focused_widget

        return None



    def is_plain_text(self, text):
        # Define a list of characters that are considered plain text
        plain_text_characters = (
            string.ascii_letters
            + string.digits
            + string.punctuation
            + " "
            + "\t"
            + "\n"
        )
        # Check if all characters in the text are in the plain text list
        return all(char in plain_text_characters for char in text)

    def create_tab_label(self):
        TerminalTab.tab_counter += 1
        tab_label_text = f"{TerminalTab.tab_counter}: {self.tab_name}"

        tab_label = Gtk.Label(label=tab_label_text)
        tab_label.set_margin_top(0)
        tab_label.set_margin_bottom(0)
        tab_label.get_style_context().add_class("tab-label-background")  # Apply the new class here


        close_icon = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        split_icon = Gtk.Image.new_from_icon_name("pan-start-symbolic", Gtk.IconSize.MENU)

        close_btn = Gtk.Button()
        close_btn.set_image(close_icon)
        close_btn.set_always_show_image(True)
        close_btn.set_relief(Gtk.ReliefStyle.NONE)  # Remove button relief
        close_btn.set_name("button-custom")  # Use "button-custom" as the class name
        close_btn.connect("clicked", self.on_tab_close, self)  # Pass 'self' as an additional argument
        close_btn.set_size_request(0, 0)  # Set the button size to 30x10 pixels
        close_btn.connect("enter", self.on_enter_button)
        close_btn.connect("leave", self.on_leave_button)

        split_btn = Gtk.Button()
        split_btn.set_image(split_icon)
        split_btn.set_always_show_image(True)
        split_btn.set_relief(Gtk.ReliefStyle.NONE)  # Remove button relief
        split_btn.set_name("button-custom")  # Use "button-custom" as the class name
        split_btn.connect("clicked", self.on_split_button_clicked)  # Pass 'self' as an additional argument
        split_btn.set_size_request(0, 0)  # Set the button size to 30x10 pixels
        split_btn.connect("enter", self.on_enter_button)
        split_btn.connect("leave", self.on_leave_button)

        tab_label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        tab_label_box.get_style_context().add_class("tab-label-background")  # Apply the new class here
        tab_label_box.pack_start(tab_label, True, True, 0)
        tab_label_box.pack_start(split_btn, False, False, 0)
        tab_label_box.pack_start(close_btn, False, False, 0)
        tab_label_box.set_size_request(-1, 0)  # Set the height of the tab bar to 10 pixels
        tab_label_box.set_size_request(-1, 0)  # Set the height of the tab bar to 10 pixels

        tab_label_box.show_all()

        return tab_label_box

    def on_enter_button(self, button):
        button.get_style_context().add_class("hover")

    def on_leave_button(self, button):
        button.get_style_context().remove_class("hover")

    def on_split_button_clicked(self, widget):
        dialog = Gtk.Dialog("Split Terminal", None, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        content_area = dialog.get_content_area()
        grid = Gtk.Grid()
        content_area.add(grid)

        self.grid.set_margin_start(0)
        self.grid.set_margin_end(0)
        self.grid.set_margin_top(0)
        self.grid.set_margin_bottom(0)


        # Left split button
        left_button = Gtk.Button.new_with_label("Left Split")
        left_button.connect("clicked", self.on_split_left)
        grid.attach(left_button, 0, 0, 1, 1)

        # Right split button
        right_button = Gtk.Button.new_with_label("Right Split")
        right_button.connect("clicked", self.on_split_right)
        grid.attach(right_button, 1, 0, 1, 1)

        # Top split button
        top_button = Gtk.Button.new_with_label("Top Split")
        top_button.connect("clicked", self.on_split_top)
        grid.attach(top_button, 0, 1, 1, 1)

        # Bottom split button
        bottom_button = Gtk.Button.new_with_label("Bottom Split")
        bottom_button.connect("clicked", self.on_split_bottom)
        grid.attach(bottom_button, 1, 1, 1, 1)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            pass
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

    def on_terminal_key_press_split(self, widget, event):
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if event.keyval == Gdk.KEY_c:  # Ctrl+C
                widget.copy_clipboard()
            elif event.keyval == Gdk.KEY_v:  # Ctrl+V
                clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
                clipboard.request_text(self.on_clipboard_text_received)


    def on_split_left(self, widget):
        self.split_terminal(Gtk.Orientation.HORIZONTAL, True)

    def on_split_right(self, widget):
        self.split_terminal(Gtk.Orientation.HORIZONTAL, False)

    def on_split_top(self, widget):
        self.split_terminal(Gtk.Orientation.VERTICAL, True)

    def on_split_bottom(self, widget):
        self.split_terminal(Gtk.Orientation.VERTICAL, False)


    def split_terminal(self, orientation, insert_first):
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

        new_terminal_grid = Gtk.Grid()
        new_terminal.connect("key-press-event", self.on_terminal_key_press)


        new_terminal_grid.attach(new_terminal, 0, 0, 1, 1)
        self.main_window.set_terminal_colors(new_terminal, self.current_theme)
        self.terminals.append(new_terminal)

        # Set expand properties for the new terminal grid
        new_terminal_grid.set_hexpand(True)
        new_terminal_grid.set_vexpand(True)

        if orientation == Gtk.Orientation.HORIZONTAL:
            if insert_first:
                self.grid.insert_column(0)
                self.grid.attach(new_terminal_grid, 0, 0, 1, len(self.terminals) + 1)
                for i in range(len(self.terminals)):
                    self.grid.attach(self.terminals[i], i + 1, 0, 1, len(self.terminals) + 1)
            else:
                self.grid.insert_column(len(self.terminals))
                for i in range(len(self.terminals)):
                    self.grid.attach(self.terminals[i], i, 0, 1, len(self.terminals) + 1)
                self.grid.attach(new_terminal_grid, len(self.terminals), 0, 1, len(self.terminals) + 1)
        else:
            if insert_first:
                self.grid.insert_row(0)
                self.grid.attach(new_terminal_grid, 0, 0, len(self.terminals) + 1, 1)
                for i in range(len(self.terminals)):
                    self.grid.attach(self.terminals[i], 0, i + 1, len(self.terminals) + 1, 1)
            else:
                self.grid.insert_row(len(self.terminals))
                for i in range(len(self.terminals)):
                    self.grid.attach(self.terminals[i], 0, i, len(self.terminals) + 1, 1)
                self.grid.attach(new_terminal_grid, 0, len(self.terminals), len(self.terminals) + 1, 1)


        # Set expand properties for all terminals in the grid
        for terminal in self.terminals:
            terminal.set_hexpand(True)
            terminal.set_vexpand(True)
            terminal.set_halign(Gtk.Align.FILL)
            terminal.set_valign(Gtk.Align.FILL)

        self.grid.show_all()
        new_terminal_grid.show_all()







