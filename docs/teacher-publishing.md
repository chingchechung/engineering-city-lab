# Manual teacher publication

Use the existing local **Engineering Maze Lab teacher Python GUI**, unchanged.
Run `py -3.12 tools\assignment_editor.py` from the reference project's checkout,
not the city repository. The pinned [editor guide](https://github.com/chingchechung/ece_hw_webproject/blob/70cc35d9ce828bcd5357f16fe85f303aa2d30cd9/docs/assignment-editor-guide.md)
describes private drafts, Allow Play and explicit public exports. No GUI is
duplicated here. Keep all private work and backups outside any served directory.

## Export, validate, then upload

1. Create/edit S01–S12 privately in the GUI. Select four or five questions, three
   or four choices as supported by the selected JSON version. Preserve v1/v2;
   do not convert silently. Students select **one** label, including v2.
2. **Validate Unit**, then **Export Selected Unit JSON** to a separate local
   public-export folder. Mark intended units **Allow Play** and **Export Public
   Manifest JSON**. The GUI verifies freshness/completeness of every allowed
   export before writing the manifest. Choosing a folder alone does not publish.
3. Review the exported fields/content and validate using the existing read-only
   validator in this city checkout (or the identical reference tool):

   ```sh
   python3 tools/validate_assignments.py /private/path/public-export/assignments/manifest.json
   ```

   Windows: `py -3 tools/validate_assignments.py C:\CourseExports\assignments\manifest.json`.
   Validate individual exports similarly by passing their exact `Sxx.json` paths.
   The manifest command verifies its schema/allowlist, every listed file's
   matching filename/unit ID, versioned data, URLs and matching normalized title.
   Missing files, symlinks, invalid units or title mismatches must be fixed before
   publication. It never visits video/Form URLs or uploads anything. The JSON
   schemas/validation rules are unchanged from the approved reference.
4. Check every **real** question/explanation video with a student-accessible
   browser: correct course/question, availability, intended language (including
   English explanation), visibility restrictions and accessibility. Check the
   actual Google Form's access, sign-in/domain restrictions, response acceptance
   and submission settings. Test a real submission only under the instructor's
   own course policy. Supported HTTPS YouTube/Forms syntax is necessary but
   does not establish content, playback or submission availability.
5. Upload only selected validated `Sxx.json` files to the site's `assignments/`
   directory. Verify the uploaded bytes and correct JSON MIME/HTTP 200 at each
   listed path. **Upload the validated manifest last**, preferably by a server-side
   atomic rename of a temporary upload. Never leave a partial JSON at its final
   URL; ask the administrator about atomic upload/rename support if needed.
6. In the app open **Assignments**, press **Refresh list**, select the published
   unit and confirm replacement. Check the title, question count, order and UTF-8
   text. Opening/refreshing the list does not replace the current attempt; a valid
   confirmed switch resets only question progress. Failed/cancelled loading
   preserves the current session. A full page reload loses practice progress.

No actual course exports or media have been published in Phase 4. Never follow
synthetic fixture YouTube/Forms links as real material. The controlled review
harness in [Phase 3 results](phase-3-results.md#windows-11-chromeedge-manual-acceptance)
intercepts them before navigation. It validates UI behavior, not real media.

## Common changes and rollback

| Operation | Safe manual order |
| --- | --- |
| Publish one additional unit | Export/validate its Sxx.json; export/validate the complete desired manifest; upload the new unit, verify it, then replace the manifest last. Existing entries stay intact. |
| Update an existing unit | Keep a private backup outside the web tree. Export/validate the changed unit and manifest together. Prefer maintenance or temporarily remove the entry first; replace the unit atomically, verify it, then publish the matching manifest last. Title changes can cause a temporary mismatch if uploads are not coordinated. |
| Remove from selection | Disable Allow Play and export/validate a new manifest, then upload it. Fresh lists will no longer discover the unit. Already loaded in-memory attempts can continue; refresh is not revocation. |
| End direct HTTP access | Remove the entry first, then explicitly delete its uploaded Sxx.json and any public temporary/backup copies. Verify a fresh direct request returns 404, clear any server/CDN cache, and check caches per institutional policy. Copies already downloaded cannot be recalled. |
| Roll back | Restore the prior matching validated unit files, verify them, then restore the prior validated manifest last. Keep rollback copies private. |

The manifest controls **discovery, not HTTP access**. A JSON file left on the server
is directly downloadable even when absent from the list, and a stale list in an
already open browser can still request its file. Do not depend on filenames,
directory-listing settings or the manifest for confidentiality.

Before every upload review the exact export list. Exclude private drafts,
retained/disabled Q05 data, disabled choices, teacher notes, authoring metadata,
unpublished answer documents, backups, fixtures and credentials. Correct answers
inside deliberately published client JSON are necessarily public. Engineering
City Lab is for practice, not secure examinations. It neither records grades nor
observes Form submissions; Google Forms is the submission system.
