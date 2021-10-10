from django.urls import path, register_converter
from .views import home, index
from .demo import Conversation
from .converters import ConversationConvertor

register_converter(ConversationConvertor, 'Conversation')

convo = Conversation()

urlpatterns = [
    path('', index, name='Index'),
    path(f'Conversation:conversation', home, name='home')
]
