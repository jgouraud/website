"""Content for the EEG academic project."""

EEG_PROJECT = {
    'category': 'academic',
    'domain': {'en': 'Biomedical AI', 'fr': 'IA biomédicale'},
    'title': {
        'en': 'Neural Networks for EEG Seizure Detection',
        'fr': 'Détection de crises épileptiques par IA',
    },
    'pitch': {
        'en': ('Built a frequency-based EEG classifier and co-evaluated four neural approaches '
               'to identify seizures in brain recordings. The study explores whether linking '
               'electrodes spatially improves detection.'),
        'fr': ('J’ai développé un classifieur EEG fréquentiel et comparé en équipe '
               'quatre modèles neuronaux pour détecter les crises épileptiques et '
               'évaluer l’apport des liens entre électrodes.'),
    },
    'skills': [
        {'en': 'Signal Processing',       'fr': 'Traitement du signal',     'icon': 'graphic_eq'},
        {'en': 'Neural Networks',         'fr': 'Réseaux de neurones',     'icon': 'psychology'},
        {'en': 'Feature Engineering',     'fr': 'Création de variables',   'icon': 'tune'},
        {'en': 'Model Evaluation',        'fr': 'Évaluation de modèles',   'icon': 'assessment'},
        {'en': 'Cross-Validation',        'fr': 'Validation croisée',     'icon': 'fact_check'},
        {'en': 'PyTorch',                 'fr': 'PyTorch',                 'icon': 'memory'},
        {'en': 'Python',                  'fr': 'Python',                  'icon': 'code'},
        {'en': 'Research Collaboration',  'fr': 'Collaboration',    'icon': 'groups'},
    ],
    'overview': {
        'en': ('Manually reviewing EEG recordings to spot seizures is time-consuming. '
               'Our team compared four neural models for classifying 12-second EEG segments, '
               'including methods that account for how scalp electrodes are positioned.'),
        'fr': ('Repérer des crises dans de longs enregistrements EEG demande une analyse '
               'manuelle chronophage. Notre équipe a comparé quatre modèles neuronaux pour '
               'classer des séquences EEG de 12 secondes, dont des approches tenant compte '
               'de la position des électrodes.'),
    },
    'methodology': {
        'en': ('I implemented the frequency-domain CNN–BiLSTM pipeline, transforming '
               'filtered EEG signals into spectral features. We harmonized data preprocessing '
               'and compared all four architectures through five-fold cross-validation '
               'on the TUSZ dataset.'),
        'fr': ('J’ai développé le modèle CNN–BiLSTM en domaine fréquentiel, à partir '
               'de signaux EEG filtrés et convertis en caractéristiques spectrales. '
               'Nous avons uniformisé le prétraitement et comparé quatre architectures '
               'par validation croisée à cinq plis sur TUSZ.'),
    },
    'key_result': {
        'value': '0.872',
        'caption': {
            'en': 'ROC AUC achieved by the best model, a Graph Transformer (higher is better).',
            'fr': 'ROC AUC du meilleur modèle, un Graph Transformer (plus élevé = meilleur).',
        },
        'secondary': {
            'en': 'Macro-F1 0.790 · 5-fold CV',
            'fr': 'Macro-F1 0,790 · 5 plis',
        },
    },
    'banner_illustration': 'eeg-decoding.png',
    'figure': {
        'file': 'roc_auc_model_comparison.svg',
        'caption': {
            'en': 'ROC AUC · paper Tables 2–3',
            'fr': 'ROC AUC · tableaux 2–3',
        },
    },
    'report_url': '/assets/project_report.pdf',
    'code_url': None,
}

EEG_TEXT = {
    'en': {
        'home': 'Home', 'academic': 'Academic Projects', 'research': 'Research Papers',
        'industrial': 'Real Life Projects', 'about': 'About',
        'academic_label': 'Academic project', 'research_label': 'Research paper',
        'industrial_label': 'Industrial project', 'report': 'Read project report',
        'code': 'View code', 'skills': 'Skills Demonstrated', 'overview': 'Project Overview',
        'methodology': 'Methodology', 'result': 'Key Result', 'no_link': 'Link not supplied',
    },
    'fr': {
        'home': 'Accueil', 'academic': 'Projets académiques', 'research': 'Articles de recherche',
        'industrial': 'Projets professionnels', 'about': 'À propos',
        'academic_label': 'Projet académique', 'research_label': 'Article de recherche',
        'industrial_label': 'Projet industriel', 'report': 'Lire le rapport',
        'code': 'Voir le code', 'skills': 'Compétences mobilisées', 'overview': 'Présentation du projet',
        'methodology': 'Méthodologie', 'result': 'Résultat clé', 'no_link': 'Lien non renseigné',
    },
}
