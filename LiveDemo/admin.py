from django.contrib import admin

from .models import Dog, DictionaryEntry, GrammarRule

# Register your models here.
class DogAdmin(admin.ModelAdmin):
    list_display = ('name', 'temperament', 'height', 'weight', 'lifespan', 'group', 'description_short',
                    'description_long', 'nicknames')

class DictionaryEntryAdmin(admin.ModelAdmin):
    list_display = ('word', 'word_type')

class GrammarRuleAdmin(admin.ModelAdmin):
    list_display = ('rule', 'addends')

admin.site.register(Dog, DogAdmin)
admin.site.register(DictionaryEntry, DictionaryEntryAdmin)
admin.site.register(GrammarRule, GrammarRuleAdmin)
