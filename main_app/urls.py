from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('checkdisease/', views.checkdisease, name='checkdisease'),
    path('post/', views.post, name='post'),
    path('messages/', views.chat_messages, name='chat_messages'),

    path('patient/', views.patient_ui, name='patient_ui'),
    path('doctor/', views.doctor_ui, name='doctor_ui'),

    # 🔥 ADD THIS LINE
    path('consult_a_doctor/', views.consult_a_doctor, name='consult_a_doctor'),
    path('pviewprofile/<str:patientusername>', views.pviewprofile, name='pviewprofile'),
    path('dviewprofile/<str:doctorusername>', views.dviewprofile, name='dviewprofile'),
    path('pconsultation_history/', views.pconsultation_history, name='pconsultation_history'),
    path('dconsultation_history/', views.dconsultation_history, name='dconsultation_history'),
    path('consultationview/<int:consultation_id>', views.consultationview, name='consultationview'),
    path('make_consultation/<str:doctorusername>', views.make_consultation, name='make_consultation'),
    path('rate_review/<int:consultation_id>', views.rate_review, name='rate_review'),
    path('close_consultation/<int:consultation_id>', views.close_consultation, name='close_consultation'),
    path('admin_ui/', views.admin_ui, name='admin_ui'),
    path('chatbot_query/', views.chatbot_query, name='chatbot_query'),
    path('get_recent_chats/', views.get_recent_chats, name='get_recent_chats'),
]