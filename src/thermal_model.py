from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


FlowRegime = Literal["laminar", "turbulent"]


@dataclass(frozen=True)
class ThermalInputs:
    # Given data
    q_w: float = 150.0
    t_ambient_c: float = 25.0

    # Processor die
    die_length_m: float = 0.0525
    die_width_m: float = 0.045

    # Heat sink geometry
    sink_length_m: float = 0.09
    sink_width_m: float = 0.116
    base_thickness_m: float = 0.0025
    n_fins: int = 60
    fin_thickness_m: float = 0.0008
    fin_height_m: float = 0.0245

    # Materials
    k_al_w_mk: float = 167.0
    # NOTE: The provided Excel reference uses 0.2 C/W to match the published
    # example outputs (R_total ~= 0.373, Tj ~= 80.96C at 150W, 25C ambient).
    r_jc_c_w: float = 0.2

    # TIM
    k_tim_w_mk: float = 4.0
    tim_thickness_m: float = 0.0001

    # Air properties @ 25C
    air_k_w_mk: float = 0.0262
    air_nu_m2_s: float = 1.57e-5
    air_pr: float = 0.71
    air_velocity_m_s: float = 1.0


@dataclass(frozen=True)
class ThermalResults:
    die_area_m2: float
    fin_spacing_m: float
    re: float
    nu: float
    h_w_m2k: float
    a_total_m2: float
    r_jc_c_w: float
    r_tim_c_w: float
    r_cond_c_w: float
    r_conv_c_w: float
    r_hs_c_w: float
    r_total_c_w: float
    t_junction_c: float
    flow_regime: FlowRegime


def _fin_spacing(width_m: float, n_fins: int, fin_thickness_m: float) -> float:
    if n_fins < 2:
        raise ValueError("n_fins must be >= 2")
    return (width_m - (n_fins * fin_thickness_m)) / (n_fins - 1)


def _nusselt(re: float, pr: float, fin_spacing_m: float, sink_length_m: float) -> tuple[float, FlowRegime]:
    # Matches the reference PDF logic:
    # laminar: Sieder-Tate-like developing flow correlation
    # turbulent: Dittus-Boelter
    if re < 2300:
        nu = 1.86 * (re * pr * (2 * fin_spacing_m / sink_length_m)) ** (1.0 / 3.0)
        return nu, "laminar"
    nu = 0.023 * (re**0.8) * (pr**0.3)
    return nu, "turbulent"


def _convection_area(
    sink_length_m: float,
    sink_width_m: float,
    n_fins: int,
    fin_height_m: float,
    fin_thickness_m: float,
) -> float:
    # Total area exposed to convection (common heat-sink approximation):
    # - fin sides
    # - fin tops
    # - exposed base between fins
    area_fin_sides = n_fins * 2.0 * fin_height_m * sink_length_m
    area_fin_tops = n_fins * fin_thickness_m * sink_length_m
    area_base_exposed = (sink_width_m - n_fins * fin_thickness_m) * sink_length_m
    return area_fin_sides + area_fin_tops + area_base_exposed


def solve_thermal_model(inputs: ThermalInputs) -> ThermalResults:
    die_area = inputs.die_length_m * inputs.die_width_m

    fin_spacing = _fin_spacing(inputs.sink_width_m, inputs.n_fins, inputs.fin_thickness_m)

    re = (inputs.air_velocity_m_s * fin_spacing) / inputs.air_nu_m2_s
    nu, regime = _nusselt(re, inputs.air_pr, fin_spacing, inputs.sink_length_m)

    h = (nu * inputs.air_k_w_mk) / (2.0 * fin_spacing)

    a_total = _convection_area(
        sink_length_m=inputs.sink_length_m,
        sink_width_m=inputs.sink_width_m,
        n_fins=inputs.n_fins,
        fin_height_m=inputs.fin_height_m,
        fin_thickness_m=inputs.fin_thickness_m,
    )

    r_tim = inputs.tim_thickness_m / (inputs.k_tim_w_mk * die_area)
    r_cond = inputs.base_thickness_m / (inputs.k_al_w_mk * die_area)
    r_conv = 1.0 / (h * a_total)

    r_hs = r_cond + r_conv
    r_total = inputs.r_jc_c_w + r_tim + r_hs

    t_junction = inputs.t_ambient_c + (inputs.q_w * r_total)

    return ThermalResults(
        die_area_m2=die_area,
        fin_spacing_m=fin_spacing,
        re=re,
        nu=nu,
        h_w_m2k=h,
        a_total_m2=a_total,
        r_jc_c_w=inputs.r_jc_c_w,
        r_tim_c_w=r_tim,
        r_cond_c_w=r_cond,
        r_conv_c_w=r_conv,
        r_hs_c_w=r_hs,
        r_total_c_w=r_total,
        t_junction_c=t_junction,
        flow_regime=regime,
    )


def results_as_dict(results: ThermalResults) -> dict[str, Any]:
    return asdict(results)
