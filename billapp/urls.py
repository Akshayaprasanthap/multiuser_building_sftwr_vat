from django.urls import re_path,path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [

    path('',views.home,name='home'),
    path('cmp_register/',views.cmp_register,name='cmp_register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('change_password/',views.change_password,name='change_password'),
    path('cmp_details/<int:id>/',views.cmp_details,name='cmp_details'),
    path('emp_register/',views.emp_register,name='emp_register'),
    path('dashboard/',views.dashboard,name='dashboard'),
     
    path('register_company/',views.register_company,name='register_company'),  
    path('register_company_details/<int:id>',views.register_company_details,name='register_company_details'),
    path('register_employee/',views.register_employee,name='register_employee'),  
    path('user_login/',views.user_login,name='user_login'),  
    path('cmp_profile/',views.cmp_profile,name='cmp_profile'),  
    path('load_edit_cmp_profile/',views.load_edit_cmp_profile,name='load_edit_cmp_profile'),  
    path('edit_cmp_profile',views.edit_cmp_profile,name='edit_cmp_profile'),  
    path('emp_profile/',views.emp_profile,name='emp_profile'),  
    path('load_edit_emp_profile/',views.load_edit_emp_profile,name='load_edit_emp_profile'),  
    path('edit_emp_profile',views.edit_emp_profile,name='edit_emp_profile'),  
    path('item_list/',views.item_list,name='item_list'),  
    path('load_item_create/',views.load_item_create,name='load_item_create'),  
    path('item_create',views.item_create,name='item_create'),  
    path('load_staff_request/',views.load_staff_request,name='load_staff_request'),  
    path('load_staff_list/',views.load_staff_list,name='load_staff_list'),  
    path('accept_staff/<int:id>',views.accept_staff,name='accept_staff'),  
    path('reject_staff/<int:id>',views.reject_staff,name='reject_staff'),  






    path('party_list/',views.party_list,name='party_list'),  
    path('load_party_create/',views.load_party_create,name='load_party_create'),
    path('addNewParty',views.addNewParty,name='addNewParty'),
    path('deleteparty/<int:id>',views.deleteparty,name='deleteparty'),
    path('view_party/<int:id>',views.view_party,name='view_party'),
    path('edit_party/<int:id>',views.edit_party,name='edit_party'),
    path('edit_saveparty/<int:id>',views.edit_saveparty,name='edit_saveparty'),
    path('history_party/<int:id>',views.history_party,name='history_party'),

]
