# 🧠 Logic Document: Dynamic Intensity Calibration (Beginner's Guide)
**Author:** Amushka Choudhary, Anushka Chatterjee, Ankita Basak.  
**Role:** CV Beginner / IoT Hobbyist  
**Project:** GreenGuard Smart Campus

---

## 1. The Problem: "Why 80.0 isn't enough?"
When we first started, we used a hardcoded threshold of `80.0` for brightness. But we found two big problems:
1. **Camera A** (an old webcam) sees the room as darker than **Camera B** (a new laptop cam).
2. **Room 402** has a big window, while **Room 405** is a dark interior lab. 

We need a way to tell the AI: *"Hey, this is what 'Dark' looks like here, and anything much brighter than this means the light is ON."*

---

## 2. The Algorithm: Baseline + Variance
We developed a 3-step logic to normalize detection across any room.

### Step A: Baseline Sampling (`I_base`)
We capture a 30-frame average of the pixel intensity when we know the room should be dark.
- **Formula:** `I_base = Σ(Mean_Intensity_per_Frame) / 30`
- **Result:** This becomes our "Zero Point" for this specific camera/room combo.

### Step B: The Dynamic Threshold (`T_dynamic`)
Instead of a fixed number, our threshold is relative to the baseline. We added a "Confidence Buffer" (α) to ignore small shifts like moving shadows or computer screens.
- **Formula:** `T_dynamic = I_base + α`
- **Standard α:** We found through trial and error that `30.0` units work best.

### Step C: Normalization for Hardware Variance
Different cameras have different **ISO/Exposure** settings. We use Mini-Max Normalization to scale our readings to a standard range (0.0 to 1.0) before passing them to the Logic Engine.
- **Normalized Intensity:** `I_norm = (I_current - I_base) / (255 - I_base)`

---

## 3. Implementation Workflow (How it runs)
1. **Initialize:** Camera starts up.
2. **Trigger Calibration:** The student/admin clicks the **"Calibrate Intensity"** button on the dashboard when the room is empty and lights are off.
3. **Capture:** The system stores `I_base` in the SQLite database for that specific `room_id`.
4. **Monitor:** 
   - Every frame, we calculate `I_current`.
   - If `I_current > T_dynamic`, we mark `Light: ON`.
   - The Logic Engine checks if `person_count == 0`.
   - **Alert!** If `Light: ON` AND `person_count == 0`, we log a wastage event.

---

## 4. Addressing "Sleeping" & Edge Cases
- **The "Monitor Glow" Case:** Computer screens can be bright. By setting our baseline when screens are off, we ensure the system doesn't get tricked by a single laptop left open.
- **The "Cloudy Day" Shift:** If the sun goes behind a cloud, the `I_base` might drop slightly. In the future, we want to implement a **Rolling Baseline** that updates every hour to account for natural light changes.

---
> [!NOTE]
> This algorithm was developed as a learning exercise for our First Year Capstone. We are using OpenCV's `cv2.cvtColor` and `numpy.mean` to keep the code simple and readable!
