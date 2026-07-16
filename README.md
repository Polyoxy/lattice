# Lattice

Beat-production engine. Theory-constrained symbolic generation (line-of-fifths
harmony core, style-carded loop grammar, measured groove parameters) with
offline rendering. Phase 1 targets the harmonic and rhythmic language of
Brent Faiyaz, Conductor Williams, and Jesús Molina — parameters cited in
`docs/research/`, design in `docs/specs/2026-07-15-beatmaker-design.md`.

## Quickstart

    uv sync
    uv run python -c "
    from lattice import make_beat
    beat = make_beat(style='faiyaz', key='C#m', bpm=72, n=5, seed=7)[0]
    print(beat.explain())
    beat.save('out/demo')"

`out/demo/beat.mid` opens anywhere; `beat.json` records every parameter
that produced the beat; re-running the same `make_beat` call regenerates
it bit-identically. GM preview: `sudo apt install --no-install-recommends
fluidsynth fluid-soundfont-gm`, then `beat.preview('out/demo/p.wav')`.
Real rendering (scsynth, texture buses, mastering) is the next phase.

## Layout

    src/lattice/theory/    spelled pitch, intervals, chords, keys
    src/lattice/harmony/   loop grammar, scoring, substitutions, elaboration
    src/lattice/voicing/   templates, constraints, minimal-motion realization
    src/lattice/groove/    drums, bass, keys, pocket pass
    src/lattice/           cards, arrange, beat, midi, explain, api
    tests/calibration/     documented-corpus coverage and ranking gates

## Verify

    uv run pytest && uv run pytest -m slow && uv run mypy && uv run ruff check

## License

Apache-2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
