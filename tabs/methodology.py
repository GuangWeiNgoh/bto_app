import streamlit as st
import os

def display():
    st.title("📚 Methodology")
    st.write("Decision Flowchart for \"HDB Resale Transactions Explorer\" and \"HDB Assistant\".")

    with open("images/HDB_Explorer_Methodology.svg", "r", encoding="utf-8") as svg_file:
        svg_content = svg_file.read()

        st.markdown(
            f'''
            <div style="display: flex; justify-content: center; overflow: hidden;">
                <div style="width: 100%; height: auto;">
                    {svg_content}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.write("")

    with st.expander("View PNG Version", expanded=False):
        st.image("images/HDB_Explorer_Methodology.png", caption="Methodology Diagram (PNG)", use_column_width=True)
