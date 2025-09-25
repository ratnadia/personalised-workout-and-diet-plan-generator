<<<<<<< HEAD
import streamlit as st
import json
import google.generativeai as genai

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Workout & Diet Planner",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    body, .reportview-container, .main {
        background: #121212;
        color: #FFFFFF;
    }
    h1, h2, h3, h4 {
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 1rem;
        border: none;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #444;
        border-radius: 10px;
        padding: 8px;
        background: #1e1e1e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    [data-testid="stMetricValue"] {
        color: #4CAF50;
        font-size: 1.3rem;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    .stTextArea>div>div>textarea {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    .stSelectbox>div>div>div>div>div>input {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

# --- API Key Configuration ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API key not found! Please create a `.streamlit/secrets.toml` file.")
    st.stop()

# --- Functions ---
def generate_plan(user_data):
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

    prompt = f"""
    You are an expert personal trainer and nutritionist. Generate a comprehensive 7-day personalized workout and diet plan.
    User details:
    - Gender: {user_data['gender']}
    - Age: {user_data['age']} years
    - Height: {user_data['height']} cm
    - Weight: {user_data['weight']} kg
    - Goal: {user_data['goal']}
    - Dietary Preferences: {user_data['diet']}
    - Food Allergies/Dislikes: {user_data['dislikes']}
    - Medical Conditions: {user_data['medical_conditions']}
    - Supplements: {user_data['supplements']}

    Response format: a single JSON object with the following keys:
    - `workout_plan`: An object with keys "Monday" to "Sunday", each containing "focus" and a list of "exercises".
    - `meal_plan`: An object with keys "Monday" to "Sunday", each containing "breakfast", "lunch", and "dinner".
    - `shopping_list`: A single list of strings of all unique ingredients.
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        # The API is configured to return JSON, so we can access it directly.
        return json.loads(response.text)
    except Exception as e:
        # If the model doesn't return valid JSON, try parsing the text and cleaning it up.
        try:
            raw_text = response.text.strip('`').strip('json').strip()
            return json.loads(raw_text)
        except Exception as e2:
            st.error(f"Failed to parse JSON response. The model may have returned invalid data.")
            st.code(response.text)
            return None

# --- Main App ---
st.title("🏋️‍♂️ AI-Powered Workout & Diet Planner 🍎")
st.markdown("""
    <div style="text-align: center; color: #E0E0E0; font-size: 1.1rem; margin-top: -1rem; margin-bottom: 2rem;">
        Fill out the form below to get a personalized 7-day plan.
    </div>
""", unsafe_allow_html=True)

# --- User Input Form ---
with st.form("user_form"):
    st.markdown("### 👤 Personal Information")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        gender = st.selectbox("Gender", ["Male", "Female"])
    with col2:
        age = st.number_input("Age", 1, 120, 25)
    with col3:
        height = st.number_input("Height (cm)", 100, 250, 170)
    with col4:
        weight = st.number_input("Weight (kg)", 30, 200, 65)

    st.markdown("### 🎯 Goals & Preferences")
    goal = st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Maintenance", "General Fitness"])
    diet = st.text_input("Dietary Preference (e.g., Vegetarian, Keto)")

    col5, col6 = st.columns(2)
    with col5:
        dislikes = st.text_area("❌ Allergies / Dislikes", height=80)
    with col6:
        medical_conditions = st.text_area("⚠️ Medical Conditions", height=80)

    supplements = st.text_area("💊 Supplements", height=60)

    submitted = st.form_submit_button("🚀 Generate My Plan")

if submitted:
    user_data = {
        "gender": gender,
        "age": age,
        "height": height,
        "weight": weight,
        "goal": goal,
        "diet": diet,
        "dislikes": dislikes,
        "medical_conditions": medical_conditions,
        "supplements": supplements
    }

    with st.spinner("Generating your personalized plan..."):
        plan = generate_plan(user_data)

    if plan:
        st.success("✅ Plan generated successfully!")

        # Dashboard-style summary
        col1, col2, col3 = st.columns(3)
        col1.metric("Age", f"{user_data['age']} yrs")
        col2.metric("Weight", f"{user_data['weight']} kg")
        col3.metric("Goal", user_data['goal'])

        # Tabs for detailed plan
        tab_workout, tab_meals, tab_shopping = st.tabs(["💪 Workout Plan", "🥗 Meal Plan", "🛒 Shopping List"])

        with tab_workout:
            st.header("7-Day Workout Plan")
            workout_plan = plan.get("workout_plan", {})
            if isinstance(workout_plan, dict):
                for day, details in workout_plan.items():
                    with st.expander(f"📅 {day} - {details.get('focus','')}"):
                        for exercise in details.get("exercises", []):
                            st.markdown(f"- {exercise}")
            elif isinstance(workout_plan, list):
                for idx, details in enumerate(workout_plan, start=1):
                    with st.expander(f"📅 Day {idx} - {details.get('focus','')}"):
                        for exercise in details.get("exercises", []):
                            st.markdown(f"- {exercise}")

        with tab_meals:
            st.header("7-Day Meal Plan")
            meal_plan = plan.get("meal_plan", {})
            if isinstance(meal_plan, dict):
                for day, meals in meal_plan.items():
                    with st.expander(f"📅 {day}"):
                        st.markdown(f"**Breakfast:** {meals.get('breakfast', 'N/A')}")
                        st.markdown(f"**Lunch:** {meals.get('lunch', 'N/A')}")
                        st.markdown(f"**Dinner:** {meals.get('dinner', 'N/A')}")
            elif isinstance(meal_plan, list):
                for idx, meals in enumerate(meal_plan, start=1):
                    with st.expander(f"📅 Day {idx}"):
                        st.markdown(f"**Breakfast:** {meals.get('breakfast', 'N/A')}")
                        st.markdown(f"**Lunch:** {meals.get('lunch', 'N/A')}")
                        st.markdown(f"**Dinner:** {meals.get('dinner', 'N/A')}")

        with tab_shopping:
            st.header("🛒 Shopping List")
            shopping_list = plan.get("shopping_list", [])
            if shopping_list:
                cols = st.columns(3)
                for idx, item in enumerate(shopping_list):
                    cols[idx % 3].markdown(f"- {item}")
            else:
                st.warning("No shopping list generated.")
=======
import streamlit as st
import json
import google.generativeai as genai

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Workout & Diet Planner",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    body, .reportview-container, .main {
        background: #121212;
        color: #FFFFFF;
    }
    h1, h2, h3, h4 {
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 1rem;
        border: none;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #444;
        border-radius: 10px;
        padding: 8px;
        background: #1e1e1e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    [data-testid="stMetricValue"] {
        color: #4CAF50;
        font-size: 1.3rem;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    .stTextArea>div>div>textarea {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    .stSelectbox>div>div>div>div>div>input {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

# --- API Key Configuration ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API key not found! Please create a `.streamlit/secrets.toml` file.")
    st.stop()

# --- Functions ---
def generate_plan(user_data):
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

    prompt = f"""
    You are an expert personal trainer and nutritionist. Generate a comprehensive 7-day personalized workout and diet plan.
    User details:
    - Gender: {user_data['gender']}
    - Age: {user_data['age']} years
    - Height: {user_data['height']} cm
    - Weight: {user_data['weight']} kg
    - Goal: {user_data['goal']}
    - Dietary Preferences: {user_data['diet']}
    - Food Allergies/Dislikes: {user_data['dislikes']}
    - Medical Conditions: {user_data['medical_conditions']}
    - Supplements: {user_data['supplements']}

    Response format: a single JSON object with the following keys:
    - `workout_plan`: An object with keys "Monday" to "Sunday", each containing "focus" and a list of "exercises".
    - `meal_plan`: An object with keys "Monday" to "Sunday", each containing "breakfast", "lunch", and "dinner".
    - `shopping_list`: A single list of strings of all unique ingredients.
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        # The API is configured to return JSON, so we can access it directly.
        return json.loads(response.text)
    except Exception as e:
        # If the model doesn't return valid JSON, try parsing the text and cleaning it up.
        try:
            raw_text = response.text.strip('`').strip('json').strip()
            return json.loads(raw_text)
        except Exception as e2:
            st.error(f"Failed to parse JSON response. The model may have returned invalid data.")
            st.code(response.text)
            return None

# --- Main App ---
st.title("🏋️‍♂️ AI-Powered Workout & Diet Planner 🍎")
st.markdown("""
    <div style="text-align: center; color: #E0E0E0; font-size: 1.1rem; margin-top: -1rem; margin-bottom: 2rem;">
        Fill out the form below to get a personalized 7-day plan.
    </div>
""", unsafe_allow_html=True)

# --- User Input Form ---
with st.form("user_form"):
    st.markdown("### 👤 Personal Information")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        gender = st.selectbox("Gender", ["Male", "Female"])
    with col2:
        age = st.number_input("Age", 1, 120, 25)
    with col3:
        height = st.number_input("Height (cm)", 100, 250, 170)
    with col4:
        weight = st.number_input("Weight (kg)", 30, 200, 65)

    st.markdown("### 🎯 Goals & Preferences")
    goal = st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Maintenance", "General Fitness"])
    diet = st.text_input("Dietary Preference (e.g., Vegetarian, Keto)")

    col5, col6 = st.columns(2)
    with col5:
        dislikes = st.text_area("❌ Allergies / Dislikes", height=80)
    with col6:
        medical_conditions = st.text_area("⚠️ Medical Conditions", height=80)

    supplements = st.text_area("💊 Supplements", height=60)

    submitted = st.form_submit_button("🚀 Generate My Plan")

if submitted:
    user_data = {
        "gender": gender,
        "age": age,
        "height": height,
        "weight": weight,
        "goal": goal,
        "diet": diet,
        "dislikes": dislikes,
        "medical_conditions": medical_conditions,
        "supplements": supplements
    }

    with st.spinner("Generating your personalized plan..."):
        plan = generate_plan(user_data)

    if plan:
        st.success("✅ Plan generated successfully!")

        # Dashboard-style summary
        col1, col2, col3 = st.columns(3)
        col1.metric("Age", f"{user_data['age']} yrs")
        col2.metric("Weight", f"{user_data['weight']} kg")
        col3.metric("Goal", user_data['goal'])

        # Tabs for detailed plan
        tab_workout, tab_meals, tab_shopping = st.tabs(["💪 Workout Plan", "🥗 Meal Plan", "🛒 Shopping List"])

        with tab_workout:
            st.header("7-Day Workout Plan")
            workout_plan = plan.get("workout_plan", {})
            if isinstance(workout_plan, dict):
                for day, details in workout_plan.items():
                    with st.expander(f"📅 {day} - {details.get('focus','')}"):
                        for exercise in details.get("exercises", []):
                            st.markdown(f"- {exercise}")
            elif isinstance(workout_plan, list):
                for idx, details in enumerate(workout_plan, start=1):
                    with st.expander(f"📅 Day {idx} - {details.get('focus','')}"):
                        for exercise in details.get("exercises", []):
                            st.markdown(f"- {exercise}")

        with tab_meals:
            st.header("7-Day Meal Plan")
            meal_plan = plan.get("meal_plan", {})
            if isinstance(meal_plan, dict):
                for day, meals in meal_plan.items():
                    with st.expander(f"📅 {day}"):
                        st.markdown(f"**Breakfast:** {meals.get('breakfast', 'N/A')}")
                        st.markdown(f"**Lunch:** {meals.get('lunch', 'N/A')}")
                        st.markdown(f"**Dinner:** {meals.get('dinner', 'N/A')}")
            elif isinstance(meal_plan, list):
                for idx, meals in enumerate(meal_plan, start=1):
                    with st.expander(f"📅 Day {idx}"):
                        st.markdown(f"**Breakfast:** {meals.get('breakfast', 'N/A')}")
                        st.markdown(f"**Lunch:** {meals.get('lunch', 'N/A')}")
                        st.markdown(f"**Dinner:** {meals.get('dinner', 'N/A')}")

        with tab_shopping:
            st.header("🛒 Shopping List")
            shopping_list = plan.get("shopping_list", [])
            if shopping_list:
                cols = st.columns(3)
                for idx, item in enumerate(shopping_list):
                    cols[idx % 3].markdown(f"- {item}")
            else:
                st.warning("No shopping list generated.")
>>>>>>> 4175920cfe924feb6304093f8c0e4b34d4bde8d7
