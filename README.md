# forward-array
A local crypto market data pipeline and PnL tracker.  
Built with Python to fetch, store, and analyze real-time price data locally.

---

## 🌱 About Me
Hello, I’m **Joshua Berry** — an aspiring backend/automation developer focused on:

- Automation & data operations  
- Building real, working systems (not toy examples)  
- Learning in public and improving one project at a time  

I work full-time outdoors in the Florida heat and spend my evenings developing tools like Forward Array.  
Consistency, discipline, and doing the boring parts well — that’s what I bring to every build.

---

## 🚀 What Forward Array Does
Forward Array currently handles:

- Scheduled price polling (local data pull & persistence)  
- Updating positions / gains using latest prices  
- Computing portfolio-level metrics (PnL and related stats)  
- Maintaining a local log so everything works offline  
- Forming the backbone for a larger automation system  

This project will continue to evolve as I learn more about Python, systems design, and backend automation.

---

## 📂 Project Structure
```text
forward-array/
├── main.py                        # Orchestrates the pipeline (entry point)
├── price_poller.py                # Fetches and logs latest market prices
├── update_gains_from_positions.py # Computes gains using latest price data
├── README.md                      # You are here
└── .gitattributes                 # Repo settings
