# GearsMap

**GearsMap** is a lightweight terminal-based system monitoring tool for Linux systems, built with Python. It provides real-time insights into CPU usage, RAM consumption, and network activity in a clean and minimal interface.

---

## Features

- **Live CPU Usage**  
  Displays current CPU usage percentage for all cores.

- **RAM Monitoring**  
  Shows total, used, and available memory in real-time.

- **Network Activity**  
  Monitors upload and download speeds for active interfaces.

- **Terminal UI**  
  Simple and clear interface that works directly in the terminal.

---

## Screenshot

*(You can add a screenshot here in the future)*

```bash
[ CPU: 23% ] [ RAM: 2.4GB / 8GB ] [ Net: ↑ 10KB/s ↓ 52KB/s ]


---

Requirements

Python 3.x

Linux OS

Modules:

psutil

time

os

platform



Install required modules using pip:

pip install psutil


---

How to Run

Simply run the script using:

python3 gearsmap.py

You may need to give it executable permissions:

chmod +x gearsmap.py


---

Use Cases

Monitor system load on older devices

Lightweight alternative to tools like htop

Integrate with custom Linux terminals or minimal setups



---

License

This project is licensed under the MIT License – see the LICENSE file for details.


---

Copyright

© 2025 Sajjad Moh. All rights reserved.
This software is distributed under the MIT License. You are free to use, modify, and distribute it, provided you include proper attribution.


---

Disclaimer

This software is provided "as is", without warranty of any kind, express or implied. The author is not liable for any damages or losses resulting from the use or misuse of this tool.
Use at your own risk.


---

Contributions

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


---

Author

Sajjad Moh.
Built with passion for Linux users who love terminal tools.
