# Native reverse-association nullability mismatch

Reviewed schema ACL preservation0.1.4 source:
0ce981ad73c8cfb89341eec189d9bcee0fbd50a8; independent review
21d98a9dfb70eb9ae66baad653bb3362c337dc7b,32tests.
Archive SHA-256106724c0062d8ea36e98e54b4ba2ca6c4efc3b6498c0cb6e72e56f32dc5ca3e4;
all nine files matched source. One Loom upload succeeded; catalog drift on its
following read was reconciled by capture and native package read, not retry.

Diagnostic capability catalog SHA-256:
67eca0dff67322253a302e606ffab1e8b08342b8812cb38c52a4fd08d3216a21;
256 native plus25supplemental operations. Package installed/enabled/compatible.

After native reload, the full persisted baseline still matched receipt025 and
the new service reported no prior preview diagnostic. Its related-state digest
was608411ad3ebedbc7565f5fb9215f29d61c2ff223ec5171ed76c8d105f815ed7a.
A new explicitly journaled diagnostic preview was performed once, to obtain
the previously unavailable native difference. It again rejected with
PREVIEW_RELATED_STATE_CHANGED.

The sole changed path was related/attributes/buildingId/allowNull.
Related associations, persisted foreign-key definition and related field
definitions retained identical digests. Post-preview related-state digest:
212a21b69298c360ff04ca28ca730aa97fc0d43e06abffd1603350096a101a0b.
The whole persistent baseline and four role snapshots remained identical.
The target zp_buildings.units remains absent; no positive authoring occurred.

This identifies the live internal mismatch, not a fix or acceptance. A bounded
Loom preservation change is assigned for both successful association creation
and rollback. Physical database nullability was already separately unqualified;
no new physical NOT NULL claim is made.
