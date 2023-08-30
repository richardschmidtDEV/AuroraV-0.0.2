import os
from gi.repository import Gtk, Vte, Gio, Gdk, GdkPixbuf, GLib
import shutil
from left_sidebar import LeftSidebar
from terminal_tab import MyNotebook, TerminalTab

from image_terminal import ImageTerminal
from automation_tool import AutomationWindow
from mainwindow_logic import MainWindowLogic
import subprocess
import threading
import theme


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Terminal")
        self.path_entry = Gtk.Entry()
      
        self.logic = MainWindowLogic(self)
        self.connect_signals()
        self.load_css()
        self.setup_window()
        self.theme_combo = self.create_theme_combo()  # Add this line to create the theme ComboBox
  
        
        self.connect("destroy", Gtk.main_quit)

        self.create_top_right_box()
        self.create_main_layout()
        self.notebook = Gtk.Notebook()
        self.vbox.pack_end(self.notebook, True, True, 0)
        self.results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)  # Create the results_box container
     
        
    def create_script_button(self):
        icon_path = "target.png"  # Update with your local PNG file path
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 24, 24)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        button = Gtk.Button()
        button.set_image(image)
        button.set_name('custom_script_button')
        button.connect("clicked", self.logic.on_script_button_clicked)
        return button


    def connect_signals(self):
        self.connect("destroy", self.logic.on_main_window_destroy)
        self.connect("destroy", self.logic.load_modes_from_file)
        self.connect("destroy", self.logic.create_mode_combo)
        self.connect("destroy", self.logic.load_modes)
        self.connect("destroy", self.logic.on_command_changed)
        self.connect("draw", self.logic.area_draw)

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css = """
        .button-custom {
            min-height: 10px;
            padding: 0px;
            margin: 0px;
        }
        .notebook-background {
            background-color: rgba(0, 0, 0, 0);
        }
        """
        css_provider.load_from_data(css.encode())
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)



    def setup_window(self):
        self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 0.0, 0.8))
        self.set_border_width(1)
        self.set_default_size(800, 600)
        self.color_picker_window = None

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.vbox)

    def create_result_area(self):
        self.result_expander = Gtk.Expander(label="Search Results")
        self.result_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(-1, 350)  # -1 means no minimum width, 150 means a minimum height of 150px

        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.result_box)
        scrolled_window.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 1.0, 0.1))
        self.result_text_view = Gtk.TextView()
        self.result_text_view.set_editable(False)
        self.result_text_view.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 1.0, 0.1))
        self.result_box.pack_start(self.result_text_view, True, True, 0)
        self.result_box.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 1.0, 0.1))

        # Set a minimum height for the result box
        self.result_box.set_size_request(-1, 350)  # -1 means no minimum width, 150 means a minimum height of 150px

        self.result_expander.add(scrolled_window)
        return self.result_expander



    def handle_search_results(self, results):
        # Clear the results area
        self.clear_results_area()
        
        # Parse the results
        exploits = self.parse_results(results)[:20]  # Limit the results to 20
        
        # Create a button for each exploit
        for title, path in exploits:
            button = Gtk.Button.new_with_label(title)
            button.connect("clicked", self.on_download_button_clicked, path)
            self.results_box.pack_start(button, False, False, 0)
            self.result_box.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 1.0, 0.1))
        self.results_box.show_all()

    def parse_results(self, results):
        exploits = []
        lines = results.split('\n')[2:-3]  # Exclude the header and footer
        for line in lines:
            title, path = line.split('|')
            title = title.strip()
            path = path.strip().split(' ')[0]
            exploits.append((title, path))
        return exploits




    def create_search_bar(self):
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search for exploits...")
        search_icon_path = "search.png"  # Path to your search icon
        search_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(search_icon_path, 24, 24)
        search_image = Gtk.Image.new_from_pixbuf(search_pixbuf)
        search_button = Gtk.Button()
        search_button.set_image(search_image)
        search_button.connect("clicked", self.logic.on_search_button_clicked, self.search_entry)
        search_box.pack_start(self.search_entry, True, True, 0)
        search_box.pack_start(search_button, False, False, 0)
        return search_box
        

    def on_search_button_clicked(self, button, search_entry):
        search_query = search_entry.get_text()
        # Execute the searchsploit command and capture the result
        result = os.popen(f"searchsploit {search_query}").read()
        # Pass the result to the main window's handler
        self.main_window.handle_search_results(result)
    
    def download_exploit_thread(self, edb_id):
        # Get the full path of the exploit using the EDB-ID
        get_path_command = ["searchsploit", "-p", edb_id]
        try:
            result = subprocess.run(get_path_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            path = result.stdout.decode().strip()
            print(f"Full path of exploit: {path}")
        except subprocess.CalledProcessError as e:
            print(f"Error getting exploit path: {e}")
            return

        # Download the exploit using the EDB-ID
        download_command = ["searchsploit", "--mirror", edb_id]
        try:
            subprocess.run(download_command, check=True)
            print(f"Exploit downloaded from EDB-ID: {edb_id}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading exploit: {e}")

    def on_download_button_clicked(self, button, search_entry):
        path = search_entry.get_text() # Get the path from search bar
        if not path:
            print("No path provided!")
            return

        # Get the EDB-ID from the path
        edb_id = path.split("/")[-1].split(".")[0]

        # Start the download process in a separate thread
        threading.Thread(target=self.download_exploit_thread, args=(edb_id,)).start()

    def create_top_right_box(self):
        top_right_box = self.create_button_box()

        # Sidebar button
        #self.sidebar_toggle_button = self.create_button('menu.png', self.logic.on_sidebar_button_clicked)
        #top_right_box.pack_start(self.sidebar_toggle_button, False, False, 0)

        # Add button
        add_button = self.create_button('add.png', self.logic.on_add_button_clicked)
        add_button.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.9, 0.5, 0.0, 0.9))
        add_button.set_margin_end(-2)
        add_button.set_margin_start(-2)  # Set the left margin here
        top_right_box.pack_start(add_button, False, False, 0)

                # Mode combo
        self.mode_combo = self.logic.create_mode_combo()
        top_right_box.pack_start(self.mode_combo, False, False, 0)
        self.mode_combo.show()
        self.logic.load_modes()
        self.mode_combo.set_margin_start(-2)
        self.mode_combo.connect('changed', self.logic.on_mode_changed)  # Connecting the signal here

        # Command combo
        self.command_combo = Gtk.ComboBoxText()
        self.command_combo.connect('changed', self.logic.on_command_changed)
        self.command_combo.set_name('custom_image_button')
        top_right_box.pack_start(self.command_combo, False, False, 0)
        self.logic.load_commands_for_mode("default")

        # Add search bar
        
        # Create and add search bar
        search_bar = self.create_search_bar()
        top_right_box.pack_start(search_bar, False, False, 0)

        download_icon_path = "download.png"  # Path to your download icon
        download_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(download_icon_path, 24, 24)
        download_image = Gtk.Image.new_from_pixbuf(download_pixbuf)
        download_button = Gtk.Button()
        download_button.set_image(download_image)
        download_button.connect("clicked", self.on_download_button_clicked, self.search_entry)
        top_right_box.pack_start(download_button, False, False, 0)

        # Theme combo
        top_right_box.pack_start(self.theme_combo, False, False, 0)  # Add the theme ComboBox here


        # Assuming you have the correct path to your local icon PNG file
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'msf.png')
        icon_size = 24  # Set the desired size

        # Load the icon image with the specified size
        icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, icon_size, icon_size)

        # Create a button for Metasploit
        self.metasploit_button = Gtk.Button()
        image_widget = Gtk.Image.new_from_pixbuf(icon_pixbuf)
        self.metasploit_button.set_image(image_widget)
     
        self.metasploit_button.set_always_show_image(True)  # Show the image even if label is present
        self.metasploit_button.connect("clicked", self.logic.on_metasploit_button_clicked)

        top_right_box.pack_start(self.metasploit_button, False, False, 0)

        # Settings button
        settings_button = self.create_button('settings.png', self.logic.on_settings_button_clicked)
        top_right_box.pack_start(settings_button, False, False, 0)

        

         # Add script button
        script_button = self.create_script_button()
        top_right_box.pack_start(script_button, False, False, 0)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('automation.png', 24, 24)
        imageSL2 = Gtk.Image.new_from_pixbuf(pixbuf)

        button2 = Gtk.Button(label="")
      
        button2.set_name('custom_image_button')
        button2.set_image(imageSL2)

     
        button2.connect("clicked", self.on_automation_button_clicked)  # Connect the button to the automation function
        top_right_box.pack_start(button2, False, False, 0)


    def on_automation_button_clicked(self, widget):
        self.main_window.on_automation_button_clicked(widget)  # Call the main window's automation function

    def on_theme_combo_changed(self, combo):
        active_iter = combo.get_active_iter()
        if active_iter is not None:
            theme_index = combo.get_model()[active_iter][0]
            selected_theme = self.logic.themes[theme_index]  # Get the selected theme
            self.apply_theme(selected_theme)
            
    def apply_theme(self, theme):
        current_page = self.notebook.get_current_page()
        if current_page >= 0:
            current_tab = self.notebook.get_nth_page(current_page)
            for terminal in current_tab.terminals:
                self.set_terminal_colors(terminal, theme)
                
        # Convert the list to Gdk.RGBA
        main_window_bg_rgba = Gdk.RGBA(theme.main_window_bg[0], theme.main_window_bg[1], theme.main_window_bg[2], theme.main_window_bg[3])

        # Apply theme to main window
        self.vbox.override_background_color(Gtk.StateType.NORMAL, main_window_bg_rgba)

    def set_terminal_colors(self, terminal, theme):
        background_color = Gdk.RGBA(*theme.terminal_bg)
        foreground_color = Gdk.RGBA(*theme.terminal_text)
        terminal.set_color_background(background_color)
        terminal.set_color_foreground(foreground_color)
         # Apply theme to main window
        self.vbox.override_background_color(
                    Gtk.StateType.NORMAL, Gdk.RGBA(*theme.main_window_bg)
                )



    def create_theme_combo(self):
        theme_store = Gtk.ListStore(int, str)
        for index, theme in enumerate(self.logic.themes):
            theme_store.append([index, f"Theme {index + 1}"])  # Modify the label as you need

        combo = Gtk.ComboBox.new_with_model(theme_store)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, "text", 1)
        combo.connect("changed", self.on_theme_combo_changed)

        return combo


    def create_main_layout(self):
        self.hpaned = Gtk.Paned()
        self.hpaned.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 1.0, 0.1))

        self.vbox.pack_end(self.hpaned, True, True, 0)
        self.sidebar = LeftSidebar(self)
        self.hpaned.pack1(self.sidebar, False, False)

        # Create a vertical paned widget for result area
        self.vpaned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.vpaned.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 1.0, 0.1))

        self.hpaned.pack2(self.vpaned, True, False)

        # Top part of vpaned (the search results)
        result_area = self.create_result_area()
        result_area.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 0.0, 0.1))

        self.vpaned.pack1(result_area, False, False)

        

    def create_button_box(self):
        top_right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        top_right_box.set_halign(Gtk.Align.FILL)
        top_right_box.set_valign(Gtk.Align.START)
        top_right_box.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 0.0, 0.8))
        self.vbox.pack_start(top_right_box, False, False, 0)
        return top_right_box

    def create_button(self, image_file, action, toggle=False):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image_file, 24, 24)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        button = Gtk.ToggleButton() if toggle else Gtk.Button()
        button.set_image(image)
        button.set_name('custom_image_button')
        button.connect("clicked" if not toggle else "toggled", action)
        return button

    def on_terminal_button_clicked(self, widget):
        current_page = self.notebook.get_current_page()
        if current_page >= 0:
            current_tab = self.notebook.get_nth_page(current_page)
            terminal_visible = not current_tab.terminals[0].get_visible()
            for terminal in current_tab.terminals:
                terminal.set_visible(terminal_visible)
            current_tab.set_visible(terminal_visible)

    def on_automation_button_clicked(self, widget):
        automation_window = AutomationWindow(self)
        automation_window.show_all()


    


win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
