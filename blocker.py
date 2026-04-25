import serial
import os
import time
import subprocess
import tkinter as tk
from tkinter import font
from threading import Thread
import re

# ==========================================
# ⚙️ CONFIGURARE GENERALĂ
# ==========================================
SERIAL_PORT = '/dev/ttyACM0' 
IFACE = "wlp0s20f3" 
MAX_RELAPSES = 20 # <--- MODIFICAT DE LA 5 LA 20 (Fără alte schimbări)

# 🌟 BAZA DE DATE LOCALĂ
KNOWN_DEVICES = {
    "7e:73:c0:8d:ef:9b": "📱 iPhone-ul lui Sol",
    "be:93:44:9a:fc:71": "📱 Telefon Juriu"
}

# 🎯 SEMNĂTURILE APLICAȚIILOR
APP_SIGNATURES = {
    "TikTok": ["tiktok", "byteoversea", "tiktokcdn", "musical.ly"],
    "YouTube": ["youtube", "googlevideo", "ytimg"],
    "Instagram": ["instagram", "cdninstagram", "fbcdn", "graph.facebook", "fna.fbcdn", "scontent", "video-"]
}

# 💥 ARTILERIA GREA PENTRU META
META_SUBNETS = [
    "31.13.0.0/16", "69.63.176.0/20", "74.119.76.0/22", "103.4.96.0/22",
    "129.134.0.0/16", "157.240.0.0/16", "173.252.0.0/16", "185.60.216.0/22"
]

# --- PALETĂ DE CULORI PRO ---
BG_MAIN = "#0B0C10"       
BG_PANEL = "#1F2833"      
FG_TEXT = "#C5C6C7"       
ACCENT_CYAN = "#66FCF1"   
SAFE_GREEN = "#45A29E"    
DANGER_RED = "#FF2A2A"    
LOCKDOWN_BG = "#1A0000"   

# ==========================================
# 🌐 LOGICA DE REȚEA (MULTI-DEVICE ROUTER SMART)
# ==========================================
def apply_network_rules(all_device_settings):
    print(f"💥 THROTTLE INIT: MULTI-DEVICE MODE")
    
    # 1. CURĂȚARE TOTALĂ
    os.system(f'sudo tc qdisc del dev {IFACE} root 2>/dev/null')
    os.system('sudo iptables -t mangle -F FORWARD 2>/dev/null')
    os.system('sudo iptables -F FORWARD 2>/dev/null')

    os.system('sudo ip6tables -F FORWARD 2>/dev/null')
    os.system('sudo ip6tables -P FORWARD DROP 2>/dev/null')

    print("🌊 SHOCKWAVE ACTIVE...")
    os.system('sudo iptables -I FORWARD 1 -j REJECT')
    time.sleep(1)
    os.system('sudo iptables -D FORWARD 1')

    # 2. CREĂM RĂDĂCINA
    os.system(f'sudo tc qdisc add dev {IFACE} root handle 1: htb default 10')
    os.system(f'sudo tc class add dev {IFACE} parent 1: classid 1:10 htb rate 1000mbit') 
    
    os.system('sudo iptables -t mangle -A FORWARD -j CONNMARK --restore-mark')

    # --- 🧠 LOGICA INTELIGENTĂ DE SELECTARE A DEVICE-URILOR ---
    active_ips = [ip for ip, config in all_device_settings.items() if any(config["apps"].values())]
    
    if len(active_ips) > 1 and "ALL" in active_ips:
        active_ips.remove("ALL")
        print("⚠️ 'ALL DEVICES' dezactivat automat pentru că ai setări pe telefoane specifice.")

    # 3. CONSTRUIM TUNELE
    mark_counter = 20 

    for ip in active_ips:
        config = all_device_settings[ip]
        latency = config["latency"]
        active_apps = config["apps"]

        target_rule = f"-s {ip}" if ip != "ALL" else ""
        target_rule_dst = f"-d {ip}" if ip != "ALL" else ""

        class_id = f"1:{mark_counter}"
        os.system(f'sudo tc class add dev {IFACE} parent 1: classid {class_id} htb rate 5kbit ceil 8kbit') 
        os.system(f'sudo tc qdisc add dev {IFACE} parent {class_id} handle {mark_counter}: netem delay {latency}ms 500ms')
        os.system(f'sudo tc filter add dev {IFACE} protocol ip parent 1: prio 1 handle {mark_counter} fw flowid {class_id}')

        for app_name, is_active in active_apps.items():
            if is_active:
                for sig in APP_SIGNATURES[app_name]:
                    os.system(f'sudo iptables -t mangle -A FORWARD {target_rule} -m string --string "{sig}" --algo bm -j MARK --set-mark {mark_counter}')
                    os.system(f'sudo iptables -t mangle -A FORWARD {target_rule_dst} -m string --string "{sig}" --algo bm -j MARK --set-mark {mark_counter}')
                
                if app_name == "Instagram":
                    for subnet in META_SUBNETS:
                        os.system(f'sudo iptables -A FORWARD {target_rule} -d {subnet} -p udp --dport 443 -j DROP')
                        os.system(f'sudo iptables -t mangle -A FORWARD {target_rule} -d {subnet} -j MARK --set-mark {mark_counter}')
                        os.system(f'sudo iptables -t mangle -A FORWARD {target_rule_dst} -s {subnet} -j MARK --set-mark {mark_counter}')

        mark_counter += 1 

    os.system('sudo iptables -t mangle -A FORWARD -m mark ! --mark 0 -j CONNMARK --save-mark')

def remove_network_rules():
    print("🚀 SYSTEM RESTORED - ALL RULES CLEARED")
    os.system(f'sudo tc qdisc del dev {IFACE} root 2>/dev/null')
    os.system('sudo iptables -t mangle -F FORWARD 2>/dev/null')
    os.system('sudo iptables -F FORWARD 2>/dev/null')
    os.system('sudo ip6tables -P FORWARD ACCEPT 2>/dev/null')

# ==========================================
# 🖥️ INTERFAȚA GRAFICĂ & MEMORIA
# ==========================================
class DopamineGuardPro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dopamine Trap")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=BG_MAIN)

        self.is_blocked = False
        self.lockdown = False
        self.saved_seconds = 0
        self.relapse_count = 0
        
        self.default_apps = {"TikTok": False, "YouTube": False, "Instagram": False}
        self.device_settings = {
            "ALL": {"latency": 13000, "apps": self.default_apps.copy()}
        }

        self.font_title = font.Font(family="Segoe UI", size=60, weight="bold")
        self.font_subtitle = font.Font(family="Consolas", size=22)
        self.font_panel = font.Font(family="Segoe UI", size=14)

        self.left_frame = tk.Frame(self.root, bg=BG_MAIN)
        self.left_frame.pack(side="left", expand=True, fill="both", padx=40, pady=40)

        self.right_frame = tk.Frame(self.root, bg=BG_PANEL, width=450, bd=0)
        self.right_frame.pack(side="right", fill="y")

        self.target_display = tk.Label(self.left_frame, text="TARGET: ALL DEVICES", font=self.font_panel, fg=ACCENT_CYAN, bg=BG_MAIN)
        self.target_display.pack(anchor="nw", pady=(0, 20))

        self.status_label = tk.Label(self.left_frame, text="SYSTEM SAFE", font=self.font_title, fg=SAFE_GREEN, bg=BG_MAIN)
        self.status_label.pack(expand=True)
        
        self.relapse_label = tk.Label(self.left_frame, text=self.get_relapse_dots(), font=("Segoe UI", 30), fg="white", bg=BG_MAIN)
        self.relapse_label.pack(pady=10)

        self.stats_label = tk.Label(self.left_frame, text="Focus Time: 0s", font=self.font_subtitle, fg=FG_TEXT, bg=BG_MAIN)
        self.stats_label.pack(pady=10)

        self.info_label = tk.Label(self.left_frame, text="PRESS [SPACE] OR BUTTON TO INITIATE", font=("Segoe UI", 12), fg="#666666", bg=BG_MAIN)
        self.info_label.pack(side="bottom", pady=20)

        panel_inner = tk.Frame(self.right_frame, bg=BG_PANEL, padx=30, pady=40)
        panel_inner.pack(fill="both", expand=True)

        tk.Label(panel_inner, text="CONTROL CENTER", font=("Segoe UI", 18, "bold"), fg="white", bg=BG_PANEL).pack(pady=(0, 20))
        
        tk.Label(panel_inner, text="1. Select Target Device", font=self.font_panel, fg=FG_TEXT, bg=BG_PANEL).pack(anchor="w", pady=(0, 5))
        self.device_listbox = tk.Listbox(panel_inner, height=5, bg="#141A21", fg="white", font=("Consolas", 11), selectbackground=ACCENT_CYAN, selectforeground="black", relief="flat", borderwidth=0)
        self.device_listbox.pack(fill="x", pady=5)
        self.device_listbox.insert(tk.END, "ALL DEVICES (Default)")
        self.device_listbox.selection_set(0)
        self.device_listbox.bind('<<ListboxSelect>>', self.on_device_select)

        tk.Button(panel_inner, text="SCAN NETWORK", command=self.scan_network, bg=ACCENT_CYAN, fg="black", font=("Segoe UI", 10, "bold"), relief="flat").pack(fill="x", pady=10)

        tk.Label(panel_inner, text="2. Select Apps to Throttle", font=self.font_panel, fg=FG_TEXT, bg=BG_PANEL).pack(anchor="w", pady=(20, 5))
        
        self.app_vars = {}
        apps_frame = tk.Frame(panel_inner, bg=BG_PANEL)
        apps_frame.pack(fill="x", pady=5)
        
        for app in APP_SIGNATURES.keys():
            var = tk.BooleanVar(value=False)
            self.app_vars[app] = var
            chk = tk.Checkbutton(apps_frame, text=app, variable=var, command=self.save_current_settings, bg=BG_PANEL, fg="white", selectcolor="#141A21", activebackground=BG_PANEL, activeforeground=ACCENT_CYAN, font=("Segoe UI", 11))
            chk.pack(side="left", padx=10)

        tk.Label(panel_inner, text="3. Set Torture Level (ms)", font=self.font_panel, fg=FG_TEXT, bg=BG_PANEL).pack(anchor="w", pady=(20, 5))
        self.latency_slider = tk.Scale(panel_inner, from_=1000, to_=20000, orient="horizontal", bg=BG_PANEL, fg=ACCENT_CYAN, font=("Consolas", 10), resolution=1000, command=lambda v: self.save_current_settings(), troughcolor="#141A21", highlightthickness=0, bd=0)
        self.latency_slider.set(13000)
        self.latency_slider.pack(fill="x", pady=5)

        # --- BINDING PENTRU SPACE ---
        self.root.bind("<space>", self.on_space_pressed)

        Thread(target=self.monitor_serial, daemon=True).start()
        self.root.bind("<Escape>", self.exit_gracefully)
        self.update_clock()

    def on_space_pressed(self, event):
        if not self.is_blocked:
            self.simulate_arduino_signal("BLOCK")
        else:
            self.simulate_arduino_signal("FREE")

    def simulate_arduino_signal(self, signal):
        if signal == "BLOCK" and not self.is_blocked:
            self.is_blocked = True
            self.relapse_count += 1
            self.relapse_label.config(text=self.get_relapse_dots())
            if self.relapse_count >= MAX_RELAPSES:
                self.root.after(0, lambda: self.trigger_lockdown(self.device_settings))
            else:
                apply_network_rules(self.device_settings)
                self.root.after(0, lambda: self.ui_to_block())
        elif signal == "FREE" and self.is_blocked and not self.lockdown:
            self.is_blocked = False
            remove_network_rules()
            self.root.after(0, self.ui_to_safe)

    def get_relapse_dots(self):
        return "🔴" * self.relapse_count + "⚪" * (MAX_RELAPSES - self.relapse_count)

    def update_clock(self):
        if self.is_blocked and not self.lockdown:
            self.saved_seconds += 1
            self.stats_label.config(text=f"Focus Time: {self.saved_seconds}s")
        self.root.after(1000, self.update_clock)

    def get_selected_ip(self):
        selection = self.device_listbox.curselection()
        if not selection or selection[0] == 0:
            return "ALL"
        value = self.device_listbox.get(selection[0])
        match = re.search(r'\[(.*?)\]', value)
        if match: return match.group(1)
        return "ALL"

    def save_current_settings(self):
        ip = self.get_selected_ip()
        if ip not in self.device_settings:
            self.device_settings[ip] = {"latency": 13000, "apps": self.default_apps.copy()}
        
        self.device_settings[ip]["latency"] = int(self.latency_slider.get())
        for app, var in self.app_vars.items():
            self.device_settings[ip]["apps"][app] = var.get()

    def on_device_select(self, event):
        ip = self.get_selected_ip()
        if ip not in self.device_settings:
            self.device_settings[ip] = {"latency": 13000, "apps": self.default_apps.copy()}
            
        settings = self.device_settings[ip]
        self.latency_slider.set(settings["latency"])
        
        for app, var in self.app_vars.items():
            var.set(settings["apps"][app])
        
        selection = self.device_listbox.curselection()
        if selection:
            self.target_display.config(text=f"TARGET: {self.device_listbox.get(selection[0])}")

    def scan_network(self):
        self.device_listbox.delete(1, tk.END)
        try:
            output = subprocess.check_output(['ip', 'neigh', 'show', 'dev', IFACE]).decode('utf-8')
            for line in output.split('\n'):
                if "lladdr" in line:
                    parts = line.split()
                    ip = parts[0]
                    mac_idx = parts.index("lladdr") + 1
                    mac = parts[mac_idx]
                    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip) or ip.endswith(".1"): continue
                    display_name = KNOWN_DEVICES.get(mac, f"Device_{mac[-5:]}")
                    self.device_listbox.insert(tk.END, f"{display_name} [{ip}]")
        except Exception as e:
            print(f"Eroare Scanare: {e}")

    def exit_gracefully(self, event=None):
        remove_network_rules()
        self.root.destroy()

    def monitor_serial(self):
        try:
            ser = serial.Serial(SERIAL_PORT, 9600, timeout=1)
            remove_network_rules()
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    self.simulate_arduino_signal(line)
                time.sleep(0.01)
        except Exception as e:
            print(f"Eroare Serial: {e}")

    def ui_to_block(self):
        self.root.configure(bg=LOCKDOWN_BG)
        self.left_frame.configure(bg=LOCKDOWN_BG)
        self.status_label.config(text="MULTI-DEVICE THROTTLE", fg=DANGER_RED, bg=LOCKDOWN_BG)
        self.info_label.config(text="APPLYING RULES - PRESS [SPACE] TO STOP", fg=ACCENT_CYAN, bg=LOCKDOWN_BG)

    def ui_to_safe(self):
        self.root.configure(bg=BG_MAIN)
        self.left_frame.configure(bg=BG_MAIN)
        self.status_label.config(text="SYSTEM SAFE", fg=SAFE_GREEN, bg=BG_MAIN)
        self.info_label.config(text="PRESS [SPACE] OR BUTTON TO INITIATE", fg="#666666", bg=BG_MAIN)

    def trigger_lockdown(self, all_device_settings):
        self.lockdown = True
        apply_network_rules(all_device_settings)
        self.root.configure(bg=LOCKDOWN_BG)
        self.status_label.config(text="SYSTEM LOCKED", fg=DANGER_RED)

if __name__ == "__main__":
    app = DopamineGuardPro()
    app.root.mainloop()