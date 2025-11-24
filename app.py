# app.py
import streamlit as st
from dataclasses import dataclass, asdict
from typing import Dict, List


# ---------- Simulation Model ----------

DEFAULT_PARAMETERS: Dict[str, float] = {
    "truck_capacity": 100.0,        # units per truck
    "num_trucks": 2.0,              # number of trucks
    "spoilage_rate_farm": 0.10,     # fraction spoiled at farm per turn
    "spoilage_rate_market": 0.05,   # fraction spoiled at market per turn
    "cost_plant": 1.0,              # cost to plant one unit
    "cost_ship": 0.2,               # shipping cost per unit
    "initial_inventory_farm": 0.0,  # starting farm inventory
    "initial_inventory_market": 0.0,# starting market inventory
    "initial_cash": 100.0,          # starting cash
}


@dataclass
class GameState:
    turn: int = 0
    inventory_farm: float = 0.0
    inventory_market: float = 0.0
    cash: float = 0.0
    profit_cum: float = 0.0
    last_plant_area: float = 0.0  # used to compute harvest with one-turn delay

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

        # Capacity & feasible shipment
        max_ship = p["truck_capacity"] * p["num_trucks"]
        feasible_ship = min(d.ship_qty, prev.inventory_farm, max_ship)

        # Harvest & farm inventory update
        harvest = prev.last_plant_area
        inventory_farm_raw = prev.inventory_farm + harvest - feasible_ship
        inventory_farm = max(0.0, inventory_farm_raw * (1.0 - p["spoilage_rate_farm"]))

        # Market inventory & sales
        inventory_market_raw = prev.inventory_market + feasible_ship
        potential_sales = min(inventory_market_raw, d.demand_market)
        sales = potential_sales
        inventory_market_after_sales = inventory_market_raw - sales
        inventory_market = inventory_market_after_sales * (1.0 - p["spoilage_rate_market"])

        # Profit & cash
        revenue = sales * d.price
        cost_plant_turn = d.plant_area * p["cost_plant"]
        cost_ship_turn = feasible_ship * p["cost_ship"]
        profit_turn = revenue - cost_plant_turn - cost_ship_turn
        cash = prev.cash + profit_turn
        profit_cum = prev.profit_cum + profit_turn

        new_state = GameState(
            turn=prev.turn + 1,
            inventory_farm=inventory_farm,
            inventory_market=inventory_market,
            cash=cash,
            profit_cum=profit_cum,
            last_plant_area=d.plant_area,
            harvest=harvest,
            feasible_ship=feasible_ship,
            sales=sales,
            revenue=revenue,
            cost_plant_turn=cost_plant_turn,
            cost_ship_turn=cost_ship_turn,
            profit_turn=profit_turn,
        )

        self.state = new_state
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
    "A simple turn-based game to explore basic supply chain concepts: "
    "planting, shipping, pricing, inventory, spoilage, and profit."
)

# Initialize model in session state
if "game" not in st.session_state:
    st.session_state.game = VeggieChainModel()

game: VeggieChainModel = st.session_state.game

# Sidebar for parameters / reset
with st.sidebar:
    st.header("Game Controls")
    if st.button("🔄 Reset Game"):
        game.init_game()
        st.success("Game reset!")

    st.markdown("---")
    st.subheader("Parameters (optional)")
    # You can expose these later if you want them tunable
    st.caption("Currently using default parameters defined in code.")

# Layout: decisions on left, metrics + charts on right
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Decisions for Today")

    # Current decisions as defaults
    d = game.decisions

    plant_area = st.number_input(
        "Plant Area (units of crop to plant)",
        min_value=0,
        max_value=500,
        value=int(d.plant_area),
        step=10,
    )

    ship_qty = st.number_input(
        "Ship Quantity (units to send to market)",
        min_value=0,
        max_value=500,
        value=int(d.ship_qty),
        step=10,
    )

    price = st.number_input(
        "Price per Unit",
        min_value=0.0,
        max_value=20.0,
        value=float(d.price),
        step=0.5,
        format="%.2f",
    )

    demand_market = st.number_input(
        "Demand at Market (units)",
        min_value=0,
        max_value=500,
        value=int(d.demand_market),
        step=10,
    )

    if st.button("▶️ Advance Day"):
        game.set_decisions(
            plant_area=plant_area,
            ship_qty=ship_qty,
            price=price,
            demand_market=demand_market,
        )
        game.advance_turn()
        st.success("Advanced one day!")

with col_right:
    st.subheader("Current Status")

    current = game.get_state()
    s = current["state"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Day", s["turn"])
    m2.metric("Cash", f"${s['cash']:.2f}")
    m3.metric("Farm Inventory", f"{s['inventory_farm']:.1f}")
    m4.metric("Market Inventory", f"{s['inventory_market']:.1f}")

    m5, m6, m7 = st.columns(3)
    m5.metric("Sales (Today)", f"{s['sales']:.1f}")
    m6.metric("Profit (Today)", f"${s['profit_turn']:.2f}")
    m7.metric("Profit (Total)", f"${s['profit_cum']:.2f}")

    st.markdown("---")
    st.subheader("History")

    history = game.get_history()
    if history:
        import pandas as pd

        # Flatten history into a DataFrame
        rows = []
        for h in history:
            row = {}
            row.update({f"state_{k}": v for k, v in h["state"].items()})
            row.update({f"dec_{k}": v for k, v in h["decisions"].items()})
            rows.append(row)
        df = pd.DataFrame(rows)

        # Show table and charts
        with st.expander("Show data table", expanded=False):
            st.dataframe(df)

        st.line_chart(
            df.set_index("state_turn")[["state_profit_turn", "state_profit_cum"]],
            height=300,
        )
        st.line_chart(
            df.set_index("state_turn")[["state_inventory_farm", "state_inventory_market"]],
            height=300,
        )
    else:
        st.info("No history yet. Make some decisions and click **Advance Day** to start the game!")
