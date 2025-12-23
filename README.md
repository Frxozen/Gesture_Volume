# Gesture_Volume
A real-time hand gesture control system that lets you adjust PC volume and play/pause media using just your webcam. Built with Python, OpenCV, and MediaPipe.

### **✨ Features**
* **Right Hand (Volume):**
    * **Pinky Up:** 🟢 **Active mode.** Pinch thumb & index finger to change volume.
    * **Pinky Down:** 🔴 **Locked mode.** Volume stays fixed so you can relax your hand.
* **Left Hand (Media):**
    * **Open Hand:** ⏯️ **Play/Pause.** Toggles video or music (YouTube, Spotify, etc.).
* **Camera Switching:** Press `C` to cycle through available cameras.
* **Smooth Motion:** Uses mathematical smoothing to prevent volume "jitter."

---

### **🛠️ Installation Guide**

**1. Prerequisites**
* You need **Python** installed on your computer. [Download Here](https://www.python.org/downloads/)
* A webcam.

**2. Setup (The Easy Way)**
It is recommended to use a "Virtual Environment" to avoid conflicts. Open your terminal (PowerShell or CMD) in the project folder and run these commands one by one:

**Step 1: Create the environment**
```powershell
python -m venv venv
