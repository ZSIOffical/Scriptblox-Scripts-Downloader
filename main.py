import tkinter as tk
from tkinter import ttk
import threading
import os
import requests
import time

invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

if not os.path.exists("Scripts"):
    os.makedirs("Scripts")

class CollectorThread(threading.Thread):
    def __init__(self, wait_time, update_output):
        threading.Thread.__init__(self)
        self.wait_time = wait_time
        self.update_output = update_output
        self.running = False
    
    def run(self):
        self.running = True
        
        for page in range(1, 9999):
            if not self.running:
                break
            
            response = requests.get(f"https://scriptblox.com/api/script/fetch?page={page}")
            data = response.json()
            
            for script in data["result"]["scripts"]:
                if not self.running:
                    break
                
                script_id = script["_id"]
                script_title = script["title"]
                script_slug = script["slug"]
                game_id = script["game"]["gameId"]
                game_name = script["game"]["name"]
                
                clean_script_title = ''.join(c for c in script_title if c not in invalid_chars)
                
                if game_id:
                    folder_name = f"{clean_script_title} - {game_id}"
                else:
                    folder_name = clean_script_title
                
                script_folder_path = os.path.join("Scripts", folder_name)
                if not os.path.exists(script_folder_path):
                    os.makedirs(script_folder_path)
                
                script_url = f"https://rawscripts.net/raw/{script_slug}"
                script_response = requests.get(script_url)
                script_content = script_response.text
                
                with open(os.path.join(script_folder_path, f"{clean_script_title}.txt"), "w", encoding="utf-8") as f:
                    f.write(script_content)
                
                self.update_output(f"Collected: {clean_script_title}")
            
            time.sleep(self.wait_time)
    
    def stop(self):
        self.running = False

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Script Collector")
        self.geometry("600x400")
        
        self.start_button = ttk.Button(self, text="Start", command=self.start_collector)
        self.start_button.pack()
        
        self.stop_button = ttk.Button(self, text="Stop", command=self.stop_collector)
        self.stop_button.pack()
        
        self.wait_time_label = ttk.Label(self, text="Wait Time: 0.0 seconds")
        self.wait_time_label.pack()
        
        self.wait_time_slider = ttk.Scale(self, from_=0, to=50, orient=tk.HORIZONTAL, command=self.update_wait_time_label)
        self.wait_time_slider.set(20)
        self.wait_time_slider.pack()
        
        self.output_console = tk.Text(self)
        self.output_console.pack(fill=tk.BOTH, expand=True)
        
        self.collector_thread = None
    
    def start_collector(self):
        wait_time = self.wait_time_slider.get() / 10.0
        
        self.collector_thread = CollectorThread(wait_time, self.update_output_console)
        self.collector_thread.start()
    
    def stop_collector(self):
        if self.collector_thread:
            self.collector_thread.stop()
    
    def update_wait_time_label(self, value=None):
        wait_time = self.wait_time_slider.get() / 10.0
        self.wait_time_label.configure(text=f"Wait Time: {wait_time:.1f} seconds")
    
    def update_output_console(self, text):
        self.output_console.insert(tk.END, text + "\n")
        self.output_console.see(tk.END)

if __name__ == '__main__':
    window = MainWindow()
    window.mainloop()
