from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank,
)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Vacancy, Service, Category, SubCategory


class GlobalSearchAPIView(APIView):
    """
    *** Global search view (PostgreSQL full-text search) ***
    *** Usings: 'russian' и 'simple' ***
    """

    def get(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Response({"query": "", "results": {}}, status=status.HTTP_200_OK)

        search_query = (
            SearchQuery(query, config="russian") |
            SearchQuery(query, config="simple")
        )

        results = {
            "services": [],
            "vacancies": [],
            "categories": [],
            "sub_categories": []
        }

        # --- Services ---
        service_vector = (
            SearchVector("title", "description", config="russian") +
            SearchVector("title", "description", config="simple")
        )
        services = (
            Service.objects
            .annotate(rank=SearchRank(service_vector, search_query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
            .values("id", "title", "description")
        )
        results["services"] = list(services)

        # --- Vacancies ---
        vacancy_vector = (
            SearchVector("title", "description", config="russian") +
            SearchVector("title", "description", config="simple")
        )
        vacancies = (
            Vacancy.objects
            .annotate(rank=SearchRank(vacancy_vector, search_query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
            .values("id", "title", "description")
        )
        results["vacancies"] = list(vacancies)

        # --- Categories ---
        category_vector = (
            SearchVector("title", config="russian") +
            SearchVector("title", config="simple")
        )
        categories = (
            Category.objects
            .annotate(rank=SearchRank(category_vector, search_query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
            .values("id", "title")
        )
        results["categories"] = list(categories)

        # --- SubCategories ---
        sub_category_vector = (
            SearchVector("title", config="russian") +
            SearchVector("title", config="simple")
        )
        sub_categories = (
            SubCategory.objects
            .annotate(rank=SearchRank(sub_category_vector, search_query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
            .values("id", "title")
        )
        results["sub_categories"] = list(sub_categories)

        return Response({
            "query": query,
            "results": results
        }, status=status.HTTP_200_OK)
