from django.contrib import admin
from .models import UserProfile, Document


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'state', 'postal_code', 'iban')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'file')
    list_filter = ('uploaded_at', 'uploaded_by')
    search_fields = ('title', 'description')
    readonly_fields = ('uploaded_at', 'uploaded_by')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
