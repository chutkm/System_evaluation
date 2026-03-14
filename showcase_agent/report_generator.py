import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:pass@localhost/db"

engine = create_engine(DATABASE_URL)

st.set_page_config(
    page_title="Мониторинг удовлетворенности студентов",
    layout="wide"
)

st.title("📊 Мониторинг удовлетворенности студентов")

df = pd.read_sql("SELECT * FROM feedback", engine)

# ---------------- ФИЛЬТРЫ ----------------

group_filter = st.sidebar.selectbox(
    "Группа",
    ["Все"] + sorted(df["group_name"].unique())
)

if group_filter != "Все":
    df = df[df["group_name"] == group_filter]

# ---------------- KPI ----------------

col1, col2, col3 = st.columns(3)

col1.metric("Средняя оценка", round(df["rating"].mean(), 2))
col2.metric("Количество отзывов", len(df))
col3.metric(
    "Негативные отзывы",
    (df["sentiment"] == "negative").sum()
)

# ---------------- ГРАФИК ОЦЕНОК ----------------

fig = px.histogram(
    df,
    x="rating",
    title="Распределение оценок"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- SENTIMENT ----------------

sentiment_counts = df["sentiment"].value_counts()

fig2 = px.pie(
    values=sentiment_counts.values,
    names=sentiment_counts.index,
    title="Тональность отзывов"
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------- ТОП ПРОБЛЕМ ----------------

st.subheader("Проблемные темы")

topics = (
    df["topics"]
    .dropna()
    .explode()
    .value_counts()
    .head(10)
)

st.bar_chart(topics)


json_file = '{""auditorium"": ""1-4 \u043a\u043e\u0440\u043f\u0443\u0441/1-204"", ""auditoriumAmount"": 34, ""auditoriumGUID"": ""6d515522-5bb6-4489-a46b-ddfd7db3af5b"", ""auditoriumOid"": 80, ""author"": ""MSTUCA\\m.semina"", ""beginLesson"": ""12:40"", ""building"": ""\u041f\u0443\u043b\u043a\u043e\u0432\u0441\u043a\u0430\u044f \u0443\u043b\u0438\u0446\u0430, \u0434\u043e\u043c 6"", ""buildingGid"": 0, ""buildingOid"": 5, ""contentOfLoadOid"": 33687, ""contentOfLoadUID"": ""\u041d\u0430\u0433\u0440\u0443\u0437\u043a\u0430.281474976752048"", ""contentTableOfLessonsName"": 3, ""contentTableOfLessonsOid"": 12, ""createddate"": ""2025-07-21T15:39:59Z00:00"", ""date"": ""2025-10-14"", ""dateOfNest"": ""/Date(1760389200000+0300)/"", ""dayOfWeek"": 2, ""dayOfWeekString"": ""\u0412\u0442"", ""detailInfo"": """", ""discipline"": ""\u0422\u0435\u043e\u0440\u0435\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u043e\u0441\u043d\u043e\u0432\u044b \u044d\u043b\u0435\u043a\u0442\u0440\u043e\u0442\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u043e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u044f \u0432\u043e\u0437\u0434\u0443\u0448\u043d\u044b\u0445 \u0441\u0443\u0434\u043e\u0432"", ""disciplineOid"": 3570, ""disciplineASAV_UID"": null, ""disciplineMDM_UID"": null, ""disciplineinplan"": null, ""disciplinetypeload"": 0, ""duration"": 2, ""endLesson"": ""14:10"", ""group"": null, ""groupGUID"": null, ""groupOid"": 0, ""groupUID"": null, ""group_facultyoid"": 0, ""group_facultyASAV_UID"": null, ""group_facultyHR_UID"": null, ""group_facultyUID"": null, ""groupHR_UID"": null, ""groupASAV_UID"": null, ""groupMDM_UID"": null, ""hideincapacity"": 0, ""isBan"": 0, ""kindOfWork"": ""\u041b\u0435\u043a\u0446\u0438\u0438"", ""kindOfWorkComplexity"": 1, ""kindOfWorkOid"": 95, ""kindOfWorkUid"": ""26003.281474976710657"", ""personHR_Person_ID"": null, ""personMDM_Person_UID"": null, ""lecturer"": ""\u0425\u0430\u043b\u044e\u0442\u0438\u043d \u0421.\u041f."", ""lecturerCustomUID"": ""dc858a98-08a2-11e7-830a-000c29ede4ea"", ""lecturerEmail"": """", ""lecturerGUID"": ""b8078f36-3901-4d9e-be47-0a59b8163b2d"", ""lecturerOid"": 1051, ""lecturerUID"": ""26115.281474976710803"", ""lecturer_postUID"": null, ""lecturer_postASAV_UID"": null, ""lecturer_postMDM_UID"": null, ""lecturerASAV_UID"": null, ""lecturerMDM_UID"": null, ""lecturer_rank"": ""\u0417\u0430\u0432\u0435\u0434\u0443\u044e\u0449\u0438\u0439 \u043a\u0430\u0444\u0435\u0434\u0440\u043e\u0439 "", ""lecturer_title"": ""\u0425\u0430\u043b\u044e\u0442\u0438\u043d \u0421\u0435\u0440\u0433\u0435\u0439 \u041f\u0435\u0442\u0440\u043e\u0432\u0438\u0447"", ""lessonNumberEnd"": 3, ""lessonNumberStart"": 3, ""lessonOid"": 127401, ""listGroups"": [], ""listSubGroups"": [], ""listOfLecturers"": [{""lecturer"": ""\u0425\u0430\u043b\u044e\u0442\u0438\u043d \u0421.\u041f."", ""lecturerCustomUID"": ""dc858a98-08a2-11e7-830a-000c29ede4ea"", ""lecturerEmail"": """", ""lecturerGUID"": null, ""lecturerOid"": 1051, ""lecturerUID"": ""26115.281474976710803"", ""lecturer_post_oid"": 25, ""lecturer_rank"": ""\u0417\u0430\u0432\u0435\u0434\u0443\u044e\u0449\u0438\u0439 \u043a\u0430\u0444\u0435\u0434\u0440\u043e\u0439 "", ""lecturer_title"": ""\u0425\u0430\u043b\u044e\u0442\u0438\u043d \u0421\u0435\u0440\u0433\u0435\u0439 \u041f\u0435\u0442\u0440\u043e\u0432\u0438\u0447""}], ""modifieddate"": ""2025-07-21T15:39:59Z00:00"", ""note"": null, ""note_description"": """", ""parentschedule"": ""\u041c\u0410\u0413-\u0410\u041a_\u0417 251"", ""replaces"": null, ""stream"": ""\u041c\u0410\u0413-\u0410\u041a_\u0417251"", ""streamOid"": 1101, ""stream_facultyoid"": 3, ""subGroup"": null, ""subGroupOid"": 0, ""subgroup_facultyoid"": 0, ""tableofLessonsName"": ""\u0421\u0435\u0442\u043a\u0430 \u043f\u0430\u0440 \u043e\u0441\u043d\u043e\u0432\u043d\u0430\u044f "", ""tableofLessonsOid"": 2, ""typeOfContingent"": null, ""url1"": """", ""url1_description"": """", ""url2"": """", ""url2_description"": """", ""deletion_mark"": 0, ""openlesson"": null, ""auditoriumfloor"": null, ""packageNumber"": null, ""disciplineUid"": null, ""streamUid"": null, ""subgroupUid"": null, ""groupSP_Uid"": null, ""group_faculty_SP_Uid"": null, ""group_id"": 1016, ""subgroup"": 0, ""update_time"": ""2025-11-18T00:01:57.189180""}'