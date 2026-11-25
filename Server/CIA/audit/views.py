#from urllib import request
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import AuditLog
from audit.utils import log_action
from Agency.models import Person, Operation, Report

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from .security import sanitize_audit_data


@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_logs(request):
    # Superuser check
    if not request.user.is_superuser:
        return Response(
            {"error": "Unauthorized. Superuser only."},
            status=status.HTTP_403_FORBIDDEN
        )

    logs = AuditLog.objects.all().order_by("-timestamp")

    # Filtering
    id =request.GET.get("id")
    user = request.GET.get("user")
    action = request.GET.get("action")
    start = request.GET.get("start")
    end = request.GET.get("end")

    if id:
        logs = logs.filter(id=id)

    if user:
        logs = logs.filter(user__username=user)

    if action:
        allowed_actions = ["CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "VIEW", "SEARCH", "API_CALL"]
        if action in allowed_actions:
            logs = logs.filter(action_type=action)

    if start and end:
        logs = logs.filter(timestamp__range=[start, end])

    # Pagination
    page_number = request.GET.get("page", 1)
    paginator = Paginator(logs, 20)
    page_obj = paginator.get_page(page_number)

    # Serialize logs
    data = [
        {
            "id": log.id,
            "user": str(log.user),
           "action": log.action_type,
            "resource": log.resource,
            "resource_id": log.resource_id,
            "ip": log.ip_address,
            "time": log.timestamp,
            "description": log.description,
            "old_data": sanitize_audit_data(log.old_data),
            "new_data": sanitize_audit_data(log.new_data),
            "request_data": sanitize_audit_data(log.request_data),
            "response_data": sanitize_audit_data(log.response_data),
            
        }
        for log in page_obj
    ]

    return Response({
        "results": data,
        "page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count
    })

@require_http_methods(["GET"])
@login_required
def get_report(request, id):
    report = get_object_or_404(Report, id=id)

    response_data = {
        "id": report.id,
        "operation": report.operation.id,
        "author": str(report.author) if report.author else None,
        "subject": report.subject,
        "created_at": report.created_at,
    }

   
    log_action(
        user=request.user,
        action_type="VIEW",
        description="Viewed intelligence report",
        resource="Report",
        resource_id=id,
        request=request,
        new_data=response_data

    )

    return JsonResponse(response_data)

@require_http_methods(["POST", "PUT", "PATCH"])
@login_required
def update_operation(request, id):
    operation = get_object_or_404(Operation, id=id)

    old_data = {
        "mission_name": str(operation.mission_name),
        "clearance_type": operation.clearance_type,
    }

  
    operation.clearance_type = "TOP-SECRET"
    operation.save()

    new_data = {
        "mission_name": str(operation.mission_name),
        "clearance_type": operation.clearance_type,
    }

    log_action(
        user=request.user,
        action_type="UPDATE",
        description="Updated operation",
        resource="Operation",
        resource_id=id,
        request=request,
        old_data=old_data,
        new_data=new_data
    )

    return JsonResponse({
        "message": "Operation updated",
        "operation_id": id
    })


@require_http_methods(["GET"])
@login_required
def get_person(request, id):
    person = get_object_or_404(Person, id=id)

    response_data = {
        "id": person.id,
        "full_name": person.full_name,
        "person_type": person.person_type,
        "unit_type": person.unit_type,
        "clearance_type": person.clearance_type,
        "status": person.status,
    }

   
    log_action(
        user=request.user,
        action_type="VIEW",
        description="Viewed personnel profile",
        resource="Person",
        resource_id=id,
        request=request,
        new_data=response_data,
    )

    return JsonResponse(response_data)
