from django.utils.html import strip_tags
from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl.analysis import analyzer, tokenizer, token_filter
from api.models import Category, SubCategory, Vacancy, Service

icu_transform_filter = token_filter(
    'icu_transform_filter',
    type='icu_transform',
    id='Any-Latin; Latin-ASCII'  # превращает всё в латиницу
)

autocomplete_analyzer = analyzer(
    'autocomplete_analyzer',
    tokenizer=tokenizer(
        'autocomplete_tokenizer',
        'edge_ngram',
        min_gram=2,
        max_gram=15
    ),
    filter=[
        'lowercase',
        'asciifolding',
        icu_transform_filter,
        'snowball',
    ],
)

autocomplete_search_analyzer = analyzer(
    'autocomplete_search_analyzer',
    tokenizer='standard',
    filter=[
        'lowercase',
        'asciifolding',
        icu_transform_filter,
        'snowball',
    ],
)

category_index = Index('categories')
category_index.settings(number_of_shards=1, number_of_replicas=0)


@registry.register_document
class CategoryDocument(Document):
    title = fields.TextField(
        analyzer=autocomplete_analyzer,
        search_analyzer=autocomplete_search_analyzer
    )
    display_ru = fields.TextField(
        analyzer=autocomplete_analyzer,
        search_analyzer=autocomplete_search_analyzer
    )
    display_uz = fields.TextField(
        analyzer=autocomplete_analyzer,
        search_analyzer=autocomplete_search_analyzer
    )

    class Index:
        name = 'categories'

    class Django:
        model = Category
        fields = ['id']


@registry.register_document
class SubCategoryDocument(Document):
    title = fields.TextField(
        analyzer=autocomplete_analyzer,
        search_analyzer=autocomplete_search_analyzer
    )
    display_ru = fields.TextField(
        analyzer=autocomplete_analyzer,
        search_analyzer=autocomplete_search_analyzer
    )
    display_uz = fields.TextField(
        analyzer=autocomplete_analyzer,
        search_analyzer=autocomplete_search_analyzer
    )

    class Index:
        name = 'sub_categories'

    class Django:
        model = SubCategory
        fields = ['id']


@registry.register_document
class VacancyDocument(Document):
    title = fields.TextField(
        analyzer=autocomplete_analyzer,
        search_analyzer=autocomplete_search_analyzer
    )
    description = fields.TextField(
        analyzer=autocomplete_analyzer,
        search_analyzer=autocomplete_search_analyzer
    )

    class Index:
        name = 'vacancies'

    class Django:
        model = Vacancy
        fields = ['id', 'price']

    def prepare_description(self, instance):
        return strip_tags(instance.description or "")


@registry.register_document
class ServiceDocument(Document):
    title = fields.TextField(
        analyzer=autocomplete_analyzer,
        search_analyzer=autocomplete_search_analyzer
    )
    description = fields.TextField(
        analyzer=autocomplete_analyzer,
        search_analyzer=autocomplete_search_analyzer
    )

    class Index:
        name = 'services'

    class Django:
        model = Service
        fields = ['id', 'price']

    def prepare_description(self, instance):
        return strip_tags(instance.description or "")