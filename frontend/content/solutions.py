"""Content for the planned business solution previews."""

SOLUTION_COPY = {
    'flowdesk': {
        'EN': {
            'kicker': 'Service operations  •  workflow automation',
            'lead': 'From incoming service requests to clear ownership, timely follow-up and actionable visibility.',
            'summary_title': 'A more organized way to handle internal requests',
            'summary': (
                'FlowDesk is designed to bring service requests into a single, trackable process. '
                'The upcoming demo will show how requests can be automatically categorized and routed, '
                'how teams can manage work in one shared queue, and how managers can spot backlog, '
                'priorities and overdue items before they become bottlenecks.'
            ),
            'steps_title': 'What the interactive demo will show',
            'steps': [
                ('Submit & route', 'Create a service request and see it categorized, prioritized and assigned to a team through an automated workflow.'),
                ('Manage the queue', 'Search and filter incoming work, update request status, and keep a traceable history of who changed what.'),
                ('Track service performance', 'Explore a dashboard for backlog, overdue requests, priority mix and scheduled operational summaries.'),
            ],
            'example_title': 'Business value',
            'example': 'For operations and internal service teams: less manual triage, fewer missed follow-ups, and clearer accountability from intake through resolution.',
        },
        'FR': {
            'kicker': 'Opérations de service  •  automatisation des workflows',
            'lead': 'Des demandes entrantes à une prise en charge claire, un suivi fiable et une meilleure visibilité.',
            'summary_title': 'Une gestion plus fluide des demandes internes',
            'summary': (
                'FlowDesk vise à centraliser les demandes dans un processus traçable. '
                'La future démo montrera comment catégoriser et orienter automatiquement les demandes, '
                'gérer les tâches dans une file partagée et suivre les priorités, le volume en attente '
                'et les retards pour éviter les blocages.'
            ),
            'steps_title': 'Ce que présentera la démo interactive',
            'steps': [
                ('Soumettre et orienter', 'Créer une demande puis voir sa catégorisation, sa priorisation et son attribution automatiques.'),
                ('Gérer la file', 'Rechercher et filtrer les demandes, modifier leur statut et conserver un historique des actions.'),
                ('Piloter les opérations', 'Consulter des indicateurs sur les demandes en attente, les retards, les priorités et les rapports réguliers.'),
            ],
            'example_title': 'Valeur métier',
            'example': 'Pour les équipes de support et les opérations : moins de tri manuel, moins de relances oubliées et une meilleure traçabilité du traitement.',
        },
    },
    'procurematch': {
        'EN': {
            'kicker': 'Procurement & finance  •  document automation',
            'lead': 'Catch invoice discrepancies before approval, without reviewing every document line by line.',
            'summary_title': 'Turn supplier documents into review-ready exceptions',
            'summary': (
                'ProcureMatch is designed to help purchasing and finance teams reconcile supplier invoices '
                'against purchase orders. The upcoming demo will use document extraction to capture invoice '
                'details, compare suppliers, quantities and unit prices, and flag differences that need '
                'human review — with a clear record of each decision.'
            ),
            'steps_title': 'What the interactive demo will show',
            'steps': [
                ('Capture the invoice', 'Upload an invoice, inspect OCR-extracted header and line items, and correct fields that need attention.'),
                ('Compare with the PO', 'Match the invoice to the purchase order and highlight price, quantity or reference discrepancies.'),
                ('Review & report', 'Route exceptions for human approval or rejection, retain an audit trail, and explore supplier variance summaries.'),
            ],
            'example_title': 'Example business scenario',
            'example': 'An invoice lists 10 chairs at CHF 135 each, while the purchase order specifies CHF 120. ProcureMatch will flag the CHF 150 price variance for review — never automatically approving the payment.',
        },
        'FR': {
            'kicker': 'Achats & finance  •  automatisation documentaire',
            'lead': 'Repérer les écarts de facturation avant validation, sans vérifier chaque ligne manuellement.',
            'summary_title': 'Transformer les factures en exceptions à examiner',
            'summary': (
                'ProcureMatch vise à aider les équipes achats et finance à rapprocher les factures '
                'fournisseurs des bons de commande. La future démo présentera l’extraction des données '
                'des factures, la comparaison des fournisseurs, quantités et prix unitaires, ainsi que '
                'la détection des écarts nécessitant une validation humaine et traçable.'
            ),
            'steps_title': 'Ce que présentera la démo interactive',
            'steps': [
                ('Lire la facture', 'Importer une facture, vérifier les champs extraits par OCR et corriger les données incertaines.'),
                ('Rapprocher la commande', 'Comparer les prix, quantités et références de la facture avec le bon de commande.'),
                ('Décider et suivre', 'Soumettre les écarts à validation humaine, conserver une piste d’audit et consulter les synthèses par fournisseur.'),
            ],
            'example_title': 'Exemple métier',
            'example': 'Une facture indique 10 chaises à CHF 135 pièce, alors que le bon de commande prévoit CHF 120. ProcureMatch signalera un écart de CHF 150 à examiner, sans approuver automatiquement le paiement.',
        },
    },
}

PAGE_LABELS = {
    'EN': {
        'breadcrumb': 'Business solutions',
        'status_title': 'Work in progress',
        'status_soon': 'Coming soon',
        'status_note': 'The interactive demo is being developed. Here is what you will be able to explore.',
        'back': 'Back to business solutions',
        'missing_art': 'Add the original illustration to the assets folder to display this preview.',
    },
    'FR': {
        'breadcrumb': 'Solutions professionnelles',
        'status_title': 'En cours de réalisation',
        'status_soon': 'Bientôt disponible',
        'status_note': 'La démo interactive est en développement. Voici les fonctionnalités prévues.',
        'back': 'Retour aux solutions professionnelles',
        'missing_art': 'Ajoutez l’illustration d’origine dans le dossier assets pour afficher cet aperçu.',
    },
}
