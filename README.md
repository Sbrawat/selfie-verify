> **Note:** This repository represents the Version 1 prototype. The project has since been decoupled into a microservice architecture.
> Please visit the active repositories:
>
> - **Backend API:** [Link to your future API repo]:
>   The containerized FastAPI backend and identity database.
> - **Frontend Demo:** [Link to your future Demo repo]:
>   he Streamlit FinTech frontend client demonstrating Step-Up Authentication.

_Archived code including Version 1 and initial experiments are preserved here for historical context._

# Selfie Verification for Account Authenticity Version 1

A Computer Vision-based security pipeline featuring Liveness Detection and Facial Matching.

## 📌 Project Overview

This project addresses the vulnerability of standard facial recognition systems to "presentation attacks" (spoofing). It implements a two-step verification process:

1. **Liveness Detection:** Monitors eye-blink patterns to ensure a physical presence.
2. **Facial Verification:** Compares 128-d facial embeddings against a registered profile.

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Libraries:** OpenCV, MediaPipe, Face_Recognition, Streamlit
- **Algorithm:** HOG (Histogram of Oriented Gradients) & Deep Learning Embeddings

## 🚀 Getting Started

1. **Clone the repo:** `git clone https://github.com/Sbrawat/selfie-verify.git`
2. **Create Virtual Env:** `python -m venv venv`
3. **Activate:** `source venv/bin/activate` (or `.\venv\Scripts\activate` on Windows)
4. **Install Dependencies:** `pip install -r requirements.txt`

## 📊 Methodology

- **Blink Detection:** Using EAR (Eye Aspect Ratio) via MediaPipe landmarks.
- **Matching:** Euclidean distance calculation between face encodings.

## 📝 Research Component

This project includes a research paper detailing:

- False Acceptance Rate (FAR) vs. False Rejection Rate (FRR)
- Effectiveness against high-resolution screen replays vs. print attacks.
