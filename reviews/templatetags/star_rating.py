from django import template

register = template.Library()

@register.filter
def star_rating(value):
    try:
        rating = float(value)
    except (ValueError, TypeError):
        return "Нет оценки"

    rating = max(0, min(rating, 5))
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5

    stars = "★" * full_stars
    if half_star:
        stars += "☆"
    return stars.ljust(5, "☆")
