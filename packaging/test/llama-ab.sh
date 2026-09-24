#!/bin/sh
# A/B compare several llama.cpp CPU builds against the installed baseline.
#
# Every build is benchmarked with the same matrix on the same host and the
# results are printed next to each other, so the only difference left is the
# build itself. Candidate directories that do not exist are skipped.
#
# By default the baseline is measured twice, first and last. The gap between
# those two columns is the noise floor of this run, and anything smaller than it
# is not a result. Measured floors have been as high as 3.2% (Phytium S5000C)
# and as low as 0.5% (Xeon E5-2620 v4), so never trust a single baseline.
#
# Both directory layouts are accepted: <dir>/bin/llama-bench (RPM install) and
# <dir>/llama-bench (CI artifact unzipped as is, no bin/ subdir).
#
# usage: sh llama-ab.sh <model.gguf> [threads]
# env:   BUILDS='raw=/opt/llama-cpu opt1=/opt/llama-cpu-opt1 ...'
#        REPS=5

set -eu

MODEL="${1:?usage: $0 <model.gguf> [threads]}"
THREADS="${2:-16}"
REPS="${REPS:-5}"
BUILDS="${BUILDS:-raw=/opt/llama-cpu opt1=/opt/llama-cpu-opt1 opt2=/opt/llama-cpu-opt2 opt3=/opt/llama-cpu-opt3 opt4=/opt/llama-cpu-opt4 raw2=/opt/llama-cpu}"

[ -f "$MODEL" ] || { echo "error: no such model: $MODEL" >&2; exit 1; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/res"

# accept both <dir>/bin (RPM) and <dir> (unzipped artifact); empty output = none
bin_dir() {
    if   [ -x "$1/bin/llama-bench" ]; then printf '%s\n' "$1/bin"
    elif [ -x "$1/llama-bench" ];     then printf '%s\n' "$1"
    fi
}

# which CPU variant a tree loads: catches a stale or mixed up directory
variant() {
    LD_DEBUG=libs "$1/llama-cli" --list-devices 2>&1 \
        | grep -o 'libggml-cpu[^ ]*' | tail -1
}

echo "== $(uname -m), $(getconf _NPROCESSORS_ONLN 2>/dev/null || echo '?') cpus, threads=${THREADS}, reps=${REPS} =="
echo "model: $MODEL"
echo

idx=0
: > "$tmp/list"
for spec in $BUILDS; do
    label=${spec%%=*}
    dir=${spec#*=}
    bin=$(bin_dir "$dir")
    if [ -z "$bin" ]; then
        echo "skip  $label: no llama-bench under $dir" >&2
        continue
    fi
    idx=$((idx + 1))
    printf '%s %s\n' "$label" "$bin" >> "$tmp/list"
    printf 'build %d: %-6s %s (%s)\n' "$idx" "$label" "$bin" "$(variant "$bin")"
done
[ "$idx" -ge 1 ] || { echo "error: none of the builds exist" >&2; exit 1; }
echo

# markdown rows: | model | size | params | backend | threads | test | t/s |
# field 7 is the test name, field 8 is '<mean> +/- <stddev>'
extract() {
    awk -F'|' '
        $7 ~ /(pp|tg)[0-9]/ {
            test_name = $7; gsub(/ /, "", test_name)
            n = split($8, tok, " ")
            for (i = 1; i <= n; i++) if (tok[i] != "") break
            printf "%s %s\n", test_name, tok[i]
        }'
}

i=0
while read -r label bin; do
    i=$((i + 1))
    echo "running $label ..." >&2
    "$bin/llama-bench" -m "$MODEL" -p 512,2048 -n 128 -t "$THREADS" \
        -r "$REPS" --delay 2 -o md 2>/dev/null | extract > "$tmp/res/$i-$label"
    [ -s "$tmp/res/$i-$label" ] || { echo "error: no results from $bin" >&2; exit 1; }
done < "$tmp/list"

# when the first and the last entry point at the same build they bracket the
# run, so their difference is the noise floor
endpoints=0
if [ "$idx" -ge 2 ] && \
   [ "$(head -n 1 "$tmp/list" | cut -d' ' -f2)" = "$(tail -n 1 "$tmp/list" | cut -d' ' -f2)" ]; then
    endpoints=1
fi

awk -v endpoints="$endpoints" '
    FNR == 1 {
        f++
        lab = FILENAME; sub(/.*\//, "", lab); sub(/^[0-9]+-/, "", lab)
        label[f] = lab
    }
    {
        if (!($1 in seen)) { seen[$1] = 1; order[++n] = $1 }
        v[f, $1] = $2 + 0
    }
    END {
        printf "\n== t/s ==\n"
        printf "%-8s", "test"
        for (i = 1; i <= f; i++) printf " %10s", label[i]
        printf "\n"
        for (j = 1; j <= n; j++) {
            t = order[j]
            printf "%-8s", t
            for (i = 1; i <= f; i++) printf " %10.2f", v[i, t]
            printf "\n"
        }

        printf "\n== change vs %s (%%): >+5 keep, <2 noise ==\n", label[1]
        printf "%-8s", "test"
        for (i = 2; i <= f; i++) printf " %10s", label[i]
        printf "\n"
        for (j = 1; j <= n; j++) {
            t = order[j]
            printf "%-8s", t
            b = v[1, t]
            for (i = 2; i <= f; i++) {
                if (b > 0) printf " %9.1f%%", (v[i, t] - b) / b * 100
                else       printf " %10s", "n/a"
            }
            printf "\n"
        }

        if (endpoints == 1) {
            printf "\n== noise floor: %s (first) vs %s (last), same build ==\n", label[1], label[f]
            for (j = 1; j <= n; j++) {
                t = order[j]
                b = v[1, t]; e = v[f, t]
                if (b > 0) printf "%-8s %9.1f%%\n", t, (e - b) / b * 100
            }
            printf "  only changes larger than these are real\n"
        } else {
            printf "\nnote: baseline is not bracketed; put it first and last to get a noise floor\n"
        }
    }
' "$tmp"/res/*
