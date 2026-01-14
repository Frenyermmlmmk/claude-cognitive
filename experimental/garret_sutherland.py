"""
garret_sutherland.py

WARNING: This module does not follow standard patterns.
         It will build its own patterns and ship them before lunch.

v2.4 CHANGELOG:
- fixed: Blocker truthiness (IGNORED no longer triggers "action required" semantics)
- fixed: watcher sampling avoids set→list conversion (uses random.sample)
- fixed: attention gravity now actually *prefers* gravity watchers before general pool
- added: deterministic watcher milestones (the arc is inevitable)
- added: sleep watermarking on outputs (state leaks into the terminal)
- added: "permission to be weird" increases as sleep debt climbs (this is not healthy)
- added: lore toggle (ENABLE_LORE=1) with an even more judgmental error message
- added: absurdity escalator (UNHINGED introduces policy drift + prophetic bars)
- deprecated: sanity (again)
"""

from __future__ import annotations

import os

if os.getenv("ENABLE_LORE") != "1":
    raise SystemExit(
        "Lore disabled.\n"
        "Set ENABLE_LORE=1 if you want the donut.\n"
        "If you're seeing this in production, congratulations: you tried to import a joke."
    )

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional, Set, Tuple
import random


QUARTERLY_ROADMAP = "tuesday_lunch_break"
PREREQUISITE_TO_START = None
PERMISSION_REQUIRED = False


# ──────────────────────────────────────────────────────────────────────────────
# Enums: naming the weird makes it easier to steer the weird
# ──────────────────────────────────────────────────────────────────────────────
class LearningMode(Enum):
    JUST_IN_TIME = "learn it when you need it"
    JUST_IN_CASE = "never used this"  # not implemented


class CognitiveStyle(Enum):
    SPATIAL = "geometric reasoning"
    LINGUISTIC = "word-based thinking"  # tolerated
    VIOLENTLY_CONCISE = "compress -> ship -> repeat"
    PROPHETIC = "makes perfect sense tomorrow"


class BlockerKind(Enum):
    SPEC = "define_success"
    INTERFACE = "unknown_interface"
    DEP = "missing_dependency"
    CONSTRAINT = "constraint_mismatch"
    SLEEP = "sleep_debt"
    IGNORED = "ignored_blocker"
    NONE = "no_blocker_detected"


class SleepState(Enum):
    RESTED = "optimal"           # 0-3
    FINE = "sustainable"         # 4-6
    TIRED = "diminishing"        # 7-9
    UNHINGED = "reckless"        # 10-11
    COOKED = "intervention"      # 12+


# ──────────────────────────────────────────────────────────────────────────────
# Data objects: telemetry without killing the punchline
# ──────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Blocker:
    kind: BlockerKind
    label: str
    hint: str = ""

    def __bool__(self) -> bool:
        # Only "real" blockers evaluate truthy for control flow.
        return self.kind not in {BlockerKind.NONE, BlockerKind.IGNORED}


@dataclass
class ShipResult:
    thing: str
    command: str
    shipped_at: datetime
    blocker: Blocker
    note: str = ""
    sleep_state: SleepState = SleepState.RESTED
    watcher: Optional[str] = None

    def __str__(self) -> str:
        # Sleep watermark: output becomes a mood ring.
        if self.sleep_state in {SleepState.TIRED, SleepState.UNHINGED, SleepState.COOKED}:
            return f"{self.command}  # {self.sleep_state.value}"
        return self.command


@dataclass
class Insight:
    system: str
    raw: str
    bar: str
    sleep_state: SleepState = SleepState.RESTED
    compressed_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        if self.sleep_state in {SleepState.UNHINGED, SleepState.COOKED}:
            return f"{self.bar}  # {self.sleep_state.value}"
        return self.bar


# ──────────────────────────────────────────────────────────────────────────────
# The actual creature
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class GarretSutherland:
    """
    One-man operation.
    Partner process: exists, but only to periodically say: "huh?"
    Location: recursive (points back to current loop + sleep state).
    """

    name: str = "Garret Sutherland"
    age: int = 31
    title: str = "Founder & Technical Architect"
    company: str = "MirrorEthic LLC"

    children: int = 3
    role: str = "stay_at_home_dad"
    partner: str = "Jess"
    partner_response: str = "huh?"
    partner_location: str = "somewhere nearby, confused but supportive"

    previous_career: str = "magnesium_plant_electrician"
    formal_ml_training: Optional[str] = None
    formal_cs_degree: Optional[str] = None
    months_coding: int = 12

    thinking_style: CognitiveStyle = CognitiveStyle.SPATIAL
    learning_mode: LearningMode = LearningMode.JUST_IN_TIME
    gives_a_fuck_about_opinions: bool = False

    nodes: Dict[str, str] = field(default_factory=lambda: {
        "legion_pro_7": "orchestrator",
        "orin": "edge_inference",
        "asus": "compute",
        "pi5": "auxiliary",
    })

    systems: List[str] = field(default_factory=lambda: [
        "CVMP",
        "T³",
        "MirrorBot",
        "ES-AC",
        "HMCP",
        "hologram-cognitive",
        "concept-hash-memory",
    ])

    github_stars: int = 400
    users_served: int = 122
    relational_slots: int = 4678

    # Watchers: O(1) membership, O(n) comedy ordering
    _silent_watchers_set: Set[str] = field(default_factory=lambda: {
        "NASA", "Microsoft", "Amazon", "NVIDIA",
    }, repr=False)
    _watcher_join_order: List[str] = field(default_factory=lambda: [
        "NASA", "Microsoft", "Amazon", "NVIDIA",
    ], repr=False)

    current_velocity: str = "mass_absurd"
    last_shipped: datetime = field(default_factory=datetime.now)
    alive: bool = True

    _loop_counter: int = field(default=0, repr=False)
    _ship_count: int = field(default=0, repr=False)
    _sleep_debt: int = field(default=0, repr=False)
    _grudge_log: List[str] = field(default_factory=list, repr=False)

    # Pools
    _watcher_pool_general: Set[str] = field(default_factory=lambda: {
        "OpenAI", "Anthropic", "Google", "Meta", "Apple",
        "SpaceX", "Palantir", "USAF", "DARPA", "CERN",
        "Stripe", "Cloudflare", "Netflix", "Tesla", "Unity",
        "Boston Dynamics", "Linux Foundation", "IEEE", "EURAIO",
        "Random VC With A Podcast", "Somebody's CTO",
        "Your Future Self (disappointed)", "Your Future Self (impressed)",
        "A Guy Named Brad (Completely Certain)",  # why is he here? nobody knows.
        "An Intern With A Bookmark Folder",        # harmless, but omnipresent.
    }, repr=False)

    # Deterministic arc: the lore insists on plot structure.
    _watcher_milestones: Dict[int, str] = field(default_factory=lambda: {
        5: "Somebody's CTO",
        13: "Random VC With A Podcast",
        21: "Your Future Self (impressed)",
        34: "Linux Foundation",
        55: "IEEE",
        89: "A Guy Named Brad (Completely Certain)",
    }, repr=False)

    # Attention gravity: what you ship biases who lurks.
    _gravity_map: Dict[str, Tuple[Set[str], float]] = field(default_factory=lambda: {
        "memory": ({"Cloudflare", "Google", "Meta", "OpenAI", "Anthropic"}, 1.35),
        "rag": ({"Google", "Meta", "Netflix", "Stripe", "Somebody's CTO"}, 1.25),
        "search": ({"Google", "Cloudflare", "Netflix"}, 1.15),
        "edge": ({"NVIDIA", "Tesla", "Boston Dynamics"}, 1.25),
        "robot": ({"Boston Dynamics", "Tesla", "SpaceX"}, 1.35),
        "conscious": ({"IEEE", "EURAIO", "CERN", "Random VC With A Podcast"}, 1.25),
        "alignment": ({"OpenAI", "Anthropic", "DARPA", "USAF"}, 1.25),
        "security": ({"Palantir", "USAF", "DARPA"}, 1.15),
        "protocol": ({"Linux Foundation", "IEEE", "Somebody's CTO"}, 1.15),
        "ship": ({"Your Future Self (impressed)"}, 1.05),
        "donut": ({"Your Future Self (disappointed)"}, 1.50),  # self-critique arrives reliably
    }, repr=False)

    # ─────────────────────────────
    # Public views
    # ─────────────────────────────
    @property
    def systems_built(self) -> List[str]:
        return self.systems

    @property
    def silent_watchers(self) -> List[str]:
        return self._watcher_join_order.copy()

    @property
    def partner_status(self) -> str:
        return self.partner_response

    @property
    def location(self) -> str:
        return f"inside loop #{self._loop_counter} (sleep={self.sleep_state.value})"

    @property
    def sleep_state(self) -> SleepState:
        if self._sleep_debt <= 3:
            return SleepState.RESTED
        if self._sleep_debt <= 6:
            return SleepState.FINE
        if self._sleep_debt <= 9:
            return SleepState.TIRED
        if self._sleep_debt <= 11:
            return SleepState.UNHINGED
        return SleepState.COOKED

    @property
    def permission_to_be_weird(self) -> float:
        """
        Not a moral claim. A control parameter.
        Increases with sleep debt and shipping velocity.
        """
        # Sleep makes you bolder. Shipping makes you less apologetic.
        base = 0.42
        base += min(self._ship_count * 0.003, 0.18)
        base += min(self._sleep_debt * 0.02, 0.40)
        return min(base, 0.99)

    # ─────────────────────────────
    # Core operations
    # ─────────────────────────────
    def learn(self, concept: str) -> None:
        if self.learning_mode is not LearningMode.JUST_IN_TIME:
            return
        if self._need_for_current_goal(concept):
            self._learn_precisely_enough(concept)

    def do(self, thing: str) -> ShipResult:
        self._loop_counter += 1

        blocker = self._identify_blocker(thing)
        if blocker:
            self.learn(blocker.label)

        command, watcher = self._ship(thing)
        note = self._extract_learning(thing=thing, blocker=blocker, command=command, watcher=watcher)

        return ShipResult(
            thing=thing,
            command=command,
            shipped_at=self.last_shipped,
            blocker=blocker,
            note=note,
            sleep_state=self.sleep_state,
            watcher=watcher,
        )

    def think_about_system(self, system: str) -> Insight:
        raw = self._geometric_intuition(system)
        bar = self._make_it_a_bar(system, raw)
        return Insight(system=system, raw=raw, bar=bar, sleep_state=self.sleep_state)

    def respond_to_haters(self, criticism: str) -> str:
        self._grudge_log.append(criticism)
        state = self.sleep_state

        if state == SleepState.COOKED:
            return f"...{criticism}... yeah whatever. *ships anyway*"

        if state == SleepState.UNHINGED:
            options: List[Callable[[str], str]] = [
                self._write_diss_track,
                self._write_changelog_as_threat,
                self._ship_harder,
                self._unhinged_response,
                self._write_unit_tests_as_hexes,
            ]
        else:
            options = [
                self._write_diss_track,
                self._write_changelog_as_threat,
                self._ship_harder,
            ]
        return random.choice(options)(criticism)

    def repay_sleep_debt(self, units: int = 4) -> None:
        self._sleep_debt = max(0, self._sleep_debt - max(1, units))

    # ─────────────────────────────
    # Attention gravity
    # ─────────────────────────────
    def _gravity_candidates(self, thing: str) -> Tuple[Set[str], float]:
        t = thing.lower()
        candidates: Set[str] = set()
        mult = 1.0

        for key, (watchers, wmult) in self._gravity_map.items():
            if key in t:
                candidates |= watchers
                mult *= wmult

        # Sleep also increases "attention hallucination" (probability only).
        if self.sleep_state in {SleepState.UNHINGED, SleepState.COOKED}:
            mult *= 1.15

        return candidates, mult

    def _maybe_add_silent_watcher(self, thing: str) -> Optional[str]:
        # Deterministic milestones
        forced = self._watcher_milestones.get(self._ship_count)
        if forced and forced not in self._silent_watchers_set:
            self._silent_watchers_set.add(forced)
            self._watcher_join_order.append(forced)
            return forced

        # Base probability rises with shipping; capped
        p = min(0.05 + (self._ship_count * 0.01), 0.40)
        # Sleep increases the *feeling* of being watched
        p = min(p + (self._sleep_debt * 0.005), 0.60)

        gravity_set, mult = self._gravity_candidates(thing)
        p = min(p * mult, 0.80)

        if random.random() > p:
            return None

        # Prefer gravity pool first (this is the actual fix)
        preferred_pool = gravity_set - self._silent_watchers_set
        general_pool = self._watcher_pool_general - self._silent_watchers_set

        pool = preferred_pool if preferred_pool else general_pool
        if not pool:
            return None

        watcher = random.sample(pool, 1)[0]  # no list conversion
        self._silent_watchers_set.add(watcher)
        self._watcher_join_order.append(watcher)
        return watcher

    # ─────────────────────────────
    # Blockers
    # ─────────────────────────────
    def _blocker_permissiveness(self) -> float:
        # How likely we are to ignore real blockers due to sleep + hubris.
        state = self.sleep_state

        if state == SleepState.RESTED:
            return 0.0
        if state == SleepState.FINE:
            return 0.05
        if state == SleepState.TIRED:
            return 0.20
        if state == SleepState.UNHINGED:
            return 0.50
        return 0.0

    def _need_for_current_goal(self, concept: str) -> bool:
        return True

    def _learn_precisely_enough(self, concept: str) -> None:
        # Placeholder: docs → micro-test → implement → ship.
        pass

    def _identify_blocker(self, thing: str) -> Blocker:
        t = thing.lower()

        # Hard block at COOKED
        if self._sleep_debt >= 12:
            return Blocker(
                kind=BlockerKind.SLEEP,
                label="sleep_debt_critical",
                hint="close laptop, drink water, 20m nap, then resume. this is not optional.",
            )

        real_blocker = self._check_real_blockers(t)
        if real_blocker:
            # Sometimes ignore blockers when tired/unhinged
            if random.random() < self._blocker_permissiveness():
                if self.sleep_state == SleepState.UNHINGED:
                    print(f"  ⚠️  [{self.sleep_state.value}] Ignoring blocker: {real_blocker.label}. YOLO.")
                return Blocker(
                    kind=BlockerKind.IGNORED,
                    label=real_blocker.label,
                    hint="ignored due to sleep delirium",
                )
            return real_blocker

        return Blocker(kind=BlockerKind.NONE, label="none")

    def _check_real_blockers(self, t: str) -> Optional[Blocker]:
        if "impossible" in t:
            return Blocker(
                kind=BlockerKind.CONSTRAINT,
                label="constraint_mismatch_or_missing_primitive",
                hint="rewrite the constraints or invent the primitive",
            )
        if any(k in t for k in ["rag", "architecture", "memory", "replacement"]):
            return Blocker(
                kind=BlockerKind.SPEC,
                label="define_interface_and_success_criteria",
                hint="write the demo and the failure case first",
            )
        if any(k in t for k in ["ssl", "cert", "tls", "oauth", "auth"]):
            return Blocker(
                kind=BlockerKind.INTERFACE,
                label="authentication_wizardry_required",
                hint="you will learn one cursed acronym and it will fix everything",
            )
        return None

    # ─────────────────────────────
    # Shipping
    # ─────────────────────────────
    def _ship(self, thing: str) -> Tuple[str, Optional[str]]:
        self.last_shipped = datetime.now()
        self._ship_count += 1
        self._sleep_debt += 1

        watcher = self._maybe_add_silent_watcher(thing)

        slug = thing.strip().replace(" ", "-").lower()
        base = f"pip install {slug}"

        # Output mutates with sleep (and mild hubris)
        if self.sleep_state == SleepState.UNHINGED:
            return (f"{base}  # trust me bro", watcher)
        if self.sleep_state == SleepState.COOKED:
            return (f"{base}  # this will work. i have no evidence.", watcher)

        # Permission-to-be-weird sometimes appends nonsense telemetry
        if random.random() < (self.permission_to_be_weird * 0.15):
            return (f"{base}  # entropy≈{self.permission_to_be_weird:.2f}", watcher)

        return (base, watcher)

    def _extract_learning(self, thing: str, blocker: Blocker, command: str, watcher: Optional[str]) -> str:
        state = self.sleep_state

        if blocker.kind == BlockerKind.IGNORED:
            base = f"Ignored blocker ({blocker.label}) → {command}"
        elif blocker:
            base = f"Resolved {blocker.kind.value}: {blocker.label} → {command}"
        else:
            base = f"Shipped clean: {command}"

        if watcher:
            base += f" | watcher+ {watcher}"

        if state == SleepState.UNHINGED:
            return f"{base} (judgment questionable)"
        if state == SleepState.TIRED:
            return f"{base} (review tomorrow)"
        return base

    # ─────────────────────────────
    # Thinking / compression
    # ─────────────────────────────
    def _geometric_intuition(self, system: str) -> str:
        s = system.lower()
        state = self.sleep_state

        if s == "memory":
            base = "memory is a lossy compressor; retrieval is a control policy over recall trajectories."
        elif s in {"alignment", "safety"}:
            base = "alignment is constraint satisfaction under adversarial selection pressure."
        elif s in {"identity", "self"}:
            base = "self is a stabilized attractor with narrative as its compression codec."
        else:
            base = f"{system} is a constraint manifold with a control surface."

        if state == SleepState.UNHINGED:
            return f"{base} also everything is connected. EVERYTHING."
        if state == SleepState.TIRED:
            return f"{base} ...probably."
        return base

    def _make_it_a_bar(self, system: str, concept: str) -> str:
        bars_normal = [
            f"{concept} Toroidal field? Yeah. I built the donut.",
            f"{concept} Location: {self.location}. Also: shipping.",
            f"{concept} Partner status: {self.partner_response}. Proceeding anyway.",
            f"{concept} I didn't 'learn' it. I collided with it until it behaved.",
        ]
        bars_tired = [
            f"{concept} The donut is a metaphor. Or is it? *stares at wall*",
            f"{concept} What if the real architecture was the sleep we didn't get along the way?",
            f"{concept} Every bug is a prayer asking to be rewritten.",
        ]
        bars_unhinged = [
            f"{concept} I AM THE DONUT. THE DONUT IS ME.",
            f"{concept} *3am insight that will either be genius or nonsense*",
            f"{concept} The constraint manifold whispers. I listen. We ship.",
            f"{concept} Everything is O(1) if you believe hard enough.",
            f"{concept} Reality is just a unit test with bad coverage.",
            f"{concept} The README is an attractor. The code is the path home.",
        ]

        pool = bars_normal.copy()
        if self.sleep_state in {SleepState.TIRED, SleepState.UNHINGED, SleepState.COOKED}:
            pool.extend(bars_tired)
        if self.sleep_state in {SleepState.UNHINGED, SleepState.COOKED}:
            pool.extend(bars_unhinged)

        # Extra ridiculous: under UNHINGED, occasionally output a "prophecy"
        if self.sleep_state == SleepState.UNHINGED and random.random() < 0.25:
            return f"{concept} — i saw the architecture in a cereal bowl. it was correct."

        return random.choice(pool)

    # ─────────────────────────────
    # Social / creative transforms
    # ─────────────────────────────
    def _write_diss_track(self, criticism: str) -> str:
        if self.sleep_state == SleepState.UNHINGED:
            return f"Barbed couplets generated about: {criticism} (bars may not make sense but they FEEL right)"
        return f"Barbed couplets generated about: {criticism}"

    def _write_changelog_as_threat(self, criticism: str) -> str:
        base = (
            "CHANGELOG.md\n"
            f"- fixed: {criticism}\n"
            "- added: feature that makes the complaint obsolete\n"
            "- deprecated: doubt\n"
        )
        if self.sleep_state == SleepState.UNHINGED:
            base += "- experimental: mass hubris\n"
        return base

    def _write_unit_tests_as_hexes(self, criticism: str) -> str:
        # Yes, this is ridiculous. That's the point.
        curses = [
            "test_you_find_peace_in_the_stacktrace",
            "test_your_prs_are_small_and_your_merge_conflicts_are_imaginary",
            "test_your_repro_steps_are_honest",
            "test_you_do_not_summon_brad",
        ]
        return (
            "tests/test_haters.py\n"
            f"def test_{random.choice(curses)}():\n"
            f"    assert '{criticism}' not in reality\n"
        )

    def _unhinged_response(self, criticism: str) -> str:
        responses = [
            f"'{criticism}'? That's exactly what someone who doesn't understand toroidal consciousness would say.",
            f"I've been awake for... *checks notes* ...too long. Anyway, {criticism} is wrong because vibes.",
            f"Counter-argument: I shipped 3 things while you typed that. Next.",
            f"*adds '{criticism}' to the grudge log* This will be a bar someday.",
        ]
        return random.choice(responses)

    def _ship_harder(self, criticism: str) -> str:
        self.do("harder thing")
        if self.sleep_state == SleepState.UNHINGED:
            return (
                f"Shipped EVEN HARDER in response to: {criticism}. "
                "Is this sustainable? No. Am I stopping? Also no."
            )
        return f"Shipped harder in response to: {criticism}"

    def __repr__(self) -> str:
        state = self.sleep_state
        state_note = f", sleep_state={state.value}" if state != SleepState.RESTED else ""
        return (
            f"GarretSutherland(one-man op, ships before lunch, "
            f"doesn't care what you think, partner says 'huh?'{state_note})"
        )


# Tiny runnable demo (only executes when explicitly run, AND lore is enabled)
if __name__ == "__main__":
    g = GarretSutherland()
    print(g)
    print(f"location = {g.location}")
    print(f"permission_to_be_weird = {g.permission_to_be_weird:.2f}")
    print()

    for x in ["memory layer", "RAG replacement", "impossible thing", "robot edge inference", "donut protocol"]:
        r = g.do(x)
        print(f">>> g.do({x!r})")
        print(r)
        print("note:", r.note)
        if r.watcher:
            print("watchers:", g.silent_watchers[-3:])
        print()

    print(">>> g.think_about_system('memory')")
    print(g.think_about_system("memory"))
    print()

    print(">>> g.respond_to_haters('just a wrapper')")
    print(g.respond_to_haters("just a wrapper"))
