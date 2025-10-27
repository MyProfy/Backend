from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from .documents import CategoryDocument, SubCategoryDocument, VacancyDocument, ServiceDocument


class CategoryDocumentSerializer(DocumentSerializer):
    class Meta:
        document = CategoryDocument
        fields = ['id', 'title', 'display_ru', 'display_uz']


class SubCategoryDocumentSerializer(DocumentSerializer):
    class Meta:
        document = SubCategoryDocument
        fields = ['id', 'title', 'display_ru', 'display_uz']


class VacancyDocumentSerializer(DocumentSerializer):
    class Meta:
        document = VacancyDocument
        fields = ['id', 'title', 'description', 'price']


class ServiceDocumentSerializer(DocumentSerializer):
    class Meta:
        document = ServiceDocument
        fields = ['id', 'title', 'description', 'price']