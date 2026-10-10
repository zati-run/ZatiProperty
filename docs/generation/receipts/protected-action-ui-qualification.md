# Protected action UI qualification

Current finding: the live manager-role probe confirms that the native collection form is hidden while generic create is denied. The temporary page and route grants were removed and verified. The source-only observations below are historical; the live result and cleanup are recorded at the end.

## Initial source-only checkpoint

2026-10-10 UTC. NocoBase CE 2.2.21, current qualified Loom native catalog. No pages generated and no protected action executed. Source contract candidate 5859045c2d1efe5befa877d06ea1fae2ca6502d7 remains blocked by independent security findings.

Live `flowSurfaces:catalog` for existing native EditFormModel returned `js` / `JSFormActionModel`, `createSupported:true`. Public configure options include title, htmlType, code and version; click is a supported event. Sanitized action descriptor is `protected-action-ui-catalog.json`. Author through discovered Loom compose/configure operations only; no raw node patch is needed for this action.

Installed documentation under `@nocobase/plugin-flow-engine/dist/ai/docs/runjs/context/form.md` explicitly documents form-action ctx.form, validateFields(), getFieldsValue(true), nested field name paths and setFieldsValue. `context/request.md` documents authenticated ctx.request with relative resource:action URL, POST method and data body, returning Axios response.data. These are source/API contracts, not a successful rendered custom-action test.

## Initial candidate pattern, superseded by the live probe

Use a native create/edit form for collecting values, with the default generic Submit removed. Add a named JS form action with htmlType button, the catalog-supported code version and bounded code authored through Loom. Validate fields, construct only the protected action allowlisted input, call relative zpPropertyTenancy:createDraftTenancy or the specific action with ctx.request, and keep form values when validation/server failure occurs. Read values explicitly; never forward the whole native record or generic form object. Current record identity/version must be mapped explicitly. Server still enforces actor, scopes, invariants and CAS. Show useful bounded error and success feedback; refresh/readback only after confirmed success. Network-unknown writes require native readback before retry.

The browser executing this generated native action is application behavior, not an agent bypassing Loom authoring. Do not use generic resource save, default form submit, triggerWorkflow as a proxy for protected mutations, or direct agent REST writes.

## Remaining qualification

The initial source inspection suggested simple lifecycle inputs might use the form/action pattern; the later live CRUD-denied probe did not qualify it. Full draft tenancy needs structured term and party inputs plus a transient reason; ownership needs interests and complete-set confirmation. This review has not qualified native non-persisted fields or collection-relation subform mapping for those exact request shapes. Do not add generic writable scratch fields or expose protected collections as CRUD to make the form work. First discover field/subform contracts on the intended form; if transient schema fields are absent, add a reusable typed Loom/native action-form capability with explicit input schema and protected-action binding, rather than inventing configure keys.

Before acceptance: native authoring/readback, actual current-role request identity, no generic POST on click/Enter, field validation and preserved failure state, exact payload and permitted account chooser, duplicate-click/unknown-write behavior, success persistence, mobile layout and keyboard, allowed/denied roles. No new Loom gap is established for button wiring; the structured/transient input composition remains an explicit open qualification.

## Follow-up: CRUD coupling remains a blocker to qualification

Pinned client bundle index-b2532057.js exports CreateFormModel as hH. Its getAclActionName returns create and submit delegates submitHandler. Native submitFromRunJs scans submitSettings actions, then falls back to this.submit() for CreateFormModel/EditFormModel unless publicFormRuntime. This establishes CRUD coupling, not a demonstrated Enter behavior; Enter must be tested. Merely removing Submit and adding JS action does not establish a safe CRUD-denied action form. No public nonpersistent arbitrary input-schema contract or exact current-revision association subform was qualified in this read-only pass.

Recommended bounded extension if ordinary forms cannot satisfy those gates: reusable ActionFormModel registered by a Loom companion, with explicit transient input schema (scalar/object/bounded array), native form controls, typed relative action binding validated against target action Swagger, custom-action ACL rendering instead of create/update ACL, explicit record/version input mapping, named submit that only dispatches that action, and no generic resource save path. Support validation, scoped record choices, pending/unknown/error preservation, success readback, native layout/mobile/keyboard. Expose through Loom catalog/compose via an explicit public contract; do not emulate this with undocumented node parameters. This is a proposal only, pending source/capability review.

## Live diagnostic result and cleanup

After explicit coordinator authorization, created a temporary page through Loom with native CreateFormModel on zp_tenancies, bound code field and JSFormActionModel titled Validate only; code only displays a message. Removed auto-generated generic Submit with native removeNode and captured native readback. Added only the owned route IDs to manager navigation, preserving existing grants. Generic create remained denied.

Fresh manager browser observed 2026-10-10T10:21:21.745Z: page/navigation title rendered; code input and JS action both absent. Screenshot visually inspected: empty page body. Thus native collection create form cannot supply this protected-action UI under the current denied generic-create permissions. Enter/button execution was impossible because controls were absent; no claim of their behavior is made. Browser intercepted all non-GET domain requests to prevent any data write; zero such attempts occurred. Evidence: screenshots/action-form-crud-denied.json and .png, action-form-probe-native.json.

Cleanup completed exclusively through Loom: removed only owned page/tab grants, verified manager route ID set exactly equals prior snapshot, destroyed exact diagnostic page via discovered destroyPage, and read back target-not-found plus no matching accessible routes. Evidence: action-form-probe-cleanup.json and routes-before/after JSON. Initial missing-icon and compose-settings validation rejections were reconciled before corrections; schema-change interruption caused no write. removeNode rejected page removal and explicitly directed destroyPage; page readback preceded the corrected cleanup. No generic CRUD permission was added.

Environment at resumed probe: NocoBase2.2.21; installed property/tenancy0.1.0; native238 + supplemental25, catalog d300687de13a3370130cda5e4404ab935e1f0ad3889af6439c5dc900adc33939. This establishes the action-form rendering gap, not lifecycle acceptance. Reusable action-form work is justified; no standalone app or manually authored page is proposed.
