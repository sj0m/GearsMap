import os
import psutil
import customtkinter as ctk
import threading
import time
import subprocess
import platform
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Set appearance mode and default color theme for customtkinter
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class SystemMonitor(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("System Resource Monitor")
        self.geometry("900x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Data history
        self.max_data_points = 60
        self.cpu_history = [0] * self.max_data_points
        self.ram_history = [0] * self.max_data_points
        self.network_history = [0] * self.max_data_points
        
        # Previous network total for calculation
        self.prev_net_io = psutil.net_io_counters()
        self.prev_net_time = time.time()
        
        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=0, pady=0)

        # Logo and title
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="System Monitor", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=(20, 10))
        
        # System info
        self.system_info_frame = ctk.CTkFrame(self.sidebar_frame)
        self.system_info_frame.pack(padx=20, pady=10, fill="x")
        
        self.hostname_label = ctk.CTkLabel(self.system_info_frame, text=f"Host: {platform.node()}")
        self.hostname_label.pack(anchor="w", padx=10, pady=2)
        
        self.os_label = ctk.CTkLabel(self.system_info_frame, text=f"OS: {platform.system()} {platform.release()}")
        self.os_label.pack(anchor="w", padx=10, pady=2)
        
        self.uptime_label = ctk.CTkLabel(self.system_info_frame, text="Uptime: Calculating...")
        self.uptime_label.pack(anchor="w", padx=10, pady=2)
        
        self.time_label = ctk.CTkLabel(self.sidebar_frame, text="")
        self.time_label.pack(padx=20, pady=10)
        
        # Mode switch
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.pack(padx=20, pady=(10, 0))
        self.appearance_mode_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                     command=self.change_appearance_mode)
        self.appearance_mode_menu.pack(padx=20, pady=(10, 10))
        self.appearance_mode_menu.set("System")
        
        # Refresh rate control
        self.refresh_label = ctk.CTkLabel(self.sidebar_frame, text="Refresh Rate:", anchor="w")
        self.refresh_label.pack(padx=20, pady=(10, 0))
        self.refresh_slider = ctk.CTkSlider(self.sidebar_frame, from_=0.5, to=5.0, number_of_steps=9,
                                          command=self.change_refresh_rate)
        self.refresh_slider.pack(padx=20, pady=(10, 0))
        self.refresh_slider.set(1.0)
        self.refresh_rate_label = ctk.CTkLabel(self.sidebar_frame, text="1.0 seconds")
        self.refresh_rate_label.pack(padx=20, pady=(5, 10))
        
        # Create button to take screenshot
        self.screenshot_button = ctk.CTkButton(self.sidebar_frame, text="Take Screenshot", command=self.take_screenshot)
        self.screenshot_button.pack(padx=20, pady=10)
        
        # Create button to process list
        self.process_button = ctk.CTkButton(self.sidebar_frame, text="Process List", command=self.open_process_window)
        self.process_button.pack(padx=20, pady=10)
        
        # Create main frame for charts
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Create resource info cards at top
        self.info_frame = ctk.CTkFrame(self.main_frame)
        self.info_frame.pack(fill="x", pady=(0, 20))
        
        # CPU info card
        self.cpu_info_frame = ctk.CTkFrame(self.info_frame)
        self.cpu_info_frame.pack(side=ctk.LEFT, fill="both", expand=True, padx=(0, 10))
        
        self.cpu_title = ctk.CTkLabel(self.cpu_info_frame, text="CPU", font=ctk.CTkFont(size=16, weight="bold"))
        self.cpu_title.pack(padx=10, pady=(10, 5))
        
        self.cpu_usage = ctk.CTkLabel(self.cpu_info_frame, text="0%", font=ctk.CTkFont(size=24))
        self.cpu_usage.pack(padx=10, pady=5)
        
        self.cpu_freq = ctk.CTkLabel(self.cpu_info_frame, text="0 MHz")
        self.cpu_freq.pack(padx=10, pady=(0, 10))
        
        # RAM info card
        self.ram_info_frame = ctk.CTkFrame(self.info_frame)
        self.ram_info_frame.pack(side=ctk.LEFT, fill="both", expand=True, padx=10)
        
        self.ram_title = ctk.CTkLabel(self.ram_info_frame, text="Memory", font=ctk.CTkFont(size=16, weight="bold"))
        self.ram_title.pack(padx=10, pady=(10, 5))
        
        self.ram_usage = ctk.CTkLabel(self.ram_info_frame, text="0%", font=ctk.CTkFont(size=24))
        self.ram_usage.pack(padx=10, pady=5)
        
        self.ram_details = ctk.CTkLabel(self.ram_info_frame, text="0/0 GB")
        self.ram_details.pack(padx=10, pady=(0, 10))
        
        # Network info card
        self.net_info_frame = ctk.CTkFrame(self.info_frame)
        self.net_info_frame.pack(side=ctk.LEFT, fill="both", expand=True, padx=(10, 0))
        
        self.net_title = ctk.CTkLabel(self.net_info_frame, text="Network", font=ctk.CTkFont(size=16, weight="bold"))
        self.net_title.pack(padx=10, pady=(10, 5))
        
        self.net_usage = ctk.CTkLabel(self.net_info_frame, text="0 KB/s", font=ctk.CTkFont(size=24))
        self.net_usage.pack(padx=10, pady=5)
        
        self.net_details = ctk.CTkLabel(self.net_info_frame, text="↑ 0 KB/s  ↓ 0 KB/s")
        self.net_details.pack(padx=10, pady=(0, 10))
        
        # Create chart frame
        self.chart_frame = ctk.CTkFrame(self.main_frame)
        self.chart_frame.pack(fill="both", expand=True)
        
        # Set up the matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 4), dpi=100)
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_color('#666666')
        self.ax.spines['left'].set_color('#666666')
        self.ax.tick_params(colors='#cccccc')
        self.ax.xaxis.label.set_color('#cccccc')
        self.ax.yaxis.label.set_color('#cccccc')
        self.ax.grid(True, linestyle='--', alpha=0.7, color='#666666')
        
        # Plot lines for CPU, RAM, and Network
        x = range(self.max_data_points)
        self.cpu_line, = self.ax.plot(x, self.cpu_history, label='CPU', linewidth=2, color='#00a2ff')
        self.ram_line, = self.ax.plot(x, self.ram_history, label='RAM', linewidth=2, color='#00ff9d')
        self.net_line, = self.ax.plot(x, self.network_history, label='Network', linewidth=2, color='#ff6e00')
        
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, self.max_data_points-1)
        self.ax.set_xticks([])
        self.ax.set_ylabel('Usage %')
        self.ax.legend(loc='upper left')
        
        # Create canvas widget
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)
        
        # Set refresh rate and start monitoring thread
        self.refresh_rate = 1.0
        self.running = True
        self.update_thread = threading.Thread(target=self.update_data)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # Update time once
        self.update_time()

    def update_data(self):
        while self.running:
            # Update CPU data
            cpu_percent = psutil.cpu_percent()
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                freq_text = f"{cpu_freq.current:.0f} MHz"
            else:
                freq_text = "N/A"
            
            # Update RAM data
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            ram_used_gb = ram.used / (1024**3)
            ram_total_gb = ram.total / (1024**3)
            
            # Update Network data
            current_net_io = psutil.net_io_counters()
            current_time = time.time()
            
            # Calculate network throughput in KB/s
            time_diff = current_time - self.prev_net_time
            recv_bytes = current_net_io.bytes_recv - self.prev_net_io.bytes_recv
            sent_bytes = current_net_io.bytes_sent - self.prev_net_io.bytes_sent
            
            recv_kb_s = (recv_bytes / time_diff) / 1024
            sent_kb_s = (sent_bytes / time_diff) / 1024
            total_kb_s = recv_kb_s + sent_kb_s
            
            # Network usage normalized to percentage (arbitrary max of 1MB/s = 100%)
            net_percent = min(100, total_kb_s / 10.24)
            
            # Update data history
            self.cpu_history.pop(0)
            self.cpu_history.append(cpu_percent)
            
            self.ram_history.pop(0)
            self.ram_history.append(ram_percent)
            
            self.network_history.pop(0)
            self.network_history.append(net_percent)
            
            self.prev_net_io = current_net_io
            self.prev_net_time = current_time
            
            # Update uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            days, remainder = divmod(int(uptime.total_seconds()), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"Uptime: {days}d {hours}h {minutes}m"
            
            # Update UI elements on main thread
            self.after(0, lambda: self.update_ui(
                cpu_percent, freq_text,
                ram_percent, ram_used_gb, ram_total_gb,
                recv_kb_s, sent_kb_s, total_kb_s,
                uptime_str
            ))
            
            # Update plot on main thread
            self.after(0, self.update_plot)
            
            # Sleep for refresh rate
            time.sleep(self.refresh_rate)
    
    def update_ui(self, cpu_percent, freq_text, ram_percent, ram_used_gb, ram_total_gb, 
                 recv_kb_s, sent_kb_s, total_kb_s, uptime_str):
        # Update CPU info
        self.cpu_usage.configure(text=f"{cpu_percent:.1f}%")
        self.cpu_freq.configure(text=freq_text)
        
        # Update RAM info
        self.ram_usage.configure(text=f"{ram_percent:.1f}%")
        self.ram_details.configure(text=f"{ram_used_gb:.1f}/{ram_total_gb:.1f} GB")
        
        # Update Network info
        # Format as MB/s if over 1000 KB/s
        if total_kb_s > 1000:
            self.net_usage.configure(text=f"{total_kb_s/1024:.2f} MB/s")
        else:
            self.net_usage.configure(text=f"{total_kb_s:.1f} KB/s")
            
        # Format send/receive details
        up_text = f"{sent_kb_s:.1f} KB/s" if sent_kb_s < 1000 else f"{sent_kb_s/1024:.2f} MB/s"
        down_text = f"{recv_kb_s:.1f} KB/s" if recv_kb_s < 1000 else f"{recv_kb_s/1024:.2f} MB/s"
        self.net_details.configure(text=f"↑ {up_text}  ↓ {down_text}")
        
        # Update uptime
        self.uptime_label.configure(text=uptime_str)
        
        # Update time
        self.update_time()
        
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.time_label.configure(text=f"{current_date}\n{current_time}")
        # Update time every second
        self.after(1000, self.update_time)
        
    def update_plot(self):
        # Update the plot data
        self.cpu_line.set_ydata(self.cpu_history)
        self.ram_line.set_ydata(self.ram_history)
        self.net_line.set_ydata(self.network_history)
        
        # Redraw the canvas
        self.canvas.draw_idle()
    
    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
        # Update plot colors based on theme
        if new_appearance_mode == "Dark" or (new_appearance_mode == "System" and ctk._get_appearance_mode() == "Dark"):
            self.fig.patch.set_facecolor('#2b2b2b')
            self.ax.set_facecolor('#2b2b2b')
            self.ax.tick_params(colors='#cccccc')
            self.ax.xaxis.label.set_color('#cccccc')
            self.ax.yaxis.label.set_color('#cccccc')
        else:
            self.fig.patch.set_facecolor('#f0f0f0')
            self.ax.set_facecolor('#f0f0f0')
            self.ax.tick_params(colors='#333333')
            self.ax.xaxis.label.set_color('#333333')
            self.ax.yaxis.label.set_color('#333333')
        self.canvas.draw_idle()
        
    def change_refresh_rate(self, value):
        self.refresh_rate = value
        self.refresh_rate_label.configure(text=f"{value:.1f} seconds")
    
    def take_screenshot(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sysmonitor_screenshot_{timestamp}.png"
        self.attributes('-topmost', 1)  # Bring window to front
        self.update()
        self.attributes('-topmost', 0)
        
        # Wait a moment for window to be fully visible
        time.sleep(0.5)
        
        try:
            # Take screenshot using scrot on Linux
            subprocess.run(['scrot', '-u', filename])
            
            # Show notification
            notification = ctk.CTkToplevel(self)
            notification.geometry("300x100")
            notification.title("Screenshot Taken")
            
            label = ctk.CTkLabel(notification, text=f"Screenshot saved as:\n{filename}")
            label.pack(padx=20, pady=20)
            
            # Auto-close notification after 3 seconds
            notification.after(3000, notification.destroy)
            
        except Exception as e:
            # Show error notification
            notification = ctk.CTkToplevel(self)
            notification.geometry("300x100")
            notification.title("Error")
            
            label = ctk.CTkLabel(notification, text=f"Error taking screenshot:\n{str(e)}")
            label.pack(padx=20, pady=20)
            
            notification.after(3000, notification.destroy)
    
    def open_process_window(self):
        # Create new window for process list
        process_window = ctk.CTkToplevel(self)
        process_window.geometry("800x600")
        process_window.title("Process List")
        
        # Create header frame
        header_frame = ctk.CTkFrame(process_window)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        # Create search box
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(header_frame, placeholder_text="Search processes...", width=200, textvariable=search_var)
        search_entry.pack(side="left", padx=(0, 10))
        
        # Create sort options
        sort_label = ctk.CTkLabel(header_frame, text="Sort by:")
        sort_label.pack(side="left", padx=(10, 5))
        
        sort_var = ctk.StringVar(value="CPU")
        sort_menu = ctk.CTkOptionMenu(header_frame, values=["CPU", "Memory", "Name"], variable=sort_var)
        sort_menu.pack(side="left", padx=5)
        
        # Create refresh button
        refresh_button = ctk.CTkButton(header_frame, text="Refresh", width=100)
        refresh_button.pack(side="right", padx=10)
        
        # Create process table
        table_frame = ctk.CTkFrame(process_window)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create table headers
        header_frame = ctk.CTkFrame(table_frame)
        header_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(header_frame, text="PID", width=80).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Name", width=200).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="CPU %", width=80).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Memory %", width=80).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Status", width=100).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Actions", width=100).pack(side="left", padx=5, pady=5)
        
        # Create scrollable frame for process list
        processes_frame = ctk.CTkScrollableFrame(table_frame)
        processes_frame.pack(fill="both", expand=True)
        
        # Function to populate process list
        def populate_processes():
            # Clear existing processes
            for widget in processes_frame.winfo_children():
                widget.destroy()
                
            # Get search term
            search_term = search_var.get().lower()
            
            # Get sort method
            sort_method = sort_var.get()
            
            # Get processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    process_info = proc.info
                    if search_term and search_term not in process_info['name'].lower():
                        continue
                    processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort processes
            if sort_method == "CPU":
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            elif sort_method == "Memory":
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            elif sort_method == "Name":
                processes.sort(key=lambda x: x['name'].lower())
            
            # Display processes
            for proc in processes[:100]:  # Limit to 100 processes for performance
                process_frame = ctk.CTkFrame(processes_frame)
                process_frame.pack(fill="x", pady=2)
                
                ctk.CTkLabel(process_frame, text=str(proc['pid']), width=80).pack(side="left", padx=5, pady=5)
                ctk.CTkLabel(process_frame, text=proc['name'], width=200).pack(side="left", padx=5, pady=5)
                ctk.CTkLabel(process_frame, text=f"{proc['cpu_percent']:.1f}%", width=80).pack(side="left", padx=5, pady=5)
                ctk.CTkLabel(process_frame, text=f"{proc['memory_percent']:.1f}%", width=80).pack(side="left", padx=5, pady=5)
                ctk.CTkLabel(process_frame, text=proc['status'], width=100).pack(side="left", padx=5, pady=5)
                
                action_frame = ctk.CTkFrame(process_frame, fg_color="transparent")
                action_frame.pack(side="left", padx=5, pady=5, fill="x", expand=True)
                
                # Create end process button
                end_button = ctk.CTkButton(action_frame, text="End", width=80, 
                                         command=lambda pid=proc['pid']: end_process(pid))
                end_button.pack(side="left", padx=5)
        
        # Function to end a process
        def end_process(pid):
            try:
                process = psutil.Process(pid)
                process.terminate()
                # Refresh the list after a short delay
                process_window.after(500, populate_processes)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Show error message
                error_window = ctk.CTkToplevel(process_window)
                error_window.geometry("300x100")
                error_window.title("Error")
                
                label = ctk.CTkLabel(error_window, text="Cannot terminate process.\nAccess denied or process not found.")
                label.pack(padx=20, pady=20)
                
                error_window.after(3000, error_window.destroy)
        
        # Initial population
        populate_processes()
        
        # Bind refresh button
        refresh_button.configure(command=populate_processes)
        
        # Bind search and sort events
        search_var.trace_add("write", lambda *args: process_window.after(500, populate_processes))
        sort_var.trace_add("write", lambda *args: populate_processes())
    
    def on_closing(self):
        self.running = False
        # Wait for thread to finish
        if self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
        self.destroy()

if __name__ == "__main__":
    # Check if required packages are installed
    required_packages = ['psutil', 'customtkinter', 'matplotlib']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages. Installing...")
        for package in missing_packages:
            try:
                subprocess.check_call(['pip', 'install', package])
                print(f"Installed {package}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}. Please install it manually.")
                exit(1)
        
        print("All packages installed. Restarting application...")
        os.execv(sys.executable, ['python'] + sys.argv)
    
    app = SystemMonitor()
    app.mainloop()
