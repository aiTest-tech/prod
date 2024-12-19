from django.urls import path
from .views import *
from .views import search_wtc_records

# from . import views

urlpatterns = [
    path('wtc/analytics/', AnalyticsAPIView.as_view(), name='analytics'),

    path('wtcsubmitdata/', TextDataView.as_view(), name='text-data'),
    path('wtc/sentiment-summary/', SentimentSummaryView.as_view(), name='wtc-sentiment-summary'),
    path('wtc/lo-scru-summary/', ScrutinySummaryView.as_view(), name='wtc-sentiment-summary'),
    path('wtc/requests-per-day/', RequestsPerDayView.as_view(), name='requests-per-day'),
    path('wtc/mode-distribution/', ModeDistributionView.as_view(), name='mode-distribution'),
    path('wtc/depr-rout-distribution/', DeprRoutDistributionView.as_view(), name='depr-rout-distribution'),
    path('wtc/type-distribution/', TypeDistributionView.as_view(), name='type-distribution'),
    path('wtc/scrutiny-statistics/', WTCStatisticsAPIView.as_view(), name='wtc_statistics_api'),
    path('search_wtc_records/', search_wtc_records, name='search_wtc_records'),
    path('primary-scrutiny-done/', primary_scrutiny_done, name='primary_scrutiny_done'),

    path('wtc/records/', WTCListViewAnaly.as_view(), name='wtc-list'),
    path('wtc/lo/', WTCLOListView.as_view(), name='wtc_lo'),


]