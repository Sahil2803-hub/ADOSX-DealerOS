from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Disagreement


def dashboard(request):
    """
    Render the DealerOS reconciliation dashboard.
    """
    return render(request, "dashboard.html")


@api_view(["GET"])
def disagreement_list(request):
    """
    Return all reconciliation disagreements.
    """

    disagreements = Disagreement.objects.all().order_by("record_ref")

    data = []

    for disagreement in disagreements:
        data.append({
            "id": disagreement.id,
            "record_ref": disagreement.record_ref,
            "reason": disagreement.reason,
            "system_a_value": (
                float(disagreement.system_a_value)
                if disagreement.system_a_value is not None
                else None
            ),
            "system_b_value": (
                float(disagreement.system_b_value)
                if disagreement.system_b_value is not None
                else None
            ),
            "location_id": disagreement.location_id,
        })

    return Response({
        "count": len(data),
        "results": data,
    })


@api_view(["GET"])
def disagreement_summary(request):
    """
    Return a summary of reconciliation results.
    """

    disagreements = Disagreement.objects.all()

    summary = {
        "total": disagreements.count(),

        "missing_in_b": disagreements.filter(
            reason="missing_in_b"
        ).count(),

        "orphan_b": disagreements.filter(
            reason="orphan_b"
        ).count(),

        "duplicate_b": disagreements.filter(
            reason="duplicate_b"
        ).count(),

        "value_mismatch": disagreements.filter(
            reason="value_mismatch"
        ).count(),
    }

    return Response(summary)