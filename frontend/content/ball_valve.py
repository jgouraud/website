"""Content for the hydropower valve academic project."""

BALL_VALVE_PROJECT = {
    'title': {
        'en': 'Anomaly Detection in Hydrolic Powerplants',
        'fr': 'Détection d’Anomalie dans des Centrales Hydroélectriques',
    },
    'domain': {
        'en': 'Predictive Maintenance · Hydropower',
        'fr': 'Maintenance prédictive · Hydroélectricité',
    },
    'pitch': {
        'en': (
            'Project exploiting sensor data from real hydro powerplants to detect abnormal '
            'behavior. Developped a CNN–LSTM autoencoder that learns healthy closure '
            'patterns, scores unusual events, and supports physically interpretable fault analysis.'
        ),
        'fr': (
            'Projet basé sur des données de centrales hydroélectriques '
            'pour détecter des évènements anormaux. Développement d’un '
            'autoencodeur CNN–LSTM qui apprend les comportements sains, évalue les anomalies '
            'et facilite l’interprétation physique des défauts.'
        ),
    },
    'skills': [
        {'en': 'Predictive Maintenance', 'fr': 'Maintenance prédictive', 'icon': 'build_circle'},
        {'en': 'Time-Series Analysis', 'fr': 'Séries temporelles', 'icon': 'show_chart'},
        {'en': 'Neural Networks', 'fr': 'Réseaux de Neurones', 'icon': 'psychology'},
        {'en': 'Unsupervised Detection', 'fr': 'Détection non supervisée', 'icon': 'troubleshoot'},
        {'en': 'Data Analysis', 'fr': 'Analyse de Données', 'icon': 'scatter_plot'},
        {'en': 'Diagnosis & Prognosis', 'fr': 'Diagnostique & Pronostique', 'icon': 'fact_check'},
    ],
    'overview': {
        'en': (
            'The AXPO Hydropower Challenge examined ball valves across five generating units '
            'across two power stations. The team combined two complementary '
            'approaches: pressure-based detection of abnormal valve operation times, and '
            'multivariate deep-learning analysis of valve-closing events. The goal was to '
            'identify potential issues from irregular data.'
        ),
        'fr': (
            'Le défi hydroélectrique AXPO portait sur les vannes de cinq turbines réparties sur 2 sites'
            '. L’équipe a combiné deux approches : '
            'la détection d’évènement inhabituelles à partir '
            'de la pression uniquement, puis l’analyse multivariée des fermetures par réseaux de neurones '
            ', afin de repérer et interprété des comportements anormaux.'
        ),
    },
    'methodology': {
        'en': (
            'For the deep-learning task, sensor data were normalized and divided into '
            'four-minute windows centered around closing transitions. A convolutional '
            'encoder and LSTM decoder learned healthy event patterns. Reconstruction '
            'error and latent-space Mahalanobis deviation were combined into a rarity '
            'score, assessed against machine- and operating-regime-specific baselines. '
            'K-means and physics-informed rules helped interpret flagged events.'
        ),
        'fr': (
            'Pour le réseau de neurones, les signaux ont été normalisés puis '
            'découpés en fenêtres de quatre minutes autour des mouvements de valves. Un encodeur '
            'convolutif et un décodeur LSTM apprennent sur les événements sains. L’erreur '
            'de reconstruction et la distance de Mahalanobis dans l’espace latent ont '
            'alimenté un score de rareté, comparé à des références adaptées aux machines '
            'et aux régimes d’exploitation. K-means et des règles physiques ont aidé '
            'à interpréter les événements détectés.'
        ),
    },
    'contribution': {
        'en': (
            'Designed and implemented the CNN–LSTM autoencoder for anomaly detection and scoring. Defined the diagnostic rules.'
        ),
        'fr': (
            'Conception et entraînement de l’autoencodeur CNN–LSTM '
            'pour la détection d’anomalies | Définition des règles de diagnostique.'
        ),
    },
    'key_result': {
        'value': '3',
        'caption': {
            'en': 'interpretable macro-groups emerged in the real test-set anomalies: multi-sensor inconsistencies, single-sensor drift, and coherent process deviations.',
            'fr': 'grands groupes interprétables ont émergé dans les anomalies du test réel : capteur dysfonctionel, dérive progressive d’un capteur et évènement physique anormal.',
        },
        'secondary': {
            'en': '5 machines · 2 hydropower stations',
            'fr': '5 machines · 2 centrales hydroélectriques',
        },
    },
    'banner_illustration': 'ball-valve-anomaly.svg',
    'figure_file': 'ball-valve-test-results.png',
    'report_url': '/assets/CIVIL426_Final_Project_Report.pdf',
}

BALL_VALVE_TEXT = {
    'en': {
        'academic': 'Academic Projects', 'academic_label': 'Academic project',
        'report': 'Read project report', 'skills': 'Skills Demonstrated',
        'overview': 'Project Overview', 'methodology': 'Methodology',
        'contribution': 'My Contribution', 'result': 'Key Findings',
        'figure': 'Test-set clustering and fault-class distribution · report Figures 10–11 (p. 15)',
        'missing_report': 'Add CIVIL426_Final_Project_Report.pdf to assets/ to enable the report link.',
    },
    'fr': {
        'academic': 'Projets académiques', 'academic_label': 'Projet académique',
        'report': 'Lire le rapport', 'skills': 'Compétences mobilisées',
        'overview': 'Présentation du projet', 'methodology': 'Méthodologie',
        'contribution': 'Ma contribution', 'result': 'Principaux résultats',
        'figure': 'Clustering et types de défauts du test · figures 10–11 du rapport (p. 15)',
        'missing_report': 'Ajoutez CIVIL426_Final_Project_Report.pdf dans assets/ pour activer le lien.',
    },
}
