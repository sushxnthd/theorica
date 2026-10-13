# Frozen exporter for the prospective nonfaithful SmallQuandle holdout.
if LoadPackage("RightQuasigroups") = fail then
    Error("RightQuasigroups is required");
fi;

out := "results/nonfaithful_public_holdout.tsv";
PrintTo(out, "");

OldIds := function(count, k, offset)
    local ids, x;
    ids := [];
    x := (offset mod count) + 1;
    while Length(ids) < Minimum(k, count) do
        if not x in ids then Add(ids, x); fi;
        x := ((x - 1 + 37) mod count) + 1;
    od;
    return ids;
end;

FreshIds := function(count, k, start, excluded)
    local ids, x;
    ids := [];
    x := (start mod count) + 1;
    while Length(ids) < Minimum(k, count - Length(excluded)) do
        if not x in ids and not x in excluded then Add(ids, x); fi;
        x := ((x - 1 + 53) mod count) + 1;
    od;
    return ids;
end;

Emit := function(n, id, table)
    local i, j;
    AppendTo(out, String(n), "\t", String(id), "\t[");
    for i in [1..Length(table)] do
        if i > 1 then AppendTo(out, ","); fi;
        AppendTo(out, "[");
        for j in [1..Length(table[i])] do
            if j > 1 then AppendTo(out, ","); fi;
            AppendTo(out, String(table[i][j]));
        od;
        AppendTo(out, "]");
    od;
    AppendTo(out, "]\n");
end;

specs := [[8, 1581, 23, 1279], [9, 11079, 29, 1376]];
for spec in specs do
    n := spec[1]; count := spec[2]; oldOffset := spec[3]; start := spec[4];
    opened := OldIds(count, 25, oldOffset);
    ids := FreshIds(count, 80, start, opened);
    for id in ids do
        Q := SmallQuandle(n, id);
        # Transpose RightQuasigroups' convention into left translations.
        Emit(n, id, TransposedMat(MultiplicationTable(Q)));
    od;
od;

Print("WROTE ", out, "\n");
QUIT;

