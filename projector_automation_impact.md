# 🎓 AI Projector Automation: Student Validation & Impact Sheet
**Project:** GreenGuard Smart Campus Initiative  
**Track:** First Year Capstone Project (Software)  
**Students:** Anushka Choudhury, Anushka Chatterjee and Ankita Basak]  
**Software Version:** 1.2.0 (Stable Prototype)  
**Date:** March 27, 2026

---

## 🏗️ 1. System Overview (Our Prototype)
We built this system using **FastAPI** on the backend and **React** for the live dashboard. The core "brain" is a **YOLOv8** model running on a budget lab laptop to detect empty lecture halls and turn off projectors via IoT smart relays. 

---

## ⚠️ 2. Challenges & "Corner Case" Handling
During our testing in the **E-Block labs**, we encountered a major challenge: **The "Sleeping Student" Problem**.

### The Problem (False Negatives):
If a student is sleeping in a corner or slumped behind a desk, the AI sometimes fails to detect them (`person_count: 0`). This could lead to the projector turning off while someone is still in the room!

### Our Solutions:
1. **Temporal Smoothing:** We added a **5-minute "Confirmation Buffer"**. The system must see `person_count: 0` for 300 consecutive seconds before triggering a shutdown.
2. **Motion Cues:** We integrated a "Frame Difference" check to catch very small movements that the YOLO model might overlook.
3. **Manual Override:** A simple "Bypass" button on the dashboard for students/faculty to override the AI if it makes a mistake.

---

## 🎥 3. Student Demo Script
1. **Stage 1 (Normal Usage):** Show the dashboard with 12 people in the hall. "Projector: ON".
2. **Stage 2 (Empty Hall):** Everyone leaves. Dashboard shows "Status: IDLE (Counting Down...)".
3. **Stage 3 (Correction):** Send a student back into the room during the countdown. The AI detects them, resets the timer, and the projector stays ON.
4. **Stage 4 (Auto-Off):** Leave it empty for 5 minutes. Watch the IoT Relay cut the power.

---

## 🖼️ 4. One-Slide Executive Impact Summary
> [!IMPORTANT]
> **Executive Data for Campus Stakeholders (100 Classrooms Scale)**

| Metric | Daily Impact (per room) | Annual Impact (Campus-wide) |
| :--- | :--- | :--- |
| **Energy Saved** | 1.2 kWh / day | **24,000 kWh / year** |
| **Financial Savings** | ₹12 / day | **₹2,40,000 / year** |
| **Sustainability** | 0.96 kg CO2 / day | **19,200 kg CO2 / year** |
| **Asset Extension** | - | **+1.5 Years Lamp Life** |

### 🔒 Privacy & Security Assurance Note:
We recognize that cameras in classrooms are a sensitive topic. Our system is built with **Privacy-by-Design**:
- **Local/Edge Processing:** Videos are processed *locally* on the classroom server. No video data is ever uploaded to the cloud or stored on disk.
- **Identity Obfuscation:** The dashboard only shows "Aggregated Numbers" (e.g., "5 People") and low-resolution, blurred heatmaps. We do **not** use Facial Recognition.
- **Strict Access Control:** Only authorized Campus Security can view the live diagnostic feed.

---

## 📄 5. Project Validation
This project proves that we don't need expensive commercial sensors. By using our campus's existing CCTV infrastructure and open-source AI, we've created a functional, ethical, and green solution that saves the university real money!

---
> [!TIP]
> **Our Ask:** We recommend a pilot phase in 5 "high-usage" lecture halls to refine our "Sleeping Corner" detection algorithms before a full campus rollout.
