# Free DOI / archival release

THEORICA is prepared for Zenodo's GitHub integration.

## Cost

Zenodo is free to use and assigns a DOI to published records.

## Release procedure

1. Sign in to Zenodo and connect the GitHub account.
2. Enable the `sushxnthd/theorica` repository in Zenodo's GitHub integration.
3. Create a GitHub release from the exact commit intended for citation.
4. Wait for Zenodo to archive the release.
5. Verify title, author, license, description, repository URL, and files before publicizing the DOI.
6. Add the DOI badge and DOI to `CITATION.cff` only after Zenodo actually assigns it.

## Before release

Confirm:

- CI is green.
- `docs/CLAIM_BOUNDARIES.md` is current.
- The native ACDB replay artifact exists.
- The native DiscoverPhysics report retains the Coulomb failure.
- `paper/PREPRINT.md` matches the public claims.
- No API key, secret, private data, or unpublished personal contact information is present.
- Release tag is immutable and records the exact commit.

Do not invent a DOI or reserve a DOI in documentation before Zenodo assigns one.
