import subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def enumerate_directories(target_url: str) -> list:
    wordlist = "usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"  # path to your wordlist
    command = ["gobuster", "dir", "-u", target_url, "-w", wordlist, "-q"]

    try:
        result = subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL)
        # Parse the result to get directories
        directories = [line.split()[-1] for line in result.splitlines() if "Status" in line]
        return directories
    except subprocess.CalledProcessError as e:
        print(f"Error during enumeration with GoBuster: {e}")
        return []


class DirectoryGUI(Gtk.Box):

    def __init__(self):
        super().__init__(spacing=10)

        # Input Field
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter target URL (e.g., http://example.com)")
        self.pack_start(self.entry, True, True, 0)

        # Button
        self.button = Gtk.Button(label="Enumerate Directories")
        self.button.connect("clicked", self.on_button_clicked)
        self.pack_start(self.button, True, True, 0)

        # Display
        self.listbox = Gtk.ListBox()
        self.pack_start(self.listbox, True, True, 0)

    def on_button_clicked(self, widget):
        url = self.entry.get_text()
        if url:
            directories = enumerate_directories(url)
            for dir in directories:
                label = Gtk.Label(dir)
                self.listbox.add(label)
            self.listbox.show_all()

if __name__ == '__main__':
    win = Gtk.Window(title="Directory Enumerator")
    win.connect("destroy", Gtk.main_quit)
    
    dir_gui = DirectoryGUI()
    win.add(dir_gui)
    win.show_all()
    Gtk.main()
