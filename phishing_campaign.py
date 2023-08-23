import gi
import requests
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class PhishingManager:

    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }

    def create_campaign(self, name, email_template, target_list):
        # For brevity, we're assuming `email_template` and `target_list` are structured for the GoPhish API.
        data = {
            "name": name,
            "template": email_template,
            "targets": target_list
        }
        response = requests.post(f"{self.api_url}/api/campaigns/", json=data, headers=self.headers)
        return response.json()

    def get_campaign_results(self, campaign_id):
        response = requests.get(f"{self.api_url}/api/campaigns/{campaign_id}/results", headers=self.headers)
        return response.json()

class PhishingCampaignGUI(Gtk.Box):

    def __init__(self, api_url, api_key):
        super().__init__(spacing=10)
        self.manager = PhishingManager(api_url, api_key)
        self.init_components()

    def init_components(self):
        # Components for creating a new campaign
        self.campaign_name_entry = Gtk.Entry()
        self.campaign_name_entry.set_placeholder_text("Campaign Name")

        self.email_template_entry = Gtk.Entry()
        self.email_template_entry.set_placeholder_text("Email Template (JSON formatted)")

        self.target_list_entry = Gtk.Entry()
        self.target_list_entry.set_placeholder_text("Target List (JSON formatted)")

        self.create_button = Gtk.Button(label="Create Campaign")
        self.create_button.connect("clicked", self.create_campaign)

        # Components to fetch results of a campaign
        self.campaign_id_entry = Gtk.Entry()
        self.campaign_id_entry.set_placeholder_text("Campaign ID to Fetch Results")
        
        self.fetch_results_button = Gtk.Button(label="Fetch Results")
        self.fetch_results_button.connect("clicked", self.fetch_results)

        self.result_label = Gtk.Label()

        # Pack everything into the box
        for widget in [self.campaign_name_entry, self.email_template_entry, self.target_list_entry, self.create_button,
                       self.campaign_id_entry, self.fetch_results_button, self.result_label]:
            self.pack_start(widget, True, True, 0)

    def create_campaign(self, widget):
        name = self.campaign_name_entry.get_text()
        email_template = self.email_template_entry.get_text()
        target_list = self.target_list_entry.get_text()

        result = self.manager.create_campaign(name, email_template, target_list)
        self.result_label.set_text(f"Campaign created with ID: {result.get('id')}")

    def fetch_results(self, widget):
        campaign_id = self.campaign_id_entry.get_text()
        results = self.manager.get_campaign_results(campaign_id)
        # For simplicity, displaying the raw results. Consider formatting this for a better UX.
        self.result_label.set_text(str(results))


if __name__ == '__main__':
    api_url = "http://gophish_instance_url"  # Change this
    api_key = "YOUR_GOPHISH_API_KEY"         # Change this

    win = Gtk.Window(title="Phishing Campaign Manager")
    win.connect("destroy", Gtk.main_quit)
    phishing_gui = PhishingCampaignGUI(api_url, api_key)
    win.add(phishing_gui)
    win.show_all()
    Gtk.main()
