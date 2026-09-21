def calculate_reduction(
    current_rate,
    target_rate,
    affected_volume,
):
    """
    Calculate reduction in rate and affected volume.
    """

    rate_reduction = (
        current_rate - target_rate
    )

    volume_reduction = (
        affected_volume * rate_reduction
    )

    return {
        "current_rate": current_rate,
        "target_rate": target_rate,
        "rate_reduction": rate_reduction,
        "affected_volume": affected_volume,
        "estimated_reduction": volume_reduction,
    }


def calculate_money_impact(
    affected_volume,
    value_per_case,
):
    """
    Calculate estimated monetary impact.

    The value_per_case must come from the actual
    assignment data/business assumptions.
    """

    return (
        affected_volume * value_per_case
    )