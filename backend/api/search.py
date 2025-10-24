from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from transliterate import translit

from .models import Vacancy, Service, Category, SubCategory


# @method_decorator(cache_page(30), name='dispatch') Serverga Redis install qigandan keyin cache qo'shamiz
class GlobalSearchAPIView(GenericAPIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Response({"query": "", "results": {}}, status=status.HTTP_200_OK)

        try:
            translit_query = translit(query, "ru")
        except Exception:
            translit_query = None

        search_query = SearchQuery(query, config="russian") | SearchQuery(query, config="simple")
        if translit_query and translit_query != query:
            search_query |= SearchQuery(translit_query, config="russian")

        results = {}

        def perform_search(model, fields):
            vector = sum(
                (SearchVector(f, config="russian") + SearchVector(f, config="simple"))
                for f in fields
            )
            queryset = (
                model.objects
                .annotate(rank=SearchRank(vector, search_query))
                .filter(rank__gte=0.1)
                .order_by("-rank")
                .values("id", *fields)
            )
            return list(queryset)

        results["services"] = perform_search(Service, ["title", "description"])
        results["vacancies"] = perform_search(Vacancy, ["title", "description"])
        results["categories"] = perform_search(Category, ["title"])
        results["sub_categories"] = perform_search(SubCategory, ["title"])

        return Response({
            "query": query,
            "results": results
        }, status=status.HTTP_200_OK)
