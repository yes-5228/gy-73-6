import csv
import io
import json

from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date, parse_time
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from tracking.models import ProgressEvent
from workers.models import Worker

from .models import MoveOrder
from .serializers import order_to_dict


def read_json(request):
    if not request.body:
        return {}
    return json.loads(request.body.decode("utf-8"))


def bad_request(message):
    return JsonResponse({"error": message}, status=400)


def apply_order_filters(queryset, params):
    status = params.get("status")
    if status:
        queryset = queryset.filter(status=status)

    move_date_from = params.get("move_date_from")
    if move_date_from:
        date_from = parse_date(move_date_from)
        if date_from:
            queryset = queryset.filter(move_date__gte=date_from)

    move_date_to = params.get("move_date_to")
    if move_date_to:
        date_to = parse_date(move_date_to)
        if date_to:
            queryset = queryset.filter(move_date__lte=date_to)

    service_area = params.get("service_area")
    if service_area:
        queryset = queryset.filter(service_area=service_area)

    worker_id = params.get("worker_id")
    if worker_id:
        try:
            wid = int(worker_id)
            queryset = queryset.filter(models.Q(assigned_to_id=wid) | models.Q(claimed_by_id=wid))
        except (ValueError, TypeError):
            pass

    has_exception = params.get("has_exception")
    if has_exception in ("1", "true", "True"):
        queryset = queryset.filter(has_exception=True)
    elif has_exception in ("0", "false", "False"):
        queryset = queryset.filter(has_exception=False)

    return queryset


@csrf_exempt
@require_http_methods(["GET", "POST"])
def order_list(request):
    if request.method == "GET":
        queryset = MoveOrder.objects.select_related("claimed_by", "assigned_to")
        queryset = apply_order_filters(queryset, request.GET)
        return JsonResponse({"orders": [order_to_dict(order) for order in queryset]})

    payload = read_json(request)
    required = ["customer_name", "customer_phone", "origin", "destination", "move_date", "move_time"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return bad_request(f"缺少字段: {', '.join(missing)}")

    order = MoveOrder.objects.create(
        customer_name=payload["customer_name"],
        customer_phone=payload["customer_phone"],
        origin=payload["origin"],
        destination=payload["destination"],
        service_area=payload.get("service_area", ""),
        move_date=parse_date(payload["move_date"]),
        move_time=parse_time(payload["move_time"]),
        items=payload.get("items", ""),
        note=payload.get("note", ""),
        has_exception=payload.get("has_exception", False),
    )
    ProgressEvent.objects.create(order=order, stage=ProgressEvent.STAGE_CREATED, message="客户已提交搬家预约")
    return JsonResponse(order_to_dict(order, include_detail=True), status=201)


@csrf_exempt
@require_http_methods(["GET"])
def order_export(request):
    queryset = MoveOrder.objects.select_related("claimed_by", "assigned_to")
    queryset = apply_order_filters(queryset, request.GET)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "订单ID",
        "客户姓名",
        "客户电话",
        "服务区域",
        "出发地",
        "目的地",
        "预约日期",
        "预约时间",
        "物品",
        "备注",
        "状态",
        "异常标记",
        "抢单师傅",
        "派单师傅",
        "创建时间",
    ])
    for order in queryset:
        writer.writerow([
            order.id,
            order.customer_name,
            order.customer_phone,
            order.service_area,
            order.origin,
            order.destination,
            order.move_date.isoformat(),
            order.move_time.strftime("%H:%M"),
            order.items,
            order.note,
            order.get_status_display(),
            "是" if order.has_exception else "否",
            order.claimed_by.name if order.claimed_by else "",
            order.assigned_to.name if order.assigned_to else "",
            order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="orders.csv"'
    return response


@require_http_methods(["GET"])
def order_detail(request, order_id):
    order = get_object_or_404(MoveOrder.objects.select_related("claimed_by", "assigned_to"), pk=order_id)
    return JsonResponse(order_to_dict(order, include_detail=True))


@csrf_exempt
@require_http_methods(["POST"])
def claim_order(request, order_id):
    order = get_object_or_404(MoveOrder, pk=order_id)
    payload = read_json(request)
    worker = get_object_or_404(Worker, pk=payload.get("worker_id"))
    if order.status != MoveOrder.STATUS_PENDING:
        return bad_request("只有待抢单订单可以抢单")

    order.claimed_by = worker
    order.status = MoveOrder.STATUS_CLAIMED
    order.save(update_fields=["claimed_by", "status", "updated_at"])
    ProgressEvent.objects.create(order=order, stage=ProgressEvent.STAGE_CLAIMED, worker=worker, message=f"{worker.name} 已抢单")
    return JsonResponse(order_to_dict(order, include_detail=True))


@csrf_exempt
@require_http_methods(["POST"])
def assign_order(request, order_id):
    order = get_object_or_404(MoveOrder, pk=order_id)
    payload = read_json(request)
    worker = get_object_or_404(Worker, pk=payload.get("worker_id"))
    if order.status not in [MoveOrder.STATUS_PENDING, MoveOrder.STATUS_CLAIMED]:
        return bad_request("当前订单状态不能派单")

    order.assigned_to = worker
    order.status = MoveOrder.STATUS_ASSIGNED
    if not order.claimed_by:
        order.claimed_by = worker
    order.save(update_fields=["assigned_to", "claimed_by", "status", "updated_at"])
    ProgressEvent.objects.create(order=order, stage=ProgressEvent.STAGE_ASSIGNED, worker=worker, message=f"平台已派单给 {worker.name}")
    return JsonResponse(order_to_dict(order, include_detail=True))
