from django.contrib import admin
from .models import Cart, Category, Mode, Stage


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "stage", "category", "question", "answer", "author", "add_date", "repeat_date"]
    list_editable = ("author", "stage")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "author", "mode"]
    list_editable = ["author", "mode"]


@admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ["sequence", "name", "interval_minute", "interval_hour", "interval_day", "mode"]
    ordering = ("sequence", )
