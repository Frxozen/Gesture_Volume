![unnamed (3)](https://github.com/user-attachments/assets/7c8f9ea7-fe07-4e73-8c6e-bce10b105326)# Gesture_Volume
A real-time hand gesture control system that lets you adjust PC volume and play/pause media using just your webcam. Built with Python, OpenCV, and MediaPipe.

![unnamed (3)](https://github.com/user-attachments/assets/f6ad527a-08c5-4986-a892-056cdccb8867)
<img width="2816" height="1536" alt="volume" src="https://github.com/user-attachments/assets/d7451dd4-0e62-4a75-b410-5274dd7ad0de" />

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

```

**Step 2: Activate it**

```powershell
.\venv\Scripts\activate

```

*(If you see a red error, run this command first: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)*

**Step 3: Install libraries**
Copy and paste this exact command to get the correct versions:

```powershell
pip install "numpy<2" "mediapipe==0.10.9" "protobuf==3.20.3" "pycaw==20181226" opencv-python comtypes

```

---

### **🚀 How to Run**

Once installed, just run:

```powershell
python gesture_volume.py

```

### **🎮 Controls Summary**

| Hand | Gesture | Action |
| --- | --- | --- |
| **Right** | **Pinky Extended (Up)** | **Unlock Volume Control** (Pinch to adjust) |
| **Right** | **Pinky Curled (Down)** | **Lock Volume** (Safe to move hand away) |
| **Left** | **Open Palm (5 Fingers)** | **Play / Pause Media** |
| **Keyboard** | **'C' Key** | **Switch Camera** |
| **Keyboard** | **'Q' Key** | **Quit App** |

### **❓ Troubleshooting**

* **Error: "Module not found"**
* Make sure you ran `.\venv\Scripts\activate` before running the python script. You should see `(venv)` at the start of your terminal line.


* **Camera not working?**
* Press **'C'** on your keyboard to switch to a different camera input.
* Make sure Zoom/Teams isn't using the camera.


* **Volume not reaching 100%?**
* Move your hand slightly further from the camera, or adjust `MAX_DIST_PIXELS` in the code (Line 14) to a lower number (e.g., 150).
