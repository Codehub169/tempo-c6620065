import streamlit as st
import json
import html

# Page config must be the very first Streamlit command
st.set_page_config(page_title="Unit Converter Pro", layout="wide", page_icon="\U0001F504")

# Load unit conversion data
@st.cache_data
def load_data():
    try:
        with open('units_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("Critical Error: `units_data.json` not found. The application cannot start.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Critical Error: `units_data.json` is malformed or contains invalid JSON. The application cannot start.")
        st.stop()

UNITS_DATA = load_data()

# Conversion functions
def convert_standard(value, from_unit, to_unit, category_data):
    """Converts between standard units based on factors relative to a base unit."""
    if from_unit == to_unit:
        return value
    
    if from_unit not in category_data['units'] or to_unit not in category_data['units']:
        st.warning(f"Conversion definition missing for {html.escape(from_unit)} or {html.escape(to_unit)}. Please check unit data.")
        return None

    from_factor = category_data['units'][from_unit]
    to_factor = category_data['units'][to_unit]

    if not isinstance(from_factor, (int, float)) or not isinstance(to_factor, (int, float)):
        st.warning(f"Invalid conversion factor type for {html.escape(from_unit)} or {html.escape(to_unit)}. Factors must be numbers.")
        return None
    
    if to_factor == 0:
        st.warning(f"Cannot convert to {html.escape(to_unit)} as its conversion factor relative to the base unit implies division by zero or an invalid setup.")
        return None

    try:
        # The factors in units_data.json are defined such that: 1 unit = factor * base_unit.
        # e.g., Length: base_unit='m'. For 'km', factor is 1000, meaning 1 km = 1000 m.
        # To convert 'value' from 'from_unit' to 'to_unit':
        # 1. Convert 'value' (in 'from_unit') to the equivalent in 'base_unit'.
        #    value_in_base_units = value * from_factor
        #    Example: Convert 2 km to meters. value=2, from_unit='km', from_factor=1000.
        #    value_in_base_units = 2 * 1000 = 2000 (meters).
        # 2. Convert 'value_in_base_units' to 'to_unit'.
        #    converted_value = value_in_base_units / to_factor
        #    Example: Convert 2000 meters (value_in_base_units) to cm. to_unit='cm', to_factor=0.01 (1 cm = 0.01 m).
        #    converted_value = 2000 / 0.01 = 200000 (cm).
        # This logic is correct based on the structure of units_data.json.
        value_in_base_units = value * from_factor
        converted_value = value_in_base_units / to_factor
        return converted_value
    except OverflowError:
        st.warning("Calculation resulted in an overflow. Please check input values or unit definitions.")
        return None
    except ZeroDivisionError: # Should be caught by to_factor == 0, but as a safeguard
        st.warning(f"Cannot convert to {html.escape(to_unit)} due to division by zero. Check unit data.")
        return None

def convert_temperature(value, from_unit, to_unit):
    """Converts between temperature units (Celsius, Fahrenheit, Kelvin)."""
    if from_unit == to_unit:
        return value

    celsius = None # Initialize celsius to avoid potential UnboundLocalError if from_unit is unknown
    # Convert input to Celsius first
    if from_unit == "F":
        celsius = (value - 32) * 5/9
    elif from_unit == "K":
        celsius = value - 273.15
    elif from_unit == "C":
        celsius = value
    else:
        st.warning(f"Unknown 'from' temperature unit: {html.escape(str(from_unit))}")
        return None

    # Convert Celsius to target unit
    if to_unit == "F":
        return (celsius * 9/5) + 32
    elif to_unit == "K":
        return celsius + 273.15
    elif to_unit == "C":
        return celsius
    else:
        st.warning(f"Unknown 'to' temperature unit: {html.escape(str(to_unit))}")
        return None

# Custom CSS for styling
def local_css():
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Poppins:wght@600&display=swap');

        body {{
            font-family: 'Inter', sans-serif;
            color: #333333;
            background-color: #F8F8F8;
        }}
        .stApp {{
            background-color: #F8F8F8;
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Poppins', sans-serif;
            color: #4A90E2; /* Primary color */
        }}
        .stButton>button {{
            background-color: #4A90E2; /* Primary color */
            color: white;
            border-radius: 5px;
            border: none;
            padding: 10px 20px;
        }}
        .stButton>button:hover {{
            background-color: #357ABD; /* Darker shade of primary */
        }}
        .stSelectbox label, .stNumberInput label {{
            font-family: 'Poppins', sans-serif;
            color: #4A90E2; /* Primary color */
        }}
        .result-display {{
            font-family: 'Poppins', sans-serif;
            font-size: 2.5em;
            color: #F5A623; /* Accent color */
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #E0E0E0;
            text-align: center;
            margin-top: 20px;
            word-wrap: break-word; /* Prevent overflow with long unit names */
        }}
        .header-title {{
            color: #4A90E2; /* Primary color */
        }}
        .secondary-text {{
            color: #50E3C2; /* Secondary color */
        }}
        /* Ensure Streamlit's default styles don't override too much */
        .stTextInput input, .stNumberInput input, .stSelectbox select {{
             border: 1px solid #E0E0E0 !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Main app layout
def main():
    local_css()

    st.markdown("<h1 class='header-title'>Unit Converter Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='secondary-text'>Your one-stop solution for quick and accurate unit conversions across various categories.</p>", unsafe_allow_html=True)

    if not UNITS_DATA:
        st.error("Unit data is not available. Application cannot proceed.")
        st.stop()

    col1, col2 = st.columns([1, 3])
    
    with col1:
        category_names = list(UNITS_DATA.keys())
        if not category_names:
            st.error("No unit categories found. Please check the unit data file.")
            st.stop()
            
        # Use a fixed key for the category selector for stability, 
        # dependent widgets will use dynamic keys based on its value.
        selected_category_name = st.selectbox("Select Category:", category_names, key="category_selector")
        
        if not selected_category_name or selected_category_name not in UNITS_DATA:
            # This case should be rare given selectbox behavior but good for robustness
            st.error("Invalid category selected or category data missing. Please check `units_data.json`.") 
            st.stop()

        category_data = UNITS_DATA[selected_category_name]
        
        if 'units' not in category_data or not isinstance(category_data['units'], dict) or not category_data['units']:
            st.error(f"No units found or units are malformed for category '{html.escape(selected_category_name)}'. Please check the unit data file.")
            st.stop()
        unit_options = list(category_data['units'].keys())

        # Dynamic keys for unit selectors and number input ensure they reset when the category changes.
        from_unit = st.selectbox("From Unit:", unit_options, key=f"from_unit_{selected_category_name}")
        to_unit = st.selectbox("To Unit:", unit_options, key=f"to_unit_{selected_category_name}")
        value_to_convert = st.number_input("Enter Value:", value=1.0, format="%.6f", key=f"value_input_{selected_category_name}")

    converted_value = None
    # Ensure all necessary inputs are valid before attempting conversion
    if value_to_convert is not None and from_unit and to_unit and selected_category_name and category_data:
        if category_data.get('type') == 'temperature':
            converted_value = convert_temperature(value_to_convert, from_unit, to_unit)
        else:
            converted_value = convert_standard(value_to_convert, from_unit, to_unit, category_data)

    with col2:
        if converted_value is not None:
            safe_from_unit = html.escape(str(from_unit)) 
            safe_to_unit = html.escape(str(to_unit))
            st.markdown(f"<div class='result-display'>{value_to_convert:.6f} {safe_from_unit} = {converted_value:.6f} {safe_to_unit}</div>", unsafe_allow_html=True)
        else:
            # Show 'Could not perform conversion' only if an attempt was made (i.e., inputs were provided and valid initially)
            if value_to_convert is not None and from_unit and to_unit: # Check if conversion was attempted
                 st.markdown("<div class='result-display'>Could not perform conversion. Please check inputs or unit data.</div>", unsafe_allow_html=True)
            else: # Initial state or incomplete input for a valid category
                st.markdown("<div class='result-display'>Enter values to see the conversion.</div>", unsafe_allow_html=True)
    
    st.markdown("---<br><small>Powered by Streamlit. Fonts: Inter & Poppins. Colors by design spec.</small>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
