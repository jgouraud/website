"""Content for the Convex DeepStack research project."""

RESEARCH_PROJECT = {
    'category': 'research',
    'domain': {'en': 'Trustworthy AI', 'fr': 'IA de confiance'},
    'title': {
        'en': 'Convex DeepStack: More Reliable Deep Learning',
        'fr': 'Convex DeepStack : un deep learning plus fiable',
    },
    'pitch': {
        'en': ('Co-developed a framework for reliable deep networks that jointly optimizes '
               'accuracy, speed and resilience to corrupted data.'),
        'fr': ('Co-développement d’un cadre pour des réseaux profonds plus fiables, qui '
               'optimise conjointement précision, rapidité et robustesse face aux données corrompues.'),
    },
    'skills': [
        {'en': 'Neural Networks',        'fr': 'Réseaux de neurones',       'icon': 'psychology'},
        {'en': 'Convex Optimization',    'fr': 'Optimisation convexe',      'icon': 'functions'},
        {'en': 'Automated ML',           'fr': 'ML automatisé',             'icon': 'auto_awesome'},
        {'en': 'Robust ML',              'fr': 'ML robuste',                'icon': 'verified_user'},
        {'en': 'Bayesian Optimization',  'fr': 'Optimisation bayésienne',   'icon': 'tune'},
        {'en': 'Conformal Methods',      'fr': 'Méthodes conformes',        'icon': 'rule'},
        {'en': 'Model Evaluation',       'fr': 'Évaluation de modèles',     'icon': 'bar_chart'},
        {'en': 'Python',                 'fr': 'Python',                    'icon': 'code'},
    ],
    'overview': {
        'en': ('Deep networks can be unpredictable to train, while reliably optimized alternatives '
               'are usually shallow. This research bridges that gap by combining independently '
               'optimized building blocks into an adaptive, deeper predictor.'),
        'fr': ('Les réseaux profonds sont parfois imprévisibles à entraîner, alors que les approches '
               'plus stables restent souvent peu profondes. Cette recherche comble cet écart en '
               'assemblant des blocs optimisés séparément dans un prédicteur plus profond et adaptable.'),
    },
    'methodology': {
        'en': ('Designed a residual-stacking strategy using standard and robust convex neural blocks. '
               'Combined Bayesian hyperparameter search with a conformal early-stop rule, then benchmarked '
               'prediction error, corruption robustness and search time against three baselines.'),
        'fr': ('Conception d’une stratégie d’empilement résiduel à partir de blocs neuronaux convexes, '
               'standards et robustes. Association d’une recherche bayésienne des hyperparamètres à un '
               'arrêt anticipé conforme, puis comparaison avec trois méthodes de référence.'),
    },
    'key_result': {
        'value': '14.03×',
        'caption': {
            'en': 'lower combined mmMSE-time score than the next-best baseline.',
            'fr': 'score combiné mmMSE-temps inférieur à la meilleure baseline suivante.',
        },
        'secondary': {
            'en': 'Score 6.07 at 40% corruption',
            'fr': 'Score 6,07 à 40 % de corruption',
        },
    },
    'banner_illustration': 'banner_illustration.png',
    'figure': {
        'file': 'figure6_accuracy_cost_zoom.png',
        'caption': {
            'en': 'Figure 6 · Prediction error vs. search time',
            'fr': 'Figure 6 · Erreur de prédiction vs temps de recherche',
        },
    },
    'report_url': '/assets/project_report.pdf',
    'code_url': None,
}

RESEARCH_TEXT = {
    'en': {
        'home': 'Home', 'academic': 'Academic Projects', 'research': 'Research Papers',
        'industrial': 'Real Life Projects', 'about': 'About',
        'academic_label': 'Academic project', 'research_label': 'Research paper',
        'industrial_label': 'Industrial project', 'report': 'Read research paper',
        'code': 'View code', 'skills': 'Skills Demonstrated', 'overview': 'Research Overview',
        'methodology': 'Methodology', 'result': 'Key Result', 'no_link': 'Link not supplied',
    },
    'fr': {
        'home': 'Accueil', 'academic': 'Projets académiques', 'research': 'Articles de recherche',
        'industrial': 'Projets professionnels', 'about': 'À propos',
        'academic_label': 'Projet académique', 'research_label': 'Article de recherche',
        'industrial_label': 'Projet industriel', 'report': 'Lire l’article',
        'code': 'Voir le code', 'skills': 'Compétences mobilisées', 'overview': 'Enjeu de recherche',
        'methodology': 'Méthodologie', 'result': 'Résultat clé', 'no_link': 'Lien non renseigné',
    },
}
