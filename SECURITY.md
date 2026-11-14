# Security and dependency maintenance

Owner: the repository maintainer. Report vulnerabilities privately to the
maintainer, without attaching customer catalogs, uploaded images, queries, or
credentials to public issues.

The portfolio contains public content. PartFinder is an unauthenticated local
demo and binds to loopback by default. A public/private-data deployment requires
its own authentication, authorization, TLS, proxy limits, and retention review.

Before releases or dependency updates, the maintainer reviews relevant upstream
advisories, updates the lockfiles, runs Windows/Linux backend and browser gates,
and verifies the supported checkpoint/model smoke test. Locking versions does not
replace vulnerability triage. GitHub Actions are pinned to reviewed commits and
run with read-only repository permissions; no project secrets are required.

Do not commit environments, private catalogs, generated previews, model weights,
or local configuration secrets. Model weights are accepted only after SHA-256
verification against the official pinned identity; arbitrary local checkpoints
and automatic network downloads at app startup are not supported.
