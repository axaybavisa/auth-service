from django.urls import path, include

# API versioning


app_name = "auth"

urlpatterns = [
    # V1 API URLs
    path("v1/auth/", include("api.v1.urls")),

    # V2 API URLs
    #path("v2/", include("api.v2.urls")),
]
