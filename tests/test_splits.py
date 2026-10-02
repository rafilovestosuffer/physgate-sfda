"""Split tests. The leakage assertion is tested by FEEDING IT A LEAK, not just by passing clean splits."""
import copy, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "data_prep"))

import pytest
import split
from split import LeakageError


def test_folds_follow_the_mechanical_rule():
    split.verify_folds_follow_rule()


def test_hand_edited_fold_is_caught():
    cfg = copy.deepcopy(split.load_cfg())
    cfg["pu"]["real_outer"]["A"] = ["KA22", "KA15", "KA16"]   # swap in a "nicer" bearing by hand
    cfg["pu"]["real_outer"]["B"] = ["KA04", "KA30"]
    with pytest.raises(ValueError, match="mechanical rule"):
        split.verify_folds_follow_rule(cfg)


def test_assertion_fires_on_a_deliberate_leak():
    with pytest.raises(LeakageError, match="KA04"):
        split.assert_no_leak({"K001", "KA04"}, {"K004", "KA04"}, "deliberately_leaky")


@pytest.mark.parametrize("reverse", [False, True])
def test_m1_bearingwise_is_disjoint_both_directions(reverse):
    b = split.pu_task_bearings("M1_PU_L3_bearingwise", reverse=reverse)
    assert not (b["source"] & b["target"])
    assert {"K001", "K002", "K003"} <= (b["target"] if reverse else b["source"])   # healthy split too
    assert len(b["source"]) and len(b["target"])


def test_b3_artificial_to_real_is_disjoint_and_correctly_populated():
    b = split.pu_task_bearings("B3_PU_artificial_to_real")
    assert not (b["source"] & b["target"])
    assert all(x.startswith(("K0", "KA0", "KI0")) and x not in {"KA04", "KI04"} for x in b["source"]
               if x.startswith(("KA", "KI")))
    assert {"KA04", "KA15", "KA16", "KA22", "KA30"} <= b["target"]
    assert not ({"KB23", "KB24", "KB27"} & (b["source"] | b["target"]))    # compound excluded


def test_leaky_config_is_rejected_when_not_declared_leaky():
    cfg = copy.deepcopy(split.load_cfg())
    cfg["tasks"]["M1_PU_L3_bearingwise"]["target_fold"] = "A"               # same fold both sides
    with pytest.raises(LeakageError):
        split.pu_task_bearings("M1_PU_L3_bearingwise", cfg=cfg)


def test_m0_is_explicitly_declared_leaky():
    """Track R reproductions are allowed to leak ONLY because they are labelled as such."""
    t = split.load_cfg()["tasks"]
    assert t["M0_PU_as_published"]["leaky"] is True
    assert t["M0_JNU_as_published"]["leaky"] is True
