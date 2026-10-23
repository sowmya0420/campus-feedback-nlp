"""streamlit run app/app.py   (from project root)"""
import sys, os, datetime
sys.path.insert(0, os.getcwd())
import pandas as pd, plotly.express as px, streamlit as st

st.set_page_config(page_title="Campus Feedback Analysis", layout="wide")
OUT = "data/outputs"
@st.cache_data
def load(name): return pd.read_csv(f"{OUT}/{name}")

page = st.sidebar.radio("Page", ["Ratings", "Recurring issues", "Flagged abusive comments", "Summaries", "Submit feedback"])

if page == "Ratings":
    r = load("ratings.csv")
    ov = r[r.category == "OVERALL"]
    st.subheader("Overall facility ratings (1-5)")
    st.plotly_chart(px.bar(ov, x="facility", y="rating", range_y=[1, 5], text="rating"), use_container_width=True)
    fac = st.selectbox("Facility", sorted(ov.facility))
    a = r[(r.facility == fac) & (r.category != "OVERALL")]
    st.plotly_chart(px.bar(a, x="category", y="rating", range_y=[1, 5], hover_data=["mentions", "negative_share"],
                           title=f"{fac}: rating by aspect"), use_container_width=True)
    st.dataframe(a.sort_values("rating"), hide_index=True)

elif page == "Recurring issues":
    i = load("issues.csv")
    st.subheader("Recurring issues (high negative share, enough mentions)")
    fac = st.selectbox("Facility", ["All"] + sorted(i.facility.unique()))
    st.dataframe(i if fac == "All" else i[i.facility == fac], hide_index=True)

elif page == "Flagged abusive comments":
    p = load("predictions.csv")
    flagged = p[p.abusive][["id", "facility", "text"]].drop_duplicates()
    st.subheader(f"{len(flagged)} comments flagged and excluded from ratings")
    st.dataframe(flagged, hide_index=True)

elif page == "Summaries":
    for row in load("summaries.csv").itertuples():
        st.markdown(f"**{row.facility.replace('_', ' ').title()}**"); st.write(row.summary)

else:
    from src.pipeline import analyse
    st.subheader("Anonymous feedback (no name or email is collected)")
    fac = st.selectbox("Facility", ["library", "hostel_mess", "canteen", "hostel_rooms", "labs", "wifi", "transport", "classrooms"])
    text = st.text_area("Your comment")
    if st.button("Submit") and text.strip():
        res = analyse(text, fac)
        row = {"timestamp": datetime.datetime.now().isoformat(timespec="seconds"), "facility": fac, "text": text,
               "abusive": res["abusive"], "aspects": "; ".join(f"{a['category']}={a['sentiment']}" for a in res["aspects"])}
        path = f"{OUT}/live_feedback.csv"
        pd.DataFrame([row]).to_csv(path, mode="a", header=not os.path.exists(path), index=False)
        st.success("Thank you, your feedback was recorded.")
        if res["abusive"]: st.warning("This comment was flagged as abusive and will be excluded from ratings.")
        else: st.write({a["category"]: a["sentiment"] for a in res["aspects"]})
