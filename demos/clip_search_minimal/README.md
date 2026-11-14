# PartFinder backend

This folder contains the read-only backend for the PartFinder portfolio demo.
Its visual interface lives in `frontend/components/partfinder_search.py`, and the
portfolio page is available at `/partfinder` when the main website starts.

The backend loads the already-provisioned ViT-B/32 checkpoint and `data/catalog.db`
once at website startup. It serves catalog images and performs text/image query
embedding only; it contains no mesh extraction, catalog-building, or embedding
generation pipeline.
