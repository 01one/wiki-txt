#!/usr/bin/env python3
import requests
from urllib.parse import urlparse
import os
import gi


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"


def get_wikipedia_content(title):
	params = {
		"action": "query",
		"format": "json",
		"prop": "extracts",
		"titles": title,
		"explaintext": True,
	}
	response = requests.get(WIKIPEDIA_API_URL, params=params)
	data = response.json()
	page_id = list(data["query"]["pages"].keys())[0]
	return data["query"]["pages"][page_id].get("extract", "")


class WikiTxt(Gtk.Application):
	def __init__(self):
		super().__init__()
		self.default_directory = os.getenv("XDG_DOWNLOAD_DIR", os.path.expanduser("~/Downloads"))

		if not os.access(self.default_directory, os.W_OK):
			self.default_directory = os.path.expanduser("~/Documents")

	def do_activate(self):
		window = Gtk.ApplicationWindow(application=self)
		window.set_title("Download Wikipedia Articles in Plain Text Format")
		window.set_default_size(1000, 700)


		main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
		main_box.set_margin_top(50)
		main_box.set_margin_start(30)
		main_box.set_margin_end(30)
		window.set_child(main_box)


		search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		search_box.set_halign(Gtk.Align.CENTER)


		url_entry = Gtk.Entry()
		url_entry.set_placeholder_text("Enter Wikipedia article URL...")
		url_entry.set_size_request(500, -1)


		download_button = Gtk.Button(label="Download")
		download_button.set_size_request(250, -1)

		search_box.append(url_entry)
		search_box.append(download_button)
		main_box.append(search_box)


		log_frame = Gtk.Frame()
		progress_scrolled_window = Gtk.ScrolledWindow()
		progress_scrolled_window.set_min_content_height(250)
		progress_text_view = Gtk.TextView()
		progress_text_view.set_editable(False)
		progress_text_view.set_cursor_visible(False)
		progress_scrolled_window.set_child(progress_text_view)
		log_frame.set_child(progress_scrolled_window)
		main_box.append(log_frame)


		dir_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		dir_button = Gtk.Button(label="Change Save Location")
		dir_label = Gtk.Label(label=f"Save Location: {self.default_directory}")
		dir_label.set_selectable(True)
		dir_label.set_xalign(0)

		dir_box.append(dir_button)
		dir_box.append(dir_label)
		main_box.append(dir_box)

		def on_download_button_clicked(_):
			url = url_entry.get_text().strip()
			if not url.startswith("https://en.wikipedia.org/wiki/"):
				self.log_message(progress_text_view, "Invalid URL. Please enter a valid Wikipedia URL.")
				return

			title = urlparse(url).path.split("/")[-1]
			self.log_message(progress_text_view, f"Fetching article: {title}")

			try:
				content = get_wikipedia_content(title)
				if not content:
					raise ValueError("No content found for the specified title.")

				save_path = os.path.join(self.default_directory, f"{title}.txt")
				with open(save_path, "w", encoding="utf-8") as file:
					file.write(content)

				self.log_message(progress_text_view, f"Article saved to {save_path}")
			except Exception as e:
				self.log_message(progress_text_view, f"Error: {str(e)}")





		def on_dir_button_clicked(_):
			dialog = Gtk.FileDialog()
			
			def on_folder_selected(dialog, result):
				try:
					folder = dialog.select_folder_finish(result)
					if folder:
						folder_path = folder.get_path()
						if folder_path:
							self.default_directory = folder_path
							dir_label.set_text(f"Save Location: {self.default_directory}")
				except Exception as e:
					print(f"Folder selection error: {e}")

			dialog.select_folder(window, None, on_folder_selected)
			
			
			
		download_button.connect("clicked", on_download_button_clicked)
		dir_button.connect("clicked", on_dir_button_clicked)

		window.present()

	def log_message(self, text_view, message):
		buffer = text_view.get_buffer()
		buffer.insert(buffer.get_end_iter(), message + "\n")


if __name__ == "__main__":
	app = WikiTxt()
	app.run()
