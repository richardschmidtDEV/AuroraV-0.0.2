import gi
import re
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gdk

class InfoPanel(Gtk.Box):

    def __init__(self):
        super().__init__(spacing=10)
        self.init_components()

    def init_components(self):
        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        menu_bar = Gtk.MenuBar()

        ports_menu_item = Gtk.MenuItem(label="Ports")
        ports_menu = Gtk.Menu()
        ports_menu_item.set_submenu(ports_menu)
        
        open_ports_item = Gtk.MenuItem(label="Open Ports")
        open_ports_item.connect("activate", self.show_open_ports)
        ports_menu.append(open_ports_item)

        menu_bar.append(ports_menu_item)

        vertical_box.pack_start(menu_bar, False, False, 0)

        self.port_info_label = Gtk.Label()
        self.port_info_label.set_halign(Gtk.Align.START)
        vertical_box.pack_start(self.port_info_label, False, False, 0)

        self.text_view = Gtk.TextView()
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        vertical_box.pack_start(self.text_view, True, True, 0)

        self.ports_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.pack_start(self.ports_box, False, False, 0)

        self.pack_start(vertical_box, True, True, 0)

    def show_open_ports(self, widget):
        dialog = Gtk.FileChooserDialog("Select a text file", None,
                                    Gtk.FileChooserAction.OPEN,
                                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            with open(filename, 'r') as file:
                content = file.read()
                open_ports_list = content.splitlines()
                nmap_output = content  # Save nmap output
                self.display_open_ports(open_ports_list, nmap_output)  # Pass nmap_output

        dialog.destroy()

    def display_open_ports(self, open_ports_list, nmap_output):
        self.port_info_label.set_text("Open Ports:")

        for line in open_ports_list:
            match = re.search(r"(\d+)/(\w+)", line)
            if match:
                port = match.group(1)
                service = match.group(2)
                port_button = Gtk.Button(label=f"{port}/{service}")
                port_button.connect("clicked", self.show_port_info, nmap_output, port, service)  # Pass nmap_output, port, and service
                self.ports_box.pack_start(port_button, False, False, 0)

        self.show_all()



    def show_port_info(self, widget, nmap_output, port, service):
        details = f"Port: {port}\nService: {service}\n"

        additional_details = re.search(rf"{port}/tcp\s+([\w\s]+)\n(.*?)(?=\d+/|$)", nmap_output, re.DOTALL)
        if additional_details:
            status = additional_details.group(1).strip()
            info = additional_details.group(2).strip()
            details += f"{status}\n{info}"

        self.text_view.get_buffer().set_text(details)



    def on_port_box_clicked(self, widget, event, port_service):  # Use port_service instead of port_info
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            port, service = port_service.split("/")
            details = f"Port: {port}\nService: {service}\nAdditional details can be displayed here."
            self.text_view.get_buffer().set_text(details)

if __name__ == '__main__':
    win = Gtk.Window(title="Info Panel")
    win.connect("destroy", Gtk.main_quit)
    
    info_panel = InfoPanel()

    win.add(info_panel)
    win.show_all()
    Gtk.main()
