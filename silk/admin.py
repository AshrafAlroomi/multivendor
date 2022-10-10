from django.contrib import admin
from .models import Request,Profile



@admin.register(Request)
class Silk(admin.ModelAdmin):
    list_display = ['id','path','query_params','raw_body','body','method',
                    'view_name','end_time','time_taken','encoded_headers','meta_time','meta_num_queries','meta_time_spent_queries','pyprofile','prof_file']


@admin.register(Profile)
class Profile(admin.ModelAdmin):
    list_display = ['name','start_time','end_time','request','time_taken']

