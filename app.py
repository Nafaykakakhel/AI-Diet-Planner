
import os
import streamlit as st
from google import genai
from google.genai import types


# -----------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------

st.set_page_config(
    page_title="AI Diet Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------------------
# CUSTOM STYLING
# -----------------------------------------

st.markdown("""
<style>
    .main {
        background-color: #f7faf8;
    }

    .main-title {
        color: #16845b;
        font-size: 38px;
        font-weight: 800;
    }

    .subtitle {
        color: #64748b;
        font-size: 17px;
    }

    .stButton > button {
        background-color: #16845b;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }

    .stButton > button:hover {
        background-color: #106b48;
        color: white;
    }

    .info-card {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------
# GEMINI CONFIGURATION
# -----------------------------------------


def get_api_key():
    """Safely retrieve the Gemini API key."""

    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""

    if not key:
        key = os.getenv("GEMINI_API_KEY", "")

    return key.strip() if key else ""


def generate_diet_plan(prompt):

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "Gemini API key is missing. "
            "Please configure GEMINI_API_KEY in Streamlit Secrets."
        )

    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-flash-latest"
    )

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=3000
            )
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text

    except Exception as error:
        error_message = str(error)

        if "401" in error_message or "UNAUTHENTICATED" in error_message:
            raise ValueError(
                "Gemini authentication failed. "
                "Check your Google AI Studio API key and "
                "Streamlit Cloud Secrets."
            ) from None

        raise RuntimeError(
            "Gemini API request failed. Please check "
            "your model configuration and API availability."
        ) from None


# -----------------------------------------
# PROMPT GENERATOR
# -----------------------------------------

def create_prompt(data):

    prompt = f"""
You are an AI nutrition education assistant.

Create a practical, well-organized meal plan using the
following user information.

USER PROFILE
------------
Age: {data['age']}
Gender: {data['gender']}
Weight: {data['weight']} kg
Height: {data['height']} cm
Activity Level: {data['activity']}
Goal: {data['goal']}

DIET PREFERENCES
----------------
Food Preference: {data['food']}
Cuisine: {data['cuisine']}
Budget: {data['budget']}
Allergies: {data['allergies']}
Additional Information: {data['additional']}

SCENARIO
--------
{data['scenario']}

SCENARIO-SPECIFIC INSTRUCTIONS
------------------------------

1. GYM & FITNESS:
   - Focus on the selected fitness goal.
   - Include appropriate protein sources.
   - Suggest pre-workout and post-workout meals.
   - Include hydration guidance.
   - Avoid extreme calorie deficits or excessive protein advice.

2. HEALTHCARE:
   - Provide general nutrition education only.
   - Do not diagnose, treat, or claim to cure any illness.
   - Do not prescribe therapeutic diets, medication changes,
     supplements, or disease-specific nutrient restrictions.
   - If a medical condition is provided, explain that the
     appropriate diet depends on clinical details and should
     be reviewed by a qualified doctor or registered dietitian.
   - For serious conditions, recommend professional guidance
     before following the suggested menu.
   - Never invent medical requirements.

3. REGULAR DIET:
   - Focus on balanced everyday nutrition.
   - Include fruits, vegetables, whole grains and protein.
   - Suggest affordable and practical meals.

OUTPUT FORMAT
-------------

# Personalized Diet Plan

## 1. Overview
Summarize the user's goal and preferences.

## 2. Daily Meal Plan
Provide a table with:
- Meal
- Suggested food
- Approximate portion
- Estimated calories

Include:
- Breakfast
- Morning snack
- Lunch
- Evening snack
- Dinner

## 3. Estimated Nutrition
Provide approximate daily:
- Calories
- Protein
- Carbohydrates
- Fat

Clearly state that these are estimates, not medical targets.

## 4. Food Recommendations
List useful food choices.

## 5. Foods to Limit
Give reasonable suggestions without unnecessary restrictions.

## 6. Hydration
Give general hydration advice.

## 7. Practical Tips
Provide useful lifestyle and meal preparation advice.

IMPORTANT SAFETY RULES
----------------------
- Do not present estimates as exact nutritional values.
- Do not guarantee weight loss or muscle gain.
- Do not recommend starvation, crash diets or extreme fasting.
- Respect allergies and food preferences.
- If information is insufficient for safe recommendations,
  explain what needs professional assessment.
- Keep the plan practical, clear and easy to follow.
- Do not pretend to be a doctor or registered dietitian.

Generate the response in clear Markdown.
"""

    return prompt


# -----------------------------------------
# HEADER
# -----------------------------------------

st.markdown(
    '<div class="main-title">🥗 AI Diet Planner</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your personal AI-powered nutrition planning assistant.'
    '</div>',
    unsafe_allow_html=True
)

st.write("")

st.info(
    "Create meal plans for fitness, general healthcare "
    "nutrition education, and everyday healthy eating."
)


# -----------------------------------------
# SIDEBAR
# -----------------------------------------

with st.sidebar:

    st.title("🥗 Diet Planner")

    st.markdown("---")

    scenario = st.selectbox(
        "Choose Diet Scenario",
        [
            "Regular Diet",
            "Gym & Fitness Diet",
            "Healthcare Diet"
        ]
    )

    st.markdown("---")

    st.caption("Powered by Google Gemini Flash")


# -----------------------------------------
# USER INPUT FORM
# -----------------------------------------

st.subheader("👤 Personal Information")

with st.form("diet_form"):

    col1, col2 = st.columns(2)

    with col1:

        age = st.number_input(
            "Age",
            min_value=18,
            max_value=100,
            value=25,
            step=1
        )

        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other", "Prefer not to say"]
        )

        weight = st.number_input(
            "Weight (kg)",
            min_value=30.0,
            max_value=300.0,
            value=70.0,
            step=0.5
        )

    with col2:

        height = st.number_input(
            "Height (cm)",
            min_value=100.0,
            max_value=250.0,
            value=170.0,
            step=0.5
        )

        activity = st.selectbox(
            "Activity Level",
            [
                "Sedentary",
                "Lightly Active",
                "Moderately Active",
                "Very Active"
            ]
        )

        goal = st.selectbox(
            "Your Goal",
            [
                "Maintain Weight",
                "Lose Weight",
                "Gain Weight",
                "Build Muscle",
                "Improve General Health"
            ]
        )

    st.markdown("---")

    st.subheader("🍎 Food Preferences")

    col3, col4 = st.columns(2)

    with col3:

        food = st.selectbox(
            "Food Type",
            [
                "Vegetarian",
                "Non-Vegetarian",
                "Vegan",
                "Eggetarian"
            ]
        )

        cuisine = st.selectbox(
            "Preferred Cuisine",
            [
                "Pakistani",
                "Indian",
                "Continental",
                "Mediterranean",
                "Mixed / No Preference"
            ]
        )

    with col4:

        budget = st.selectbox(
            "Daily Food Budget",
            [
                "Low Budget",
                "Medium Budget",
                "High Budget",
                "No Budget Restriction"
            ]
        )

        allergies = st.text_input(
            "Food Allergies",
            placeholder="Example: peanuts, milk, eggs"
        )

    st.markdown("---")

    st.subheader("🎯 Additional Information")

    if scenario == "Gym & Fitness Diet":

        additional = st.text_area(
            "Workout Details",
            placeholder=(
                "Example: Gym 5 days a week, "
                "strength training, workout in the evening."
            )
        )

    elif scenario == "Healthcare Diet":

        additional = st.text_area(
            "Health Information (Optional)",
            placeholder=(
                "Describe the general health concern. "
                "Do not include private identifying information."
            )
        )

        st.warning(
            "This mode provides general nutrition education, "
            "not a therapeutic diet or medical treatment. "
            "Consult a qualified healthcare professional."
        )

    else:

        additional = st.text_area(
            "Additional Preferences",
            placeholder=(
                "Example: Office worker, prefer simple "
                "homemade meals."
            )
        )

    submitted = st.form_submit_button(
        "✨ Generate My Diet Plan",
        use_container_width=True
    )


# -----------------------------------------
# GENERATE DIET PLAN
# -----------------------------------------

if submitted:

    if height <= 0 or weight <= 0:
        st.error("Please enter valid height and weight.")

    elif not allergies.strip():
        allergies = "None specified"

    data = {
        "scenario": scenario,
        "age": age,
        "gender": gender,
        "weight": weight,
        "height": height,
        "activity": activity,
        "goal": goal,
        "food": food,
        "cuisine": cuisine,
        "budget": budget,
        "allergies": allergies,
        "additional": additional
    }

    prompt = create_prompt(data)

    try:

        with st.spinner(
            "🥗 Gemini is preparing your personalized diet plan..."
        ):

            diet_plan = generate_diet_plan(prompt)

        st.session_state["diet_plan"] = diet_plan
        st.session_state["diet_scenario"] = scenario

    except ValueError as error:
        st.error(str(error))

    except Exception as error:
        st.error(
            "Unable to generate your diet plan. "
            "Please check your API key, internet connection, "
            "model availability and API quota."
        )

        with st.expander("Technical error details"):
            st.code(str(error))


# -----------------------------------------
# DISPLAY RESULT
# -----------------------------------------

if st.session_state.get("diet_plan"):

    st.markdown("---")

    st.subheader("📋 Your Personalized Diet Plan")

    st.caption(
        f"Scenario: {st.session_state.get('diet_scenario', '')}"
    )

    st.markdown(st.session_state["diet_plan"])

    st.markdown("---")

    st.download_button(
        label="📥 Download Diet Plan",
        data=st.session_state["diet_plan"],
        file_name="my_diet_plan.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.success("Your diet plan is ready!")

    st.caption(
        "Disclaimer: AI-generated nutrition information may "
        "be inaccurate. Consult a qualified professional for "
        "personalized medical nutrition advice."
    )


# -----------------------------------------
# FOOTER
# -----------------------------------------

st.markdown("---")

st.caption(
    "AI Diet Planner | Built with Streamlit and Google Gemini"
)
