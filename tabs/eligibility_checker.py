import streamlit as st

def display():
    st.title("🏠 BTO Eligibility Checker")
    st.write("Check your eligibility for BTO flats here.")
    
    # Citizenship Dropdown
    citizenship_options = ["Singapore Citizen", "Singapore Permanent Resident", "Foreigner"]
    citizen = st.selectbox("Select your citizenship status:", citizenship_options)

    # Age Input
    age = st.number_input("Enter your age:", min_value=0)

    # Family nucleus Dropdown
    family_nucleus_options = [
        "Public Scheme (spouse, parents, children)",
        "Fiancé/Fiancée Scheme",
        "Orphan Scheme (unmarried siblings)",
        "Single Bachelor Scheme (age 35 and above)"
    ]
    family_nucleus = st.selectbox("Select your family nucleus type:", family_nucleus_options)

    # Income Ceiling Input
    income = st.number_input("Enter your average gross monthly household income (SGD):", min_value=0)

    # Property Ownership Radio Button
    owns_property = st.radio("Do you own any other property locally or overseas?", ("Yes", "No"), index=1)

    # Previous Property Disposal Radio Button
    disposed_property = st.radio("Have you disposed of any private property within the last 30 months?", ("Yes", "No"), index=1)

    if st.button("Check Eligibility"):
        # Eligibility logic
        eligible = True
        eligibility_message = ""

        # Check Citizenship
        if citizen == "Foreigner":
            eligible = False
            eligibility_message += "At least one applicant must be a Singapore Citizen or Permanent Resident.\n"

        # Check Age
        if age < 21:
            eligible = False
            eligibility_message += "Applicants must be at least 21 years old.\n"

        # Check Family nucleus
        if family_nucleus == "Single Bachelor Scheme (age 35 and above)" and age < 35:
            eligible = False
            eligibility_message += "Applicants under the Single Bachelor Scheme must be at least 35 years old.\n"
        
        # Special Check for Fiancé/Fiancée Scheme
        if family_nucleus == "Fiancé/Fiancée Scheme" and citizen == "Foreigner" and age < 21:
            eligible = False
            eligibility_message += "You must be at least 21 years old and engaged to apply under the Fiancé/Fiancée Scheme.\n"
        
        if family_nucleus == "Public Scheme (spouse, parents, children)" and citizen == "Foreigner":
            eligible = False
            eligibility_message += "You cannot apply under the Public Scheme with a foreigner as a spouse unless you are married.\n"

        # Check Income ceiling (example values)
        if income > 14_000:  # Change this value based on current BTO income ceiling
            eligible = False
            eligibility_message += "Average gross monthly household income must not exceed $14,000.\n"

        # Check Property ownership
        if owns_property == "Yes":
            eligible = False
            eligibility_message += "Applicants must not own any other property locally or overseas.\n"

        # Check Previous property disposal
        if disposed_property == "Yes":
            eligible = False
            eligibility_message += "Applicants must not have disposed of any private property within the last 30 months.\n"

        # Final eligibility output
        if eligible:
            st.success("You are eligible to apply for a BTO flat!")
        else:
            st.error("You are not eligible to apply for a BTO flat:\n" + eligibility_message)

# Run the function to display the eligibility checker
if __name__ == "__main__":
    display()
