from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Disagreement, Location


def dashboard(request):
    """
    Render the DealerOS reconciliation dashboard.
    """
    return render(request, "dashboard.html")


def get_tenant_disagreements(request):
    """
    Return disagreements belonging only to the requested organization.

    The organization is resolved through the Location table rather than
    trusting a disagreement record to contain an organization directly.
    """
    org_id = request.query_params.get("org_id")

    if not org_id:
        return None, Response(
            {
                "error": "org_id query parameter is required."
            },
            status=400,
        )

    tenant_locations = Location.objects.filter(
        org_id=org_id
    ).values_list(
        "location_id",
        flat=True,
    )

    disagreements = Disagreement.objects.filter(
        location_id__in=tenant_locations
    ).order_by("record_ref")

    return disagreements, None


@api_view(["GET"])
def disagreement_list(request):
    """
    Return disagreements for a single organization.
    """
    disagreements, error_response = get_tenant_disagreements(request)

    if error_response:
        return error_response

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
    Return reconciliation summary for a single organization.
    """
    disagreements, error_response = get_tenant_disagreements(request)

    if error_response:
        return error_response

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