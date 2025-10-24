from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from functools import reduce

try:
    from transliterate import translit
except ImportError:
    translit = lambda text, lang_code: None  # fallback если нет transliterate

from .models import Vacancy, Service, Category, SubCategory


class GlobalSearchAPIView(GenericAPIView):

    def get(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Response({
                "query": "",
                "results": {},
                "error": None
            }, status=status.HTTP_200_OK)

        results = {}
        error_message = None

        try:
            translit_query = None
            try:
                translit_query = translit(query, "ru")
            except Exception as e:
                error_message = f"translit_error: {e}"

            try:
                search_query = SearchQuery(query, config="russian") | SearchQuery(query, config="simple")
                if translit_query and translit_query != query:
                    search_query |= SearchQuery(translit_query, config="russian")
            except Exception as e:
                search_query = SearchQuery(query, config="simple")
                error_message = f"searchquery_error: {e}"

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

            results["services"] = perform_search(Service, ["title", "description"])
            results["vacancies"] = perform_search(Vacancy, ["title", "description"])
            results["categories"] = perform_search(Category, ["title"])
            results["sub_categories"] = perform_search(SubCategory, ["title"])

        except Exception as e:
            error_message = f"general_error: {type(e).__name__}: {e}"

        return Response({
            "query": query,
            "results": results,
            "error": error_message
        }, status=status.HTTP_200_OK)
