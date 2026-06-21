from datetime import date, time, timedelta

from django.core.management.base import BaseCommand

from orders.models import MoveOrder
from tracking.models import ProgressEvent
from workers.models import Worker


class Command(BaseCommand):
    help = "Seed demo workers and moving orders."

    def handle(self, *args, **options):
        workers = [
            {
                "name": "张师傅",
                "phone": "13800000001",
                "vehicle": "4.2米厢货",
                "service_area": "浦东新区",
                "rating": 4.9,
            },
            {
                "name": "李师傅",
                "phone": "13800000002",
                "vehicle": "金杯面包车",
                "service_area": "徐汇区",
                "rating": 4.8,
            },
            {
                "name": "王师傅",
                "phone": "13800000003",
                "vehicle": "6.8米货车",
                "service_area": "静安区",
                "rating": 4.7,
            },
        ]
        for data in workers:
            Worker.objects.get_or_create(phone=data["phone"], defaults=data)

        if MoveOrder.objects.exists():
            self.stdout.write(self.style.SUCCESS("Demo data already exists."))
            return

        orders = [
            {
                "customer_name": "陈女士",
                "customer_phone": "13900000088",
                "origin": "上海市徐汇区漕溪北路 88 号",
                "destination": "上海市浦东新区张江路 168 号",
                "service_area": "徐汇区",
                "move_date": date.today() + timedelta(days=2),
                "move_time": time(9, 30),
                "items": "两室一厅家具、冰箱、洗衣机、纸箱 20 个",
                "note": "需要拆装一张双人床",
                "status": MoveOrder.STATUS_PENDING,
                "has_exception": False,
            },
            {
                "customer_name": "刘先生",
                "customer_phone": "13900000089",
                "origin": "上海市浦东新区世纪大道 100 号",
                "destination": "上海市浦东新区陆家嘴环路 1000 号",
                "service_area": "浦东新区",
                "move_date": date.today() + timedelta(days=1),
                "move_time": time(14, 0),
                "items": "办公用品、电脑 10 台、文件柜 5 个",
                "note": "周末搬迁，需电梯",
                "status": MoveOrder.STATUS_ASSIGNED,
                "has_exception": False,
            },
            {
                "customer_name": "赵女士",
                "customer_phone": "13900000090",
                "origin": "上海市静安区南京西路 1266 号",
                "destination": "上海市徐汇区衡山路 516 号",
                "service_area": "静安区",
                "move_date": date.today(),
                "move_time": time(10, 0),
                "items": "钢琴一台、沙发、电视柜",
                "note": "钢琴需额外保护，客户临时改时间",
                "status": MoveOrder.STATUS_IN_PROGRESS,
                "has_exception": True,
            },
            {
                "customer_name": "孙先生",
                "customer_phone": "13900000091",
                "origin": "上海市浦东新区张江高科路 500 号",
                "destination": "上海市松江区文汇路 1000 号",
                "service_area": "浦东新区",
                "move_date": date.today() - timedelta(days=1),
                "move_time": time(8, 0),
                "items": "一室一厅家具、洗衣机、纸箱 15 个",
                "note": "",
                "status": MoveOrder.STATUS_COMPLETED,
                "has_exception": False,
            },
        ]
        worker_list = list(Worker.objects.all())
        for idx, data in enumerate(orders):
            order = MoveOrder.objects.create(**data)
            if idx == 1 and worker_list:
                order.assigned_to = worker_list[0]
                order.claimed_by = worker_list[0]
                order.save()
            if idx == 2 and worker_list:
                order.assigned_to = worker_list[1] if len(worker_list) > 1 else worker_list[0]
                order.claimed_by = order.assigned_to
                order.save()
            ProgressEvent.objects.create(order=order, stage=ProgressEvent.STAGE_CREATED, message="客户已提交搬家预约")

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
