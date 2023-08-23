import subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


def enumerate_directories(target_url: str) -> list:
    wordlist = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"  # path to your wordlist

    command = ["gobuster", "dir", "-u", target_url, "-w", wordlist]

    try:
        result = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)

        # Parse the result to get directories
        directories = [line.split()[-1] for line in result.splitlines() if "Status" in line]
        return directories
    except subprocess.CalledProcessError as e:
        print(f"Error during enumeration with GoBuster: {e}")
        return []


class DirectoryVisualizer(Gtk.Box):

    def __init__(self):
        super().__init__(spacing=10)
        self.data = {}  # Structure can be: {directory: [subdirectories]}

        # Entry Field for URL
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter target URL (e.g., http://example.com)")
        self.pack_start(self.entry, True, True, 0)

        # Button to Start Enumeration
        self.button = Gtk.Button(label="Enumerate Directories")
        self.button.connect("clicked", self.on_button_clicked)
        self.pack_start(self.button, True, True, 0)

        # Drawing Area for Visualization
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(600, 400)  # Set preferred size
        self.drawing_area.connect("draw", self.on_draw)
        self.pack_start(self.drawing_area, True, True, 0)

    def on_button_clicked(self, widget):
        url = self.entry.get_text()
        if url:
            directories = enumerate_directories(url)
            # For simplicity, we are assuming that each directory doesn't have subdirectories
            # In a real-world implementation, you'd enumerate each directory for subdirectories
            self.data = {dir: [] for dir in directories}
            self.drawing_area.queue_draw()

    def on_draw(self, widget, cr):
        for idx, (dir, subdirs) in enumerate(self.data.items()):
            cr.set_source_rgb(0.5, 0.5, 1)  # Color for the directory nodes
            cr.arc(100, 50 + idx * 100, 20, 0, 2 * 3.14159)
            cr.fill()

            for subdir_idx, subdir in enumerate(subdirs):
                cr.set_source_rgb(1, 0, 0)  # Color for the subdirectory nodes
                cr.arc(200 + subdir_idx * 50, 50 + idx * 100, 10, 0, 2 * 3.14159)
                cr.fill()
                cr.set_source_rgb(0, 0, 0)
                cr.move_to(100, 50 + idx * 100)
                cr.line_to(200 + subdir_idx * 50, 50 + idx * 100)
                cr.stroke()

    def update_data(self, new_data):
        self.data = new_data
        self.drawing_area.queue_draw()  # Request a redraw with the new data


if __name__ == '__main__':
    win = Gtk.Window(title="Directory Visualizer")
    win.connect("destroy", Gtk.main_quit)

    visual_gui = DirectoryVisualizer()
    win.add(visual_gui)
    win.show_all()
    Gtk.main()
