FROM docker.elastic.co/elasticsearch/elasticsearch:8.8.2

RUN elasticsearch-plugin install --batch analysis-icu && \
    elasticsearch-plugin install --batch analysis-smartcn && \
    elasticsearch-plugin install --batch analysis-kuromoji && \
    elasticsearch-plugin install --batch analysis-stempel && \
    elasticsearch-plugin install --batch analysis-nori && \
    elasticsearch-plugin install --batch analysis-phonetic