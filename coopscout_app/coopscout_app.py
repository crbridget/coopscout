import tkinter as tk
from tkinter import messagebox, ttk
import schedule
import time
import threading
import pickle
import sys
import os

# Add parent directory to path to import scraper
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from scraper.scraper import NUWorksScraper
from supabase import create_client

SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"

class CoopScoutApp:
    def __init__(self):
        self.user_email = None
        self.cookies_saved = False
        self.scraper_running = False
        self.setup_gui()
    
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("CoopScout Auto-Scraper")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        
        # Title
        title = tk.Label(
            self.root, 
            text="CoopScout Daily Job Scraper", 
            font=("Arial", 18, "bold")
        )
        title.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Set up automatic daily job scraping from NUworks",
            font=("Arial", 10)
        )
        instructions.pack(pady=5)
        
        # Setup Frame
        setup_frame = tk.LabelFrame(self.root, text="Setup", padx=20, pady=20)
        setup_frame.pack(padx=20, pady=10, fill="both")
        
        tk.Label(setup_frame, text="Your Email:", font=("Arial", 10)).pack(anchor="w")
        self.email_entry = tk.Entry(setup_frame, width=40, font=("Arial", 10))
        self.email_entry.pack(pady=5)
        
        self.save_cookies_btn = tk.Button(
            setup_frame, 
            text="Step 1: Login & Save Cookies",
            command=self.save_cookies,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        self.save_cookies_btn.pack(pady=10)
        
        # Status indicator
        self.status_label = tk.Label(
            setup_frame, 
            text="Not configured", 
            fg="red",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(pady=5)
        
        # Schedule Frame
        schedule_frame = tk.LabelFrame(self.root, text="Schedule", padx=20, pady=20)
        schedule_frame.pack(padx=20, pady=10, fill="both")
        
        tk.Label(schedule_frame, text="Scrape daily at:", font=("Arial", 10)).pack(anchor="w")
        
        time_frame = tk.Frame(schedule_frame)
        time_frame.pack(pady=5)
        
        self.hour_var = tk.StringVar(value="02")
        self.minute_var = tk.StringVar(value="00")
        
        tk.Label(time_frame, text="Hour:", font=("Arial", 10)).pack(side="left")
        hour_spin = ttk.Spinbox(
            time_frame, 
            from_=0, 
            to=23, 
            width=5,
            textvariable=self.hour_var,
            font=("Arial", 10)
        )
        hour_spin.pack(side="left", padx=5)
        
        tk.Label(time_frame, text="Minute:", font=("Arial", 10)).pack(side="left", padx=(10, 0))
        minute_spin = ttk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            width=5,
            textvariable=self.minute_var,
            font=("Arial", 10)
        )
        minute_spin.pack(side="left", padx=5)
        
        # Search parameters
        tk.Label(schedule_frame, text="Search term:", font=("Arial", 10)).pack(anchor="w", pady=(10, 0))
        self.search_entry = tk.Entry(schedule_frame, width=40, font=("Arial", 10))
        self.search_entry.insert(0, "software engineering")
        self.search_entry.pack(pady=5)
        
        tk.Label(schedule_frame, text="Location:", font=("Arial", 10)).pack(anchor="w")
        self.location_entry = tk.Entry(schedule_frame, width=40, font=("Arial", 10))
        self.location_entry.insert(0, "Boston, MA, USA")
        self.location_entry.pack(pady=5)
        
        # Start button
        self.start_btn = tk.Button(
            self.root,
            text="Step 2: Start Auto-Scraper",
            command=self.start_scheduler,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        self.start_btn.pack(pady=20)
        
        # Manual scrape button
        self.manual_btn = tk.Button(
            self.root,
            text="Run Manual Scrape Now",
            command=self.manual_scrape,
            font=("Arial", 10),
            state="disabled"
        )
        self.manual_btn.pack()
        
        self.root.mainloop()
    
    def save_cookies(self):
        self.user_email = self.email_entry.get().strip()
        if not self.user_email:
            messagebox.showerror("Error", "Please enter your email")
            return
        
        messagebox.showinfo(
            "Login Required",
            "A browser will open. Please:\n\n"
            "1. Log in to NUworks\n"
            "2. Complete Duo authentication\n"
            "3. Wait for the page to fully load\n"
            "4. Come back here and click OK"
        )
        
        try:
            scraper = NUWorksScraper(headless=False)
            scraper.initialize_driver()
            scraper.navigate_to_page()
            
            messagebox.showinfo("Waiting", "Complete login, then click OK")
            
            # Save cookies
            cookies = scraper.driver.get_cookies()
            pickle.dump(cookies, open(f"cookies_{self.user_email}.pkl", "wb"))
            scraper.close()
            
            self.cookies_saved = True
            self.status_label.config(text="Ready to scrape!", fg="green")
            self.manual_btn.config(state="normal")
            messagebox.showinfo("Success", "Setup complete! You can now start the auto-scraper.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save cookies: {str(e)}")
    
    def scrape_jobs(self):
        """Main scraping function that runs on schedule"""
        if not self.cookies_saved:
            print("Error: Cookies not saved")
            return
        
        try:
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled scrape...")
            
            # Load cookies
            cookies = pickle.load(open(f"cookies_{self.user_email}.pkl", "rb"))
            
            # Scrape jobs
            from scraper.scraper import scrape_with_cookies
            jobs = scrape_with_cookies(
                cookies,
                search_term=self.search_entry.get(),
                location=self.location_entry.get()
            )
            
            # Upload to Supabase
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            for job in jobs:
                job['user_id'] = self.user_email
                supabase.table('jobs').upsert(job, on_conflict='title,company,user_id').execute()
            
            print(f"Successfully scraped and uploaded {len(jobs)} jobs")
            
        except Exception as e:
            print(f"Error during scrape: {str(e)}")
    
    def manual_scrape(self):
        """Run scrape immediately"""
        if not self.cookies_saved:
            messagebox.showerror("Error", "Please save cookies first")
            return
        
        messagebox.showinfo("Scraping", "Starting manual scrape... Check console for progress.")
        
        # Run in background thread so GUI doesn't freeze
        thread = threading.Thread(target=self.scrape_jobs, daemon=True)
        thread.start()
    
    def start_scheduler(self):
        if not self.cookies_saved:
            messagebox.showerror("Error", "Please save cookies first (Step 1)")
            return
        
        if self.scraper_running:
            messagebox.showinfo("Info", "Auto-scraper is already running!")
            return
        
        # Get scheduled time
        hour = self.hour_var.get().zfill(2)
        minute = self.minute_var.get().zfill(2)
        scrape_time = f"{hour}:{minute}"
        
        # Schedule the job
        schedule.every().day.at(scrape_time).do(self.scrape_jobs)
        
        self.scraper_running = True
        self.status_label.config(
            text=f"Running! Scrapes daily at {scrape_time}",
            fg="green"
        )
        
        # Disable setup controls
        self.save_cookies_btn.config(state="disabled")
        self.start_btn.config(state="disabled")
        
        # Run scheduler in background thread
        def run_schedule():
            while self.scraper_running:
                schedule.run_pending()
                time.sleep(60)
        
        threading.Thread(target=run_schedule, daemon=True).start()
        
        messagebox.showinfo(
            "Success",
            f"Auto-scraper is now running!\n\n"
            f"Jobs will be scraped daily at {scrape_time}\n"
            f"Keep this window open or minimize it."
        )


if __name__ == '__main__':
    app = CoopScoutApp()
