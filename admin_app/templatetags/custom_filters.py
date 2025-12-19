from django import template
register = template.Library()

@register.filter
def sum_likes(songs):
    return sum(song.likes.count() for song in songs)