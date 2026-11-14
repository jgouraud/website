# PartFinder runtime decisions

PartFinder is a portfolio page, not a separate application. Its search interface
is rendered by `frontend/components/partfinder_search.py`; the read-only runtime
and ASGI hooks remain under `demos/clip_search_minimal`.

At website startup, the backend opens the existing catalog and loads the verified
ViT-B/32 checkpoint once. The model, catalog vectors, catalog-image route, and
upload limits are shared by visitors. Browser sessions retain only their own query
text/image embeddings and do not write to the catalog.

The repository deliberately contains no mesh extraction, preview rendering,
catalog construction, or catalog-encoding pipeline. The application only reads
the already-provisioned database and checkpoint. Query-time CLIP encoding remains
necessary for visitor searches.

Uploads are limited to one PNG/JPEG/WEBP image of at most 12 MiB and 40 megapixels.
Descriptions are limited to 2,000 characters. Search allows two concurrent CPU
tasks with a 30-second visitor deadline. The application remains read-only and
does not download model assets at startup or during inference.
