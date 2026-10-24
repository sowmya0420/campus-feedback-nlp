"""streamlit run app/app.py   (from project root)"""
import sys, os, datetime
sys.path.insert(0, os.getcwd())
import pandas as pd, plotly.express as px, streamlit as st

st.set_page_config(page_title="Campus Feedback Analysis", layout="wide")
OUT = "data/outputs"
@st.cache_data
def load(name): return pd.read_csv(f"{OUT}/{name}")

page = st.sidebar.radio("Page", ["Ratings", "Aspect sentiment", "Recurring issues", "Flagged abusive comments", "Summaries", "Submit feedback"])

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

elif page == "Aspect sentiment":
    r, p = load("ratings.csv"), load("predictions.csv")
    p = p[(~p.abusive) & (p.category != "general")]   # same filter as the ratings: no abusive or aspect-less comments
    st.subheader("Aspect-based sentiment")
    st.caption("Each comment is split into aspects (such as food quality or price). "
               "Every aspect is labelled positive, neutral or negative by the DistilBERT model. "
               "Abusive comments and comments with no specific aspect are left out, as in the ratings.")
    fac = st.selectbox("Facility", ["All"] + sorted(r.facility.unique()))
    a = r[r.category != "OVERALL"]
    if fac != "All":
        a = a[a.facility == fac]
    mix = a.groupby("category")[["positive", "neutral", "negative"]].sum().reset_index()
    mix["total"] = mix[["positive", "neutral", "negative"]].sum(axis=1)
    mix = mix.sort_values("total", ascending=False)
    c1, c2, c3 = st.columns(3)
    c1.metric("Positive", int(mix.positive.sum()))
    c2.metric("Neutral", int(mix.neutral.sum()))
    c3.metric("Negative", int(mix.negative.sum()))
    long = mix.melt(id_vars="category", value_vars=["positive", "neutral", "negative"],
                    var_name="sentiment", value_name="mentions")
    st.plotly_chart(px.bar(long, x="category", y="mentions", color="sentiment", barmode="stack",
                           color_discrete_map={"positive": "#2e9e5b", "neutral": "#9aa0a6", "negative": "#d64545"},
                           category_orders={"category": list(mix.category),
                                            "sentiment": ["positive", "neutral", "negative"]},
                           title=f"Sentiment by aspect: {fac.replace('_', ' ')}"), use_container_width=True)

    st.markdown("#### Comments with their aspect sentiment")
    t = p if fac == "All" else p[p.facility == fac]
    f1, f2 = st.columns(2)
    asp = f1.selectbox("Aspect", ["All"] + sorted(t.category.unique()))
    sen = f2.selectbox("Sentiment", ["All", "positive", "neutral", "negative"])
    if asp != "All":
        t = t[t.category == asp]
    if sen != "All":
        t = t[t.sentiment == sen]
    st.caption(f"{len(t)} aspect mentions")
    st.dataframe(t[["facility", "text", "category", "sentiment"]], hide_index=True)

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