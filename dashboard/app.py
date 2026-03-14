# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from sqlalchemy import create_engine
# from bot.config import DATABASE_SYNC_URL

# engine = create_engine(DATABASE_SYNC_URL)

# st.set_page_config(
#     page_title="Мониторинг удовлетворенности студентов",
#     layout="wide"
# )

# st.title("📊 Мониторинг удовлетворенности студентов")

# df = pd.read_sql("SELECT * FROM feedback", engine)

# # ---------------- ФИЛЬТРЫ ----------------

# group_filter = st.sidebar.selectbox(
#     "Группа",
#     ["Все"] + sorted(df["group_name"].unique())
# )

# if group_filter != "Все":
#     df = df[df["group_name"] == group_filter]

# # ---------------- KPI ----------------

# col1, col2, col3 = st.columns(3)

# col1.metric("Средняя оценка", round(df["rating"].mean(), 2))
# col2.metric("Количество отзывов", len(df))
# col3.metric(
#     "Негативные отзывы",
#     (df["sentiment"] == "negative").sum()
# )

# # ---------------- ГРАФИК ОЦЕНОК ----------------

# fig = px.histogram(
#     df,
#     x="rating",
#     title="Распределение оценок"
# )

# st.plotly_chart(fig, use_container_width=True)

# # ---------------- SENTIMENT ----------------

# sentiment_counts = df["sentiment"].value_counts()

# fig2 = px.pie(
#     values=sentiment_counts.values,
#     names=sentiment_counts.index,
#     title="Тональность отзывов"
# )

# st.plotly_chart(fig2, use_container_width=True)

# # ---------------- ТОП ПРОБЛЕМ ----------------

# st.subheader("Проблемные темы")

# topics = (
#     df["topics"]
#     .dropna()
#     .explode()
#     .value_counts()
#     .head(10)
# )

# st.bar_chart(topics)

#--------------------------------
# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from sqlalchemy import create_engine
# from bot.config import DATABASE_SYNC_URL

# # ----------------- Подключение -----------------
# engine = create_engine(DATABASE_SYNC_URL)
# df = pd.read_sql("SELECT * FROM feedback", engine)

# # ----------------- Настройка страницы -----------------
# st.set_page_config(
#     page_title="Мониторинг удовлетворенности студентов",
#     layout="wide"
# )
# st.title("📊 Мониторинг удовлетворенности студентов")

# # ----------------- Сайдбар фильтры -----------------
# st.sidebar.header("Фильтры")

# # Фильтр по группам
# group_filter = st.sidebar.selectbox(
#     "Группа",
#     ["Все"] + sorted(df["group_name"].dropna().unique())
# )

# # Фильтр по дисциплинам (как в старом коде)
# discipline_filter = st.sidebar.selectbox(
#     "Дисциплина",
#     ["Все"] + sorted(df["discipline"].dropna().unique())
# )

# # Функция для извлечения ФИО преподавателя
# def extract_teacher_name(name: str) -> str:
#     if not name or not isinstance(name, str):
#         return ""
#     parts = name.strip().split()
#     return " ".join(parts[-2:])  # берём последние два слова как ФИО

# # создаём колонку с чистым ФИО преподавателя
# df["teacher_clean"] = df["teacher"].apply(extract_teacher_name)

# # Фильтр по преподавателю (используем teacher_clean)
# teacher_filter = st.sidebar.selectbox(
#     "Преподаватель",
#     ["Все"] + sorted(df["teacher_clean"].dropna().unique())
# )

# # ----------------- Применяем фильтры -----------------
# if group_filter != "Все":
#     df = df[df["group_name"] == group_filter]

# if discipline_filter != "Все":
#     df = df[df["discipline"] == discipline_filter]

# if teacher_filter != "Все":
#     df = df[df["teacher_clean"] == teacher_filter]

# # ----------------- KPI -----------------
# st.subheader("📌 Основные показатели")
# col1, col2, col3 = st.columns(3)
# col1.metric("Средняя оценка", round(df["rating"].mean(), 2))
# col2.metric("Количество отзывов", len(df))
# col3.metric("Негативные отзывы", (df["sentiment"] == "negative").sum())

# # ----------------- Временная динамика -----------------
# st.subheader("📈 Динамика оценок по времени")
# df['lesson_date'] = pd.to_datetime(df['lesson_date'])
# time_df = df.groupby('lesson_date')['rating'].mean().reset_index()
# fig_time = px.line(
#     time_df,
#     x='lesson_date',
#     y='rating',
#     title="Средняя оценка по дате занятия",
#     markers=True
# )
# st.plotly_chart(fig_time, use_container_width=True)

# # ----------------- Распределение оценок -----------------
# st.subheader("📊 Распределение оценок")
# fig_rating = px.histogram(df, x='rating', nbins=5)
# st.plotly_chart(fig_rating, use_container_width=True)

# # ----------------- Тональность отзывов -----------------
# st.subheader("💬 Тональность отзывов")
# sentiment_counts = df["sentiment"].value_counts()
# fig_sentiment = px.pie(
#     values=sentiment_counts.values,
#     names=sentiment_counts.index,
#     title="Тональность отзывов"
# )
# st.plotly_chart(fig_sentiment, use_container_width=True)

# # ----------------- Топ проблемных тем -----------------
# st.subheader("⚠️ Проблемные темы")
# topics = df["topics"].dropna().explode().value_counts().head(10)
# st.bar_chart(topics)

# # ----------------- Топ проблемных преподавателей -----------------
# st.subheader("👩‍🏫 Рекомендации преподавателям")
# topics_df = df.explode("topics")

# teacher_sentiments = (
#     topics_df.groupby("teacher_clean")["sentiment"]
#     .value_counts(normalize=True)
#     .unstack()
#     .fillna(0)
# )
# negative_teachers = teacher_sentiments.sort_values(by='negative', ascending=False).head(5)

# for teacher, row in negative_teachers.iterrows():
#     st.markdown(f"**{teacher}**: {row.get('negative', 0)*100:.1f}% негативных отзывов")
#     if row.get('negative', 0) > 0.3:
#         st.markdown("⚠️ Рекомендация: обратить внимание на качество преподавания")

# # # ----------------- Тепловая карта по дням -----------------
# # st.subheader("🔥 Тепловая карта оценок по дням и парам")
# # if 'lesson_number' in df.columns:
# #     heatmap_data = df.pivot_table(
# #         index='lesson_number',
# #         columns=df['lesson_date'].dt.date,
# #         values='rating',
# #         aggfunc='mean'
# #     )
# #     fig_heat = go.Figure(
# #         data=go.Heatmap(
# #             z=heatmap_data.values,
# #             x=[str(d) for d in heatmap_data.columns],
# #             y=heatmap_data.index,
# #             colorscale='Viridis'
# #         )
# #     )
# #     fig_heat.update_layout(title="Средние оценки по парам и дате")
# #     st.plotly_chart(fig_heat, use_container_width=True)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from bot.config import DATABASE_SYNC_URL

# ----------------- Подключение -----------------
engine = create_engine(DATABASE_SYNC_URL)
df = pd.read_sql("SELECT * FROM feedback", engine)

# ----------------- Настройка страницы -----------------
st.set_page_config(
    page_title="Мониторинг удовлетворенности студентов",
    layout="wide"
)

st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-size: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("📊 Мониторинг удовлетворенности студентов")

# ----------------- Сайдбар фильтры -----------------
st.sidebar.header("Фильтры")

# Фильтр по группам
group_filter = st.sidebar.selectbox(
    "Группа",
    ["Все"] + sorted(df["group_name"].dropna().unique())
)

# Фильтр по дисциплинам
discipline_filter = st.sidebar.selectbox(
    "Дисциплина",
    ["Все"] + sorted(df["discipline"].dropna().unique())
)

# Функция для извлечения ФИО преподавателя
def extract_teacher_name(name: str) -> str:
    if not name or not isinstance(name, str):
        return ""
    parts = name.strip().split()
    return " ".join(parts[-2:])  # берём последние два слова как ФИО

# создаём колонку с чистым ФИО преподавателя
df["teacher_clean"] = df["teacher"].apply(extract_teacher_name)

# Фильтр по преподавателю
teacher_filter = st.sidebar.selectbox(
    "Преподаватель",
    ["Все"] + sorted(df["teacher_clean"].dropna().unique())
)

# ----------------- Применяем фильтры -----------------
if group_filter != "Все":
    df = df[df["group_name"] == group_filter]

if discipline_filter != "Все":
    df = df[df["discipline"] == discipline_filter]

if teacher_filter != "Все":
    df = df[df["teacher_clean"] == teacher_filter]

# ----------------- KPI -----------------
st.subheader("📌 Основные показатели")
col1, col2, col3 = st.columns(3)
col1.metric("Средняя оценка", round(df["rating"].mean(), 2))
col2.metric("Количество отзывов", len(df))
col3.metric("Негативные отзывы", (df["sentiment"] == "negative").sum())

# ----------------- Временная динамика -----------------
st.subheader("📈 Динамика оценок по времени")
df['lesson_date'] = pd.to_datetime(df['lesson_date'])
time_df = df.groupby('lesson_date')['rating'].mean().reset_index()
fig_time = px.line(
    time_df,
    x='lesson_date',
    y='rating',
    title="Средняя оценка по дате занятия",
    markers=True
)
st.plotly_chart(fig_time, use_container_width=True)

# ----------------- Распределение оценок -----------------
st.subheader("📊 Распределение оценок")

fig_rating = px.histogram(
    df,
    x="rating",
    nbins=5
)

fig_rating.update_xaxes(
    tickmode="linear",
    dtick=1
)

st.plotly_chart(fig_rating, use_container_width=True)

# ----------------- Тональность отзывов -----------------
st.subheader("💬 Тональность отзывов")
sentiment_counts = df["sentiment"].value_counts()
fig_sentiment = px.pie(
    values=sentiment_counts.values,
    names=sentiment_counts.index,
    title="Тональность отзывов"
)
st.plotly_chart(fig_sentiment, use_container_width=True)

# ----------------- Проблемные темы (только negative) -----------------
st.subheader("⚠️ Проблемные темы")
negative_topics = df[df['sentiment'] == 'negative']
negative_counts = negative_topics["topics"].dropna().explode().value_counts().head(10)
st.bar_chart(negative_counts)

# ----------------- Аналогичные зоны (только positive) -----------------
st.subheader("✅ Позитивные стороны")
positive_topics = df[df['sentiment'] == 'positive']
positive_counts = positive_topics["topics"].dropna().explode().value_counts().head(10)
st.bar_chart(positive_counts)

# ----------------- Топ проблемных преподавателей -----------------
st.subheader("👩‍🏫 Рекомендации преподавателям")
teacher_sentiments = (
    df.explode("topics")
      .groupby("teacher_clean")["sentiment"]
      .value_counts(normalize=True)
      .unstack()
      .fillna(0)
)
negative_teachers = teacher_sentiments.sort_values(by='negative', ascending=False).head(5)

for teacher, row in negative_teachers.iterrows():
    st.markdown(f"**{teacher}**: {row.get('negative', 0)*100:.1f}% негативных отзывов")
    if row.get('negative', 0) > 0.3:
        st.markdown("⚠️ Рекомендация: обратить внимание на качество преподавания")

# # ----------------- Тепловая карта по дням -----------------
# st.subheader("🔥 Тепловая карта оценок по дням и парам")
# if 'lesson_number' in df.columns:
#     heatmap_data = df.pivot_table(
#         index='lesson_number',
#         columns=df['lesson_date'].dt.date,
#         values='rating',
#         aggfunc='mean'
#     )
#     fig_heat = go.Figure(
#         data=go.Heatmap(
#             z=heatmap_data.values,
#             x=[str(d) for d in heatmap_data.columns],
#             y=heatmap_data.index,
#             colorscale='Viridis'
#         )
#     )
#     fig_heat.update_layout(title="Средние оценки по парам и дате")
#     st.plotly_chart(fig_heat, use_container_width=True)