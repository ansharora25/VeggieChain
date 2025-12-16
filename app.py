# app.py
import streamlit as st
import random
from dataclasses import dataclass, asdict
from typing import Dict, List


# ---------- Simulation Model ----------

DEFAULT_PARAMETERS: Dict[str, float] = {
    "truck_capacity": 100.0,
    "num_trucks": 2.0,
    "spoilage_rate_farm": 0.10,
    "spoilage_rate_market": 0.05,
    "cost_plant": 1.0,
    "cost_ship": 0.2,
    "initial_inventory_farm": 0.0,
    "initial_inventory_market": 0.0,
    "initial_cash": 100.0,
}

WEATHER_EFFECTS = {
    "Sunny ☀️": 1.2,
    "Rainy 🌧️": 1.0,
    "Storm 🌪️": 0.7,
}


@dataclass
class GameState:
    turn: int = 0
    inventory_farm: float = 0.0
    inventory_market: float = 0.0
    cash: float = 0.0
    profit_cum: float = 0.0
    last_plant_area: float = 0.0

    # Weather
    weather: str = "Rainy 🌧️"
    weather_multiplier: float = 1.0

    # per-turn results
    harvest: float = 0.0
    feasible_ship: float = 0.0
    sales: float = 0.0
    revenue: float = 0.0
    cost_plant_turn: float = 0.0
    cost_ship_turn: float = 0.0
    profit_turn: float = 0.0


@dataclass
class Decisions:
    plant_area: float = 50.0
    ship_qty: float = 80.0
    price: float = 3.0
    demand_market: float = 100.0


class VeggieChainModel:
    def __init__(self, parameters: Dict[str, float] | None = None):
        self.parameters: Dict[str, float] = dict(DEFAULT_PARAMETERS)
        if parameters:
            self.parameters.update(parameters)
        self.state: GameState = GameState()
        self.decisions: Decisions = Decisions()
        self.history: List[Dict] = []
        self.init_game()

    def init_game(self):
        p = self.parameters
        self.state = GameState(
            turn=0,
            inventory_farm=p["initial_inventory_farm"],
            inventory_market=p["initial_inventory_market"],
            cash=p["initial_cash"],
            profit_cum=0.0,
            last_plant_area=0.0,
            weather="Rainy 🌧️",
            weather_multiplier=1.0,
        )
        self.decisions = Decisions()
        self.history = []

    def set_decisions(self, plant_area: float, ship_qty: float,
                      price: float, demand_market: float):
        self.decisions = Decisions(
            plant_area=float(plant_area),
            ship_qty=float(ship_qty),
            price=float(price),
            demand_market=float(demand_market),
        )

    def advance_turn(self):
        p = self.parameters
        d = self.decisions
        prev = self.state

        # 🌦️ Random weather
        weather, multiplier = random.choice(list(WEATHER_EFFECTS.items()))

        # Capacity & shipment
        max_ship = p["truck_capacity"] * p["num_trucks"]
        feasible_ship = min(d.ship_qty, prev.inventory_farm, max_ship)

        # Harvest with weather effect
        base_harvest = prev.last_plant_area
        harvest = base_harvest * multiplier

        inventory_farm_raw = prev.inventory_farm + harvest - feasible_ship
        inventory_farm = max(0.0, inventory_farm_raw * (1.0 - p["spoilage_rate_farm"]))

        # Market inventory & sales
        inventory_market_raw = prev.inventory_market + feasible_ship
        sales = min(inventory_market_raw, d.demand_market)
        inventory_market_after_sales = inventory_market_raw - sales
        inventory_market = inventory_market_after_sales * (1.0 - p["spoilage_rate_market"])

        # Financials
        revenue = sales * d.price
        cost_plant_turn = d.plant_area * p["cost_plant"]
        cost_ship_turn = feasible_ship * p["cost_ship"]
        profit_turn = revenue - cost_plant_turn - cost_ship_turn
        cash = prev.cash + profit_turn
        profit_cum = prev.profit_cum + profit_turn

        self.state = GameState(
            turn=prev.turn + 1,
            inventory_farm=inventory_farm,
            inventory_market=inventory_market,
            cash=cash,
            profit_cum=profit_cum,
            last_plant_area=d.plant_area,
            weather=weather,
            weather_multiplier=multiplier,
            harvest=harvest,
            feasible_ship=feasible_ship,
            sales=sales,
            revenue=revenue,
            cost_plant_turn=cost_plant_turn,
            cost_ship_turn=cost_ship_turn,
            profit_turn=profit_turn,
        )

        self.history.append(self.get_state())

    def get_state(self) -> Dict:
        return {
            "state": asdict(self.state),
            "decisions": asdict(self.decisions),
            "parameters": dict(self.parameters),
        }

    def get_history(self) -> List[Dict]:
        return self.history


# ---------- Streamlit App ----------

st.set_page_config(page_title="VeggieChain", page_icon="🥕", layout="wide")

st.title("🥕 VeggieChain – Farm-to-Market Supply Chain Game")
st.markdown(
    "Manage a vegetable supply chain. After Day 4, demand becomes unpredictable. "
    "Weather affects harvest every day."
)

if "game" not in st.session_state:
    st.session_state.game = VeggieChainModel()

game: VeggieChainModel = st.session_state.game

# Sidebar
with st.sidebar:
    st.header("Game Controls")
    if st.button("🔄 Reset Game"):
        game.init_game()
        st.success("Game reset!")
    st.markdown("---")
    st.caption("🌦️ Weather is random daily\n📈 Demand randomizes after Day 4")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Decisions for Today")
    d = game.decisions

    plant_area = st.number_input("Plant Area", 0, 500, int(d.plant_area), step=10)
    ship_qty = st.number_input("Ship Quantity", 0, 500, int(d.ship_qty), step=10)
    price = st.number_input("Price per Unit", 0.0, 20.0, float(d.price), step=0.5)

    if game.state.turn < 4:
        demand_market = st.number_input("Market Demand", 0, 500, int(d.demand_market), step=10)
        st.caption("Demand is player-controlled (Days 1–4)")
    else:
        st.info("Demand is randomized from Day 5 onward")
        demand_market = int(d.demand_market)

    if st.button("▶️ Advance Day"):
        if game.state.turn >= 4:
            demand_market = random.randint(50, 200)

        game.set_decisions(plant_area, ship_qty, price, demand_market)
        game.advance_turn()
        st.success(f"Advanced one day! Demand used: {demand_market}")

with col_right:
    st.subheader("Current Status")
    s = game.get_state()["state"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Day", s["turn"])
    m2.metric("Cash", f"${s['cash']:.2f}")
    m3.metric("Farm Inventory", f"{s['inventory_farm']:.1f}")
    m4.metric("Market Inventory", f"{s['inventory_market']:.1f}")

    m5, m6, m7 = st.columns(3)
    m5.metric("Sales", f"{s['sales']:.1f}")
    m6.metric("Profit Today", f"${s['profit_turn']:.2f}")
    m7.metric("Total Profit", f"${s['profit_cum']:.2f}")

    st.markdown("### 🌦️ Weather Today")
    st.info(f"{s['weather']} (Harvest ×{s['weather_multiplier']})")

    st.markdown("---")
    st.subheader("History & Trends")

    if game.history:
        import pandas as pd

        rows = []
        for h in game.history:
            r = {}
            r.update({f"state_{k}": v for k, v in h["state"].items()})
            r.update({f"dec_{k}": v for k, v in h["decisions"].items()})
            rows.append(r)

        df = pd.DataFrame(rows).set_index("state_turn")

        st.line_chart(df[["state_profit_turn", "state_profit_cum"]])
        st.line_chart(df[["state_inventory_farm", "state_inventory_market"]])
        st.line_chart(df[["dec_demand_market"]])
    else:
        st.info("No history yet. Advance the day to start.")

