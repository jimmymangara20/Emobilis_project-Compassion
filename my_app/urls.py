from django.urls import path
from . import views

app_name = 'myapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('appointment/', views.appointment, name='appointment'),
    path('sponsorship_form/<int:id>', views.sponsorship_form, name='sponsorship_form'),
    path('sponsor_a_child/', views.sponsor_a_child, name='sponsor_a_child'),
    path('gallery/', views.gallery, name='gallery'),
    path('team/', views.team, name='team'),
    path('account/', views.account, name='account'),
    path('sponsor/', views.sponsor, name='sponsor'),

    # Appointments
    path('show_appointments/', views.retrieve_appointments, name='show_appointments'),
    path('appo/delete/<int:id>', views.delete_appointments, name='delete_appointments'),
    path('appo/edit/<int:appointment_id>', views.edit_appointments, name='edit_appointments'),

    # Sponsorship
    path('show_sponsorship/', views.show_sponsorship, name='show_sponsorship'),
    path('spon/delete/<int:id>', views.delete_sponsorship, name='delete_sponsorship'),
    path('spo/edit/<int:sponsor_id>', views.edit_sponsorship, name='edit_sponsorship'),
    path('upload/', views.upload_image, name='upload_image'),
    path('callback/', views.LNMCallbackUrlAPIView.as_view(), name='callback'),
    path('confirm_support/', views.confirm_support, name='confirm_support'),
    path('support_later/<int:id>', views.support_later, name='support_later'),
    path('view_support_later/', views.get_support_laters, name='view_support_laters'),
    path('view_supports/', views.show_supports, name='show_supports'),
    path('view_mysupports/', views.show_mysupports, name='show_mysupports'),
    path('profile/', views.profile, name='profile'),
]
