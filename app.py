import html

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="SolarDoc: Solar Fault Expert",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# 0. STYLING
# =====================================================================
CSS = """
<style>
.hero {
    background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
    padding: 1.6rem 2rem;
    border-radius: 18px;
    color: #1d1d1d;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.25);
}
.hero h1 {
    margin: 0;
    font-size: 2.1rem;
    font-weight: 800;
    color: #1d1d1d;
}
.hero p {
    margin: 0.4rem 0 0 0;
    font-size: 1rem;
    color: #3a3a3a;
}
.stat-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.7rem;
}
.stat-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    opacity: 0.7;
}
.stat-value {
    font-size: 1.7rem;
    font-weight: 700;
    line-height: 1.2;
}
.fault-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.4rem;
}
.fault-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.fault-title {
    font-size: 1.25rem;
    font-weight: 700;
}
.badge {
    color: #111111;
    font-weight: 700;
    font-size: 0.75rem;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    letter-spacing: 0.05em;
}
.bar-bg {
    width: 100%;
    height: 10px;
    background: rgba(128, 128, 128, 0.25);
    border-radius: 999px;
    margin: 0.8rem 0 0.3rem 0;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 999px;
}
.fault-meta {
    font-size: 0.9rem;
    opacity: 0.75;
    margin-bottom: 0.6rem;
}
.action-box {
    background: rgba(255, 210, 0, 0.10);
    border-left: 4px solid #ffd200;
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin-top: 0.6rem;
}
.safety-banner {
    background: #7a1f1f;
    color: #ffffff;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    font-weight: 600;
    margin-bottom: 1rem;
    border: 1px solid #ff4b4b;
}
.empty-box {
    text-align: center;
    padding: 2.5rem 1rem;
    border: 2px dashed rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    opacity: 0.85;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

URGENCY_COLOR = {
    "EMERGENCY": "#ff4b4b",
    "HIGH": "#ff8c42",
    "MEDIUM": "#ffd23f",
    "LOW": "#4cc9f0",
}

# =====================================================================
# 1. KNOWLEDGE BASE, PART A: CONDITIONS (observable facts / symptoms)
#    key -> (category, human-readable statement)
# =====================================================================
GROUPS = [
    "Solar panels",
    "Inverter",
    "Battery",
    "Charge controller",
    "Wiring and protection",
    "Load and usage",
    "Environment and history",
]

SYMPTOMS = {
    # --- Solar panels (8) ---
    "p_low_sunny": (
        "Solar panels",
        "Panels give little or no output on a bright, clear day",
    ),
    "p_dirty": (
        "Solar panels",
        "Panels are visibly covered with dust, mud, or bird droppings",
    ),
    "p_shade": (
        "Solar panels",
        "Panels are shaded by trees, poles, or nearby buildings during the day",
    ),
    "p_cracked": ("Solar panels", "A panel glass is cracked or chipped"),
    "p_burn_marks": (
        "Solar panels",
        "Brown or burnt marks are visible on a panel or its cells",
    ),
    "p_hot_back": (
        "Solar panels",
        "The back of a panel or its junction box feels unusually hot",
    ),
    "p_loose_mount": (
        "Solar panels",
        "Panel clamps or mounting rails are loose or rusted",
    ),
    "p_low_edges": (
        "Solar panels",
        "Output is low only in early morning and late evening",
    ),
    # --- Inverter (12) ---
    "i_off": ("Inverter", "Inverter display is completely dead"),
    "i_beep": ("Inverter", "Inverter beeps continuously"),
    "i_overload_led": ("Inverter", "Overload indicator is lit"),
    "i_fan_loud": ("Inverter", "Cooling fan runs loudly or never stops"),
    "i_hot_case": ("Inverter", "Inverter casing is hot to touch"),
    "i_burn_smell": ("Inverter", "A burning smell comes from the inverter"),
    "i_error_code": ("Inverter", "Inverter shows an error code (F or E series)"),
    "i_no_battery_switch": (
        "Inverter",
        "Inverter does not switch to battery when mains fails",
    ),
    "i_low_ac_volt": ("Inverter", "Measured AC output voltage is below 200 V"),
    "i_high_ac_volt": ("Inverter", "Measured AC output voltage is above 250 V"),
    "i_restarts": ("Inverter", "Inverter shuts down and restarts repeatedly"),
    "i_ac_wont_start": ("Inverter", "Air conditioner will not start on inverter power"),
    # --- Battery (10) ---
    "b_short_backup": (
        "Battery",
        "Backup lasts far less than before (under 1 hour for a normal load)",
    ),
    "b_no_charge_day": ("Battery", "Battery voltage does not rise during the day"),
    "b_swollen": ("Battery", "Battery case is swollen or bulging"),
    "b_low_water": ("Battery", "Lead-acid electrolyte is below the top of the plates"),
    "b_terminal_corrosion": (
        "Battery",
        "White or green corrosion on battery terminals",
    ),
    "b_hot_charging": ("Battery", "Battery becomes hot while charging"),
    "b_left_discharged": ("Battery", "Battery was left flat for several days"),
    "b_older_4y": ("Battery", "Battery is more than four years old"),
    "b_low_volt_alarm": ("Battery", "Inverter gives a low-battery alarm"),
    "b_not_full": ("Battery", "Battery never reaches full charge"),
    # --- Charge controller (5) ---
    "c_no_led": ("Charge controller", "Charge controller shows no indicator light"),
    "c_stuck_bulk": (
        "Charge controller",
        "Controller stays in bulk or boost mode and never reaches float",
    ),
    "c_hot": ("Charge controller", "Charge controller is hot to touch"),
    "c_fault_blink": ("Charge controller", "Controller fault LED is blinking"),
    "c_wrong_type": (
        "Charge controller",
        "Battery-type setting does not match the installed battery",
    ),
    # --- Wiring and protection (8) ---
    "w_breaker_trips": ("Wiring and protection", "A DC or AC breaker trips frequently"),
    "w_cable_hot": (
        "Wiring and protection",
        "Cable insulation feels hot or is discoloured",
    ),
    "w_loose_terminal": ("Wiring and protection", "Terminal screws feel loose"),
    "w_lights_flicker": (
        "Wiring and protection",
        "Lights flicker or dim when a large load starts",
    ),
    "w_tingle": (
        "Wiring and protection",
        "Metal parts of the system give a mild electric tingle",
    ),
    "w_fuse_blown": ("Wiring and protection", "A DC fuse has blown"),
    "w_plastic_smell": (
        "Wiring and protection",
        "A smell of burnt plastic comes from the wiring",
    ),
    "w_rcd_trips": (
        "Wiring and protection",
        "RCD or ELCB trips when the system is switched on",
    ),
    # --- Load and usage (4) ---
    "l_fans_slow": ("Load and usage", "Ceiling fans run slower than usual on backup"),
    "l_motor_fail": (
        "Load and usage",
        "A motor appliance (pump, fridge) fails to start on inverter",
    ),
    "l_overload_light": (
        "Load and usage",
        "Overload happens with only fans and lights switched on",
    ),
    "l_load_near_max": (
        "Load and usage",
        "Connected load is usually near the inverter's rated capacity",
    ),
    # --- Environment and history (8) ---
    "e_monsoon": (
        "Environment and history",
        "The problem began during monsoon or humid weather",
    ),
    "e_summer_peak": (
        "Environment and history",
        "The problem is worse on hot afternoons above 40 °C",
    ),
    "e_new_install": (
        "Environment and history",
        "The system was installed within the last month",
    ),
    "e_recent_storm": (
        "Environment and history",
        "There was lightning or a power surge recently",
    ),
    "e_mains_spikes": ("Environment and history", "Utility voltage spikes often"),
    "e_long_mains_off": (
        "Environment and history",
        "Grid power is off for long periods",
    ),
    "e_monitor_low_yield": (
        "Environment and history",
        "Monitoring app shows yield well below expected",
    ),
    "e_monitor_no_data": (
        "Environment and history",
        "Monitoring app shows no data from the inverter",
    ),
}

# =====================================================================
# 2. KNOWLEDGE BASE, PART B: CONCLUSIONS (faults)
#    key -> (fault name, urgency, explanation, recommended action)
# =====================================================================
FAULTS = {
    "SAFETY_FIRE": (
        "Possible fire or electrical overheating hazard",
        "EMERGENCY",
        "Burning smells and heat are warning signs of a live fault that can start a fire.",
        "Switch off the inverter, open the DC isolator and AC breaker, do not touch the wiring or battery, and call a licensed electrician now.",
    ),
    "WIRE_LOOSE": (
        "Loose or high-resistance connection",
        "HIGH",
        "A loose terminal creates resistance, which produces heat and arcing.",
        "Power down, tighten all terminals to the torque in the equipment manual, and inspect for discolouration.",
    ),
    "WIRE_OVERCURRENT": (
        "Undersized cable or overcurrent",
        "HIGH",
        "Current is exceeding what the cable or breaker is rated to carry.",
        "Compare the cable gauge with the current rating, reduce the load, and fit the correct breaker size.",
    ),
    "PANEL_HOTSPOT": (
        "Panel hotspot or cell damage",
        "HIGH",
        "A damaged or shaded cell forced to carry current heats up and can burn the module.",
        "Disconnect the affected string, have the panel inspected, and replace it under warranty if damaged.",
    ),
    "PANEL_CRACK": (
        "Cracked or damaged panel",
        "HIGH",
        "Cracks let moisture into the cells, causing shorts and lost output.",
        "Isolate the panel and replace it.",
    ),
    "SOILING": (
        "Soiling from dust, mud or bird droppings",
        "MEDIUM",
        "Dirt on the glass blocks sunlight and reduces output.",
        "Clean the panels early in the morning with water and a soft cloth. Do not use abrasive tools.",
    ),
    "SHADING": (
        "Partial shading",
        "MEDIUM",
        "A shadow on even one cell can reduce the output of a whole string.",
        "Trim trees, relocate the panels, or use optimisers or a bypass-diode-aware design.",
    ),
    "PANEL_MOUNT": (
        "Loose or corroded panel mounting",
        "MEDIUM",
        "Wind movement shifts panels and stresses cables and clamps.",
        "Tighten clamps and replace corroded rails.",
    ),
    "UNDERPERFORM": (
        "General array under-performance",
        "LOW",
        "Output is below expected without one clear cause. Dirt, orientation, and ageing often combine.",
        "Compare with the expected yield for your location, check tilt and orientation, and ask a technician to run a string test.",
    ),
    "INV_OVERLOAD": (
        "Inverter overload trip",
        "MEDIUM",
        "The inverter is cutting off because connected load exceeds its rating.",
        "Switch off some heavy loads, restart, and avoid starting several motors together.",
    ),
    "INV_FAULT": (
        "Internal inverter fault",
        "HIGH",
        "The inverter electronics report a fault or fail to power up.",
        "Note the error code, power-cycle once, and if the fault persists contact the supplier for service.",
    ),
    "INV_OVERHEAT": (
        "Inverter overheating",
        "HIGH",
        "Blocked vents, dust, poor ventilation, or high ambient temperature trigger thermal shutdown.",
        "Improve airflow, clean the fan and filters, keep it out of direct sun, and leave about 30 cm of clearance.",
    ),
    "INV_AC_HIGH": (
        "High inverter output voltage",
        "HIGH",
        "Output above about 250 V can damage sensitive appliances.",
        "Disconnect sensitive appliances, check the output settings, and contact the supplier.",
    ),
    "INV_AC_LOW": (
        "Low inverter output voltage",
        "HIGH",
        "Low voltage is often caused by a weak battery or an overloaded inverter.",
        "Check battery voltage and reduce the load. If the problem persists, have the inverter serviced.",
    ),
    "INV_TRANSFER": (
        "Transfer or source-priority setting fault",
        "MEDIUM",
        "The inverter does not switch to battery mode when mains power fails.",
        "Check the source-priority setting and the transfer relay wiring.",
    ),
    "MAINS_SURGE": (
        "Grid voltage surges",
        "MEDIUM",
        "Frequent surges stress the inverter and connected appliances.",
        "Install a voltage stabiliser or surge protective device on the mains input.",
    ),
    "LOAD_OVERSIZED": (
        "Load exceeds system capacity",
        "HIGH",
        "Demand is greater than the inverter, battery, or panel capacity.",
        "Reduce simultaneous loads, or upgrade the inverter and battery sizing.",
    ),
    "BATT_AGED": (
        "Ageing or failing battery",
        "HIGH",
        "Capacity fades with age and cycling, so backup time drops sharply.",
        "Test the capacity and replace the battery if it is below about 70% of its rating.",
    ),
    "BATT_DEEP_DISCHARGE": (
        "Deep-discharge damage",
        "HIGH",
        "Leaving lead-acid batteries flat causes irreversible sulphation.",
        "Recharge slowly, check the cell voltages, and avoid discharging below about 50%.",
    ),
    "BATT_UNDERCHARGE": (
        "Battery not charging fully",
        "HIGH",
        "The battery is not receiving enough energy from the panels or the controller.",
        "Check panel output, controller mode, and battery voltage at the terminals.",
    ),
    "BATT_LOW_WATER": (
        "Low electrolyte level",
        "HIGH",
        "Plates exposed to air are damaged and capacity drops.",
        "After charging, top up with distilled water only, to the marked level.",
    ),
    "BATT_OVERHEAT": (
        "Battery overheating",
        "HIGH",
        "Heat during charging can mean overcharging, low electrolyte, or a failing cell.",
        "Stop charging, check the float voltage and water level, and inspect before reuse.",
    ),
    "BATT_CORROSION": (
        "Terminal corrosion",
        "MEDIUM",
        "Corrosion adds resistance and wastes energy.",
        "Disconnect, clean with baking soda and water, apply petroleum jelly, and tighten.",
    ),
    "BATT_SWELL": (
        "Swollen battery",
        "HIGH",
        "Gas build-up or an internal short can make a swollen battery rupture or burn.",
        "Disconnect it, move it to a ventilated area, and replace it immediately.",
    ),
    "CTRL_FAULT": (
        "Charge controller fault",
        "HIGH",
        "The controller has detected an internal fault or an open circuit.",
        "Check the wiring, reset the controller, and replace it if the fault repeats.",
    ),
    "CTRL_SETTING": (
        "Incorrect charge-controller settings",
        "MEDIUM",
        "A wrong battery type or charge profile prevents proper charging.",
        "Set the battery type and voltage thresholds to match the battery datasheet.",
    ),
    "CTRL_OVERHEAT": (
        "Charge controller overheating",
        "MEDIUM",
        "The controller is overloaded or poorly ventilated.",
        "Confirm the array current is within the controller rating and improve airflow.",
    ),
    "EARTH_FAULT": (
        "Earth leakage or insulation fault",
        "HIGH",
        "Current is leaking to earth, which trips the RCD and creates a shock risk.",
        "Shut the system down, isolate it, and have an electrician test the insulation and earthing.",
    ),
    "FUSE_BLOWN": (
        "Blown DC fuse",
        "HIGH",
        "A fuse blows to protect against a short circuit or overcurrent.",
        "Find and remove the cause first, then replace the fuse with one of the same rating.",
    ),
    "MONITOR_COMM": (
        "Monitoring communication loss",
        "LOW",
        "The inverter is not sending data to the monitoring logger or app.",
        "Check the Wi-Fi or logger connection and restart the logger.",
    ),
}

URGENCY_RANK = {"EMERGENCY": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

# =====================================================================
# 3. KNOWLEDGE BASE, PART C: RULES
#    IF all conditions are true THEN conclude fault with certainty factor
# =====================================================================
RAW_RULES = [
    # Safety and wiring
    (["i_burn_smell"], "SAFETY_FIRE", 0.95),
    (["w_plastic_smell"], "SAFETY_FIRE", 0.95),
    (["w_cable_hot"], "WIRE_OVERCURRENT", 0.60),
    (["w_cable_hot", "w_loose_terminal"], "WIRE_LOOSE", 0.90),
    (["w_cable_hot", "w_breaker_trips"], "WIRE_OVERCURRENT", 0.90),
    (["w_loose_terminal"], "WIRE_LOOSE", 0.75),
    (["w_loose_terminal", "w_lights_flicker"], "WIRE_LOOSE", 0.85),
    (["w_lights_flicker", "i_low_ac_volt"], "WIRE_LOOSE", 0.70),
    (["w_breaker_trips"], "WIRE_OVERCURRENT", 0.50),
    (["w_breaker_trips", "l_load_near_max"], "LOAD_OVERSIZED", 0.80),
    (["w_fuse_blown"], "FUSE_BLOWN", 0.85),
    (["w_fuse_blown", "e_recent_storm"], "MAINS_SURGE", 0.75),
    (["w_rcd_trips"], "EARTH_FAULT", 0.80),
    (["w_rcd_trips", "w_tingle"], "EARTH_FAULT", 0.95),
    (["w_tingle"], "EARTH_FAULT", 0.70),
    # Battery
    (["b_swollen"], "BATT_SWELL", 0.95),
    (["b_swollen", "b_hot_charging"], "BATT_SWELL", 0.98),
    (["b_low_water"], "BATT_LOW_WATER", 0.90),
    (["b_low_water", "b_hot_charging"], "BATT_OVERHEAT", 0.90),
    (["b_hot_charging"], "BATT_OVERHEAT", 0.60),
    (["b_terminal_corrosion"], "BATT_CORROSION", 0.85),
    (["b_terminal_corrosion", "b_short_backup"], "BATT_CORROSION", 0.80),
    (["b_left_discharged"], "BATT_DEEP_DISCHARGE", 0.90),
    (["b_left_discharged", "b_not_full"], "BATT_DEEP_DISCHARGE", 0.95),
    (["b_short_backup", "b_older_4y"], "BATT_AGED", 0.90),
    (["b_short_backup"], "BATT_AGED", 0.50),
    (["b_no_charge_day", "p_low_sunny"], "BATT_UNDERCHARGE", 0.70),
    (["b_no_charge_day"], "BATT_UNDERCHARGE", 0.50),
    (["e_long_mains_off", "b_short_backup"], "BATT_UNDERCHARGE", 0.70),
    (["l_fans_slow", "b_not_full"], "BATT_UNDERCHARGE", 0.60),
    # Solar panels
    (["p_burn_marks"], "PANEL_HOTSPOT", 0.90),
    (["p_burn_marks", "p_hot_back"], "PANEL_HOTSPOT", 0.95),
    (["p_hot_back"], "PANEL_HOTSPOT", 0.50),
    (["p_cracked"], "PANEL_CRACK", 0.95),
    (["p_cracked", "p_low_sunny"], "PANEL_CRACK", 0.98),
    (["p_low_sunny", "p_dirty"], "SOILING", 0.85),
    (["p_low_sunny", "e_monsoon", "p_dirty"], "SOILING", 0.90),
    (["p_low_sunny", "p_shade"], "SHADING", 0.85),
    (["p_low_edges", "p_shade"], "SHADING", 0.85),
    (["p_low_edges"], "SHADING", 0.40),
    (["p_loose_mount"], "PANEL_MOUNT", 0.80),
    (["p_low_sunny"], "UNDERPERFORM", 0.40),
    (["e_monitor_low_yield", "p_low_sunny"], "UNDERPERFORM", 0.80),
    (["e_new_install", "p_low_sunny"], "UNDERPERFORM", 0.75),
    # Inverter
    (["i_off"], "INV_FAULT", 0.60),
    (["i_error_code"], "INV_FAULT", 0.70),
    (["i_beep"], "INV_FAULT", 0.45),
    (["i_beep", "b_low_volt_alarm"], "BATT_DEEP_DISCHARGE", 0.85),
    (["i_overload_led"], "INV_OVERLOAD", 0.85),
    (["i_overload_led", "l_load_near_max"], "LOAD_OVERSIZED", 0.90),
    (["i_overload_led", "l_overload_light"], "INV_FAULT", 0.85),
    (["i_hot_case", "i_fan_loud"], "INV_OVERHEAT", 0.85),
    (["i_hot_case", "e_summer_peak"], "INV_OVERHEAT", 0.80),
    (["i_hot_case"], "INV_OVERHEAT", 0.60),
    (["i_fan_loud"], "INV_OVERHEAT", 0.50),
    (["i_restarts", "i_hot_case"], "INV_OVERHEAT", 0.75),
    (["i_restarts", "b_short_backup"], "BATT_AGED", 0.70),
    (["i_high_ac_volt"], "INV_AC_HIGH", 0.80),
    (["i_high_ac_volt", "e_mains_spikes"], "MAINS_SURGE", 0.85),
    (["i_low_ac_volt"], "INV_AC_LOW", 0.70),
    (["i_low_ac_volt", "l_load_near_max"], "LOAD_OVERSIZED", 0.75),
    (["i_no_battery_switch"], "INV_TRANSFER", 0.85),
    (["i_ac_wont_start", "l_motor_fail"], "LOAD_OVERSIZED", 0.75),
    # Charge controller
    (["c_hot"], "CTRL_OVERHEAT", 0.80),
    (["c_hot", "b_hot_charging"], "CTRL_OVERHEAT", 0.70),
    (["c_fault_blink"], "CTRL_FAULT", 0.85),
    (["b_no_charge_day", "c_no_led"], "CTRL_FAULT", 0.85),
    (["b_no_charge_day", "c_stuck_bulk"], "CTRL_SETTING", 0.80),
    (["c_wrong_type", "b_not_full"], "CTRL_SETTING", 0.90),
    (["c_wrong_type"], "CTRL_SETTING", 0.60),
    (["c_stuck_bulk"], "CTRL_SETTING", 0.50),
    # Load and environment
    (["l_motor_fail"], "LOAD_OVERSIZED", 0.60),
    (["l_load_near_max", "e_summer_peak"], "LOAD_OVERSIZED", 0.85),
    (["e_monitor_no_data"], "MONITOR_COMM", 0.85),
]

RULES = [
    {"id": f"R{i:02d}", "if": conds, "then": fault, "cf": cf}
    for i, (conds, fault, cf) in enumerate(RAW_RULES, start=1)
]


# =====================================================================
# 4. KNOWLEDGE-BASE VALIDATION
# =====================================================================
def validate_knowledge_base():
    errors = []
    for r in RULES:
        for c in r["if"]:
            if c not in SYMPTOMS:
                errors.append(f"{r['id']} uses unknown condition '{c}'")
        if r["then"] not in FAULTS:
            errors.append(f"{r['id']} concludes unknown fault '{r['then']}'")
        if not 0.0 < r["cf"] <= 1.0:
            errors.append(f"{r['id']} has invalid certainty factor {r['cf']}")
    return errors


# =====================================================================
# 5. INFERENCE ENGINE: forward chaining with certainty factors
# =====================================================================
def forward_chain(facts):
    fired = [r for r in RULES if set(r["if"]).issubset(facts)]
    beliefs = {}
    for r in fired:
        prev = beliefs.get(r["then"], 0.0)
        # MYCIN combination: CF_new = CF_old + CF_rule * (1 - CF_old)
        beliefs[r["then"]] = prev + r["cf"] * (1.0 - prev)
    return fired, beliefs


def rule_text(rule):
    conditions = " AND ".join(f"\u201c{SYMPTOMS[c][1]}\u201d" for c in rule["if"])
    return f"IF {conditions} THEN {FAULTS[rule['then']][0]}"


def reset_all():
    for key in SYMPTOMS:
        st.session_state[key] = False


# =====================================================================
# 6. UI HELPERS
# =====================================================================
def stat_card(label, value):
    return (
        '<div class="stat-card">'
        f'<div class="stat-label">{html.escape(label)}</div>'
        f'<div class="stat-value">{html.escape(str(value))}</div>'
        "</div>"
    )


def fault_card(name, urgency, cf, explanation, action):
    color = URGENCY_COLOR[urgency]
    width = min(max(cf, 0.0), 1.0) * 100
    return (
        '<div class="fault-card" style="border-left:6px solid ' + color + ';">'
        '<div class="fault-head">'
        f'<span class="fault-title">{html.escape(name)}</span>'
        f'<span class="badge" style="background:{color};">{urgency}</span>'
        "</div>"
        '<div class="bar-bg">'
        f'<div class="bar-fill" style="width:{width:.1f}%;background:{color};"></div>'
        "</div>"
        f'<div class="fault-meta">Certainty: {cf:.0%}</div>'
        f"<div>{html.escape(explanation)}</div>"
        '<div class="action-box">'
        f"<b>Recommended action:</b> {html.escape(action)}"
        "</div>"
        "</div>"
    )


# =====================================================================
# 7. SESSION DEFAULTS AND KB CHECK
# =====================================================================
kb_errors = validate_knowledge_base()
if kb_errors:
    st.error("Knowledge base validation failed:")
    for e in kb_errors:
        st.write(f"- {e}")
    st.stop()

for key in SYMPTOMS:
    st.session_state.setdefault(key, False)

# Working memory from current checkbox states
facts = {key for key in SYMPTOMS if st.session_state.get(key, False)}
fired_rules, beliefs = forward_chain(facts)

# =====================================================================
# 8. SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    threshold = st.slider(
        "Minimum certainty to report",
        0.30,
        0.95,
        0.50,
        0.05,
        help="Conclusions below this certainty are hidden in the Diagnosis tab.",
    )
    st.button("🧹 Reset all observations", on_click=reset_all, use_container_width=True)

    st.divider()
    st.markdown(stat_card("Conditions", len(SYMPTOMS)), unsafe_allow_html=True)
    st.markdown(stat_card("Rules", len(RULES)), unsafe_allow_html=True)
    st.markdown(stat_card("Fault conclusions", len(FAULTS)), unsafe_allow_html=True)

# =====================================================================
# 9. HEADER
# =====================================================================
st.markdown(
    """
<div class="hero">
  <h1>☀️ SolarDoc</h1>
  <p>Fault diagnosis for off-grid and hybrid solar home systems, using a rule-based
  expert system with forward chaining and certainty factors.</p>
</div>
""",
    unsafe_allow_html=True,
)

# =====================================================================
# 10. TABS
# =====================================================================
results = [(f, cf) for f, cf in beliefs.items() if cf >= threshold]
results.sort(key=lambda x: (URGENCY_RANK[FAULTS[x[0]][1]], -x[1]))

group_counts = {
    g: sum(1 for k, (grp, _) in SYMPTOMS.items() if grp == g and k in facts)
    for g in GROUPS
}
# Tab labels must stay constant between reruns. If a label changes (for example
# by embedding a live count), Streamlit rebuilds the tab bar and jumps back to
# the first tab. Counts are therefore shown inside the tabs instead.
tab_labels = list(GROUPS)
tab_labels += ["🩺 Diagnosis", "📚 Knowledge base", "ℹ️ How it works"]
tabs = st.tabs(tab_labels)

# --- Observation tabs ---
for group, tab in zip(GROUPS, tabs[: len(GROUPS)]):
    with tab:
        st.subheader(group)
        st.caption(
            "Tick every statement that is true for your system. "
            f"Selected in this category: {group_counts[group]}"
        )
        items = [(k, text) for k, (grp, text) in SYMPTOMS.items() if grp == group]
        left, right = st.columns(2)
        for idx, (key, text) in enumerate(items):
            with left if idx % 2 == 0 else right:
                st.checkbox(text, key=key)

# --- Diagnosis tab ---
with tabs[len(GROUPS)]:
    st.subheader(f"Diagnosis ({len(results)})")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            stat_card("Observations ticked", f"{len(facts)} / {len(SYMPTOMS)}"),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(stat_card("Rules fired", len(fired_rules)), unsafe_allow_html=True)
    with c3:
        top = results[0][0] if results else None
        top_text = FAULTS[top][1] if top else "None"
        st.markdown(stat_card("Highest urgency", top_text), unsafe_allow_html=True)

    if not facts:
        st.markdown(
            '<div class="empty-box"><h3>No observations yet</h3>'
            "<p>Tick statements in the category tabs to start a diagnosis.</p></div>",
            unsafe_allow_html=True,
        )
    else:
        if any(FAULTS[f][1] == "EMERGENCY" for f, _ in results):
            st.markdown(
                '<div class="safety-banner">⚠️ SAFETY ALERT: Possible fire hazard. '
                "Switch off the system at the DC isolator and AC breaker, and call a "
                "licensed electrician before anything else.</div>",
                unsafe_allow_html=True,
            )

        if not results:
            st.success(
                "No fault reached the selected certainty threshold. "
                "Lower the threshold in the sidebar or select more observations."
            )

        for fault_key, cf in results:
            name, urgency, explanation, action = FAULTS[fault_key]
            st.markdown(
                fault_card(name, urgency, cf, explanation, action),
                unsafe_allow_html=True,
            )
            with st.expander("Rules that fired for this conclusion"):
                for r in fired_rules:
                    if r["then"] == fault_key:
                        st.write(f"**{r['id']}** (CF {r['cf']:.2f}): {rule_text(r)}")

        below = [(f, cf) for f, cf in beliefs.items() if cf < threshold]
        if below:
            with st.expander(f"Possible faults below the threshold ({len(below)})"):
                for f, cf in sorted(below, key=lambda x: -x[1]):
                    st.write(f"{FAULTS[f][0]}: {cf:.0%}")

# --- Knowledge base tab ---
with tabs[len(GROUPS) + 1]:
    st.subheader("Knowledge base")
    st.caption("The inference engine reads only these tables.")

    rows = [
        {
            "ID": r["id"],
            "IF (conditions)": " AND ".join(SYMPTOMS[c][1] for c in r["if"]),
            "THEN (conclusion)": FAULTS[r["then"]][0],
            "Certainty factor": r["cf"],
        }
        for r in RULES
    ]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    st.subheader("Fault conclusions")
    fault_rows = [
        {"Fault": v[0], "Urgency": v[1], "Recommended action": v[3]}
        for v in FAULTS.values()
    ]
    st.dataframe(pd.DataFrame(fault_rows), hide_index=True, use_container_width=True)

# --- How it works tab ---
with tabs[len(GROUPS) + 2]:
    st.subheader("How the expert system works")
    st.markdown(
        """
**1. Knowledge base.** Conditions are observable facts, such as "Battery is more than four years old". Conclusions are faults with a recommended action. Rules link them in the form IF conditions THEN conclusion, each with a certainty factor (CF) from 0 to 1.

**2. Working memory.** The set of conditions the user has ticked. Reset clears it.

**3. Inference engine (forward chaining).** On every update the engine scans all rules. A rule fires only when every one of its conditions is in working memory. Facts drive conclusions, so the method is data-driven.

**4. Certainty handling.** Each fired rule gives a CF. When several rules support the same fault, their CFs are combined with the MYCIN formula CF = CF₁ + CF₂ × (1 − CF₁). Agreement from independent rules raises confidence, and the result never exceeds 1.

**5. Explanation facility.** Every conclusion lists the rules that fired, which answers "why did the system conclude this?"

**6. Safety priority.** Conclusions are sorted by urgency, and an emergency rule (burning smell, plastic smell, or swollen battery) raises a safety alert first.

**7. Limitations.** The system uses only the stated observations and cannot measure voltage, so it does not replace an electrician's test. The certainty values are estimates based on general practice for small solar home systems and should be checked against the actual equipment datasheet.
"""
    )