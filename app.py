import streamlit as st
import json

# Load unit conversion data
@st.cache_data
def load_data():
    with open('units_data.json', 'r') as f:
        data = json.load(f)
    return data

UNITS_DATA = load_data()

# Conversion functions
def convert_standard(value, from_unit, to_unit, category_data):
    """Converts between standard units based on factors relative to a base unit."""
    if from_unit == to_unit:
        return value
    
    from_factor = category_data['units'][from_unit]
    to_factor = category_data['units'][to_unit]
    base_unit_value = value * from_factor
    converted_value = base_unit_value / to_factor
    return converted_value

def convert_temperature(value, from_unit, to_unit):
    """Converts between temperature units (Celsius, Fahrenheit, Kelvin)."""
    if from_unit == to_unit:
        return value

    # Convert input to Celsius first
    if from_unit == "F":
        celsius = (value - 32) * 5/9
    elif from_unit == "K":
        celsius = value - 273.15
    else: # from_unit == "C"
        celsius = value

    # Convert Celsius to target unit
    if to_unit == "F":
        return (celsius * 9/5) + 32
    elif to_unit == "K":
        return celsius + 273.15
    else: # to_unit == "C"
        return celsius

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
    st.set_page_config(page_title="Unit Converter Pro", layout="wide", page_icon="🔄")
    local_css()

    st.markdown("<h1 class='header-title'>Unit Converter Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='secondary-text'>Your one-stop solution for quick and accurate unit conversions across various categories.</p>", unsafe_allow_html=True)

    # User inputs
    col1, col2 = st.columns([1, 3])
    
    with col1:
        category_names = list(UNITS_DATA.keys())
        selected_category_name = st.selectbox("Select Category:", category_names)
        
        category_data = UNITS_DATA[selected_category_name]
        unit_options = list(category_data['units'].keys())

        from_unit = st.selectbox("From Unit:", unit_options, key=f"from_unit_{selected_category_name}")
        to_unit = st.selectbox("To Unit:", unit_options, key=f"to_unit_{selected_category_name}")
        value_to_convert = st.number_input("Enter Value:", value=1.0, format="%.4f")

    # Perform conversion and display result
    converted_value = None
    if value_to_convert is not None and from_unit and to_unit:
        if category_data.get('type') == 'temperature':
            converted_value = convert_temperature(value_to_convert, from_unit, to_unit)
        else:
            converted_value = convert_standard(value_to_convert, from_unit, to_unit, category_data)

    with col2:
        if converted_value is not None:
            st.markdown(f"<div class='result-display'>{value_to_convert:.4f} {from_unit} = {converted_value:.4f} {to_unit}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='result-display'>Enter values to see the conversion.</div>", unsafe_allow_html=True)
    
    st.markdown("---<br><small>Powered by Streamlit. Fonts: Inter & Poppins. Colors by design spec.</small>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
