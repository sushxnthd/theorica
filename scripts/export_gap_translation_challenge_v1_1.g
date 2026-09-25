# Translation-Action Challenge v1.1 public-corpus exporter.
#
# This extends v1 without changing the learner:
# - keeps all original SmallGrp and sampled SmallQuandle cases;
# - adds faithful connected quandles;
# - adds public nonassociative small loops.
#
# Tables use GAP's 1-based multiplication-table encoding. Python converts to
# zero-based indices. Quandle tables are transposed to align the package's
# right-translation convention with THEORICA's left-translation convention.

if LoadPackage("smallgrp") = fail then
    Error("SmallGrp is required");
fi;
if LoadPackage("RightQuasigroups") = fail then
    Error("RightQuasigroups is required");
fi;

out := "results/translation_action_challenge_v1_1.tsv";
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

SampleIds := function(count, k, offset)
    local ids, x;
    ids := [];
    if count = 0 then
        return ids;
    fi;
    x := (offset mod count) + 1;
    while Length(ids) < Minimum(k, count) do
        if not x in ids then
            Add(ids, x);
        fi;
        x := ((x - 1 + 37) mod count) + 1;
    od;
    return ids;
end;

# Original public group corpus.
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

# Original sampled quandle negatives/abstention controls.
quandleSpecs := [
    [6, 73, 25, 11],
    [7, 298, 25, 17],
    [8, 1581, 25, 23],
    [9, 11079, 25, 29]
];

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
            "RQ:SmallQuandle:op",
            n,
            id,
            table
        );
    od;
od;

# New positive cross-family corpus: faithful connected quandles.
# The filter is part of the theorem-promise benchmark design, not learner input.
for n in [6, 7, 8, 9] do
    qs := ConnectedQuandles(n, IsFaithfulRightQuasigroup);
    ids := SampleIds(Length(qs), 25, 101 + 13*n);
    for id in ids do
        Q := qs[id];
        table := TransposedMat(MultiplicationTable(Q));
        Emit(
            Concatenation(
                "faithful_connected_quandle_op_",
                String(n), "_filtered_", String(id)
            ),
            "RQ:FaithfulQuandle:op",
            n,
            id,
            table
        );
    od;
od;

# New public nonassociative-loop corpus. Loops are quasigroups, so their
# left translations are permutations without transposition.
# SmallLoops contains 5 order-5 and 107 order-6 nonassociative loops.
for id in [1..5] do
    L := SmallLoop(5, id);
    Emit(
        Concatenation("smallloop_5_", String(id)),
        "RQ:SmallLoop",
        5,
        id,
        MultiplicationTable(L)
    );
od;

ids := SampleIds(107, 25, 41);
for id in ids do
    L := SmallLoop(6, id);
    Emit(
        Concatenation("smallloop_6_", String(id)),
        "RQ:SmallLoop",
        6,
        id,
        MultiplicationTable(L)
    );
od;

Print("WROTE ", out, "\n");
QUIT;
