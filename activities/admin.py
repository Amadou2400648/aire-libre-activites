from django.contrib import admin

from .models import Category, Activity


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','created_at')
   # list_filter = ('name', 'created_at')
    search_fields = ('name',)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'location_city', 'start_time', 'end_time','proposer','category')
    list_filter = ('proposer', 'category', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Activity, ActivityAdmin)


