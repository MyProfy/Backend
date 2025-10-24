from functools import reduce
from transliterate import translit, detect_language
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .models import Vacancy, Service, Category, SubCategory


def normalize_query(query: str) -> str:
    try:
        lang = detect_language(query)
        if lang != "ru":
            query = translit(query, "ru")
    except Exception:
        pass
    return query


class GlobalSearchAPIView(GenericAPIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Response({
                "query": "",
                "results": {},
                "error": None
            }, status=status.HTTP_200_OK)

        query = normalize_query(query)

        search_query = (
            SearchQuery(query, config="russian", search_type="plain") |
            SearchQuery(query, config="simple", search_type="plain")
        )

        def perform_search(model, fields):
            vectors = [SearchVector(f, config="russian") + SearchVector(f, config="simple") for f in fields]
            vector = reduce(lambda a, b: a + b, vectors)
            queryset = (
                model.objects
                .annotate(rank=SearchRank(vector, search_query))
                .filter(rank__gte=0.1)
                .order_by("-rank")
                .values("id", *fields)
            )
            return list(queryset)

        results = {
            "services": perform_search(Service, ["title", "description"]),
            "vacancies": perform_search(Vacancy, ["title", "description"]),
            "categories": perform_search(Category, ["title"]),
            "sub_categories": perform_search(SubCategory, ["title"]),
        }

        return Response({
            "query": query,
            "results": results,
        }, status=status.HTTP_200_OK)