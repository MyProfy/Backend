from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from elasticsearch_dsl import Q

from .documents import (
    CategoryDocument,
    SubCategoryDocument,
    VacancyDocument,
    ServiceDocument,
)
from .serializers import (
    CategoryDocumentSerializer,
    SubCategoryDocumentSerializer,
    VacancyDocumentSerializer,
    ServiceDocumentSerializer,
)


class GlobalSearchView(APIView):
    def get(self, request):
        query = request.GET.get("q")
        if not query:
            return Response(
                {"detail": "Параметр 'q' обязателен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        q = Q(
            "multi_match",
            query=query,
            fuzziness="AUTO",
            type="best_fields",
            fields=[
                "title^4",
                "display_ru^3",
                "display_uz^2",
                "description^1"
            ],
            operator="or",
        )

        categories = CategoryDocument.search().query(q)[:5]
        sub_categories = SubCategoryDocument.search().query(q)[:5]
        vacancies = VacancyDocument.search().query(q)[:5]
        services = ServiceDocument.search().query(q)[:5]

        data = {
            "query": query,
            "results": {
                "categories": CategoryDocumentSerializer(categories, many=True).data,
                "sub_categories": SubCategoryDocumentSerializer(sub_categories, many=True).data,
                "vacancies": VacancyDocumentSerializer(vacancies, many=True).data,
                "services": ServiceDocumentSerializer(services, many=True).data,
            },
        }

        return Response(data, status=status.HTTP_200_OK)
