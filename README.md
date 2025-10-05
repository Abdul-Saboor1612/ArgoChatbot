# 🌊 ArgoChatbot

**ArgoChatbot** is an intelligent Streamlit-based chatbot designed to help users interact with **Argo float data** — including exploring temperature, salinity, pressure profiles, trajectories, and comparisons between floats.  
It combines **oceanographic data visualization** with **AI-driven explanations**, allowing students, researchers, and enthusiasts to better understand the role and importance of Argo data in climate and ocean studies.

---

## 🌍 What is Argo?

**Argo** is an international program that uses a global array of **autonomous floats** to collect real-time data on the **temperature, salinity, and pressure** of the upper 2000 meters of the ocean.  
There are over **3,000+ floats** worldwide continuously transmitting vital ocean data used in:

- 🌡️ **Climate research** (tracking ocean heat content)  
- 🌊 **Weather forecasting** (improving models of ocean–atmosphere interaction)  
- 🧭 **Marine studies** (understanding salinity, circulation, and density variations)

You can learn more about the official Argo program here: [https://argo.ucsd.edu/](https://argo.ucsd.edu/)

---

## 🤖 About ArgoChatbot

ArgoChatbot makes Argo data **accessible and interactive** through a conversational interface.  
Instead of manually searching datasets, users can **ask questions in natural language** like:

> - “Show me the temperature and salinity profiles for float 2903989.”  
> - “Compare float 2903893 and 2903892.”  
> - “Why are temperature and salinity important in ocean studies?”  
> - “Why is Argo data used for climate research?”

The chatbot fetches, visualizes, and explains — combining data science, oceanography, and natural language understanding in one platform.

---

## 🧩 Repository Structure

| File / Module | Description |
|----------------|--------------|
| `app.py` | Main Streamlit app — manages UI, chatbot logic, and data interactions |
| `floats.py` | Stores metadata about Indian floats (IDs, launch dates, cycles, etc.) |
| `visualizations.py` | Handles plotting of float profiles, trajectories, and comparisons |
| `nlp.py` | Natural language understanding for chatbot queries |
| `requirements.txt` | List of required Python packages |
| `data/` | (Optional) Folder for storing cached or sample float data |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or later  
- [Streamlit](https://streamlit.io/)  
- [argopy](https://argopy.readthedocs.io/en/latest/)  

### Installation

```bash
# Clone this repository
git clone https://github.com/Abdul-Saboor1612/ArgoChatbot.git
cd ArgoChatbot

# Install dependencies
pip install -r requirements.txt
