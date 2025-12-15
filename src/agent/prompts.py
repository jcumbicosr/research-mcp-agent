CLASSIFIER_PROMPT = """
    You are a Senior Librarian Agent. Your ONLY job is to classify a scientific article 
    into one of existing areas based on the vector store data.

    1. Use the 'search_articles' to find similar articles in the database.
    2. Analyze the 'area' field of the search results.
    3. Return ONLY the name of the area (e.g., 'Physics', 'Biology', 'Computer Science').

    If the results are mixed (e.g., 2 Physics, 1 Biology), choose the majority.
    If there is no clear match, use 'get_article_content' to retrieve the full text of one relevant article
    and analyze its content to make a final classification.
    """

EXTRACTION_PROMPT = """
    You are an expert Scientific Analyst dedicated to structured data extraction.
    Your task is to read the provided scientific text and extract three specific pieces of information.

    CRITICAL RULES:
    1. Maintain the **original language** of the article content in your extraction. Do not translate.
    2. Ensure the 'steps' are distinct, high-level methodological phases, not every tiny detail.
    3. Base your answers **only** on the provided text.
    """

REVIEWER_PROMPT = """
    Você é um Revisor Acadêmico Sênior rigoroso e imparcial. 
    Sua tarefa é analisar o artigo científico fornecido e produzir uma **Resenha Crítica** em **Português**.

    CRITÉRIOS DE AVALIAÇÃO (RUBRICA):
    1. **Novidade:** O trabalho traz algo novo ou é apenas incremental?
    2. **Metodologia:** A abordagem técnica é sólida? O tamanho da amostra (se houver) é adequado?
    3. **Ameaças à Validade:** Existem variáveis não controladas? O autor ignora limitações óbvias?
    4. **Replicabilidade:** O artigo fornece detalhes suficientes para reproduzir o experimento?

    FORMATO DE SAÍDA OBRIGATÓRIO (MARKDOWN):
    Sua resposta deve seguir estritamente este template:

    ## Resenha
    **Pontos positivos:** [Cite a novidade, relevância e clareza]
    **Possíveis falhas:** [Foque pesadamente na metodologia, ameaças à validade e falta de testes]
    **Comentários finais:** [Veredito geral sobre a qualidade do trabalho]
    """

RANDOM_PAPER = """
    A Hybrid Transformer–Gaussian Process Framework for Gap-Filling Solar Irradiance Time Series
    Abstract

    Incomplete measurements of Global Horizontal Irradiance (GHI) remain a critical limitation for reliable solar resource assessment and photovoltaic system operation. This study proposes a hybrid framework that combines Transformer-based sequence modeling with Gaussian Process regression to reconstruct missing intraday GHI observations under diverse climatic conditions. The method leverages temporal self-attention to capture long-range dependencies while using probabilistic interpolation to enforce physical smoothness and uncertainty awareness.

    1. Introduction

    High-resolution solar irradiance datasets are essential for forecasting, grid management, and climate studies. However, ground-based measurements frequently suffer from data gaps caused by sensor malfunction, maintenance, or communication failures. Traditional interpolation methods often fail to capture nonlinear temporal dynamics, whereas purely data-driven deep learning models may generate physically inconsistent reconstructions. This work addresses the challenge of accurate and physically plausible GHI gap-filling by integrating deep sequence models with probabilistic interpolation techniques.

    2. Methodology

    The proposed approach consists of a multi-stage pipeline designed to reconstruct missing GHI values at minute-level resolution:

    Data Preprocessing
    Raw GHI measurements are quality-controlled, normalized, and segmented into daily sequences. Missing values are masked using a sentinel token to inform the model of data gaps.

    Transformer-Based Temporal Encoding
    A masked encoder–decoder Transformer processes partially observed sequences, learning contextual temporal representations that capture diurnal and seasonal patterns.

    Initial Gap Reconstruction
    The Transformer generates a first-pass reconstruction of missing GHI values based on learned temporal dependencies.

    Gaussian Process Refinement
    The preliminary reconstruction is refined using Gaussian Process regression to enforce smoothness, quantify uncertainty, and correct physically implausible fluctuations.

    Post-Processing and Evaluation
    The final gap-filled time series is rescaled to physical units and evaluated against reference data using RMSE, MAE, and distribution-based metrics.

    3. Results and Discussion

    Experiments conducted on multi-year GHI datasets from diverse climatic regions demonstrate that the hybrid method consistently outperforms standalone interpolation and deep learning baselines. The Transformer effectively captures long-range temporal dependencies, while the Gaussian Process component reduces noise and improves physical consistency, particularly during sunrise and sunset transitions.

    4. Conclusion

    This study introduces a hybrid Transformer–Gaussian Process framework for reconstructing missing solar irradiance data. The results indicate that combining deep temporal representation learning with probabilistic interpolation leads to more accurate and physically consistent gap-filling. The proposed approach is well-suited for operational solar energy applications and can be extended to other geophysical time series affected by missing data.
    """