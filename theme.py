

import json
import os

class Theme:
    def __init__(self, terminal_bg, terminal_text, main_window_bg, main_window_text, sidebar_bg, sidebar_text):
        self.terminal_bg = terminal_bg
        self.terminal_text = terminal_text
        self.main_window_bg = main_window_bg
        self.main_window_text = main_window_text
        self.sidebar_bg = sidebar_bg
        self.sidebar_text = sidebar_text

def load_themes_from_file(root_dir):
    file_path = os.path.join(root_dir, 'theme.json')

    with open(file_path, 'r') as file:
        themes_data = json.load(file)

    themes = []
    for theme_data in themes_data:
        theme = Theme(
            terminal_bg=theme_data['terminal_bg'],
            terminal_text=theme_data['terminal_text'],
            main_window_bg=theme_data['main_window_bg'],
            main_window_text=theme_data['main_window_text'],
            sidebar_bg=theme_data['sidebar_bg'],
            sidebar_text=theme_data['sidebar_text']
        )
        themes.append(theme)

    return themes
