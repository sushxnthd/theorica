# Public-corpus exporter for Translation-Action Challenge v1.
#
# Sources:
# - GAP Small Groups Library
# - GAP RightQuasigroups SmallQuandle library
#
# Output format: TSV
# name<TAB>source<TAB>order<TAB>library_id<TAB>table
#
# Tables use GAP's 1-based multiplication-table encoding. The Python runner
# converts entries to zero-based indices. Small-quandle tables are transposed
# so that GAP's right-translation convention becomes THEORICA's left-
# translation convention.

if LoadPackage("smallgrp") = fail then
    Error("SmallGrp is required");
fi;
if LoadPackage("RightQuasigroups") = fail then
    Error("RightQuasigroups is required");
fi;

# Prevent GAP from inserting line-continuation backslashes into long table strings.
SizeScreen([1000000,1000000]);

out := "results/translation_action_challenge_v1.tsv";
PrintTo(out, "");

Emit := function(name, source, n, id, table)
    local i, j;
    AppendTo(out, name, "\t", source, "\t", String(n), "\t",
        String(id), "\t[");
    for i in [1..Length(table)] do
        if i > 1 then
            AppendTo(out, ",");
        fi;
        AppendTo(out, "[");
        for j in [1..Length(table[i])] do
            if j > 1 then
                AppendTo(out, ",");
            fi;
            AppendTo(out, String(table[i][j]));
        od;
        AppendTo(out, "]");
    od;
    AppendTo(out, "]\n");
end;

GroupTable := function(G)
    local els;
    els := Elements(G);
    return List(els, a -> List(els, b -> Position(els, a*b)));
end;

# Orders were frozen before evaluation. These are external public-catalogue
# identifiers rather than hand-picked structures.
groupOrders := [24, 32, 36, 40, 48];
for n in groupOrders do
    count := NumberSmallGroups(n);
    for id in [1..count] do
        G := SmallGroup(n, id);
        Emit(
            Concatenation("smallgroup_", String(n), "_", String(id)),
            "SmallGrp",
            n,
            id,
            GroupTable(G)
        );
    od;
od;

# Deterministic, pre-frozen samples from public SmallQuandle libraries.
# Counts are documented by RightQuasigroups for orders < 12.
quandleSpecs := [
    [6, 73, 25, 11],
    [7, 298, 25, 17],
    [8, 1581, 25, 23],
    [9, 11079, 25, 29]
];

SampleIds := function(count, k, offset)
    local ids, x;
    ids := [];
    x := (offset mod count) + 1;
    while Length(ids) < k do
        if not x in ids then
            Add(ids, x);
        fi;
        x := ((x - 1 + 37) mod count) + 1;
    od;
    return ids;
end;

for spec in quandleSpecs do
    n := spec[1];
    count := spec[2];
    k := spec[3];
    offset := spec[4];
    ids := SampleIds(count, k, offset);
    for id in ids do
        Q := SmallQuandle(n, id);
        table := TransposedMat(MultiplicationTable(Q));
        Emit(
            Concatenation("smallquandle_op_", String(n), "_", String(id)),
            "RightQuasigroups:SmallQuandle:opposite",
            n,
            id,
            table
        );
    od;
od;

Print("WROTE ", out, "\n");
QUIT;
