VeggieChain – Farm-to-Market Supply Chain Simulator

VeggieChain is an interactive Streamlit-based simulation game that teaches the fundamentals of supply chain management using a simple farm-to-market vegetable flow. Players make daily decisions about planting, shipping, pricing, and demand — and see how those decisions affect inventory levels, spoilage, revenue, and cumulative profit.

This project is built for students, beginners, and anyone who wants a hands-on, visual introduction to supply chain thinking.

Live App

Play VeggieChain here:
https://veggiechain-79rnm2tmqkmyuzpbpjb4pf.streamlit.app


How the Game Works

Each day, the player decides:

Plant Area: How many units of crop to plant

Ship Quantity: How much inventory to send to market

Price per Unit: Price offered at the city market

Market Demand: Expected demand for the day

The simulation models:

Harvest with a one-day planting delay

Spoilage at both farm and market

Shipping capacity limits

Sales, revenue, costs, and daily profit

Cumulative profit and inventory visualization

The dashboard updates with:

Metrics (cash, inventories, sales, profit)

Turn-by-turn history table

Line charts for inventory and profit trends

Key Learning Concepts

VeggieChain introduces core supply chain ideas:

Production planning

Transportation constraints

Demand fulfillment

Spoilage & perishability

Price vs. demand interactions

Profit optimization through trade-offs

Perfect for SCM students, business clubs, and classroom demonstrations.

Tech Stack

Python

Streamlit (Web UI)

Pandas (Tabular data and charts)

Dataclasses (Model structure)

Project Structure
VeggieChain/
│── app.py                # Main Streamlit application
│── veggiechain_model.py  # (optional future split for model logic)
│── requirements.txt      # Python dependencies
│── README.md             # Project documentation

Run Locally
Install dependencies
pip install -r requirements.txt

Run the Streamlit app
streamlit run app.py


Or, if Windows PATH issues occur:

python -m streamlit run app.py

Deploying on Streamlit Cloud

Push repo to GitHub

Go to https://share.streamlit.io

Select the repo → Choose branch → Set “app.py” as main file

Click Deploy

Share your public game link 🎉

Contributing

Pull requests, feature ideas, and UI improvements are welcome.
Future enhancements may include weather effects, dynamic demand, multi-day production, or advanced SCM scenarios.

📜 License

MIT License — feel free to use, modify, and learn from this project.
