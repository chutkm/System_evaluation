# def generate_recommendations(metrics):

#     recommendations = []

#     if metrics["avg_rating"] < 3.5:
#         recommendations.append(
#             "Низкая средняя оценка дисциплин. Рекомендуется провести аудит качества преподавания."
#         )

#     if metrics["negative_share"] > 0.3:
#         recommendations.append(
#             "Высокая доля негативных отзывов. Необходимо выявить проблемные дисциплины."
#         )

#     return recommendations

def generate_recommendations(metrics):

    recommendations = []

    avg_rating = metrics.get("avg_rating", 0)
    negative_share = metrics.get("negative_share", 0)

    # --- оценка средней оценки ---
    if avg_rating >= 4.5:
        recommendations.append(
            "Очень высокий уровень удовлетворенности студентов. Рекомендуется сохранить текущие методы преподавания и распространить лучшие практики."
        )

    elif 4.0 <= avg_rating < 4.5:
        recommendations.append(
            "Хороший уровень преподавания. Можно дополнительно развивать интерактивные методы обучения и практические задания."
        )

    elif 3.5 <= avg_rating < 4.0:
        recommendations.append(
            "Средний уровень удовлетворенности. Рекомендуется проанализировать темы с наибольшим количеством замечаний студентов."
        )

    elif 3.0 <= avg_rating < 3.5:
        recommendations.append(
            "Низкая средняя оценка дисциплины. Желательно пересмотреть формат проведения занятий и нагрузку студентов."
        )

    else:
        recommendations.append(
            "Критически низкая средняя оценка. Рекомендуется провести аудит качества преподавания и методических материалов."
        )

    # --- анализ доли негативных отзывов ---
    if negative_share == 0:
        recommendations.append(
            "Негативных отзывов не обнаружено. Ваши студенты довольны — благодарим за качественную работу!"
        )

    elif 0 < negative_share <= 0.1:
        recommendations.append(
            "Очень низкая доля негативных отзывов. Текущий уровень преподавания оценивается студентами положительно."
        )

    elif 0.1 < negative_share <= 0.3:
        recommendations.append(
            "Наблюдается умеренное количество негативных отзывов. Рекомендуется проанализировать отдельные проблемные темы."
        )

    elif 0.3 < negative_share <= 0.5:
        recommendations.append(
            "Высокая доля негативных отзывов. Необходимо выявить проблемные дисциплины и провести корректирующие меры."
        )

    else:
        recommendations.append(
            "Критически высокая доля негативных отзывов. Требуется срочный анализ качества преподавания и обратной связи от студентов."
        )

    return recommendations