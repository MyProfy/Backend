from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from transliterate import translit
from django.db.models import Q

from .models import Vacancy, Service, Category, SubCategory


class GlobalSearchAPIView(GenericAPIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Response({"query": "", "results": {}}, status=status.HTTP_200_OK)

        translit_query = translit(query, "ru", reversed=False)
        search_query = (
            SearchQuery(query, config="russian") |
            SearchQuery(query, config="simple") |
            SearchQuery(translit_query, config="russian")
        )

        results = {
            "services": [],
            "vacancies": [],
            "categories": [],
            "sub_categories": []
        }

        # ---------- Services ----------
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

        if not services.exists():
            services = Service.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            ).values("id", "title", "description")

        results["services"] = list(services)

        # ---------- Vacancies ----------
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

        if not vacancies.exists():
            vacancies = Vacancy.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            ).values("id", "title", "description")

        results["vacancies"] = list(vacancies)

        # ---------- Categories ----------
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

        if not categories.exists():
            categories = Category.objects.filter(
                Q(title__icontains=query)
            ).values("id", "title")

        results["categories"] = list(categories)

        # ---------- SubCategories ----------
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

        if not sub_categories.exists():
            sub_categories = SubCategory.objects.filter(
                Q(title__icontains=query)
            ).values("id", "title")

        results["sub_categories"] = list(sub_categories)

        return Response({
            "query": query,
            "results": results
        }, status=status.HTTP_200_OK)
