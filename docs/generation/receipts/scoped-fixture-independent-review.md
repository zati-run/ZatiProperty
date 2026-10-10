# Scoped constructor fixture source review

Root independently reviewed exact3dbe2d4595dc9106c7f97c8266e114665f168a1d (adcf712 plus requested correction). Eight safety tests pass on DGX. Approved bounded synthetic fixture construction through discovered Loom operations, one durable journal per step. The correction enforces exact owned permissions before and after every later step, rejects duplicate actions/resources, non-main resources and disabled action configuration. Existing roles, resource/action/scope rows and user identifiers remain preservation invariants. Credentials remain private and are never receipt contents.

Live custom-action permission behavior and effective scoped-constructor denial are not established by these source tests. A fresh complete ACL baseline is required after fixture creation. This is not permission to broaden existing application roles.
